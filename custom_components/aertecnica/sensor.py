"""Sensor platform for Aertecnica Central Vacuum."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import AertecnicaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica sensors."""
    coordinator: AertecnicaCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for sensor_type, config in SENSOR_TYPES.items():
        entities.append(AertecnicaSensor(coordinator, entry, sensor_type, config))

    async_add_entities(entities)


class AertecnicaSensor(CoordinatorEntity[AertecnicaCoordinator], SensorEntity):
    """Representation of an Aertecnica sensor."""

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._config = config
        self._attr_name = f"{entry.title} {config['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_has_entity_name = False

        # Set device class and state class
        if config.get("device_class"):
            self._attr_device_class = config["device_class"]
        if config.get("state_class"):
            self._attr_state_class = config["state_class"]

        # Set unit of measurement
        if config.get("unit"):
            self._attr_native_unit_of_measurement = config["unit"]

        # Set icon
        if config.get("icon"):
            self._attr_icon = config["icon"]

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Aertecnica",
            model=coordinator.data.get("card_model", "Unknown") if coordinator.data else "Unknown",
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        data = self.coordinator.data

        # Map sensor types to data keys
        sensor_mapping = {
            "card_model": "card_model",
            "card_hours": "card_hours",
            "motor_hours": "motor_hours",
            "bag_hours": "bag_hours",
            "filter_hours": "filter_hours",
            "bag_level": "bag_level",
            "filter_level": "filter_level",
            "pressure_level": "pressure_level_name",
            "pressure_1": "pressure_1",
            "pressure_2": "pressure_2",
            "pressure_diff": "pressure_diff",
            "temperature": "temperature",
            "motor_power": "motor_power",
            "pressure_setpoint": "pressure_setpoint",
            "residual_max_time": "residual_max_time",
        }

        data_key = sensor_mapping.get(self._sensor_type)
        if data_key:
            value = data.get(data_key)

            # Special handling for residual_max_time to update unit dynamically
            if self._sensor_type == "residual_max_time":
                unit = data.get("residual_max_time_unit", "s")
                self._attr_native_unit_of_measurement = unit

            return value

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        data = self.coordinator.data
        attributes = {}

        # Add common attributes
        if self._sensor_type == "card_model":
            attributes["model_id"] = data.get("card_model_id")

        # Add system status for motor_power sensor
        if self._sensor_type == "motor_power":
            attributes["motor_on"] = data.get("motor_on")
            attributes["standby_active"] = data.get("standby_active")
            attributes["pid_mode"] = data.get("pid_mode")

        # Add pressure attributes
        if self._sensor_type == "pressure_level":
            attributes["pressure_1"] = data.get("pressure_1")
            attributes["pressure_2"] = data.get("pressure_2")
            attributes["pressure_diff"] = data.get("pressure_diff")

        # Add alarm/lock info to relevant sensors
        if self._sensor_type in ["bag_level", "filter_level"]:
            if self._sensor_type == "bag_level":
                attributes["prealarm"] = data.get("prealarm_full_bag")
                attributes["lock"] = data.get("lock_full_bag")
            else:
                attributes["prealarm"] = data.get("prealarm_dirty_filter")
                attributes["lock"] = data.get("lock_dirty_filter")

        # Add all alarms to temperature sensor
        if self._sensor_type == "temperature":
            attributes["prealarm_max_temp"] = data.get("prealarm_max_temp")
            attributes["lock_max_temperature"] = data.get("lock_max_temperature")
            attributes["temp_reset_prohibited"] = data.get("temp_reset_prohibited")

        return attributes if attributes else None
