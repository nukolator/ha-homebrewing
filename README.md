# Home Brewing — Home Assistant Integration

A Home Assistant integration for tracking home brew fermentation progress using Tilt or generic MQTT sensors, with thermostat-style heater control.

## Features

- **Fermentation Progress** — tracks gravity drop from OG to FG as a percentage
- **Estimated ABV** — calculates current estimated alcohol by volume
- **Heater Control** — thermostat-style climate entity to control a brew heater switch within a target temperature range
- **Supports Tilt and generic MQTT sensors** — any HA sensor entity can be used for SG and temperature

## Installation via HACS

1. In HACS, go to **Integrations** → **Custom Repositories**
2. Add this repo URL and select **Integration** as the category
3. Install **Home Brewing** from HACS
4. Restart Home Assistant

## Configuration

After installation, go to **Settings → Devices & Services → Add Integration** and search for **Home Brewing**.

You will be prompted to enter:

| Field | Description |
|---|---|
| Brew Name | A name for this brew (e.g. "Coopers Pale Ale") |
| Kit Brand | Coopers, Morgan's, Black Rock, Brigalow, or Other |
| Original Gravity (OG) | The starting SG of your wort |
| Expected Final Gravity (FG) | The target SG at end of fermentation |
| SG Sensor | Any HA sensor entity reporting specific gravity |
| Temperature Sensor | Any HA sensor entity reporting temperature (°C) |
| Heater Switch | The switch entity controlling your brew heater |
| Target Temp Min | Lower bound of your fermentation temperature range |
| Target Temp Max | Upper bound of your fermentation temperature range |

## Entities Created

| Entity | Type | Description |
|---|---|---|
| `sensor.<brew_name>_fermentation_progress` | Sensor | % complete based on gravity drop |
| `sensor.<brew_name>_estimated_abv` | Sensor | Estimated ABV % |
| `climate.<brew_name>_heater` | Climate | Thermostat controlling the heater switch |

## Heater Control Logic

The climate entity operates in **HEAT** or **OFF** mode:
- When temperature drops below **Target Temp Min**, the heater switch turns **on**
- When temperature reaches **Target Temp Max**, the heater switch turns **off**
- Setting the mode to **OFF** turns the heater off immediately

## Supported Sensors

Any Home Assistant sensor entity works — including:
- **Tilt Hydrometer** (via MQTT)
- **Generic MQTT sensors**
- **iSpindel** or other Bluetooth/Wi-Fi hydrometers exposed as HA sensors

## Contributing

Pull requests welcome. Please open an issue first for significant changes.

## Credits

Icon by [Dooder](https://www.flaticon.com/free-icons/foam) via Flaticon.

## License

MIT
