"""Sensor platform for Home Brewing integration."""

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    CONF_BREW_NAME,
    CONF_BEER_STYLE,
    CONF_OG,
    CONF_FG,
    CONF_SG_SENSOR,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Home Brewing sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FermentationProgressSensor(hass, entry, data),
            EstimatedABVSensor(hass, entry, data),
        ]
    )


class HomebrewingSensorBase(SensorEntity):
    """Base class for Home Brewing sensors."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, data: dict) -> None:
        self._hass = hass
        self._entry = entry
        self._data = {**data, **entry.options}
        self._brew_name = data[CONF_BREW_NAME]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._brew_name,
            "model": self._data.get(CONF_BEER_STYLE) or "Home Brew",
        }

    async def async_added_to_hass(self) -> None:
        """Register state change listener and do initial update."""
        self._update()
        self.async_on_remove(
            async_track_state_change_event(
                self._hass,
                [self._data[CONF_SG_SENSOR]],
                self._handle_state_change,
            )
        )

    @callback
    def _handle_state_change(self, event) -> None:
        self._update()
        self.async_write_ha_state()

    def _update(self) -> None:
        raise NotImplementedError


class FermentationProgressSensor(HomebrewingSensorBase):
    """Sensor tracking fermentation progress as a percentage of gravity drop."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:beer"

    def __init__(self, hass, entry, data) -> None:
        super().__init__(hass, entry, data)
        self._attr_name = f"{self._brew_name} Fermentation Progress"
        self._attr_unique_id = f"{entry.entry_id}_fermentation_progress"
        self._attr_native_value = None
        self.entity_id = "sensor.homebrewing_fermentation_progress"

    def _update(self) -> None:
        og = float(self._data[CONF_OG])
        fg = float(self._data[CONF_FG])
        sg_state = self._hass.states.get(self._data[CONF_SG_SENSOR])

        if sg_state is None or sg_state.state in ("unknown", "unavailable"):
            return

        try:
            current = float(sg_state.state)
            if og == fg:
                self._attr_native_value = 0.0
                return
            progress = ((og - current) / (og - fg)) * 100
            self._attr_native_value = round(max(0.0, min(100.0, progress)), 1)
        except (ValueError, ZeroDivisionError):
            self._attr_native_value = None


class EstimatedABVSensor(HomebrewingSensorBase):
    """Sensor tracking estimated ABV based on current vs original gravity."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:percent"

    def __init__(self, hass, entry, data) -> None:
        super().__init__(hass, entry, data)
        self._attr_name = f"{self._brew_name} Estimated ABV"
        self._attr_unique_id = f"{entry.entry_id}_estimated_abv"
        self._attr_native_value = None
        self.entity_id = "sensor.homebrewing_estimated_abv"

    def _update(self) -> None:
        og = float(self._data[CONF_OG])
        sg_state = self._hass.states.get(self._data[CONF_SG_SENSOR])

        if sg_state is None or sg_state.state in ("unknown", "unavailable"):
            return

        try:
            current = float(sg_state.state)
            self._attr_native_value = round((og - current) * 131.25, 2)
        except ValueError:
            self._attr_native_value = None
