"""Config flow for Aertecnica Central Vacuum integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    BAUDRATE_OPTIONS,
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

SCAN_INTERVAL_SELECTOR = vol.All(vol.Coerce(int), vol.Range(min=1, max=60))
SLAVE_ID_SELECTOR = vol.All(vol.Coerce(int), vol.Range(min=1, max=247))

RTU_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERIAL_PORT, default="/dev/ttyUSB0"): str,
        vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In(
            BAUDRATE_OPTIONS
        ),
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): SLAVE_ID_SELECTOR,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): SCAN_INTERVAL_SELECTOR,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)

TCP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): SLAVE_ID_SELECTOR,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): SCAN_INTERVAL_SELECTOR,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect to the device."""


async def validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> str:
    """Validate the connection and return the entry title."""
    client = AertecnicaModbusClient(
        modbus_type=data[CONF_MODBUS_TYPE],
        slave_id=data[CONF_SLAVE_ID],
        host=data.get(CONF_HOST),
        port=data.get(CONF_PORT),
        serial_port=data.get(CONF_SERIAL_PORT),
        baudrate=data.get(CONF_BAUDRATE),
    )

    try:
        if not await client.connect():
            raise CannotConnect("Could not connect to the Modbus device")

        card_model = await client.read_card_model()
        if card_model is None:
            raise CannotConnect("Could not read card model")
    finally:
        await client.disconnect()

    return f"{DEFAULT_NAME} ({card_model})"


class AertecnicaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aertecnica Central Vacuum."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            if user_input[CONF_MODBUS_TYPE] == MODBUS_TYPE_RTU:
                return await self.async_step_rtu()
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

    async def _async_try_create_entry(
        self,
        modbus_type: str,
        unique_id: str,
        user_input: dict[str, Any],
        errors: dict[str, str],
    ) -> FlowResult | None:
        """Validate the connection and create the entry.

        Returns None and fills in errors when validation fails.
        """
        user_input[CONF_MODBUS_TYPE] = modbus_type

        try:
            title = await validate_connection(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
            return None
        except Exception:
            _LOGGER.exception("Unexpected exception during validation")
            errors["base"] = "unknown"
            return None

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=title, data=user_input)

    async def async_step_rtu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle RTU configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            result = await self._async_try_create_entry(
                MODBUS_TYPE_RTU,
                f"{MODBUS_TYPE_RTU}_{user_input[CONF_SERIAL_PORT]}",
                user_input,
                errors,
            )
            if result is not None:
                return result

        return self.async_show_form(
            step_id="rtu", data_schema=RTU_SCHEMA, errors=errors
        )

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle TCP configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            result = await self._async_try_create_entry(
                MODBUS_TYPE_TCP,
                f"{MODBUS_TYPE_TCP}_{user_input[CONF_HOST]}_{user_input[CONF_PORT]}",
                user_input,
                errors,
            )
            if result is not None:
                return result

        return self.async_show_form(
            step_id="tcp", data_schema=TCP_SCHEMA, errors=errors
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
        # Deliberately not assigned to self.config_entry: that assignment is
        # deprecated and removed in Home Assistant 2025.12.
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_scan_interval = self._entry.options.get(
            CONF_SCAN_INTERVAL,
            self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=current_scan_interval
                ): SCAN_INTERVAL_SELECTOR,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
