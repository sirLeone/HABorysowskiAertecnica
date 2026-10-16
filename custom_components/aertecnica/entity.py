"""Base entity for Aertecnica Central Vacuum."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import AertecnicaCoordinator


class AertecnicaEntity(CoordinatorEntity[AertecnicaCoordinator]):
    """Base class for all Aertecnica entities.

    Entity names come from ``translation_key`` on the entity description, so
    they are translated and prefixed with the device name by Home Assistant.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AertecnicaCoordinator,
        entry: ConfigEntry,
        description: EntityDescription,
        unique_id_key: str | None = None,
    ) -> None:
        """Initialize the entity.

        ``unique_id_key`` allows keeping a historical unique_id suffix that
        differs from the description key.
        """
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_key or description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=(coordinator.data or {}).get("card_model"),
        )
