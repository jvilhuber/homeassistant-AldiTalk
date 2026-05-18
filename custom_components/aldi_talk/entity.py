"""The AldiTalk base entity."""

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN


class AldiTalkCoordinatorEntity(CoordinatorEntity):
    """AldiTalk base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, sensor: dict) -> None:
        """Initialize the Trias base entity."""
        super().__init__(coordinator)
        self._key = sensor["key"]
        stable_id = coordinator.config.get("contract_id") or coordinator.config.get(
            "username"
        )
        self._attr_unique_id = f"{stable_id}_{sensor['key']}"
        self._attr_name = sensor["name"]
        self._attr_icon = sensor["icon"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, stable_id)},
            manufacturer="Aldi Talk",
            name=stable_id,
        )

    @property
    def native_value(self):
        """Return the state of the device."""
        return self.coordinator.api_data.get(self._key)
