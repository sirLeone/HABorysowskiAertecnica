"""Switch platform for Aertecnica Central Vacuum."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOCK_BITS, PREALARM_BITS
from .coordinator import AertecnicaCoordinator
from .entity import AertecnicaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica switches."""
    coordinator: AertecnicaCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([AertecnicaMotorSwitch(coordinator, entry)])


class AertecnicaMotorSwitch(AertecnicaEntity, SwitchEntity):
    """Representation of an Aertecnica motor switch."""

    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry, "motor_switch", "Motor")

    @property
    def is_on(self) -> bool | None:
        """Return true if the motor is on."""
        if not self.coordinator.data:
            return None

        return self.coordinator.data.get("motor_on", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the motor on."""
        _LOGGER.debug("Turning on Aertecnica motor")
        if not await self.coordinator.async_motor_start():
            _LOGGER.error("Failed to turn on motor")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the motor off."""
        _LOGGER.debug("Turning off Aertecnica motor")
        if not await self.coordinator.async_motor_stop():
            _LOGGER.error("Failed to turn off motor")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        data = self.coordinator.data
        attributes = {
            "motor_power": data.get("motor_power"),
            "standby_active": data.get("standby_active"),
            "start_stop_active": data.get("start_stop_active"),
            "any_lock_active": data.get("any_lock_active"),
            "any_prealarm_active": data.get("any_prealarm_active"),
        }

        if data.get("any_lock_active"):
            attributes["active_locks"] = [
                label for key, (_, label) in LOCK_BITS.items() if data.get(key)
            ]

        if data.get("any_prealarm_active"):
            attributes["active_prealarms"] = [
                label for key, (_, label) in PREALARM_BITS.items() if data.get(key)
            ]

        return attributes
