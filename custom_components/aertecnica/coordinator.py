"""Data update coordinator for Aertecnica Central Vacuum."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_BAUDRATE,
    CONF_HOST,
    CONF_MODBUS_TYPE,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .modbus_client import AertecnicaModbusClient

_LOGGER = logging.getLogger(__name__)


class AertecnicaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Aertecnica data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

        # Initialize Modbus client
        modbus_type = entry.data[CONF_MODBUS_TYPE]
        slave_id = entry.data[CONF_SLAVE_ID]

        self.client = AertecnicaModbusClient(
            hass=hass,
            modbus_type=modbus_type,
            slave_id=slave_id,
            host=entry.data.get(CONF_HOST),
            port=entry.data.get(CONF_PORT),
            serial_port=entry.data.get(CONF_SERIAL_PORT),
            baudrate=entry.data.get(CONF_BAUDRATE),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        if not self.client.is_connected:
            _LOGGER.debug("Reconnecting to Modbus device")
            if not await self.client.connect():
                raise UpdateFailed("Failed to connect to Modbus device")

        data = await self.client.read_all_data()

        if data is None:
            raise UpdateFailed("Failed to read data from Modbus device")

        _LOGGER.debug("Successfully updated data: %s", data)
        return data

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await self.client.disconnect()

    async def async_motor_start(self) -> bool:
        """Start the motor."""
        result = await self.client.write_motor_control(start=True)
        if result:
            await self.async_request_refresh()
        return result

    async def async_motor_stop(self) -> bool:
        """Stop the motor."""
        result = await self.client.write_motor_control(start=False)
        if result:
            await self.async_request_refresh()
        return result

    async def async_reset_lock(self) -> bool:
        """Reset lock."""
        result = await self.client.write_reset_lock()
        if result:
            await self.async_request_refresh()
        return result
