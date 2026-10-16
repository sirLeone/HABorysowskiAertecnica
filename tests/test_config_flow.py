"""Tests for the config and options flows."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aertecnica.const import (
    CONF_BAUDRATE,
    CONF_HOST,
    CONF_MODBUS_TYPE,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    DOMAIN,
    MODBUS_TYPE_RTU,
    MODBUS_TYPE_TCP,
)

from .conftest import TCP_ENTRY_DATA


@pytest.fixture
def mock_validation_client() -> Generator[MagicMock]:
    """Mock the Modbus client used for validating the connection."""
    with patch(
        "custom_components.aertecnica.config_flow.AertecnicaModbusClient",
        autospec=True,
    ) as client_cls:
        client = client_cls.return_value
        client.connect = AsyncMock(return_value=True)
        client.disconnect = AsyncMock()
        client.read_card_model = AsyncMock(return_value="Perfect")
        yield client


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Skip the real entry setup."""
    with patch(
        "custom_components.aertecnica.async_setup_entry", return_value=True
    ) as setup:
        yield setup


async def test_tcp_flow_creates_entry(
    hass: HomeAssistant, mock_validation_client: MagicMock, mock_setup_entry: AsyncMock
) -> None:
    """The TCP flow validates the connection and creates an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODBUS_TYPE: MODBUS_TYPE_TCP}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "tcp"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "192.0.2.10", CONF_PORT: 502, CONF_SLAVE_ID: 1, CONF_SCAN_INTERVAL: 5},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Aertecnica (Perfect)"
    assert result["data"][CONF_MODBUS_TYPE] == MODBUS_TYPE_TCP
    assert result["data"][CONF_HOST] == "192.0.2.10"
    assert result["result"].unique_id == "tcp_192.0.2.10_502"
    mock_validation_client.disconnect.assert_awaited_once()
    assert mock_setup_entry.call_count == 1


async def test_rtu_flow_creates_entry(
    hass: HomeAssistant, mock_validation_client: MagicMock, mock_setup_entry: AsyncMock
) -> None:
    """The RTU flow creates an entry keyed by the serial port."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODBUS_TYPE: MODBUS_TYPE_RTU}
    )
    assert result["step_id"] == "rtu"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_SERIAL_PORT: "/dev/ttyUSB0", CONF_BAUDRATE: 19200, CONF_SLAVE_ID: 1},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_MODBUS_TYPE] == MODBUS_TYPE_RTU
    assert result["result"].unique_id == "rtu_/dev/ttyUSB0"


async def test_tcp_flow_cannot_connect(
    hass: HomeAssistant, mock_validation_client: MagicMock
) -> None:
    """A failed connection shows the cannot_connect error."""
    mock_validation_client.connect.return_value = False

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODBUS_TYPE: MODBUS_TYPE_TCP}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.10", CONF_PORT: 502, CONF_SLAVE_ID: 1}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_tcp_flow_unexpected_error(
    hass: HomeAssistant, mock_validation_client: MagicMock
) -> None:
    """An unexpected exception shows the unknown error."""
    mock_validation_client.read_card_model.side_effect = RuntimeError("boom")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODBUS_TYPE: MODBUS_TYPE_TCP}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.10", CONF_PORT: 502, CONF_SLAVE_ID: 1}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test_tcp_flow_already_configured(
    hass: HomeAssistant, mock_validation_client: MagicMock
) -> None:
    """Configuring the same host and port twice aborts."""
    MockConfigEntry(
        domain=DOMAIN, data=TCP_ENTRY_DATA, unique_id="tcp_192.0.2.10_502"
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODBUS_TYPE: MODBUS_TYPE_TCP}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.10", CONF_PORT: 502, CONF_SLAVE_ID: 1}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_client: MagicMock
) -> None:
    """The options flow stores a new scan interval."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 15}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert config_entry.options == {CONF_SCAN_INTERVAL: 15}
