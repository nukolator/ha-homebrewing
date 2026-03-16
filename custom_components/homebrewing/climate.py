"""Climate platform for Home Brewing heater control."""
import time

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    CONF_BREW_NAME,
    CONF_KIT_BRAND,
    CONF_TEMP_SENSOR,
    CONF_HEATER_SWITCH,
    CONF_TARGET_TEMP_MIN,
    CONF_TARGET_TEMP_MAX,
)

# Minimum seconds between heater switch events to protect the power switch
MIN_SWITCH_INTERVAL = 300  # 5 minutes


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the brew heater climate entity."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BrewHeaterClimate(hass, entry, data)])


class BrewHeaterClimate(ClimateEntity):
    """Thermostat-style controller for a brew heater switch."""

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 10
    _attr_max_temp = 35
    _attr_target_temperature_step = 0.5

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, data: dict) -> None:
        self._hass = hass
        self._entry = entry
        self._data = {**data, **entry.options}
        self._brew_name = data[CONF_BREW_NAME]
        self._attr_name = f"{self._brew_name} Heater"
        self._attr_unique_id = f"{entry.entry_id}_heater"
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_target_temperature_low = float(data[CONF_TARGET_TEMP_MIN])
        self._attr_target_temperature_high = float(data[CONF_TARGET_TEMP_MAX])
        self._attr_current_temperature = None
        self._attr_hvac_action = HVACAction.IDLE
        self.entity_id = "climate.homebrewing_heater"
        self._last_switch_time: float = 0.0  # epoch seconds of last heater switch

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._brew_name,
            "manufacturer": self._data.get(CONF_KIT_BRAND, "Unknown"),
            "model": "Home Brew",
        }

    async def async_added_to_hass(self) -> None:
        """Register listeners and do initial update."""
        self._refresh()
        self.async_on_remove(
            async_track_state_change_event(
                self._hass,
                [self._data[CONF_TEMP_SENSOR], self._data[CONF_HEATER_SWITCH]],
                self._handle_state_change,
            )
        )

    @callback
    def _handle_state_change(self, event) -> None:
        self._refresh()
        self.async_write_ha_state()

    def _refresh(self) -> None:
        """Read current temperature and heater state, then act."""
        temp_state = self._hass.states.get(self._data[CONF_TEMP_SENSOR])
        if temp_state and temp_state.state not in ("unknown", "unavailable"):
            try:
                self._attr_current_temperature = float(temp_state.state)
            except ValueError:
                pass

        switch_state = self._hass.states.get(self._data[CONF_HEATER_SWITCH])
        if switch_state:
            self._attr_hvac_action = (
                HVACAction.HEATING
                if switch_state.state == "on"
                else HVACAction.IDLE
            )

        if (
            self._attr_hvac_mode == HVACMode.HEAT
            and self._attr_current_temperature is not None
        ):
            self._apply_thermostat_logic()

    def _apply_thermostat_logic(self) -> None:
        """Turn heater on/off based on temperature vs target range.

        A minimum switch interval guards against rapid on/off cycling when the
        temperature is close to either threshold, protecting the power switch
        from excessive switching stress.
        """
        temp = self._attr_current_temperature
        low = self._attr_target_temperature_low
        high = self._attr_target_temperature_high
        switch = self._data[CONF_HEATER_SWITCH]
        switch_state = self._hass.states.get(switch)
        heater_on = switch_state and switch_state.state == "on"

        want_on = temp < low and not heater_on
        want_off = temp >= high and heater_on

        if not (want_on or want_off):
            return

        now = time.monotonic()
        elapsed = now - self._last_switch_time

        if elapsed < MIN_SWITCH_INTERVAL:
            # Too soon — skip this switch to protect the power switch
            return

        self._last_switch_time = now

        if want_on:
            self._hass.async_create_task(
                self._hass.services.async_call(
                    "switch", "turn_on", {"entity_id": switch}
                )
            )
        else:
            self._hass.async_create_task(
                self._hass.services.async_call(
                    "switch", "turn_off", {"entity_id": switch}
                )
            )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Handle HVAC mode changes."""
        self._attr_hvac_mode = hvac_mode
        if hvac_mode == HVACMode.OFF:
            # Bypass the switch interval — a manual OFF should always be respected
            self._last_switch_time = 0.0
            await self._hass.services.async_call(
                "switch", "turn_off", {"entity_id": self._data[CONF_HEATER_SWITCH]}
            )
        else:
            self._apply_thermostat_logic()
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs) -> None:
        """Handle target temperature range updates."""
        if "target_temp_low" in kwargs:
            self._attr_target_temperature_low = kwargs["target_temp_low"]
        if "target_temp_high" in kwargs:
            self._attr_target_temperature_high = kwargs["target_temp_high"]
        self._apply_thermostat_logic()
        self.async_write_ha_state()
