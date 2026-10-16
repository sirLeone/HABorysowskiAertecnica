"""Tests for the pure Modbus parsing helpers and the client wrapper."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pymodbus.exceptions import ModbusException

from custom_components.aertecnica.const import (
    DATA_BLOCK_SIZE,
    MODBUS_TYPE_RTU,
    MODBUS_TYPE_TCP,
    REG_RESET_CONTROL,
    RESET_LOCK,
    CONTROL_SERIAL_START,
    CONTROL_SERIAL_STOP,
)
from custom_components.aertecnica.modbus_client import (
    AertecnicaModbusClient,
    detect_device_id_kwarg,
    parse_registers,
    to_signed_word,
)

from .conftest import SAMPLE_REGISTERS


def test_to_signed_word() -> None:
    """16-bit register values are interpreted as two's complement."""
    assert to_signed_word(0) == 0
    assert to_signed_word(250) == 250
    assert to_signed_word(0x7FFF) == 32767
    assert to_signed_word(0x8000) == -32768
    assert to_signed_word(0xFF38) == -200


def test_parse_registers_sample() -> None:
    """The sample block is decoded into the expected data dict."""
    data = parse_registers(SAMPLE_REGISTERS)

    assert data["card_model"] == "Perfect"
    assert data["card_model_id"] == 1
    assert data["card_hours"] == 123.4
    assert data["motor_hours"] == 56.7
    assert data["bag_hours"] == 8.9
    assert data["filter_hours"] == 1.0
    assert data["bag_level"] == 2
    assert data["filter_level"] == 3
    assert data["pressure_level"] == 2
    assert data["pressure_level_name"] == "OK"
    assert data["pressure_1"] == 150
    assert data["pressure_2"] == 140
    assert data["pressure_diff"] == 10
    assert data["temperature"] == 25.0
    assert data["motor_power"] == 75
    assert data["pressure_setpoint"] == 200
    assert data["residual_max_time"] == 42.0
    assert data["residual_max_time_unit"] == "min"

    assert data["pid_mode"] == 0
    assert data["motor_on"] is True
    assert data["standby_active"] is False
    assert data["prealarm_full_bag"] is True
    assert data["prealarm_dirty_filter"] is False
    assert data["any_prealarm_active"] is True
    assert data["any_lock_active"] is False


def test_parse_registers_flags_and_locks() -> None:
    """Interpretation flags and lock bits change how values are decoded."""
    registers = list(SAMPLE_REGISTERS)
    registers[1] = 0x001F  # all "no decimal" flags set, time in seconds
    registers[12] = 0xFF38  # -200 -> -200.0 without decimals
    registers[13] = 0x0002 | 0x0040  # PID maintain pressure + standby
    registers[14] = 0x0001 | 0x0020  # locks: max time + max temperature

    data = parse_registers(registers)

    assert data["card_hours"] == 1234.0
    assert data["motor_hours"] == 567.0
    assert data["temperature"] == -200.0
    assert data["residual_max_time_unit"] == "s"
    assert data["pid_mode"] == 2
    assert data["standby_active"] is True
    assert data["motor_on"] is False
    assert data["any_prealarm_active"] is False
    assert data["lock_max_time"] is True
    assert data["lock_max_temperature"] is True
    assert data["lock_full_bag"] is False
    assert data["any_lock_active"] is True


def test_parse_registers_unknown_values() -> None:
    """Unknown card models and pressure levels fall back to 'Unknown'."""
    registers = list(SAMPLE_REGISTERS)
    registers[0] = 99
    registers[8] = 7

    data = parse_registers(registers)

    assert data["card_model"] == "Unknown"
    assert data["pressure_level_name"] == "Unknown"


def test_parse_registers_short_block() -> None:
    """A truncated register block is rejected."""
    with pytest.raises(ValueError):
        parse_registers(SAMPLE_REGISTERS[:-1])


def test_detect_device_id_kwarg() -> None:
    """The unit id keyword follows the pymodbus signature."""

    def new_api(address: int, *, count: int = 1, device_id: int = 1) -> None:
        pass

    def old_api(address: int, *, count: int = 1, slave: int = 1) -> None:
        pass

    assert (
        detect_device_id_kwarg(SimpleNamespace(read_holding_registers=new_api))
        == "device_id"
    )
    assert (
        detect_device_id_kwarg(SimpleNamespace(read_holding_registers=old_api))
        == "slave"
    )


async def test_detect_device_id_kwarg_with_real_pymodbus() -> None:
    """The installed pymodbus accepts whichever keyword we detect."""
    client = AertecnicaModbusClient(MODBUS_TYPE_TCP, slave_id=1, host="127.0.0.1", port=502)

    assert client._device_kwargs in ({"device_id": 1}, {"slave": 1})


@pytest.fixture
def fake_pymodbus() -> MagicMock:
    """A fake pymodbus client with the new keyword API."""
    fake = MagicMock()
    fake.connected = True

    async def read_holding_registers(address: int, *, count: int = 1, device_id: int = 1):
        return SimpleNamespace(
            isError=lambda: False,
            registers=SAMPLE_REGISTERS[address : address + count],
        )

    async def write_register(address: int, value: int, *, device_id: int = 1):
        fake.written.append((address, value, device_id))
        return SimpleNamespace(isError=lambda: False)

    fake.written = []
    fake.read_holding_registers = read_holding_registers
    fake.write_register = write_register
    return fake


@pytest.fixture
def client(fake_pymodbus: MagicMock) -> AertecnicaModbusClient:
    """An Aertecnica client wrapping the fake pymodbus client."""
    with patch(
        "custom_components.aertecnica.modbus_client.AsyncModbusSerialClient",
        return_value=fake_pymodbus,
    ):
        return AertecnicaModbusClient(
            MODBUS_TYPE_RTU, slave_id=7, serial_port="/dev/ttyUSB0", baudrate=19200
        )


async def test_client_read_all_data(client: AertecnicaModbusClient) -> None:
    """The full block is read with the right unit id and parsed."""
    assert client.is_connected
    assert client._device_kwargs == {"device_id": 7}

    data = await client.read_all_data()

    assert data is not None
    assert data["motor_hours"] == 56.7
    assert await client.read_card_model() == "Perfect"


async def test_client_writes(client: AertecnicaModbusClient, fake_pymodbus: MagicMock) -> None:
    """Motor control and reset lock write the documented bits."""
    assert await client.write_motor_control(True)
    assert await client.write_motor_control(False)
    assert await client.write_reset_lock()

    assert fake_pymodbus.written == [
        (REG_RESET_CONTROL, CONTROL_SERIAL_START, 7),
        (REG_RESET_CONTROL, CONTROL_SERIAL_STOP, 7),
        (REG_RESET_CONTROL, RESET_LOCK, 7),
    ]


async def test_client_handles_errors(client: AertecnicaModbusClient, fake_pymodbus: MagicMock) -> None:
    """Device errors and exceptions are turned into None/False results."""
    error_result = SimpleNamespace(isError=lambda: True, registers=[])
    fake_pymodbus.read_holding_registers = AsyncMock(return_value=error_result)
    assert await client.read_all_data() is None

    fake_pymodbus.read_holding_registers = AsyncMock(side_effect=ModbusException("boom"))
    assert await client.read_card_model() is None

    fake_pymodbus.write_register = AsyncMock(side_effect=OSError("port gone"))
    assert await client.write_reset_lock() is False


async def test_client_short_block_is_rejected(client: AertecnicaModbusClient, fake_pymodbus: MagicMock) -> None:
    """A device answering with too few registers yields no data."""
    short = SimpleNamespace(isError=lambda: False, registers=[1] * (DATA_BLOCK_SIZE - 1))
    fake_pymodbus.read_holding_registers = AsyncMock(return_value=short)

    assert await client.read_all_data() is None
