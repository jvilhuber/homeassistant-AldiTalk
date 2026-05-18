from typing_extensions import Self

import voluptuous as vol
from requests.exceptions import RequestException
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from .aldi_talk import AldiTalk
from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def is_matching(self, other_flow: Self) -> bool:
        return False

    async def async_step_user(self, user_input: dict[str, str] | None = None):
        if user_input is not None:
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
            except RequestException:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {vol.Required("username"): str, vol.Required("password"): str}
                    ),
                    errors={"base": "cannot_connect"},
                )
            except (RuntimeError, HomeAssistantError):
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {vol.Required("username"): str, vol.Required("password"): str}
                    ),
                    errors={"base": "cannot_connect"},
                )

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
