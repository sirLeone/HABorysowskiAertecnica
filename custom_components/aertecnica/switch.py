"""Switch platform for Aertecnica Central Vacuum."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AertecnicaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica switches."""
    coordinator: AertecnicaCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [AertecnicaMotorSwitch(coordinator, entry)]
    async_add_entities(entities)


class AertecnicaMotorSwitch(CoordinatorEntity[AertecnicaCoordinator], SwitchEntity):
    """Representation of an Aertecnica motor switch."""

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Motor"
        self._attr_unique_id = f"{entry.entry_id}_motor_switch"
        self._attr_has_entity_name = False
        self._attr_icon = "mdi:fan"

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Aertecnica",
            model=coordinator.data.get("card_model", "Unknown") if coordinator.data else "Unknown",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the motor is on."""
        if not self.coordinator.data:
            return None

        return self.coordinator.data.get("motor_on", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the motor on."""
        _LOGGER.debug("Turning on Aertecnica motor")
        result = await self.coordinator.async_motor_start()
        if not result:
            _LOGGER.error("Failed to turn on motor")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the motor off."""
        _LOGGER.debug("Turning off Aertecnica motor")
        result = await self.coordinator.async_motor_stop()
        if not result:
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

        # Add lock details
        if data.get("any_lock_active"):
            locks = []
            if data.get("lock_max_time"):
                locks.append("Max Time")
            if data.get("lock_max_pressure"):
                locks.append("Max Pressure")
            if data.get("lock_num_starts"):
                locks.append("Num Starts")
            if data.get("lock_dirty_filter"):
                locks.append("Dirty Filter")
            if data.get("lock_full_bag"):
                locks.append("Full Bag")
            if data.get("lock_max_temperature"):
                locks.append("Max Temperature")
            if data.get("lock_appliance"):
                locks.append("Appliance")

            attributes["active_locks"] = locks

        # Add prealarm details
        if data.get("any_prealarm_active"):
            prealarms = []
            if data.get("prealarm_max_time"):
                prealarms.append("Max Time")
            if data.get("prealarm_max_pressure"):
                prealarms.append("Max Pressure")
            if data.get("prealarm_num_starts"):
                prealarms.append("Num Starts")
            if data.get("prealarm_dirty_filter"):
                prealarms.append("Dirty Filter")
            if data.get("prealarm_full_bag"):
                prealarms.append("Full Bag")
            if data.get("prealarm_max_temp"):
                prealarms.append("Max Temperature")
            if data.get("prealarm_appliance"):
                prealarms.append("Appliance")

            attributes["active_prealarms"] = prealarms

        return attributes
