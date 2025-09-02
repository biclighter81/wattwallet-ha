"""Config flow for wattwallet integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

DOMAIN = "wattwallet"


class WattwalletConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wattwallet."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input:
            invalid_entities = []
            for entity_id in user_input["stromzaehler"]:
                state = self.hass.states.get(entity_id)
                if not state:
                    invalid_entities.append(entity_id)
                    continue
                attrs = state.attributes
                if attrs.get("state_class") not in ("total", "total_increasing"):
                    invalid_entities.append(entity_id)
                if attrs.get("unit_of_measurement") not in ("Wh", "kWh"):
                    invalid_entities.append(entity_id)
            if invalid_entities:
                errors["stromzaehler"] = (
                    "Mindestens eine Entität erfüllt nicht alle Anforderungen: "
                    "state_class muss 'total' oder 'total_increasing' und unit_of_measurement 'Wh' oder 'kWh' sein."
                )

            if not errors:
                name = user_input.pop("name")
                return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default="wattwallet"): str,
                    vol.Required("stromzaehler"): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            multiple=True,
                            filter={"domain": "sensor", "device_class": "energy"},
                        )
                    ),
                    vol.Required("interval", default=300): int,
                    vol.Required("api_token"): str,
                    vol.Required("target_url"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return WattwalletOptionsFlowHandler(config_entry)


class WattwalletOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Wattwallet options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        errors = {}

        if user_input is not None:
            hass = self.hass
            invalid_entities = []
            for entity_id in user_input["stromzaehler"]:
                state = hass.states.get(entity_id)
                if not state:
                    invalid_entities.append(entity_id)
                    continue
                attrs = state.attributes
                if attrs.get("state_class") not in ("total", "total_increasing"):
                    invalid_entities.append(entity_id)
                if attrs.get("unit_of_measurement") not in ("Wh", "kWh"):
                    invalid_entities.append(entity_id)
            if invalid_entities:
                errors["stromzaehler"] = (
                    "Mindestens eine Entität erfüllt nicht alle Anforderungen: "
                    "state_class muss 'total' oder 'total_increasing' und unit_of_measurement 'Wh' oder 'kWh' sein."
                )
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        data = self.config_entry.data

        def get_option(key, default=None):
            return options.get(key, data.get(key, default))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "stromzaehler", default=get_option("stromzaehler", [])
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            multiple=True,
                            filter={"domain": "sensor", "device_class": "energy"},
                        )
                    ),
                    vol.Required("interval", default=get_option("interval", 300)): int,
                    vol.Required("api_token", default=get_option("api_token", "")): str,
                    vol.Required(
                        "target_url", default=get_option("target_url", "")
                    ): str,
                }
            ),
            errors=errors,
        )
