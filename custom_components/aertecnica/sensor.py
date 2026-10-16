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
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AertecnicaConfigEntry
from .coordinator import AertecnicaCoordinator
from .entity import AertecnicaEntity

AttrsFn = Callable[[dict[str, Any]], dict[str, Any]]


def _pick(*keys: str) -> AttrsFn:
    """Build an attributes function copying the given data keys."""
    return lambda data: {key: data.get(key) for key in keys}


@dataclass(frozen=True, kw_only=True)
class AertecnicaSensorEntityDescription(SensorEntityDescription):
    """Describes an Aertecnica sensor."""

    data_key: str | None = None
    unit_key: str | None = None
    attrs_fn: AttrsFn | None = None


SENSOR_DESCRIPTIONS: tuple[AertecnicaSensorEntityDescription, ...] = (
    AertecnicaSensorEntityDescription(
        key="card_model",
        translation_key="card_model",
        icon="mdi:information-outline",
        attrs_fn=lambda data: {"model_id": data.get("card_model_id")},
    ),
    AertecnicaSensorEntityDescription(
        key="card_hours",
        translation_key="card_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
    ),
    AertecnicaSensorEntityDescription(
        key="motor_hours",
        translation_key="motor_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:engine-outline",
    ),
    AertecnicaSensorEntityDescription(
        key="bag_hours",
        translation_key="bag_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:air-filter",
    ),
    AertecnicaSensorEntityDescription(
        key="filter_hours",
        translation_key="filter_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:air-filter",
    ),
    AertecnicaSensorEntityDescription(
        key="bag_level",
        translation_key="bag_level",
        icon="mdi:delete",
        attrs_fn=lambda data: {
            "prealarm": data.get("prealarm_full_bag"),
            "lock": data.get("lock_full_bag"),
        },
    ),
    AertecnicaSensorEntityDescription(
        key="filter_level",
        translation_key="filter_level",
        icon="mdi:air-filter",
        attrs_fn=lambda data: {
            "prealarm": data.get("prealarm_dirty_filter"),
            "lock": data.get("lock_dirty_filter"),
        },
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_level",
        translation_key="pressure_level",
        data_key="pressure_level_name",
        icon="mdi:gauge",
        attrs_fn=_pick("pressure_1", "pressure_2", "pressure_diff"),
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_1",
        translation_key="pressure_1",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_2",
        translation_key="pressure_2",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_diff",
        translation_key="pressure_diff",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    AertecnicaSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        attrs_fn=_pick(
            "prealarm_max_temp", "lock_max_temperature", "temp_reset_prohibited"
        ),
    ),
    AertecnicaSensorEntityDescription(
        key="motor_power",
        translation_key="motor_power",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:engine",
        attrs_fn=_pick("motor_on", "standby_active", "pid_mode"),
    ),
    AertecnicaSensorEntityDescription(
        key="pressure_setpoint",
        translation_key="pressure_setpoint",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.PRESSURE,
        icon="mdi:target",
    ),
    AertecnicaSensorEntityDescription(
        key="residual_max_time",
        translation_key="residual_max_time",
        # The device reports minutes or seconds depending on a flag
        unit_key="residual_max_time_unit",
        icon="mdi:timer-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AertecnicaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aertecnica sensors."""
    coordinator = entry.runtime_data

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
        entry: AertecnicaConfigEntry,
        description: AertecnicaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, description)
        self._data_key = description.data_key or description.key

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._data_key)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement, dynamic when the device decides it."""
        unit_key = self.entity_description.unit_key
        if unit_key is None:
            return super().native_unit_of_measurement
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(unit_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        attrs_fn = self.entity_description.attrs_fn
        if attrs_fn is None or not self.coordinator.data:
            return None
        return attrs_fn(self.coordinator.data)
