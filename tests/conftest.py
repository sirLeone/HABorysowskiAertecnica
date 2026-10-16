"""Shared fixtures for the Aertecnica tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aertecnica.const import (
    CONF_HOST,
    CONF_MODBUS_TYPE,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DOMAIN,
    MODBUS_TYPE_TCP,
)
from custom_components.aertecnica.modbus_client import parse_registers

# Register block 0x0000..0x0011 for a "Perfect" card with:
# - hours with decimals, residual time in minutes (flags = 0x0020)
# - motor on, pre-alarm "full bag" (system status = 0x0010 | 0x1000)
# - no locks
SAMPLE_REGISTERS: list[int] = [
    1,  # card model: Perfect
    0x0020,  # interpretation flags
    1234,  # card hours -> 123.4
    567,  # motor hours -> 56.7
    89,  # bag hours -> 8.9
    10,  # filter hours -> 1.0
    2,  # bag level
    3,  # filter level
    2,  # pressure level -> OK
    150,  # pressure 1
    140,  # pressure 2
    10,  # pressure diff
    250,  # temperature -> 25.0
    0x0010 | 0x1000,  # system status
    0x0000,  # lock status
    75,  # motor power
    200,  # pressure setpoint
    42,  # residual max time -> 42 min
]

SAMPLE_DATA = parse_registers(SAMPLE_REGISTERS)

TCP_ENTRY_DATA = {
    CONF_MODBUS_TYPE: MODBUS_TYPE_TCP,
    CONF_HOST: "192.0.2.10",
    CONF_PORT: 502,
    CONF_SLAVE_ID: 1,
    CONF_SCAN_INTERVAL: 5,
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading custom integrations in all tests."""


@pytest.fixture
def mock_client() -> Generator[MagicMock]:
    """Mock the Modbus client used by the coordinator."""
    with patch(
        "custom_components.aertecnica.coordinator.AertecnicaModbusClient",
        autospec=True,
    ) as client_cls:
        client = client_cls.return_value
        client.is_connected = False
        client.connect = AsyncMock(return_value=True)
        client.disconnect = AsyncMock()
        client.read_all_data = AsyncMock(return_value=dict(SAMPLE_DATA))
        client.write_motor_control = AsyncMock(return_value=True)
        client.write_reset_lock = AsyncMock(return_value=True)
        yield client


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Return a TCP config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Aertecnica (Perfect)",
        data=TCP_ENTRY_DATA,
        unique_id="tcp_192.0.2.10_502",
        entry_id="test_entry",
    )
