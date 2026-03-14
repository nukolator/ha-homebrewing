"""Config flow for Home Brewing integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_BREW_NAME,
    CONF_KIT_BRAND,
    CONF_OG,
    CONF_FG,
    CONF_SG_SENSOR,
    CONF_TEMP_SENSOR,
    CONF_HEATER_SWITCH,
    CONF_TARGET_TEMP_MIN,
    CONF_TARGET_TEMP_MAX,
    KIT_BRANDS,
    DEFAULT_OG,
    DEFAULT_FG,
    DEFAULT_TARGET_TEMP_MIN,
    DEFAULT_TARGET_TEMP_MAX,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BREW_NAME): str,
        vol.Required(CONF_KIT_BRAND): selector.selector(
            {"select": {"options": KIT_BRANDS}}
        ),
        vol.Required(CONF_OG, default=DEFAULT_OG): selector.selector(
            {
                "number": {
                    "min": 1.000,
                    "max": 1.120,
                    "step": 0.001,
                    "mode": "box",
                }
            }
        ),
        vol.Required(CONF_FG, default=DEFAULT_FG): selector.selector(
            {
                "number": {
                    "min": 1.000,
                    "max": 1.040,
                    "step": 0.001,
                    "mode": "box",
                }
            }
        ),
        vol.Required(CONF_SG_SENSOR): selector.selector(
            {"entity": {"domain": "sensor"}}
        ),
        vol.Required(CONF_TEMP_SENSOR): selector.selector(
            {"entity": {"domain": "sensor"}}
        ),
        vol.Required(CONF_HEATER_SWITCH): selector.selector(
            {"entity": {"domain": "switch"}}
        ),
        vol.Required(CONF_TARGET_TEMP_MIN, default=DEFAULT_TARGET_TEMP_MIN): selector.selector(
            {
                "number": {
                    "min": 10,
                    "max": 35,
                    "step": 0.5,
                    "mode": "slider",
                    "unit_of_measurement": "°C",
                }
            }
        ),
        vol.Required(CONF_TARGET_TEMP_MAX, default=DEFAULT_TARGET_TEMP_MAX): selector.selector(
            {
                "number": {
                    "min": 10,
                    "max": 35,
                    "step": 0.5,
                    "mode": "slider",
                    "unit_of_measurement": "°C",
                }
            }
        ),
    }
)


class HomebrewingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Home Brewing."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            if user_input[CONF_TARGET_TEMP_MIN] >= user_input[CONF_TARGET_TEMP_MAX]:
                errors["base"] = "temp_range_invalid"
            elif user_input[CONF_OG] <= user_input[CONF_FG]:
                errors["base"] = "gravity_range_invalid"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_BREW_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
