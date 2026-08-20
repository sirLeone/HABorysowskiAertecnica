"""Sensor platform for Aertecnica Central Vacuum."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AertecnicaCoordinator
from .entity import AertecnicaEntity


@dataclass(frozen=True, kw_only=True)
class AertecnicaSensorEntityDescription(SensorEntityDescription):
    """Describes an Aertecnica sensor."""

    data_key: str
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[AertecnicaSensorEntityDescription, ...] = (
    AertecnicaSensorEntityDescription(
        key="card_model",
        name="Card Model",
        data_key="card_model",
        icon="mdi:information-outline",
        attrs_fn=lambda data: {"model_id": data.get("card_model_id")},
    ),
    AertecnicaSensorEntityDescription(
        key="card_hours",
        name="Card Hours",
        data_key="card_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
    ),
    AertecnicaSensorEntityDescription(
        key="motor_hours",
        name="Motor Hours",
        data_key="motor_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:engine-outline",
    ),
    AertecnicaSensorEntityDescription(
        key="bag_hours",
        name="Bag Hours",
        data_key="bag_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:air-filter",
    ),
    AertecnicaSensorEntityDescription(
        key="filter_hours",
        name="Filter Hours",
        data_key="filter_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:air-filter",
    ),
    AertecnicaSensorEntityDescription(
        key="bag_level",
        name="Bag Level",
        data_key="bag_level",
        icon="mdi:delete",
        attrs_fn=lambda data: {
            "prealarm": data.get("prealarm_full_bag"),
            "lock": data.get("lock_full_bag"),
        },
    ),
    AertecnicaSensorEntityDescription(
        key="filter_level",
        name="Filter Level",
        data_key="filter_level",
        icon="mdi:air-filter",
        attrs_fn=lambda data: {
            "prealarm": data.get("prealarm_dirty_filter"),
            "lock": data.get("lock_dirty_filter"),
        },
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_level",
        name="Pressure Level",
        data_key="pressure_level_name",
        icon="mdi:gauge",
        attrs_fn=lambda data: {
            "pressure_1": data.get("pressure_1"),
            "pressure_2": data.get("pressure_2"),
            "pressure_diff": data.get("pressure_diff"),
        },
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_1",
        name="Pressure 1",
        data_key="pressure_1",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_2",
        name="Pressure 2",
        data_key="pressure_2",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_diff",
        name="Pressure Differential",
        data_key="pressure_diff",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    AertecnicaSensorEntityDescription(
        key="temperature",
        name="Temperature",
        data_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        attrs_fn=lambda data: {
            "prealarm_max_temp": data.get("prealarm_max_temp"),
            "lock_max_temperature": data.get("lock_max_temperature"),
            "temp_reset_prohibited": data.get("temp_reset_prohibited"),
        },
    ),
    AertecnicaSensorEntityDescription(
        key="motor_power",
        name="Motor Power",
        data_key="motor_power",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:engine",
        attrs_fn=lambda data: {
            "motor_on": data.get("motor_on"),
            "standby_active": data.get("standby_active"),
            "pid_mode": data.get("pid_mode"),
        },
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_setpoint",
        name="Pressure Setpoint",
        data_key="pressure_setpoint",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        icon="mdi:target",
    ),
    AertecnicaSensorEntityDescription(
        key="residual_max_time",
        name="Residual Max Time",
        data_key="residual_max_time",
        icon="mdi:timer-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica sensors."""
    coordinator: AertecnicaCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AertecnicaSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class AertecnicaSensor(AertecnicaEntity, SensorEntity):
    """Representation of an Aertecnica sensor."""

    entity_description: AertecnicaSensorEntityDescription

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
        description: AertecnicaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, description.key, description.name)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        # The residual time unit depends on a device interpretation flag
        if self.entity_description.key == "residual_max_time":
            if not self.coordinator.data:
                return None
            return self.coordinator.data.get("residual_max_time_unit", "s")
        return super().native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        attrs_fn = self.entity_description.attrs_fn
        if attrs_fn is None or not self.coordinator.data:
            return None
        return attrs_fn(self.coordinator.data)
