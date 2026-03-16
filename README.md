# ha-homebrewing

A Home Assistant integration designed for using canned brews and simple gear to monitor and automate your brew.

Supports Tilt and generic MQTT sensors — any HA sensor entity can be used for SG and temperature.

---

## Installation

In HACS, go to **Integrations → Custom Repositories**, add this repo URL and select **Integration** as the category.

After installation, go to **Settings → Devices & Services → Add Integration** and search for **Home Brewing**.

You'll be prompted for:
- A name for this brew (e.g. `Coopers Pale Ale`)
- Your SG sensor entity
- Your temperature sensor entity
- Original gravity (OG) and target final gravity (FG)

---

## Dashboard

A pre-built brew dashboard is included in the `dashboards/` folder.

### Prerequisites

Install the following via HACS before importing the dashboard:

- **[apexcharts-card](https://github.com/RomRider/apexcharts-card)** — used for the SG history charts

### Beer glass card (bundled)

The dashboard uses a custom Lovelace card (`www/brew-glass-card.js`) that displays fermentation progress, estimated ABV, and brew temperature as animated beer glass fill indicators.

**To install:**

1. Copy `www/brew-glass-card.js` from this repo to `/config/www/` on your Home Assistant instance.
2. In HA, go to **Settings → Dashboards**, open the three-dot menu and select **Resources**.
3. Click **Add resource** and enter:
   - URL: `/local/brew-glass-card.js`
   - Resource type: **JavaScript module**
4. Reload the browser.

The card is configured in the dashboard YAML automatically — no extra setup needed once the resource is registered.

### Importing the dashboard

1. Go to **Settings → Dashboards → Add Dashboard**.
2. Choose **Start with an empty dashboard**, then open the three-dot menu and select **Edit → Raw configuration editor**.
3. Paste the contents of `dashboards/dashboard.yaml`.
4. Find and replace `new_norfolk_brown_ale` with your actual brew's entity slug (e.g. if your brew is called `Coopers Pale Ale` the slug will be `coopers_pale_ale`).

Your brew slug can be confirmed by checking **Settings → Devices & Services → Home Brewing** and looking at the entity IDs listed there.

---

## Contributing

Pull requests welcome. Please open an issue first for significant changes.
