"""Binary sensor platform for Aertecnica Central Vacuum."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AertecnicaCoordinator
from .entity import AertecnicaEntity

BINARY_SENSOR_DESCRIPTIONS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="motor_status",
        name="Motor Status",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:engine",
    ),
    BinarySensorEntityDescription(
        key="standby_status",
        name="Standby Status",
        icon="mdi:power-sleep",
    ),
    BinarySensorEntityDescription(
        key="micro_line_status",
        name="Micro Line Closed",
        icon="mdi:electric-switch-closed",
    ),
    BinarySensorEntityDescription(
        key="any_prealarm",
        name="Pre-Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:alert-outline",
    ),
    BinarySensorEntityDescription(
        key="any_lock",
        name="Lock",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:lock-alert-outline",
    ),
)

# Binary sensor key -> coordinator data key
DATA_KEYS = {
    "motor_status": "motor_on",
    "standby_status": "standby_active",
    "micro_line_status": "micro_line_closed",
    "any_prealarm": "any_prealarm_active",
    "any_lock": "any_lock_active",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica binary sensors."""
    coordinator: AertecnicaCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AertecnicaBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class AertecnicaBinarySensor(AertecnicaEntity, BinarySensorEntity):
    """Representation of an Aertecnica binary sensor."""

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry, description.key, description.name)
        self.entity_description = description
        self._data_key = DATA_KEYS[description.key]

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._data_key)
