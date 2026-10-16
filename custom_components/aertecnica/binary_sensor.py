"""Binary sensor platform for Aertecnica Central Vacuum."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AertecnicaConfigEntry
from .coordinator import AertecnicaCoordinator
from .entity import AertecnicaEntity


@dataclass(frozen=True, kw_only=True)
class AertecnicaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes an Aertecnica binary sensor."""

    data_key: str


BINARY_SENSOR_DESCRIPTIONS: tuple[AertecnicaBinarySensorEntityDescription, ...] = (
    AertecnicaBinarySensorEntityDescription(
        key="motor_status",
        translation_key="motor_status",
        data_key="motor_on",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:engine",
    ),
    AertecnicaBinarySensorEntityDescription(
        key="standby_status",
        translation_key="standby_status",
        data_key="standby_active",
        icon="mdi:power-sleep",
    ),
    AertecnicaBinarySensorEntityDescription(
        key="micro_line_status",
        translation_key="micro_line_status",
        data_key="micro_line_closed",
        icon="mdi:electric-switch-closed",
    ),
    AertecnicaBinarySensorEntityDescription(
        key="any_prealarm",
        translation_key="any_prealarm",
        data_key="any_prealarm_active",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:alert-outline",
    ),
    AertecnicaBinarySensorEntityDescription(
        key="any_lock",
        translation_key="any_lock",
        data_key="any_lock_active",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:lock-alert-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AertecnicaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica binary sensors."""
    coordinator = entry.runtime_data

    async_add_entities(
        AertecnicaBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class AertecnicaBinarySensor(AertecnicaEntity, BinarySensorEntity):
    """Representation of an Aertecnica binary sensor."""

    entity_description: AertecnicaBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: AertecnicaConfigEntry,
        description: AertecnicaBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry, description)

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)
