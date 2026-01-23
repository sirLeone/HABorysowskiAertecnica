"""Config flow for Aertecnica Central Vacuum integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BAUDRATE,
    CONF_HOST,
    CONF_MODBUS_TYPE,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    DEFAULT_BAUDRATE,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    MODBUS_TYPE_RTU,
    MODBUS_TYPE_TCP,
)
from .modbus_client import AertecnicaModbusClient

_LOGGER = logging.getLogger(__name__)


async def validate_rtu_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate RTU connection."""
    client = AertecnicaModbusClient(
        hass=hass,
        modbus_type=MODBUS_TYPE_RTU,
        serial_port=data[CONF_SERIAL_PORT],
        baudrate=data[CONF_BAUDRATE],
        slave_id=data[CONF_SLAVE_ID],
    )

    try:
        await client.connect()
        result = await client.read_card_model()
        await client.disconnect()

        if result is None:
            raise ValueError("Could not read card model")

        return {"title": f"{DEFAULT_NAME} ({result})"}
    except Exception as err:
        _LOGGER.error("Error connecting to Modbus RTU: %s", err)
        raise


async def validate_tcp_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate TCP connection."""
    client = AertecnicaModbusClient(
        hass=hass,
        modbus_type=MODBUS_TYPE_TCP,
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        slave_id=data[CONF_SLAVE_ID],
    )

    try:
        await client.connect()
        result = await client.read_card_model()
        await client.disconnect()

        if result is None:
            raise ValueError("Could not read card model")

        return {"title": f"{DEFAULT_NAME} ({result})"}
    except Exception as err:
        _LOGGER.error("Error connecting to Modbus TCP: %s", err)
        raise


class AertecnicaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aertecnica Central Vacuum."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._modbus_type: str | None = None
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._modbus_type = user_input[CONF_MODBUS_TYPE]

            if self._modbus_type == MODBUS_TYPE_RTU:
                return await self.async_step_rtu()
            else:
                return await self.async_step_tcp()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_MODBUS_TYPE, default=MODBUS_TYPE_TCP): vol.In(
                    {
                        MODBUS_TYPE_TCP: "Modbus TCP",
                        MODBUS_TYPE_RTU: "Modbus RTU (Serial)",
                    }
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_step_rtu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle RTU configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_MODBUS_TYPE] = MODBUS_TYPE_RTU

            try:
                info = await validate_rtu_connection(self.hass, user_input)
            except Exception:
                _LOGGER.exception("Unexpected exception during RTU validation")
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{MODBUS_TYPE_RTU}_{user_input[CONF_SERIAL_PORT]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SERIAL_PORT, default="/dev/ttyUSB0"): str,
                vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In(
                    [9600, 19200, 38400, 57600, 115200]
                ),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=247)
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="rtu", data_schema=data_schema, errors=errors
        )

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle TCP configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_MODBUS_TYPE] = MODBUS_TYPE_TCP

            try:
                info = await validate_tcp_connection(self.hass, user_input)
            except Exception:
                _LOGGER.exception("Unexpected exception during TCP validation")
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{MODBUS_TYPE_TCP}_{user_input[CONF_HOST]}_{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=247)
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="tcp", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AertecnicaOptionsFlowHandler:
        """Get the options flow for this handler."""
        return AertecnicaOptionsFlowHandler(config_entry)


class AertecnicaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Aertecnica."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.data.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
