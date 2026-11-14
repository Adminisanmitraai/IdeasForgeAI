/* Section 7: shared market directory, geographical anchors and homepage map. */
(function () {
  'use strict';
  const previousHero = window.heroSlider;
  if (typeof previousHero !== 'function' || previousHero.iconexMarkets) return;

  const markets = [
    { id: 'in', code: 'IN', name: 'Republic of India', region: 'South Asia HQ', city: 'New Delhi & Hyderabad', focus: 'Government exhibitions, international summits and turnkey pavilions.', pinLocation: 'New Delhi', lon: 77.2, lat: 28.6 },
    { id: 'bh', code: 'BH', name: 'Kingdom of Bahrain', region: 'GCC Regional Hub', city: 'Manama', focus: 'Ministerial conferences, HSE forums and cross-border industry platforms.', lon: 50.6, lat: 26.2 },
    { id: 'sa', code: 'SA', name: 'Kingdom of Saudi Arabia', region: 'GCC Market', city: 'Al Khobar & Riyadh', focus: 'Energy conclaves, international summits and industry delegations.', pinLocation: 'Riyadh', lon: 46.7, lat: 24.7 },
    { id: 'ae', code: 'AE', name: 'United Arab Emirates', region: 'GCC Market', city: 'Dubai & Abu Dhabi', focus: 'International exhibitions, business delegations and industry platforms.', pinLocation: 'Abu Dhabi', lon: 54.4, lat: 24.5 },
    { id: 'om', code: 'OM', name: 'Sultanate of Oman', region: 'GCC Market', city: 'Muscat', focus: 'Energy and HSE forums, industry conferences and delegate exchange.', lon: 58.4, lat: 23.6 },
    { id: 'kw', code: 'KW', name: 'State of Kuwait', region: 'GCC Market', city: 'Kuwait City', focus: 'Industry conferences, energy forums and government participation.', lon: 48.0, lat: 29.4 },
    { id: 'gb', code: 'UK', name: 'United Kingdom', region: 'European Partner Network', city: 'London', focus: 'Cross-border partnerships and international delegate participation.', lon: -0.1, lat: 51.5 },
    { id: 'us', code: 'US', name: 'United States of America', region: 'North American Partner Network', city: '', focus: 'International delegate connections and cross-border industry partnerships.', pinLocation: 'Central United States', lon: -95.0, lat: 39.0 }
  ];
  const byId = new Map(markets.map(market => [market.id, market]));
  const overline = 'CROSS-BORDER REACH &amp; GLOBAL FOOTPRINT';
  const lead = 'iCONEX supports projects and industry platforms across multiple markets—connecting governments, international delegates, and enterprise ecosystems worldwide.';
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const text = value => value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  // The land, pins and callouts use one plate carrée frame: 180°W–180°E, 90°N–60°S.
  const mapWidth = 1200;
  const mapHeight = 500;
  const project = ({ lon, lat }) => [
    (lon + 180) / 360 * mapWidth,
    (90 - lat) / 150 * mapHeight
  ];
  const point = coords => coords.map(value => value.toFixed(4)).join(' ');

  // Presentation-only vertical callouts. Geographic coordinates remain unchanged.
  // All positions are in the same 1200 x 500 equirectangular map frame.
  const callouts = {
    sa: { y: 40, side: 'left', name: 'SAUDI ARABIA', direction: 'up' },
    kw: { y: 80, side: 'right', name: 'KUWAIT', direction: 'up' },
    us: { y: 425, side: 'center', name: 'USA', direction: 'down' },
    gb: { y: 370, side: 'center', name: 'UK', direction: 'down' },
    bh: { y: 375, side: 'left', name: 'BAHRAIN', direction: 'down' },
    ae: { y: 430, side: 'center', name: 'UAE', direction: 'down' },
    om: { y: 390, side: 'right', name: 'OMAN', direction: 'down' },
    in: { y: 330, side: 'center', name: 'INDIA', direction: 'down' }
  };
  function leaderCallout(market) {
    const [x, y] = project(market);
    const spec = callouts[market.id];
    const upper = spec.direction === 'up';
    const labelX = x + (spec.side === 'left' ? -12 : spec.side === 'right' ? 12 : 0);
    const anchor = spec.side === 'left' ? 'end' : spec.side === 'right' ? 'start' : 'middle';
    const lineEnd = spec.y + (upper ? 12 : -14);
    const labelY = spec.y + (upper ? 4 : 0);
    return `<g class="ix-markets-callout" data-market="${market.id}">
      <line class="ix-markets-leader" x1="${x.toFixed(4)}" y1="${y.toFixed(4)}" x2="${x.toFixed(4)}" y2="${lineEnd}"/>
      <text class="ix-markets-callout-text" x="${labelX.toFixed(4)}" y="${labelY}" text-anchor="${anchor}">${spec.name}</text>
    </g>`;
  }
  function button(market, isPin) {
    const label = text(market.name);
    const attrs = `type="button" data-market="${market.id}" aria-controls="ix-markets-tip" aria-expanded="false" aria-pressed="false"`;
    if (!isPin) return `<button class="ix-markets-pill" ${attrs}>${label}</button>`;
    const [x, y] = project(market);
    return `<button class="ix-markets-pin" ${attrs} aria-label="${label}" style="left:${(x / mapWidth * 100).toFixed(6)}%;top:${(y / mapHeight * 100).toFixed(6)}%"><svg class="ix-markets-teardrop" aria-hidden="true" viewBox="0 0 18 24" focusable="false"><path d="M9 0C3.9 0 0 4 0 9c0 6.2 5.8 12.2 9 15 3.2-2.8 9-8.8 9-15 0-5-3.9-9-9-9Z" fill="#E8C15A"/><circle cx="9" cy="8.5" r="3.6" fill="#07152B"/></svg></button>`;
  }
  function mapStage() {
    return `<ix-markets-map class="ix-markets-stage">
      <div class="ix-markets-viewport" role="group" aria-label="Interactive world map of eight iCONEX markets">
        <div class="ix-markets-canvas">
          <img class="ix-markets-base" src="./assets/world-markets.svg?v=20261113-geo" width="${mapWidth}" height="${mapHeight}" alt="" loading="lazy" decoding="async">
          <svg class="ix-markets-overlay" viewBox="0 0 ${mapWidth} ${mapHeight}" aria-hidden="true" focusable="false">
            ${markets.map(leaderCallout).join('')}
          </svg>
          ${markets.map(market => button(market, true)).join('')}
        </div>
      </div>
      <div id="ix-markets-tip" class="ix-markets-tooltip" role="tooltip" hidden>
        <p class="ix-markets-tooltip-region"></p><strong class="ix-markets-tooltip-name"></strong><p class="ix-markets-tooltip-city"></p><p class="ix-markets-tooltip-focus"></p>
      </div>
      <div class="ix-markets-directory" role="group" aria-label="Select a market">${markets.map(market => button(market, false)).join('')}</div>
    </ix-markets-map>`;
  }
  function desks() {
    const destinations = [
      ['SOUTH ASIA HEADQUARTERS', 'New Delhi, Republic of India', 'Driving large-scale government exhibitions, international summits, and turnkey pavilion engineering across India and APAC.', '+91 11 4912 2344', 'connect@iconex.in'],
      ['MIDDLE EAST REGIONAL HUB', 'Manama, Kingdom of Bahrain', 'Delivering high-level ministerial conferences, HSE forums, and cross-border industry platforms across the GCC.', '+973 1740 2889', 'info@iconexgulf.com']
    ];
    return `<div class="ix-markets-desks">${destinations.map(([badge, city, description, phone, email]) => `<article class="ix-markets-desk"><p class="ix-markets-desk-tag">${badge}</p><h3 class="ix-markets-desk-title">${city}</h3><p class="ix-markets-desk-copy">${description}</p><p class="ix-markets-desk-links"><a href="tel:${phone.replace(/\s/g, '')}">${phone}</a><span aria-hidden="true">·</span><a href="mailto:${email}">${email}</a></p></article>`).join('')}</div>`;
  }
  function header(tag, title) {
    return `<header class="ix-markets-header"><p class="ix-markets-overline">${overline}</p><${tag} class="ix-markets-title" id="ix-markets-heading">${title}</${tag}><p class="ix-markets-lead">${lead}</p></header>`;
  }
  function section() {
    return `<section class="ix-markets" id="global-markets" aria-labelledby="ix-markets-heading" data-ix-section="global-presence"><div class="ix-markets-inner">${header('h2', 'Experience Across Markets')}${mapStage()}${desks()}<div class="ix-markets-cta-wrap"><a class="ix-markets-cta" href="/global-presence" data-ix-route>Explore Our Global Presence <span class="ix-markets-cta-arrow" aria-hidden="true">→</span></a></div></div></section>`;
  }
  window.iconexGlobalPresencePage = function globalPresencePage() {
    const countries = markets.map(market => `<article class="ix-markets-country"><p class="ix-markets-tooltip-region">${market.region}</p><h2 class="ix-markets-country-name">${text(market.name)}</h2>${market.city ? `<p class="ix-markets-country-city">${text(market.city)}</p>` : ''}<p class="ix-markets-country-focus">${text(market.focus)}</p></article>`);
    return `<section id="ix-markets-directory-page" class="ix-markets ix-markets-page" aria-labelledby="ix-markets-heading"><div class="ix-markets-inner">${header('h1', 'Global Presence')}<div class="ix-markets-country-list">${countries.join('')}</div>${desks()}</div></section>`;
  };
  function withMarkets() {
    const html = previousHero.apply(this, arguments);
    const fragment = document.createElement('template');
    fragment.innerHTML = html;
    const methodology = fragment.content.querySelector('#methodology');
    if (!methodology || fragment.content.querySelector('#global-markets')) return html;
    const addition = document.createElement('template');
    addition.innerHTML = section();
    methodology.after(addition.content);
    return fragment.innerHTML;
  }
  Object.assign(withMarkets, previousHero);
  withMarkets.iconexMarkets = true;
  window.heroSlider = withMarkets;

  // The clean-URL bridge installs its route table after this module.
  const initialMarketAnchor = location.hash === '#global-markets';
  function connectDirectory() {
    if (typeof routes === 'undefined') return;
    routes['/global-presence'] = window.iconexGlobalPresencePage;
    if (location.pathname.replace(/\/$/, '') === '/global-presence' &&
        !document.getElementById('ix-markets-directory-page')) window.render();
    if (initialMarketAnchor && document.getElementById('global-markets')) {
      history.replaceState(history.state, '', location.pathname + location.search + '#global-markets');
      requestAnimationFrame(() => document.getElementById('global-markets')?.scrollIntoView());
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', connectDirectory, {once: true});
  else connectDirectory();

  class MarketMap extends HTMLElement {
    connectedCallback() {
      this.viewport = this.querySelector('.ix-markets-viewport');
      this.canvas = this.querySelector('.ix-markets-canvas');
      this.tooltip = this.querySelector('.ix-markets-tooltip');
      this.buttons = Array.from(this.querySelectorAll('button[data-market]'));
      this.selected = null;
      this.shown = null;
      this.events = new AbortController();
      const options = {signal: this.events.signal};
      this.addEventListener('click', event => {
        const button = this.marketButton(event.target);
        if (!button) return;
        this.selected = this.selected === button.dataset.market ? null : button.dataset.market;
        this.show(this.selected, button.classList.contains('ix-markets-pill'));
      }, options);
      this.addEventListener('pointerover', event => {
        if (event.pointerType !== 'mouse') return;
        const button = this.marketButton(event.target);
        if (button && !button.contains(event.relatedTarget)) this.show(button.dataset.market, false);
        if (this.tooltip.contains(event.target)) clearTimeout(this.dismissTimer);
      }, options);
      this.addEventListener('pointerout', event => {
        if (event.pointerType !== 'mouse') return;
        if (!this.marketButton(event.target) && !this.tooltip.contains(event.target)) return;
        if (this.marketButton(event.relatedTarget) || this.tooltip.contains(event.relatedTarget)) return;
        this.scheduleRestore();
      }, options);
      this.addEventListener('focusin', event => {
        const button = this.marketButton(event.target);
        if (button) this.show(button.dataset.market, true);
      }, options);
      this.addEventListener('focusout', event => {
        if (!this.marketButton(event.relatedTarget)) this.scheduleRestore();
      }, options);
      document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && this.shown) { this.selected = null; this.show(null, false); }
      }, options);
      document.addEventListener('pointerdown', event => {
        if (this.shown && !this.contains(event.target)) { this.selected = null; this.show(null, false); }
      }, options);
      this.viewport.addEventListener('scroll', () => this.position(), {passive: true, ...options});
      this.resize = new ResizeObserver(() => this.position());
      this.resize.observe(this.viewport);
      // Start mobile over the Gulf and South Asia, with the full map available to pan.
      this.viewport.scrollLeft = this.canvas.clientWidth * .64 - this.viewport.clientWidth / 2;
    }
    disconnectedCallback() {
      this.events?.abort();
      this.resize?.disconnect();
      clearTimeout(this.dismissTimer);
    }
    marketButton(target) {
      if (!(target instanceof Element)) return null;
      const button = target.closest('button[data-market]');
      return button && this.contains(button) ? button : null;
    }
    scheduleRestore() {
      clearTimeout(this.dismissTimer);
      if (!this.shown) return;
      this.dismissTimer = setTimeout(() => {
        const focused = this.marketButton(document.activeElement);
        this.show(focused?.dataset.market || this.selected, false);
      }, 200);
    }
    show(id, pan) {
      clearTimeout(this.dismissTimer);
      const market = byId.get(id);
      this.shown = market ? id : null;
      for (const button of this.buttons) {
        const active = button.dataset.market === this.shown;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-expanded', String(active));
        button.setAttribute('aria-pressed', String(button.dataset.market === this.selected));
        if (active) button.setAttribute('aria-describedby', 'ix-markets-tip');
        else button.removeAttribute('aria-describedby');
      }
      this.canvas.classList.toggle('has-active', Boolean(market));
      for (const callout of this.canvas.querySelectorAll('.ix-markets-callout')) callout.classList.toggle('is-active', callout.dataset.market === this.shown);
      this.tooltip.hidden = !market;
      if (!market) return;
      this.tooltip.querySelector('.ix-markets-tooltip-region').textContent = market.region;
      this.tooltip.querySelector('.ix-markets-tooltip-name').textContent = market.name;
      const city = this.tooltip.querySelector('.ix-markets-tooltip-city');
      city.textContent = market.pinLocation || market.city;
      city.hidden = !city.textContent;
      this.tooltip.querySelector('.ix-markets-tooltip-focus').textContent = market.focus;
      const pin = this.querySelector(`.ix-markets-pin[data-market="${id}"]`);
      if (pan && this.viewport.scrollWidth > this.viewport.clientWidth) {
        this.viewport.scrollTo({left: pin.offsetLeft - this.viewport.clientWidth / 2, behavior: motion.matches ? 'instant' : 'smooth'});
      }
      this.position();
    }
    position() {
      if (!this.shown) return;
      const pin = this.querySelector(`.ix-markets-pin[data-market="${this.shown}"]`);
      const pinRect = pin.getBoundingClientRect();
      const stage = this.getBoundingClientRect();
      const view = this.viewport.getBoundingClientRect();
      const width = this.tooltip.offsetWidth;
      const height = this.tooltip.offsetHeight;
      const x = pinRect.left + pinRect.width / 2;
      this.tooltip.style.visibility = x < view.left || x > view.right ? 'hidden' : 'visible';
      // Prefer the nearest placement that leaves neighbouring market buttons reachable.
      const y = pinRect.top + pinRect.height / 2;
      const visiblePins = this.buttons.filter(button => button.classList.contains('ix-markets-pin'))
        .map(button => button.getBoundingClientRect());
      const candidates = [
        [x - width / 2, pinRect.top - height - 5],
        [x - width / 2, pinRect.bottom + 5],
        [pinRect.right + 5, y - height / 2],
        [pinRect.left - width - 5, y - height / 2]
      ];
      let best = null;
      for (const [candidateX, candidateY] of candidates) {
        const left = Math.max(view.left + 4, Math.min(candidateX, view.right - width - 4));
        const top = Math.max(view.top + 4, Math.min(candidateY, view.bottom - height - 4));
        const overlap = visiblePins.reduce((area, other) => area +
          Math.max(0, Math.min(left + width, other.right) - Math.max(left, other.left)) *
          Math.max(0, Math.min(top + height, other.bottom) - Math.max(top, other.top)), 0);
        if (!best || overlap < best.overlap) best = { left, top, overlap };
        if (!overlap) break;
      }
      this.tooltip.style.left = `${best.left - stage.left - this.clientLeft}px`;
      this.tooltip.style.top = `${best.top - stage.top - this.clientTop}px`;
    }
  }
  if (!customElements.get('ix-markets-map')) customElements.define('ix-markets-map', MarketMap);
})();
