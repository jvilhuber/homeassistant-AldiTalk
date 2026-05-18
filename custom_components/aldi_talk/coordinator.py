"""Example integration using DataUpdateCoordinator."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from .aldi_talk import AldiTalk
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AldiTalkCoordinator(DataUpdateCoordinator):
    """AldiTalk coordinator."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize AldiTalk coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Aldi Talk Sensor",
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
        )

        self.hass = hass
        self.config_entry = entry
        self.config = entry.data

        self.aldi_talk = AldiTalk(self.config["username"], self.config["password"])

        self.api_data: dict = {}

    async def _async_update_data(self):
        """Fetch data from API endpoint and handle errors per HA expectations."""
        try:
            data = await self.hass.async_add_executor_job(self.aldi_talk.get_data)
            self.api_data = data
            return self.api_data
        except ValueError as err:
            raise ConfigEntryAuthFailed("Authentication failed") from err
        except Exception as err:
            raise UpdateFailed("Error fetching data") from err
