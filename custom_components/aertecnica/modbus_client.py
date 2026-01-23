"""Modbus client for Aertecnica Central Vacuum."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant

from .const import (
    CARD_MODELS,
    DEFAULT_TIMEOUT,
    FLAG_BAG_HOURS_NO_DECIMAL,
    FLAG_CARD_HOURS_NO_DECIMAL,
    FLAG_FILTER_HOURS_NO_DECIMAL,
    FLAG_MAX_TIME_MINUTES,
    FLAG_MOTOR_HOURS_NO_DECIMAL,
    FLAG_TEMPERATURE_NO_DECIMAL,
    LOCK_APPLIANCE,
    LOCK_DIRTY_FILTER,
    LOCK_FULL_BAG,
    LOCK_MAX_PRESSURE,
    LOCK_MAX_TEMPERATURE,
    LOCK_MAX_TIME,
    LOCK_NUM_STARTS,
    MODBUS_TYPE_RTU,
    MODBUS_TYPE_TCP,
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
    STATUS_MICRO_LINE_CLOSED,
    STATUS_MOTOR_ON,
    STATUS_PID_MASK,
    STATUS_PREALARM_APPLIANCE,
    STATUS_PREALARM_DIRTY_FILTER,
    STATUS_PREALARM_FULL_BAG,
    STATUS_PREALARM_MAX_PRESSURE,
    STATUS_PREALARM_MAX_TEMP,
    STATUS_PREALARM_MAX_TIME,
    STATUS_PREALARM_NUM_STARTS,
    STATUS_STANDBY_ACTIVE,
    STATUS_START_STOP_ACTIVE,
    STATUS_TEMP_RESET_PROHIBITED,
    CONTROL_SERIAL_START,
    CONTROL_SERIAL_STOP,
)

_LOGGER = logging.getLogger(__name__)


class AertecnicaModbusClient:
    """Modbus client for Aertecnica Central Vacuum system."""

    def __init__(
        self,
        hass: HomeAssistant,
        modbus_type: str,
        slave_id: int,
        host: str | None = None,
        port: int | None = None,
        serial_port: str | None = None,
        baudrate: int | None = None,
    ) -> None:
        """Initialize the Modbus client."""
        self.hass = hass
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

    async def connect(self) -> bool:
        """Connect to the Modbus device."""
        if self._client is None:
            return False

        try:
            async with self._lock:
                result = await self._client.connect()
                if result:
                    _LOGGER.info("Connected to Aertecnica Modbus device")
                else:
                    _LOGGER.error("Failed to connect to Aertecnica Modbus device")
                return result
        except Exception as err:
            _LOGGER.error("Error connecting to Modbus device: %s", err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        if self._client is None:
            return

        try:
            async with self._lock:
                self._client.close()
                _LOGGER.info("Disconnected from Aertecnica Modbus device")
        except Exception as err:
            _LOGGER.error("Error disconnecting from Modbus device: %s", err)

    async def _read_holding_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        """Read holding registers."""
        if self._client is None:
            return None

        try:
            async with self._lock:
                result = await self._client.read_holding_registers(
                    address=address,
                    count=count,
                    slave=self.slave_id,
                )

                if result.isError():
                    _LOGGER.error(
                        "Error reading register 0x%04x: %s", address, result
                    )
                    return None

                return result.registers
        except ModbusException as err:
            _LOGGER.error("Modbus exception reading register 0x%04x: %s", address, err)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error reading register 0x%04x: %s", address, err)
            return None

    async def _write_register(self, address: int, value: int) -> bool:
        """Write a single register."""
        if self._client is None:
            return False

        try:
            async with self._lock:
                result = await self._client.write_register(
                    address=address,
                    value=value,
                    slave=self.slave_id,
                )

                if result.isError():
                    _LOGGER.error("Error writing register 0x%04x: %s", address, result)
                    return False

                _LOGGER.debug("Successfully wrote value %s to register 0x%04x", value, address)
                return True
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing register 0x%04x: %s", address, err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error writing register 0x%04x: %s", address, err)
            return False

    async def read_all_data(self) -> dict[str, Any] | None:
        """Read all data from the device."""
        # Read all registers in one call (0x0000 to 0x0011 = 18 registers)
        registers = await self._read_holding_registers(REG_CARD_MODEL, 18)

        if registers is None or len(registers) < 18:
            _LOGGER.error("Failed to read all registers")
            return None

        # Parse interpretation flags
        flags = registers[REG_INTERPRETATION_FLAGS]

        # Helper function to convert values based on flags
        def get_hours_value(value: int, flag: int) -> float:
            """Convert hours value based on decimal flag."""
            if flags & flag:
                return float(value)  # No decimal
            return value / 10.0  # With decimal

        def get_temperature_value(value: int) -> float:
            """Convert temperature value (signed word)."""
            # Convert unsigned to signed
            if value > 32767:
                value = value - 65536
            if flags & FLAG_TEMPERATURE_NO_DECIMAL:
                return float(value)
            return value / 10.0

        def get_residual_time_value(value: int) -> tuple[float, str]:
            """Convert residual time value and return with unit."""
            if flags & FLAG_MAX_TIME_MINUTES:
                return float(value), "min"
            return float(value), "s"

        # Parse all data
        data = {
            "card_model": CARD_MODELS.get(registers[REG_CARD_MODEL], "Unknown"),
            "card_model_id": registers[REG_CARD_MODEL],
            "interpretation_flags": flags,
            "card_hours": get_hours_value(
                registers[REG_CARD_HOURS], FLAG_CARD_HOURS_NO_DECIMAL
            ),
            "motor_hours": get_hours_value(
                registers[REG_MOTOR_HOURS], FLAG_MOTOR_HOURS_NO_DECIMAL
            ),
            "bag_hours": get_hours_value(
                registers[REG_BAG_HOURS], FLAG_BAG_HOURS_NO_DECIMAL
            ),
            "filter_hours": get_hours_value(
                registers[REG_FILTER_HOURS], FLAG_FILTER_HOURS_NO_DECIMAL
            ),
            "bag_level": registers[REG_BAG_LEVEL],
            "filter_level": registers[REG_FILTER_LEVEL],
            "pressure_level": registers[REG_PRESSURE_LEVEL],
            "pressure_level_name": PRESSURE_LEVEL_NAMES.get(
                registers[REG_PRESSURE_LEVEL], "Unknown"
            ),
            "pressure_1": registers[REG_PRESSURE_1],
            "pressure_2": registers[REG_PRESSURE_2],
            "pressure_diff": registers[REG_PRESSURE_DIFF],
            "temperature": get_temperature_value(registers[REG_TEMPERATURE]),
            "system_status": registers[REG_SYSTEM_STATUS],
            "lock_status": registers[REG_LOCK_STATUS],
            "motor_power": registers[REG_MOTOR_POWER],
            "pressure_setpoint": registers[REG_PRESSURE_SETPOINT],
        }

        # Add residual time with proper unit
        residual_time, time_unit = get_residual_time_value(
            registers[REG_RESIDUAL_MAX_TIME]
        )
        data["residual_max_time"] = residual_time
        data["residual_max_time_unit"] = time_unit

        # Parse system status bits
        system_status = registers[REG_SYSTEM_STATUS]
        data["pid_mode"] = system_status & STATUS_PID_MASK
        data["micro_line_closed"] = bool(system_status & STATUS_MICRO_LINE_CLOSED)
        data["start_stop_active"] = bool(system_status & STATUS_START_STOP_ACTIVE)
        data["motor_on"] = bool(system_status & STATUS_MOTOR_ON)
        data["standby_active"] = bool(system_status & STATUS_STANDBY_ACTIVE)
        data["temp_reset_prohibited"] = bool(
            system_status & STATUS_TEMP_RESET_PROHIBITED
        )

        # Parse pre-alarms
        data["prealarm_max_time"] = bool(system_status & STATUS_PREALARM_MAX_TIME)
        data["prealarm_max_pressure"] = bool(
            system_status & STATUS_PREALARM_MAX_PRESSURE
        )
        data["prealarm_num_starts"] = bool(system_status & STATUS_PREALARM_NUM_STARTS)
        data["prealarm_dirty_filter"] = bool(
            system_status & STATUS_PREALARM_DIRTY_FILTER
        )
        data["prealarm_full_bag"] = bool(system_status & STATUS_PREALARM_FULL_BAG)
        data["prealarm_max_temp"] = bool(system_status & STATUS_PREALARM_MAX_TEMP)
        data["prealarm_appliance"] = bool(system_status & STATUS_PREALARM_APPLIANCE)

        # Parse locks
        lock_status = registers[REG_LOCK_STATUS]
        data["lock_max_time"] = bool(lock_status & LOCK_MAX_TIME)
        data["lock_max_pressure"] = bool(lock_status & LOCK_MAX_PRESSURE)
        data["lock_num_starts"] = bool(lock_status & LOCK_NUM_STARTS)
        data["lock_dirty_filter"] = bool(lock_status & LOCK_DIRTY_FILTER)
        data["lock_full_bag"] = bool(lock_status & LOCK_FULL_BAG)
        data["lock_max_temperature"] = bool(lock_status & LOCK_MAX_TEMPERATURE)
        data["lock_appliance"] = bool(lock_status & LOCK_APPLIANCE)

        # Determine if any lock or prealarm is active
        data["any_lock_active"] = bool(lock_status & 0x00BF)
        data["any_prealarm_active"] = bool(system_status & 0xBF00)

        return data

    async def read_card_model(self) -> str | None:
        """Read the card model."""
        registers = await self._read_holding_registers(REG_CARD_MODEL, 1)
        if registers:
            return CARD_MODELS.get(registers[0], "Unknown")
        return None

    async def write_motor_control(self, start: bool) -> bool:
        """Control motor start/stop via serial control."""
        if start:
            value = CONTROL_SERIAL_START
        else:
            value = CONTROL_SERIAL_STOP

        return await self._write_register(REG_RESET_CONTROL, value)

    async def write_reset_lock(self) -> bool:
        """Send reset lock command."""
        return await self._write_register(REG_RESET_CONTROL, RESET_LOCK)

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._client is not None and self._client.connected
