"""AldiTalk sensor integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AldiTalkCoordinator
from .entity import AldiTalkCoordinatorEntity

_LOGGER = logging.getLogger(__name__)

# Descriptions for aggregated sensors (translation keys are static)
SENSOR_DESCRIPTIONS = [
    {
        "key": "remaining_data_volume",
        "translation_key": "remaining_data_volume",
        "icon": "mdi:access-point",
    },
    {
        "key": "remaining_data_percentage",
        "translation_key": "remaining_data_percentage",
        "icon": "mdi:percent-outline",
    },
    {
        "key": "total_data_volume",
        "translation_key": "total_data_volume",
        "icon": "mdi:access-point-check",
    },
    {
        "key": "start_date",
        "translation_key": "start_date",
        "icon": "mdi:calendar",
    },
    {
        "key": "end_date",
        "translation_key": "end_date",
        "icon": "mdi:calendar",
    },
    {
        "key": "account_balance",
        "translation_key": "account_balance",
        "icon": "mdi:cash-multiple",
    },
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AldiTalk sensors."""

    coordinator: AldiTalkCoordinator = hass.data[DOMAIN][entry.entry_id]

    supports_data_sensors = coordinator.api_data.get("supports_data_sensors", True)

    # Remove stale sensors if data sensors are not supported
    if not supports_data_sensors:
        registry = er.async_get(hass)
        stale_keys = {
            "remaining_data_volume",
            "remaining_data_percentage",
            "total_data_volume",
            "start_date",
            "end_date",
        }
        for entity_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
            if entity_entry.domain != "sensor" or not entity_entry.unique_id:
                continue

            if any(entity_entry.unique_id.endswith(f"_{key}") for key in stale_keys):
                registry.async_remove(entity_entry.entity_id)

    # Always create the balance sensor
    entities = [
        BalanceSensor(SENSOR_DESCRIPTIONS[5], coordinator),
    ]

    if supports_data_sensors:
        # Aggregated sensors (total over all packs)
        entities += [
            RemainingVolumeSensor(SENSOR_DESCRIPTIONS[0], coordinator),
            PercentageSensor(SENSOR_DESCRIPTIONS[1], coordinator),
            VolumeSensor(SENSOR_DESCRIPTIONS[2], coordinator),
            DateSensor(SENSOR_DESCRIPTIONS[3], coordinator),
            DateSensor(SENSOR_DESCRIPTIONS[4], coordinator),
            BalanceSensor(SENSOR_DESCRIPTIONS[5], coordinator),
        ]

        # Individual sensors for each data pack, but only if more than one pack exists
        data_packs = coordinator.api_data.get("data_packs_raw", [])
        if len(data_packs) > 1:
            for idx, pack in enumerate(data_packs, start=1):
                entities.append(
                    RemainingVolumePackSensor(
                        coordinator,
                        pack_index=idx,
                        pack_data=pack,
                    )
                )
                entities.append(
                    PercentagePackSensor(
                        coordinator,
                        pack_index=idx,
                        pack_data=pack,
                    )
                )
                entities.append(
                    TotalVolumePackSensor(
                        coordinator,
                        pack_index=idx,
                        pack_data=pack,
                    )
                )

    async_add_entities(entities)


# ============================================================
#  AGGREGATED SENSORS (total values)
# ============================================================


class VolumeSensor(AldiTalkCoordinatorEntity, SensorEntity):
    def __init__(self, sensor, coordinator):
        super().__init__(coordinator, sensor)
        self._attr_device_class = SensorDeviceClass.DATA_SIZE
        self._attr_native_unit_of_measurement = UnitOfInformation.GIGABYTES
        self._attr_suggested_unit_of_measurement = UnitOfInformation.GIGABYTES
        self._attr_suggested_display_precision = 1


class RemainingVolumeSensor(VolumeSensor):
    def __init__(self, sensor, coordinator):
        super().__init__(sensor, coordinator)
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_last_reset = coordinator.api_data.get("start_date")


class PercentageSensor(AldiTalkCoordinatorEntity, SensorEntity):
    def __init__(self, sensor, coordinator):
        super().__init__(coordinator, sensor)
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 1


class DateSensor(AldiTalkCoordinatorEntity, SensorEntity):
    def __init__(self, sensor, coordinator):
        super().__init__(coordinator, sensor)
        self._attr_device_class = SensorDeviceClass.TIMESTAMP


class BalanceSensor(AldiTalkCoordinatorEntity, SensorEntity):
    def __init__(self, sensor, coordinator):
        super().__init__(coordinator, sensor)
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self._attr_state_class = SensorStateClass.TOTAL


# ============================================================
#  INDIVIDUAL PACK SENSORS (with translation placeholders)
# ============================================================


class PackSensorBase(AldiTalkCoordinatorEntity, SensorEntity):
    """Base class for per‑pack sensors with translation placeholders."""

    def __init__(
        self,
        coordinator,
        pack_index: int,
        pack_data: dict,
        sensor_key: str,
        translation_key: str,
        icon: str,
    ):
        """Initialize the sensor."""
        self._pack_index = pack_index
        self._pack_data = pack_data

        sensor_desc = {
            "key": sensor_key,
            "translation_key": translation_key,  # one key for all packs
            "icon": icon,
        }
        super().__init__(coordinator, sensor_desc)

        # Enable translation and pass the pack number as a placeholder
        self._attr_has_entity_name = True
        self._attr_translation_placeholders = {"pack_number": str(pack_index)}

    @property
    def extra_state_attributes(self):
        """Return additional attributes for debugging or custom cards."""
        allocated = float(self._pack_data.get("allocated_kb", 0))
        used = float(self._pack_data.get("used_kb", 0))
        return {
            "pack_index": self._pack_index,
            "allocated_gb": round(allocated / (1024 * 1024), 2),
            "used_gb": round(used / (1024 * 1024), 2),
            "expiration_date": self._pack_data.get("next_expiration"),
        }


class RemainingVolumePackSensor(PackSensorBase):
    """Remaining volume for a single pack."""

    def __init__(self, coordinator, pack_index: int, pack_data: dict):
        super().__init__(
            coordinator,
            pack_index,
            pack_data,
            sensor_key=f"datapack_{pack_index}_remaining_volume",
            translation_key="datapack_remaining_volume",
            icon="mdi:access-point",
        )
        self._attr_device_class = SensorDeviceClass.DATA_SIZE
        self._attr_native_unit_of_measurement = UnitOfInformation.GIGABYTES
        self._attr_suggested_unit_of_measurement = UnitOfInformation.GIGABYTES
        self._attr_suggested_display_precision = 1
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self):
        allocated = float(self._pack_data.get("allocated_kb", 0))
        used = float(self._pack_data.get("used_kb", 0))
        return round((allocated - used) / (1024 * 1024), 2)


class PercentagePackSensor(PackSensorBase):
    """Remaining percentage for a single pack."""

    def __init__(self, coordinator, pack_index: int, pack_data: dict):
        super().__init__(
            coordinator,
            pack_index,
            pack_data,
            sensor_key=f"datapack_{pack_index}_percentage",
            translation_key="datapack_percentage",
            icon="mdi:percent-outline",
        )
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 1

    @property
    def native_value(self):
        allocated = float(self._pack_data.get("allocated_kb", 0))
        used = float(self._pack_data.get("used_kb", 0))
        if allocated > 0:
            return round(((allocated - used) / allocated) * 100, 1)
        return 0.0


class TotalVolumePackSensor(PackSensorBase):
    """Total (allocated) volume for a single pack."""

    def __init__(self, coordinator, pack_index: int, pack_data: dict):
        super().__init__(
            coordinator,
            pack_index,
            pack_data,
            sensor_key=f"datapack_{pack_index}_total_volume",
            translation_key="datapack_total_volume",
            icon="mdi:access-point-check",
        )
        self._attr_device_class = SensorDeviceClass.DATA_SIZE
        self._attr_native_unit_of_measurement = UnitOfInformation.GIGABYTES
        self._attr_suggested_unit_of_measurement = UnitOfInformation.GIGABYTES
        self._attr_suggested_display_precision = 1
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        allocated = float(self._pack_data.get("allocated_kb", 0))
        return round(allocated / (1024 * 1024), 2)
