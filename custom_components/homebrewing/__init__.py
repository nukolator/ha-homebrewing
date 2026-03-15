"""Home Brewing integration for Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, PLATFORMS, CONF_BREW_NAME, CONF_FG, CONF_SG_SENSOR

FG_TOLERANCE = 0.002


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Brewing from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register FG alert listener
    _register_fg_alert(hass, entry)

    return True


def _register_fg_alert(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a listener that fires when SG is within tolerance of FG."""
    data = {**entry.data, **entry.options}
    brew_name = data[CONF_BREW_NAME]
    fg = float(data[CONF_FG])
    sg_sensor = data[CONF_SG_SENSOR]
    alert_threshold = fg + FG_TOLERANCE
    alerted_key = f"{DOMAIN}_{entry.entry_id}_fg_alerted"

    @callback
    def _check_fg(event) -> None:
        new_state = event.data.get("new_state")
        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        try:
            current_sg = float(new_state.state)
        except ValueError:
            return

        # Only alert once per brew, reset if gravity goes back up
        if current_sg > alert_threshold:
            hass.data[alerted_key] = False
            return

        if hass.data.get(alerted_key):
            return

        hass.data[alerted_key] = True

        message = (
            f"{brew_name} has reached its final gravity! "
            f"Current SG: {current_sg:.3f} — target FG: {fg:.3f}. "
            "Time to cold crash or bottle!"
        )

        # Persistent notification
        hass.async_create_task(
            hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": f"🍺 {brew_name} — Fermentation Complete!",
                    "message": message,
                    "notification_id": f"{DOMAIN}_fg_alert_{entry.entry_id}",
                },
            )
        )

        # Mobile push notification
        hass.async_create_task(
            hass.services.async_call(
                "notify",
                "notify",
                {
                    "title": f"🍺 {brew_name} — Fermentation Complete!",
                    "message": message,
                },
            )
        )

    entry.async_on_unload(
        async_track_state_change_event(hass, [sg_sensor], _check_fg)
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.data.pop(f"{DOMAIN}_{entry.entry_id}_fg_alerted", None)
    return unload_ok
