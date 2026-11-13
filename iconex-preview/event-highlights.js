/* The six gallery frames are shared by the homepage and the full gallery. */
(function () {
  'use strict';

  const filters = [
    ['all', 'All Highlights'],
    ['summits', 'International Summits'],
    ['stalls', 'Custom Exhibition Stalls'],
    ['vip', 'VIP Delegations & Keynotes']
  ];

  const frames = [
    {
      id: 'conclave', category: 'summits', badge: 'GLOBAL SUMMIT SERIES',
      title: 'Global HSE & Energy Leadership Conclave',
      meta: 'Gulf Convention Centre, Kingdom of Bahrain · Ministerial Plenary',
      caption: 'Bringing together energy ministers, HSE regulators, and global industry pioneers on a unified keynote stage.',
      image: 'iconex-global-hse-stage.avif', alt: 'Keynote speaker on a Global HSE stage in front of a seated audience.',
      label: 'Global HSE archive photograph', note: 'Opening keynote address at Global HSE, Gulf Convention Centre, Kingdom of Bahrain, 19–22 May 2025.'
    },
    {
      id: 'dgh', category: 'stalls', badge: 'TURNKEY PAVILION',
      title: 'Custom Exhibition Stalls & Holographic Displays',
      meta: 'Curved LED Columns & Interactive Offshore Energy Kiosks',
      caption: 'Spaces that make an impact—integrating custom architecture, large-format digital screens, and interactive showcase zones.',
      image: 'gallery-dgh-offshore.avif', alt: 'DGH pavilion concept with an underwater LED vista and an interactive offshore drilling model.',
      label: 'DGH concept render', note: 'The DGH concept pairs an immersive underwater display with a physical offshore drilling model.'
    },
    {
      id: 'imr', category: 'stalls', badge: 'EXHIBITION SHOWCASE',
      title: 'Multi-Sector Corporate Exhibition Architecture',
      meta: 'IMR Resources · One Brand, Six Sectors',
      caption: 'Connected multi-vertical exhibition environment combining executive hospitality lounges and structured B2B meeting zones.',
      image: 'imr-slide3-background.avif', alt: 'Elevated view of the green-and-white IMR Resources pavilion design, its canopy and connected meeting spaces.',
      label: 'IMR concept render', note: 'IMR Resources design proposal for a six-sector pavilion.'
    },
    {
      id: 'suites', category: 'vip', badge: 'EXECUTIVE HOSPITALITY',
      title: 'VIP Lounges & Bilateral Dialogue Suites',
      meta: 'Yashobhoomi (IICC), New Delhi · Government & CXO Delegations',
      caption: 'Private diplomatic suites and bespoke conference rooms engineered for high-stakes stakeholder engagement.',
      image: 'gallery-vip-lounge.avif', alt: 'DGH hospitality concept showing a round meeting table and lounge chairs beside interactive offshore exhibits.',
      label: 'DGH hospitality concept render', note: 'This DGH design study illustrates the hospitality layout for this highlight.'
    },
    {
      id: 'energy', category: 'summits', badge: 'SUSTAINABILITY EXPO',
      title: 'Global Sustainability & Clean Energy Forum',
      meta: 'New Delhi, India · 500+ Global Delegates',
      caption: 'Cross-border dialogue accelerating clean technology adoption and industrial circularity.',
      image: 'gallery-gedc-india.avif', alt: 'A speaker presents to a seated panel at the Global Energy Digitalisation Conclave in New Delhi.',
      label: 'GEDC India archive', note: 'Related programme photograph from the Global Energy Digitalisation Conclave, New Delhi, 25–26 May 2023.'
    },
    {
      id: 'spilltech', category: 'vip', badge: 'TECHNICAL WORKSHOPS',
      title: 'SPILLTECH & Global Emergency Response Symposia',
      meta: 'Bahrain, Oman & India · Hands-On Industry Training',
      caption: 'Interactive technical demonstrations and live crisis-response workshops connecting practitioners worldwide.',
      image: 'gallery-spilltech.avif', alt: 'A keynote speaker addresses the audience from a SPILLTECH lectern in front of offshore imagery.',
      label: 'SPILLTECH 2023 archive', note: 'Keynote photograph from iCONEX’s SPILLTECH 2023 archive.'
    }
  ];
  const lead = 'Step onto the exhibition floor and inside our ministerial summits—a visual archive of precision-engineered pavilions, VIP delegations, and global knowledge platforms.';
  const entities = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'};
  const escape = value => value.replace(/[&<>"']/g, char => entities[char]);

  function tile(frame, index) {
    return `<article class="ixg-tile" data-key="${frame.id}" data-frame="${index + 1}" data-category="${frame.category}">
      <button class="ixg-open" type="button" data-open="${frame.id}" aria-haspopup="dialog" aria-label="Open ${escape(frame.title)}">
        <img class="ixg-photo" src="./assets/${frame.image}" alt="${escape(frame.alt)}" loading="lazy" decoding="async">
        <span class="ixg-scrim" aria-hidden="true"></span>
        ${frame.label ? `<span class="ixg-provenance">${escape(frame.label)}</span>` : ''}
        <span class="ixg-expand" aria-hidden="true">↗</span>
        <span class="ixg-content"><span class="ixg-badge">${escape(frame.badge)}</span>
          <span class="ixg-name">${escape(frame.title)}</span>
          <span class="ixg-meta">${escape(frame.meta)}</span>
          <span class="ixg-caption">${escape(frame.caption)}</span>
        </span>
      </button>
    </article>`;
  }

  function lightbox(prefix) {
    return `<dialog class="ixg-dialog" aria-labelledby="${prefix}-light-title" aria-describedby="${prefix}-light-meta ${prefix}-light-caption">
      <div class="ixg-dialog-panel">
        <button type="button" class="ixg-close" aria-label="Close preview" autofocus>×</button>
        <div class="ixg-dialog-media"><img class="ixg-dialog-photo" alt=""></div>
        <div class="ixg-dialog-info">
          <p class="ixg-dialog-badge"></p><h2 class="ixg-dialog-name" id="${prefix}-light-title" aria-live="polite" aria-atomic="true"></h2>
          <p class="ixg-dialog-meta" id="${prefix}-light-meta"></p><p class="ixg-dialog-caption" id="${prefix}-light-caption"></p>
          <p class="ixg-dialog-note"></p>
          <div class="ixg-controls"><button type="button" class="ixg-prev" aria-label="Previous highlight">←</button>
            <span class="ixg-position" role="status" aria-atomic="true"></span>
            <button type="button" class="ixg-next" aria-label="Next highlight">→</button>
          </div>
        </div>
      </div>
    </dialog>`;
  }

  function galleryArchive() {
    const id = 'ix-gallery-archive';
    return `<ix-event-highlights class="ixg" id="${id}"><section class="ixg-inner" aria-labelledby="${id}-title">
      <header class="ixg-intro"><p class="ixg-overline">THE DELIVER STAGE IN ACTION</p>
        <h1 class="ixg-title" id="${id}-title">Visual Proof — Event Gallery &amp; Highlights</h1><p class="ixg-lead">${lead}</p>
      </header>
      <div class="ixg-filters" role="group" aria-label="Filter gallery highlights">
        ${filters.map(([key, label]) => `<button class="ixg-filter" data-filter="${key}" type="button" aria-controls="${id}-grid" aria-pressed="${key === 'all'}">${escape(label)}</button>`).join('')}
      </div>
      <p class="ixg-sr" role="status" aria-atomic="true">6 highlights shown</p>
      <div class="ixg-grid" id="${id}-grid" data-filter="all">${frames.map(tile).join('')}</div>
      ${lightbox(id)}
    </section></ix-event-highlights>`;
  }
  window.iconexFullGallery = () => galleryArchive() + window.realEventGallery();

  class EventHighlights extends HTMLElement {
    connectedCallback() {
      this.filter = 'all';
      this.visibleFrames = frames;
      this.dialog = this.querySelector('.ixg-dialog');
      this.filters = Array.from(this.querySelectorAll('.ixg-filter'));
      this.grid = this.querySelector('.ixg-grid');
      this.onClick = event => this.handleClick(event);
      this.onKey = event => this.handleKey(event);
      this.onClose = () => {
        // Discard any queued close event from a previous opening.
        if (this.dialog.open) return;
        const opener = this.opener;
        this.opener = null;
        if (this.isConnected && opener?.isConnected) opener.focus({preventScroll: true});
      };
      this.addEventListener('click', this.onClick);
      this.addEventListener('keydown', this.onKey);
      this.dialog.addEventListener('close', this.onClose);
    }
    disconnectedCallback() {
      this.removeEventListener('click', this.onClick);
      this.removeEventListener('keydown', this.onKey);
      this.dialog.removeEventListener('close', this.onClose);
      if (this.dialog.open) this.dialog.close();
      this.opener = null;
    }
    filterBy(key) {
      if (key === this.filter) return;
      this.filter = key;
      this.visibleFrames = key === 'all' ? frames : frames.filter(frame => frame.category === key);
      this.grid.dataset.filter = key;
      for (const item of this.grid.children) item.hidden = key !== 'all' && item.dataset.category !== key;
      for (const button of this.filters) button.setAttribute('aria-pressed', String(button.dataset.filter === key));
      this.querySelector('.ixg-sr').textContent = `${this.visibleFrames.length} highlights shown`;
    }
    handleClick(event) {
      if (event.target === this.dialog) { this.dialog.close(); return; }
      const button = event.target.closest('button');
      if (!button || !this.contains(button)) return;
      if (button.matches('.ixg-filter')) { this.filterBy(button.dataset.filter); return; }
      if (button.matches('.ixg-open')) {
        this.opener = button;
        this.showFrame(this.visibleFrames.findIndex(frame => frame.id === button.dataset.open));
        this.dialog.showModal();
        this.dialog.querySelector('.ixg-close').focus({preventScroll: true});
      } else if (button.matches('.ixg-close')) this.dialog.close();
      else if (button.matches('.ixg-prev')) this.showFrame(this.index - 1);
      else if (button.matches('.ixg-next')) this.showFrame(this.index + 1);
    }
    handleKey(event) {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      if (this.dialog.open) {
        if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
          event.preventDefault();
          this.showFrame(this.index + (event.key === 'ArrowRight' ? 1 : -1));
        } else if (event.key === 'Tab') {
          const close = this.dialog.querySelector('.ixg-close');
          const next = this.dialog.querySelector('.ixg-next');
          if (event.shiftKey && document.activeElement === close) { event.preventDefault(); next.focus(); }
          else if (!event.shiftKey && document.activeElement === next) { event.preventDefault(); close.focus(); }
        }
        // The native modal handles Escape and keeps background content inert.
        return;
      }
      const filterIndex = this.filters.indexOf(event.target);
      if (filterIndex < 0) return;
      let targetIndex;
      if (event.key === 'ArrowRight') targetIndex = (filterIndex + 1) % this.filters.length;
      else if (event.key === 'ArrowLeft') targetIndex = (filterIndex + this.filters.length - 1) % this.filters.length;
      else if (event.key === 'Home') targetIndex = 0;
      else if (event.key === 'End') targetIndex = this.filters.length - 1;
      else return;
      event.preventDefault();
      this.filters[targetIndex].focus();
    }
    showFrame(index) {
      const total = this.visibleFrames.length;
      this.index = (index + total) % total;
      const frame = this.visibleFrames[this.index];
      const image = this.dialog.querySelector('.ixg-dialog-photo');
      image.alt = frame.alt;
      image.src = './assets/' + frame.image;
      this.dialog.querySelector('.ixg-dialog-badge').textContent = frame.badge;
      this.dialog.querySelector('.ixg-dialog-name').textContent = frame.title;
      this.dialog.querySelector('.ixg-dialog-meta').textContent = frame.meta;
      this.dialog.querySelector('.ixg-dialog-caption').textContent = frame.caption;
      this.dialog.querySelector('.ixg-dialog-note').textContent = frame.note;
      this.dialog.querySelector('.ixg-position').textContent = `${this.index + 1} / ${total}`;
    }
  }
  if (!customElements.get('ix-event-highlights')) customElements.define('ix-event-highlights', EventHighlights);
})();
