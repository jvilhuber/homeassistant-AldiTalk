from typing_extensions import Self

import logging
import voluptuous as vol
from requests.exceptions import RequestException
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from .aldi_talk import AldiTalk
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self._user_input: dict[str, str] | None = None

    def is_matching(self, other_flow: Self) -> bool:
        """Return True if this flow matches another flow (same username)."""
        if self._user_input and hasattr(other_flow, "_user_input"):
            other_input = other_flow._user_input
            if other_input:
                return self._user_input.get("username") == other_input.get("username")
        return False

    def _show_connection_error(self, error: Exception):
        _LOGGER.exception("Cannot connect while setting up Aldi Talk: %s", error)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("username"): str, vol.Required("password"): str}
            ),
            errors={"base": "cannot_connect"},
        )

    async def async_step_user(self, user_input: dict[str, str] | None = None):
        if user_input is not None:
            # Store username for is_matching comparison
            self._user_input = user_input

            api = AldiTalk(user_input["username"], user_input["password"])
            try:
                # Validate credentials and fetch account data in executor
                await self.hass.async_add_executor_job(api.update)
                contract_id = await self.hass.async_add_executor_job(
                    api.get_contract_id
                )
            except ValueError:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {vol.Required("username"): str, vol.Required("password"): str}
                    ),
                    errors={"base": "invalid_auth"},
                )
            except RequestException as error:
                return self._show_connection_error(error)
            except (RuntimeError, HomeAssistantError) as error:
                return self._show_connection_error(error)

            # Use contract_id as the stable unique id for the config entry
            await self.async_set_unique_id(contract_id)
            self._abort_if_unique_id_configured()

            data = {**user_input, "contract_id": contract_id}
            return self.async_create_entry(title=user_input["username"], data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("username"): str, vol.Required("password"): str}
            ),
        )
