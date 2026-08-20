"""Base entity for Aertecnica Central Vacuum."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import AertecnicaCoordinator


class AertecnicaEntity(CoordinatorEntity[AertecnicaCoordinator]):
    """Base class for all Aertecnica entities."""

    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
        key: str,
        name_suffix: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} {name_suffix}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=(coordinator.data or {}).get("card_model", "Unknown"),
        )
