# Home Brewing Integration

A Home Assistant integration for tracking home brew fermentation progress using Tilt or generic MQTT sensors, with thermostat-style heater control.

---

## Installation

1. Install via [HACS](https://hacs.xyz) by adding `https://github.com/nukolator/ha-homebrewing` as a custom repository
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for **Home Brewing** and follow the setup wizard

---

## Initial Setup

When you first add the integration you will be asked to fill in the following:

| Field | Description |
|---|---|
| **Brew Name** | A name for this brew (e.g. "Coopers Pale Ale"). Used to name all entities. |
| **Kit Brand** | Select from Coopers, Morgan's, Black Rock, Brigalow, or Other. |
| **Original Gravity (OG)** | The starting specific gravity of your wort, measured before fermentation begins. Typically between 1.035 and 1.060 for kit brews. |
| **Expected Final Gravity (FG)** | The target specific gravity at the end of fermentation. Check your kit instructions — typically between 1.008 and 1.016. |
| **SG Sensor** | Any Home Assistant sensor entity reporting specific gravity. Works with Tilt hydrometers or generic MQTT sensors. |
| **Temperature Sensor** | Any Home Assistant sensor entity reporting temperature in °C. |
| **Heater Switch** | The switch entity controlling your brew heater or heat mat. |
| **Target Temperature Min** | The lower bound of your fermentation temperature range. The heater will turn on when temperature drops below this. |
| **Target Temperature Max** | The upper bound of your fermentation temperature range. The heater will turn off when temperature reaches this. |

---

## Updating Settings

After setup, you can update your brew settings at any time without removing and re-adding the integration.

Go to **Settings → Devices & Services → Home Brewing → Configure**.

The following settings can be updated:

| Field | Description |
|---|---|
| **Original Gravity (OG)** | Update if you took a revised OG reading after topping up. |
| **Expected Final Gravity (FG)** | Update if your target FG changes based on fermentation progress. |
| **SG Sensor** | Reassign to a different sensor if needed. |
| **Temperature Sensor** | Reassign to a different sensor if needed. |
| **Heater Switch** | Reassign to a different switch if needed. |
| **Target Temperature Min** | Adjust your lower temperature bound. |
| **Target Temperature Max** | Adjust your upper temperature bound. |

> **Note:** Brew Name and Kit Brand cannot be changed after initial setup. To change these, remove and re-add the integration.

---

## Entities

After setup the integration creates the following entities, grouped under a single device named after your brew:

| Entity | Type | Description |
|---|---|---|
| `sensor.<brew>_fermentation_progress` | Sensor | Fermentation progress as a percentage of gravity drop from OG to FG |
| `sensor.<brew>_estimated_abv` | Sensor | Estimated alcohol by volume based on current vs original gravity |
| `climate.<brew>_heater` | Climate | Thermostat-style controller for your heater switch |

---

## Heater Control

The climate entity operates in two modes:

- **Heat** — actively monitors temperature and controls the heater switch within your target range
- **Off** — turns the heater off immediately and stops monitoring

When in Heat mode:
- Temperature drops below **Target Temp Min** → heater turns **on**
- Temperature reaches **Target Temp Max** → heater turns **off**

---

## Dashboard

A pre-built dashboard is included in the [`dashboards/`](https://github.com/nukolator/ha-homebrewing/tree/main/dashboards) folder. It requires [apexcharts-card](https://github.com/RomRider/apexcharts-card) installed via HACS.

See the [README](https://github.com/nukolator/ha-homebrewing) for import instructions.

---

## Supported Sensors

Any Home Assistant sensor entity works, including:

- Tilt Hydrometer (via MQTT)
- Generic MQTT sensors
- iSpindel or other Bluetooth/Wi-Fi hydrometers exposed as HA sensors

---

## Credits

Icon by [Dooder](https://www.flaticon.com/free-icons/foam) via Flaticon.
