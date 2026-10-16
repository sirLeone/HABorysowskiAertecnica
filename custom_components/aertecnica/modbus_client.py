"""Modbus client for Aertecnica Central Vacuum."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
import inspect
import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    CARD_MODELS,
    CONTROL_SERIAL_START,
    CONTROL_SERIAL_STOP,
    DATA_BLOCK_SIZE,
    DATA_BLOCK_START,
    DEFAULT_TIMEOUT,
    FLAG_BAG_HOURS_NO_DECIMAL,
    FLAG_CARD_HOURS_NO_DECIMAL,
    FLAG_FILTER_HOURS_NO_DECIMAL,
    FLAG_MAX_TIME_MINUTES,
    FLAG_MOTOR_HOURS_NO_DECIMAL,
    FLAG_TEMPERATURE_NO_DECIMAL,
    LOCK_ANY_MASK,
    LOCK_BITS,
    MODBUS_TYPE_RTU,
    MODBUS_TYPE_TCP,
    PREALARM_ANY_MASK,
    PREALARM_BITS,
    PRESSURE_LEVEL_NAMES,
    REG_BAG_HOURS,
    REG_BAG_LEVEL,
    REG_CARD_HOURS,
    REG_CARD_MODEL,
    REG_FILTER_HOURS,
    REG_FILTER_LEVEL,
    REG_INTERPRETATION_FLAGS,
    REG_LOCK_STATUS,
    REG_MOTOR_HOURS,
    REG_MOTOR_POWER,
    REG_PRESSURE_1,
    REG_PRESSURE_2,
    REG_PRESSURE_DIFF,
    REG_PRESSURE_LEVEL,
    REG_PRESSURE_SETPOINT,
    REG_RESET_CONTROL,
    REG_RESIDUAL_MAX_TIME,
    REG_SYSTEM_STATUS,
    REG_TEMPERATURE,
    RESET_LOCK,
    SERIAL_DATABITS,
    SERIAL_PARITY,
    SERIAL_STOPBITS,
    STATUS_PID_MASK,
    SYSTEM_STATUS_BITS,
)

_LOGGER = logging.getLogger(__name__)

# Hour counters: data key, register, "no decimal" interpretation flag
HOURS_REGISTERS: tuple[tuple[str, int, int], ...] = (
    ("card_hours", REG_CARD_HOURS, FLAG_CARD_HOURS_NO_DECIMAL),
    ("motor_hours", REG_MOTOR_HOURS, FLAG_MOTOR_HOURS_NO_DECIMAL),
    ("bag_hours", REG_BAG_HOURS, FLAG_BAG_HOURS_NO_DECIMAL),
    ("filter_hours", REG_FILTER_HOURS, FLAG_FILTER_HOURS_NO_DECIMAL),
)

# Registers copied to the data dict verbatim
RAW_REGISTERS: tuple[tuple[str, int], ...] = (
    ("bag_level", REG_BAG_LEVEL),
    ("filter_level", REG_FILTER_LEVEL),
    ("pressure_level", REG_PRESSURE_LEVEL),
    ("pressure_1", REG_PRESSURE_1),
    ("pressure_2", REG_PRESSURE_2),
    ("pressure_diff", REG_PRESSURE_DIFF),
    ("system_status", REG_SYSTEM_STATUS),
    ("lock_status", REG_LOCK_STATUS),
    ("motor_power", REG_MOTOR_POWER),
    ("pressure_setpoint", REG_PRESSURE_SETPOINT),
)


def to_signed_word(value: int) -> int:
    """Interpret a 16-bit register value as a signed integer."""
    return value - 0x10000 if value > 0x7FFF else value


def parse_registers(registers: Sequence[int]) -> dict[str, Any]:
    """Convert the raw data block (0x0000..0x0011) into coordinator data.

    Pure function so it can be tested without any Modbus hardware.
    """
    if len(registers) < DATA_BLOCK_SIZE:
        raise ValueError(
            f"Expected {DATA_BLOCK_SIZE} registers, got {len(registers)}"
        )

    flags = registers[REG_INTERPRETATION_FLAGS]

    data: dict[str, Any] = {
        "card_model": CARD_MODELS.get(registers[REG_CARD_MODEL], "Unknown"),
        "card_model_id": registers[REG_CARD_MODEL],
        "interpretation_flags": flags,
    }

    # Hour counters: value is in tenths of an hour unless the flag says otherwise
    for key, register, no_decimal_flag in HOURS_REGISTERS:
        value = registers[register]
        data[key] = float(value) if flags & no_decimal_flag else value / 10.0

    for key, register in RAW_REGISTERS:
        data[key] = registers[register]

    data["pressure_level_name"] = PRESSURE_LEVEL_NAMES.get(
        registers[REG_PRESSURE_LEVEL], "Unknown"
    )

    temperature = to_signed_word(registers[REG_TEMPERATURE])
    data["temperature"] = (
        float(temperature)
        if flags & FLAG_TEMPERATURE_NO_DECIMAL
        else temperature / 10.0
    )

    data["residual_max_time"] = float(registers[REG_RESIDUAL_MAX_TIME])
    data["residual_max_time_unit"] = "min" if flags & FLAG_MAX_TIME_MINUTES else "s"

    system_status = registers[REG_SYSTEM_STATUS]
    data["pid_mode"] = system_status & STATUS_PID_MASK
    for key, bit in SYSTEM_STATUS_BITS.items():
        data[key] = bool(system_status & bit)
    for key, (bit, _) in PREALARM_BITS.items():
        data[key] = bool(system_status & bit)

    lock_status = registers[REG_LOCK_STATUS]
    for key, (bit, _) in LOCK_BITS.items():
        data[key] = bool(lock_status & bit)

    data["any_lock_active"] = bool(lock_status & LOCK_ANY_MASK)
    data["any_prealarm_active"] = bool(system_status & PREALARM_ANY_MASK)

    return data


def detect_device_id_kwarg(client: Any) -> str:
    """Return the keyword pymodbus uses for the unit id.

    pymodbus < 3.10 calls it ``slave``; 3.10 and later call it ``device_id``.
    """
    params = inspect.signature(client.read_holding_registers).parameters
    return "device_id" if "device_id" in params else "slave"


class AertecnicaModbusClient:
    """Modbus client for Aertecnica Central Vacuum system."""

    def __init__(
        self,
        modbus_type: str,
        slave_id: int,
        host: str | None = None,
        port: int | None = None,
        serial_port: str | None = None,
        baudrate: int | None = None,
    ) -> None:
        """Initialize the Modbus client.

        Must be called from within a running event loop: recent pymodbus
        versions bind the client to the loop at construction time.
        """
        self.modbus_type = modbus_type
        self.slave_id = slave_id
        self._client: AsyncModbusSerialClient | AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

        if modbus_type == MODBUS_TYPE_TCP:
            self._client = AsyncModbusTcpClient(
                host=host,
                port=port,
                timeout=DEFAULT_TIMEOUT,
            )
        elif modbus_type == MODBUS_TYPE_RTU:
            self._client = AsyncModbusSerialClient(
                port=serial_port,
                baudrate=baudrate,
                bytesize=SERIAL_DATABITS,
                stopbits=SERIAL_STOPBITS,
                parity=SERIAL_PARITY,
                timeout=DEFAULT_TIMEOUT,
            )

        self._device_kwargs: dict[str, int] = (
            {detect_device_id_kwarg(self._client): slave_id}
            if self._client is not None
            else {}
        )

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._client is not None and self._client.connected

    async def connect(self) -> bool:
        """Connect to the Modbus device."""
        if self._client is None:
            return False

        try:
            async with self._lock:
                result = await self._client.connect()
        except Exception as err:  # noqa: BLE001 - pymodbus raises assorted errors
            _LOGGER.error("Error connecting to Modbus device: %s", err)
            return False

        if result:
            _LOGGER.info("Connected to Aertecnica Modbus device")
        else:
            _LOGGER.error("Failed to connect to Aertecnica Modbus device")
        return bool(result)

    async def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        if self._client is None:
            return

        try:
            async with self._lock:
                self._client.close()
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error disconnecting from Modbus device: %s", err)
        else:
            _LOGGER.info("Disconnected from Aertecnica Modbus device")

    async def _request(
        self,
        description: str,
        method: Callable[..., Awaitable[Any]],
        **kwargs: Any,
    ) -> Any | None:
        """Run a Modbus request under the lock, returning None on any failure."""
        try:
            async with self._lock:
                result = await method(**kwargs, **self._device_kwargs)
        except ModbusException as err:
            _LOGGER.error("Modbus exception while %s: %s", description, err)
            return None
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Unexpected error while %s: %s", description, err)
            return None

        if result.isError():
            _LOGGER.error("Device error while %s: %s", description, result)
            return None

        return result

    async def _read_holding_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        """Read holding registers."""
        if self._client is None:
            return None

        result = await self._request(
            f"reading register 0x{address:04x}",
            self._client.read_holding_registers,
            address=address,
            count=count,
        )
        return None if result is None else list(result.registers)

    async def _write_register(self, address: int, value: int) -> bool:
        """Write a single register."""
        if self._client is None:
            return False

        result = await self._request(
            f"writing register 0x{address:04x}",
            self._client.write_register,
            address=address,
            value=value,
        )
        if result is None:
            return False

        _LOGGER.debug("Wrote value 0x%04x to register 0x%04x", value, address)
        return True

    async def read_all_data(self) -> dict[str, Any] | None:
        """Read and parse the full data block from the device."""
        registers = await self._read_holding_registers(
            DATA_BLOCK_START, DATA_BLOCK_SIZE
        )
        if registers is None:
            return None

        try:
            return parse_registers(registers)
        except ValueError as err:
            _LOGGER.error("Failed to parse device data: %s", err)
            return None

    async def read_card_model(self) -> str | None:
        """Read the card model."""
        registers = await self._read_holding_registers(REG_CARD_MODEL, 1)
        if not registers:
            return None
        return CARD_MODELS.get(registers[0], "Unknown")

    async def write_motor_control(self, start: bool) -> bool:
        """Control motor start/stop via serial control."""
        value = CONTROL_SERIAL_START if start else CONTROL_SERIAL_STOP
        return await self._write_register(REG_RESET_CONTROL, value)

    async def write_reset_lock(self) -> bool:
        """Send reset lock command."""
        return await self._write_register(REG_RESET_CONTROL, RESET_LOCK)
