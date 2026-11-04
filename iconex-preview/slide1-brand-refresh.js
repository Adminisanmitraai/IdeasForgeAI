/* ICONEX: scoped Slide 1 replacement. Original routes, timer and slides 2/3 remain owned by app.js. */
(function () {
  'use strict';
  const VERSION = '20261104-brand374b8c-v2-plain-bold';
  const original = window.heroSlider;
  if (typeof original !== 'function' || original.iconexBrandVersion === VERSION) return;

  const photos = [
    { key: 'stage', src: 'iconex-global-hse-stage.avif', cx: 460, cy: 140, r: 245, label: 'Conference keynote stage and audience' },
    { key: 'delegation', src: 'iconex-vip-delegation.avif', cx: 225, cy: 425, r: 235, label: 'Event participants at an opening programme' },
    { key: 'portrait', src: 'iconex-attendee-portrait.avif', cx: 805, cy: 145, r: 145, label: 'Conference participant in a seating area' },
    { key: 'group', src: 'iconex-global-hse-group.avif', cx: 670, cy: 420, r: 220, label: 'Participants at a Global HSE event backdrop' },
    { key: 'delegates', src: 'iconex-industry-delegates.avif', cx: 190, cy: 735, r: 124, label: 'Delegates attending an industry conference' },
    { key: 'audience', src: 'iconex-conference-audience.avif', cx: 475, cy: 735, r: 210, label: 'Audience attending a conference presentation' },
    { key: 'networking', src: 'iconex-event-networking.avif', cx: 835, cy: 690, r: 145, label: 'Participants pictured at an industry event' }
  ];
  function points(p) {
    return `${p.cx},${p.cy-p.r} ${p.cx+p.r},${p.cy} ${p.cx},${p.cy+p.r} ${p.cx-p.r},${p.cy}`;
  }
  function mosaic() {
    const clips = photos.map(p => `<clipPath id="s1clip-${p.key}"><polygon points="${points(p)}"/></clipPath>`).join('');
    const tiles = photos.map(p => `<g><image href="./assets/${p.src}" x="${p.cx-p.r}" y="${p.cy-p.r}" width="${2*p.r}" height="${2*p.r}" preserveAspectRatio="xMidYMid slice" clip-path="url(#s1clip-${p.key})"/><polygon points="${points(p)}" fill="none" stroke="#ffffff" stroke-width="5" stroke-linejoin="round"/></g>`).join('');
    return `<figure class="s1-brand-mosaic" aria-label="Conference and event photo mosaic supplied for ICONEX"><svg class="s1-brand-art" viewBox="0 0 980 850" role="img" aria-labelledby="s1-mosaic-title" preserveAspectRatio="xMidYMid meet"><title id="s1-mosaic-title">Seven event photographs showing conference stages, audiences and professional participants.</title><defs>${clips}</defs><g aria-hidden="true"><path d="M 885 -100 L 1020 35 L 885 170 L 750 35 Z" fill="#374b8c" opacity=".12"/><path d="M 860 490 L 890 520 L 860 550 L 830 520 Z" fill="#ffffff" opacity=".7"/>${tiles}</g></svg></figure>`;
  }
  function content() {
    return `<div class="s1-brand-grid">
      <div class="s1-brand-copy">
        <h1 class="s1-visually-hidden">Inspire, Innovate, Implement</h1>
        <ul class="s1-brand-list" aria-label="Our guiding principles">
          <li>Inspire</li><li>Innovate</li><li>Implement</li>
        </ul>
        <p class="s1-brand-description">We specialize in organizing international conferences, exhibitions, and summits for governments and major industries, connecting stakeholders across borders to accelerate a sustainable future.</p>
        <div class="s1-brand-actions">
          <a class="s1-brand-button s1-brand-primary" href="#/contact"><span>Contact Us</span><span aria-hidden="true">↗</span></a>
          <a class="s1-brand-button s1-brand-secondary" href="https://www.iconexglobal.com/events/all-events" target="_blank" rel="noopener noreferrer"><span>Upcoming Events</span><span aria-hidden="true">↗</span><span class="s1-visually-hidden"> (opens in a new tab)</span></a>
        </div>
      </div>${mosaic()}
    </div>`;
  }
  function updatedHero() {
    const html = original.apply(this, arguments);
    const template = document.createElement('template');
    template.innerHTML = html;
    const first = template.content.querySelector('#iconex-slide-1');
    if (!first) return html;
    first.classList.add('s1-brand-final');
    first.dataset.brandVersion = VERSION;
    first.innerHTML = content();
    return template.innerHTML;
  }
  updatedHero.iconexBrandVersion = VERSION;
  window.heroSlider = updatedHero;
  // Reuse app.js cleanup/initialisation; never start a second carousel timer.
  if ((location.hash === '' || location.hash === '#/' || location.hash === '#') && typeof window.render === 'function') {
    window.render();
  }
})();
