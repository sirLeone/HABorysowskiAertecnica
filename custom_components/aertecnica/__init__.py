"""The Aertecnica Central Vacuum integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import AertecnicaCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.SWITCH,
]

AertecnicaConfigEntry = ConfigEntry[AertecnicaCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AertecnicaConfigEntry) -> bool:
    """Set up Aertecnica Central Vacuum from a config entry."""
    _LOGGER.debug("Setting up Aertecnica integration")

    coordinator = AertecnicaCoordinator(hass, entry)
    # Raises ConfigEntryNotReady on failure so Home Assistant retries later
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload the entry when options (e.g. scan interval) change
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: AertecnicaConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Aertecnica integration")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_shutdown()

    return unload_ok


async def async_update_listener(hass: HomeAssistant, entry: AertecnicaConfigEntry) -> None:
    """Handle config entry options update."""
    await hass.config_entries.async_reload(entry.entry_id)
