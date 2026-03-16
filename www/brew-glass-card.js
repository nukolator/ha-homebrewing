class BrewGlassCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._firstRender = true;
  }

  setConfig(config) {
    if (!config.glasses || !Array.isArray(config.glasses)) {
      throw new Error('brew-glass-card: "glasses" array is required');
    }
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _pct(glass) {
    const state = this._hass.states[glass.entity];
    if (!state) return 0;
    const val = parseFloat(state.state);
    const min = glass.min ?? 0;
    const max = glass.max ?? 100;
    return Math.max(0, Math.min(100, ((val - min) / (max - min)) * 100));
  }

  _stateStr(glass) {
    const state = this._hass.states[glass.entity];
    if (!state) return 'unavailable';
    const val = parseFloat(state.state);
    const unit = glass.unit ?? state.attributes.unit_of_measurement ?? '';
    const precision = glass.precision ?? 1;
    return isNaN(val) ? state.state : `${val.toFixed(precision)}${unit}`;
  }

  _render() {
    const GH = 110, GT = 8;
    const bot = GT + GH;

    const foamPath = [
      'M 0,22',
      'Q 7,9 14,22 Q 21,35 28,22',
      'Q 35,9 42,22 Q 49,35 56,22',
      'Q 63,9 70,22',
      'L 70,31 L 0,31 Z'
    ].join(' ');

    const glassesHtml = this.config.glasses.map((g, i) => {
      const pct = this._pct(g);
      const stateStr = this._stateStr(g);
      const beer = g.beer_color ?? '#C97510';
      const foam = g.foam_color ?? '#FAE8B4';
      const off = ((1 - pct / 100) * GH).toFixed(2);

      return `
        <div class="col">
          <svg class="glass" width="74" height="${bot + 8}" viewBox="0 0 74 ${bot + 8}">
            <defs>
              <clipPath id="gcp-${i}">
                <polygon points="3,${GT} 71,${GT} 59,${bot} 15,${bot}"/>
              </clipPath>
            </defs>
            <g clip-path="url(#gcp-${i})">
              <rect class="liq" id="liq-${i}"
                x="0" y="${GT}" width="74" height="${GH}"
                fill="${beer}"
                style="transform:translateY(${this._firstRender ? GH : off}px)"/>
              <path class="foam" id="foam-${i}"
                d="${foamPath}" fill="${foam}"
                style="transform:translateY(${this._firstRender ? GH : off}px);opacity:${this._firstRender ? 0 : 1}"/>
            </g>
            <polygon
              points="3,${GT} 71,${GT} 59,${bot} 15,${bot}"
              fill="none" stroke="var(--divider-color, rgba(0,0,0,0.22))" stroke-width="1.5" stroke-linejoin="round"/>
            <line x1="8" y1="${GT + 4}" x2="19" y2="${bot - 5}"
              stroke="rgba(255,255,255,0.35)" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          <div class="val">${stateStr}</div>
          <div class="lbl">${g.name ?? g.entity}</div>
        </div>`;
    }).join('');

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { padding: 16px; }
        .row {
          display: flex;
          justify-content: space-around;
          align-items: flex-end;
          gap: 8px;
          flex-wrap: wrap;
        }
        .col {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          flex: 1;
          min-width: 80px;
        }
        .glass { overflow: visible; }
        .liq, .foam { transition: none; }
        .val {
          font-size: 15px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .lbl {
          font-size: 12px;
          color: var(--secondary-text-color);
          text-align: center;
        }
      </style>
      <ha-card>
        <div class="row">${glassesHtml}</div>
      </ha-card>`;

    if (this._firstRender) {
      this._firstRender = false;
      requestAnimationFrame(() => requestAnimationFrame(() => {
        this.config.glasses.forEach((g, i) => {
          setTimeout(() => {
            const pct = this._pct(g);
            const off = ((1 - pct / 100) * GH).toFixed(2);
            const tr = 'transform 1.4s cubic-bezier(0.18, 0, 0.08, 1)';
            const liq = this.shadowRoot.getElementById(`liq-${i}`);
            const foam = this.shadowRoot.getElementById(`foam-${i}`);
            if (liq) { liq.style.transition = tr; liq.style.transform = `translateY(${off}px)`; }
            if (foam) {
              foam.style.transition = tr + ', opacity 0.4s ease 1.2s';
              foam.style.transform = `translateY(${off}px)`;
              foam.style.opacity = '1';
            }
          }, i * 150 + 50);
        });
      }));
    }
  }

  getCardSize() { return 3; }
}

customElements.define('brew-glass-card', BrewGlassCard);
