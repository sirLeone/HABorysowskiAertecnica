"""Button platform for Aertecnica Central Vacuum."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AertecnicaConfigEntry
from .coordinator import AertecnicaCoordinator
from .entity import AertecnicaEntity

_LOGGER = logging.getLogger(__name__)

RESET_LOCK_BUTTON = ButtonEntityDescription(
    key="reset_lock",
    translation_key="reset_lock",
    icon="mdi:lock-reset",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AertecnicaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica buttons."""
    async_add_entities([AertecnicaResetLockButton(entry.runtime_data, entry)])


class AertecnicaResetLockButton(AertecnicaEntity, ButtonEntity):
    """Button that resets an active lock on the vacuum unit."""

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: AertecnicaConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry, RESET_LOCK_BUTTON)

    async def async_press(self) -> None:
        """Send the reset lock command."""
        _LOGGER.debug("Sending reset lock command")
        if not await self.coordinator.async_reset_lock():
            raise HomeAssistantError("Failed to send reset lock command")
