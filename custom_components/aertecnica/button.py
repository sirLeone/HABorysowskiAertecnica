"""Button platform for Aertecnica Central Vacuum."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AertecnicaCoordinator
from .entity import AertecnicaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica buttons."""
    coordinator: AertecnicaCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([AertecnicaResetLockButton(coordinator, entry)])


class AertecnicaResetLockButton(AertecnicaEntity, ButtonEntity):
    """Button that resets an active lock on the vacuum unit."""

    _attr_icon = "mdi:lock-reset"

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry, "reset_lock", "Reset Lock")

    async def async_press(self) -> None:
        """Send the reset lock command."""
        _LOGGER.debug("Sending reset lock command")
        if not await self.coordinator.async_reset_lock():
            raise HomeAssistantError("Failed to send reset lock command")
