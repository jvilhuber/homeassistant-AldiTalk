"""The AldiTalk base entity."""

from homeassistant.const import CONF_USERNAME
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
            CONF_USERNAME
        )
        self._attr_unique_id = f"{stable_id}_{sensor['key']}"
        self._attr_translation_key = sensor["translation_key"]
        self._attr_icon = sensor["icon"]
        account_data = getattr(coordinator, "api_data", {}) or {}
        first_name = account_data.get("first_name") or coordinator.config.get(
            CONF_USERNAME
        )
        offer_name = account_data.get("offer_name") or None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, stable_id)},
            configuration_url="https://www.alditalk-kundenportal.de/portal/auth/uebersicht/",
            manufacturer="Aldi Talk",
            model=offer_name,
            name=first_name,
            serial_number=coordinator.config.get("contract_id") or stable_id,
        )

    @property
    def native_value(self):
        """Return the state of the device."""
        return self.coordinator.api_data.get(self._key)
