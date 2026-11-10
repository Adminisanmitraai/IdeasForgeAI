/* Section 6 only. After methodology.js, before header-navigation.js.
 * GEMS facts/link checked against globalems.in on 10 November 2026.
 * Pavilion briefs are supplied design material, not proof of completed delivery.
 * No external dependencies, form submission, storage or analytics.
 */
(function () {
  'use strict';
  const VERSION = '20261110-platforms-v1';
  const previousHero = window.heroSlider;
  if (typeof previousHero !== 'function' || window.__iconexPlatforms === VERSION) return;
  window.__iconexPlatforms = VERSION;
  const initialAnchor = location.hash;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
  const categories = [
    ['all', 'All Platforms'], ['summits', 'Summits & Conferences'],
    ['pavilions', 'Custom Exhibitions & Pavilions'], ['workshops', 'Workshops & Training']
  ];
  const icons = {
    date: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/>',
    place: '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    scale: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    sector: '<path d="M3 21V9l6 3V7l6 3V3h6v18H3ZM7 17h1m3 0h1m4 0h1"/>',
    space: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 3v4M13 3v4M18 3v4M3 8h4M3 13h4M3 18h4"/>',
    feature: '<path d="m12 3 9 5-9 5-9-5 9-5ZM3 12l9 5 9-5M3 16l9 5 9-5"/>'
  };
  const icon = name => `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${icons[name]}</svg>`;
  const items = [
    {id:'gems', category:'summits', tag:'Summits & Conferences', badge:'UPCOMING SUMMIT · 6TH EDITION',
      title:'GEMS 2026 — Global Summit on Emergency Medical Services',
      subtitle:'Beyond Response: Designing Intelligent, Autonomous & Resilient EMS Systems',
      meta:[['date','Date','20 – 21 November 2026'],['place','Venue','Vivanta Hyderabad, Begumpet — India'],['scale','Expected scale','500+ Global EMS Leaders & Policymakers | 50+ Exhibitors']],
      description:'India’s premier platform uniting international health ministers, military medical commanders, and technology pioneers to drive system intelligence and resilience architecture.',
      note:'Advertised scale; not confirmed attendance. Event details checked 10 November 2026.',
      register:'https://www.globalems.in/registration?sub=Delegate-Registration', details:'https://www.globalems.in/about-conference'},
    {id:'dgh', category:'pavilions', tag:'Custom Exhibitions & Pavilions', badge:'GOVERNMENT SHOWCASE',
      title:'DGH — High-Tech Integrated Exhibition Stall',
      subtitle:'Directorate General of Hydrocarbons, Ministry of Petroleum & Natural Gas, Govt of India',
      image:'./assets/dgh-showcase.avif', alt:'DGH exhibition design visual from the supplied iCONEX presentation, with curved digital columns and a large globe display', mediaLabel:'Presentation visual · delivery unverified',
      meta:[['sector','Sector','Energy & Infrastructure / Oil & Gas'],['space','Brief footprint','19.5m × 11m Custom Turnkey Pavilion'],['feature','Features','Holographic Displays, Curved LED Columns & VIP Suite']],
      description:'Turnkey spatial engineering connecting high-impact architecture, immersive digital showcases, holographic exploration zones, and dedicated private VIP bilateral meeting rooms.',
      note:'Project brief · final scope and delivery status require confirmation.',
      evidence:'This case-study preview presents the supplied showcase brief and iCONEX presentation visual. The presentation describes delivered work, while other project materials describe concepts; completion and the 19.5m × 11m footprint have not been independently reconciled. No completion date, measured result or government endorsement is claimed.',
      source:'Source: supplied Section 6 project brief and Iconex_High_Resolution_Master, slides 8–9.'},
    {id:'hindalco', category:'pavilions', tag:'Custom Exhibitions & Pavilions', badge:'PAVILION ARCHITECTURE',
      title:'Hindalco — Engineering Better Futures', subtitle:'Intelligent Mining, Advanced Materials & Circularity',
      image:'./assets/hindalco-showcase.avif', alt:'Proposed Hindalco pavilion visual with a circular canopy, planted central landmark and interactive mine model', mediaLabel:'Proposed pavilion concept',
      meta:[['sector','Sector','Mining & Metals / Sustainable Manufacturing'],['space','Architecture','Four-Side Open Immersive Pavilion'],['feature','Feature','Interactive Living Mine Model & Hologram Gateways']],
      description:'A four-side open experiential pavilion structuring complex industrial storytelling—from responsible resource extraction to high-precision aluminium and copper technologies.',
      note:'Design proposal · not presented as completed construction.',
      evidence:'This is a proposed pavilion concept, not evidence of completed construction. The features describe the supplied design brief and remain subject to client approval, organiser requirements and engineering review.',
      source:'Source: supplied Section 6 brief and Iconex_High_Resolution_Master, slide 13 (proposed pavilion concept).'},
    {id:'imr', category:'pavilions', tag:'Custom Exhibitions & Pavilions', badge:'CORPORATE TRADE EXPERIENCE',
      title:'IMR Resources — One Brand, Six Sectors', subtitle:'Global Supply Chain & Raw Material Sourcing',
      image:'./assets/imr-slide3-background.avif', alt:'IMR Resources exhibition pavilion concept with a continuous canopy, reception, media wall and meeting spaces', mediaLabel:'Exhibition design proposal',
      meta:[['sector','Sector','Corporate Trade & Multi-Vertical Commodities'],['space','Layout','Connected Multi-Vertical Journey & Business Lounge'],['feature','Focus','B2B Matchmaking & Sector Hospitality']],
      description:'Unifying six distinct business divisions under one continuous architectural canopy, combining global media walls, executive suites, and structured B2B trade engagement.',
      note:'Design proposal · not presented as completed construction.',
      evidence:'This is an exhibition design proposal using the supplied IMR visual. Spaces and engagement features represent design intent, not verified built work or measured business results.',
      source:'Source: supplied Section 6 brief and the IMR concept image previously supplied for this website.'}
  ];
  function gemsState(now = Date.now()) {
    if (now >= Date.parse('2026-11-22T00:00:00+05:30')) return {badge:'PAST SUMMIT · 6TH EDITION', register:false, pulse:false};
    if (now >= Date.parse('2026-11-20T00:00:00+05:30')) return {badge:'SUMMIT DATES · 6TH EDITION', register:true, pulse:true};
    return {badge:items[0].badge, register:true, pulse:true};
  }
  const metadata = item => `<dl class="ix-platform-meta">${item.meta.map(([kind,label,value]) => `<div>${icon(kind)}<div><dt>${esc(label)}</dt><dd>${esc(value)}</dd></div></div>`).join('')}</dl>`;
  function summitPoster() {
    // Typographic event artwork: never mislabel another event's photograph as GEMS.
    return `<div class="ix-platform-media ix-gems-poster" role="img" aria-label="GEMS 2026 event artwork: 6th edition, 20–21 November 2026, Hyderabad">
      <div class="ix-platform-art"><svg viewBox="0 0 640 320" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs><pattern id="ix-gems-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#c59b27" stroke-opacity=".12"/></pattern></defs><rect width="640" height="320" fill="url(#ix-gems-grid)"/><circle cx="540" cy="80" r="140" fill="none" stroke="#c59b27" stroke-opacity=".18"/><path d="M0 225h365l26-40 25 82 31-151 29 109h164" fill="none" stroke="#e8c15a" stroke-width="2" stroke-opacity=".6"/></svg><div class="ix-gems-poster-copy"><span>6TH GLOBAL SUMMIT</span><strong>GEMS <em>2026</em></strong><p>Emergency Medical Services</p><small>20–21 NOVEMBER · HYDERABAD</small></div></div>
    </div>`;
  }
  function photo(item) {
    return `<div class="ix-platform-media"><img class="ix-platform-photo" src="${item.image}" alt="${esc(item.alt)}" width="800" height="450" loading="lazy" decoding="async"><span class="ix-platform-media-label">${esc(item.mediaLabel)}</span><span class="ix-platform-media-fallback" hidden>Preview image unavailable</span></div>`;
  }
  function card(item) {
    const gems = item.id === 'gems';
    const state = gems ? gemsState() : {badge:item.badge};
    return `<article class="ix-platform-card" data-platform-category="${item.category}" data-platform-id="${item.id}" aria-labelledby="ix-platform-title-${item.id}">
      ${gems ? summitPoster() : photo(item)}
      <div class="ix-platform-body"><div class="ix-platform-card-top"><span class="ix-platform-category">${esc(item.tag)}</span><span class="ix-platform-badge ${gems ? 'ix-platform-badge-gold' : ''}">${state.pulse ? '<span class="ix-platform-dot" aria-hidden="true"></span>' : ''}${esc(state.badge)}</span></div>
        <h3 id="ix-platform-title-${item.id}">${esc(item.title)}</h3><p class="ix-platform-subtitle">${esc(item.subtitle)}</p>
        ${metadata(item)}<p class="ix-platform-description">${esc(item.description)}</p><p class="ix-platform-note">${esc(item.note)}</p>
        <div class="ix-platform-actions">${gems ? `${state.register ? `<a class="ix-platform-primary" href="${esc(item.register)}" target="_blank" rel="noopener noreferrer">Register as Delegate<span class="ix-platform-sr"> (official website, opens in a new tab)</span></a>` : ''}<a class="ix-platform-detail" href="${item.details}" target="_blank" rel="noopener noreferrer">View Summit Details <span aria-hidden="true">→</span><span class="ix-platform-sr"> (opens in a new tab)</span></a>` : `<button class="ix-platform-detail" type="button" data-platform-case="${item.id}" aria-haspopup="dialog" aria-controls="ix-platform-case-dialog">Explore Case Study <span aria-hidden="true">→</span><span class="ix-platform-sr">: ${esc(item.title)}</span></button>`}</div>
      </div></article>`;
  }
  function section() {
    return `<section id="featured-platforms" class="ix-platforms" data-ix-section="featured-events" aria-labelledby="ix-platforms-title" data-platforms-version="${VERSION}">
      <div class="ix-platforms-inner"><header class="ix-platforms-intro"><p class="ix-platforms-overline">GLOBAL INDUSTRY PLATFORMS</p><h2 id="ix-platforms-title">Featured Platforms &amp; Events Showcase</h2><p class="ix-platforms-lead">Explore our flagship summits, international conferences, and precision-engineered exhibition pavilions connecting governments, leaders, and enterprise stakeholders across borders.</p></header>
        <div class="ix-platform-filters" role="group" aria-label="Filter featured platforms">${categories.map(([id,label]) => `<button type="button" data-platform-filter="${id}" aria-pressed="${id==='all'}" aria-controls="ix-platform-results">${esc(label)}</button>`).join('')}</div>
        <p id="ix-platform-result-count" class="ix-platform-result-count" role="status" aria-live="polite" aria-atomic="true">4 platforms shown</p>
        <div class="ix-platform-grid" id="ix-platform-results">${items.map(card).join('')}</div>
        <div class="ix-platform-empty" hidden><h3>No workshops or training programmes are currently featured</h3><p>Browse the event directory for published programmes or contact iCONEX about your requirements.</p><a class="ix-platform-detail" href="/events/all-events" data-ix-route>Explore all events <span aria-hidden="true">→</span></a></div>
        <footer class="ix-platform-footer"><p>Looking for our complete archive of summits, conferences, and technical workshops?</p><a class="ix-platform-archive" href="/events/all-events" data-ix-route>Explore All Events &amp; Platforms <span aria-hidden="true">→</span></a></footer>
      </div>
      <dialog id="ix-platform-case-dialog" aria-labelledby="ix-platform-case-title"><div class="ix-platform-dialog-top"><span>PROJECT &amp; DESIGN SHOWCASE</span><button type="button" data-platform-close aria-label="Close case study">✕</button></div><div class="ix-platform-dialog-content"></div></dialog>
    </section>`;
  }
  function heroWithPlatforms() {
    const html = previousHero.apply(this, arguments);
    const tpl = document.createElement('template'); tpl.innerHTML = html;
    const method = tpl.content.querySelector('#methodology');
    if (!method || tpl.content.querySelector('#featured-platforms')) return html;
    const fragment = document.createElement('template'); fragment.innerHTML = section();
    const slot = tpl.content.querySelector('#ix-featured-events-slot');
    const added = fragment.content.firstElementChild;
    if (slot) slot.replaceWith(added); else method.after(added);
    if (!tpl.content.querySelector('[data-ix-section="global-presence"], #ix-global-presence-slot')) {
      const next = document.createElement('template'); next.id = 'ix-global-presence-slot'; next.dataset.ixSlot = 'global-presence'; added.after(next);
    }
    return tpl.innerHTML;
  }
  Object.assign(heroWithPlatforms, previousHero); heroWithPlatforms.iconexPlatformsVersion = VERSION; window.heroSlider = heroWithPlatforms;
  let currentDialog = null, trigger = null, priorOverflow = '';
  function releaseDialog(restore = true) {
    document.body.style.overflow = priorOverflow;
    const old = trigger; currentDialog = null; trigger = null;
    if (restore && old && old.isConnected) old.focus({preventScroll:true});
  }
  function closeDialog(restore = true) {
    if (!currentDialog) return;
    const dialog = currentDialog;
    // Release before close dispatch so a subsequent close event cannot restore stale state.
    releaseDialog(restore); if (dialog.open) dialog.close();
  }
  function openCase(button) {
    const item = items.find(value => value.id === button.dataset.platformCase && value.id !== 'gems');
    const dialog = document.getElementById('ix-platform-case-dialog');
    if (!item || !dialog || typeof dialog.showModal !== 'function') return;
    closeDialog(false);
    dialog.querySelector('.ix-platform-dialog-content').innerHTML = `<p class="ix-platform-category">${esc(item.badge)}</p><h2 id="ix-platform-case-title">${esc(item.title)}</h2><p>${esc(item.subtitle)}</p>${photo(item)}${metadata(item)}<h3>Project overview</h3><p>${esc(item.description)}</p><div class="ix-platform-evidence"><h3>Project and media status</h3><p>${esc(item.evidence)}</p><p>${esc(item.source)}</p></div><a class="ix-platform-primary" href="/contact" data-ix-route>Discuss a similar brief <span aria-hidden="true">→</span></a>`;
    currentDialog = dialog; trigger = button; priorOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden'; dialog.showModal(); dialog.querySelector('[data-platform-close]').focus();
  }
  function filter(button) {
    const root = button.closest('#featured-platforms'); if (!root) return;
    const value = button.dataset.platformFilter; let count = 0;
    root.querySelectorAll('[data-platform-filter]').forEach(el => el.setAttribute('aria-pressed', String(el === button)));
    root.querySelectorAll('.ix-platform-card').forEach(el => {
      const show = value === 'all' || el.dataset.platformCategory === value;
      el.hidden = !show;
      if (show) {
        count++;
        if (!motion.matches && typeof el.animate === 'function') {
          el.getAnimations().forEach(animation => animation.cancel());
          el.animate([{opacity:0, transform:'scale(.985)'},{opacity:1, transform:'scale(1)'}], {duration:200, easing:'ease-out'});
        }
      }
    });
    root.querySelector('.ix-platform-empty').hidden = count !== 0;
    root.querySelector('#ix-platform-result-count').textContent = count ? `${count} ${count === 1 ? 'platform' : 'platforms'} shown` : 'No featured programmes in this category';
  }
  document.addEventListener('click', function (event) {
    if (!(event.target instanceof Element)) return;
    const filterButton = event.target.closest('#featured-platforms [data-platform-filter]');
    if (filterButton) { filter(filterButton); return; }
    const caseButton = event.target.closest('#featured-platforms [data-platform-case]');
    if (caseButton) { openCase(caseButton); return; }
    if (event.target.closest('#ix-platform-case-dialog [data-platform-close]')) { closeDialog(); return; }
    if (currentDialog && event.target.closest('#ix-platform-case-dialog a[data-ix-route]')) closeDialog(false);
    if (currentDialog && event.target === currentDialog) {
      const r = currentDialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closeDialog();
    }
  });
  document.addEventListener('cancel', event => { if (event.target === currentDialog) { event.preventDefault(); closeDialog(); } }, true);
  document.addEventListener('close', event => { if (event.target === currentDialog && !event.target.open) releaseDialog(); }, true);
  document.addEventListener('keydown', function (event) {
    if (currentDialog && event.key === 'Tab') {
      const list = Array.from(currentDialog.querySelectorAll('button:not([disabled]), a[href], [tabindex="0"]')).filter(el => el.getClientRects().length);
      const first = list[0], last = list[list.length-1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
    const button = event.target instanceof Element ? event.target.closest('#featured-platforms [data-platform-filter]') : null;
    if (!button || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
    const buttons = Array.from(button.parentElement.querySelectorAll('button')); const i = buttons.indexOf(button);
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length-1 : (i + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
    event.preventDefault(); buttons[next].focus(); buttons[next].scrollIntoView({block:'nearest',inline:'nearest',behavior:'auto'});
  });
  document.addEventListener('error', event => {
    const img = event.target;
    if (img instanceof HTMLImageElement && img.matches('#featured-platforms .ix-platform-photo')) {
      img.hidden = true; const fallback = img.parentElement.querySelector('.ix-platform-media-fallback'); if (fallback) fallback.hidden = false;
    }
  }, true);
  function initialise() {
    const main = document.getElementById('main'); if (!main) return;
    new MutationObserver(() => { if (currentDialog && !currentDialog.isConnected) closeDialog(false); }).observe(main, {childList:true});
    if (initialAnchor === '#featured-platforms') restoreAnchor();
  }
  function restoreAnchor() {
    requestAnimationFrame(() => {
      const target = document.getElementById('featured-platforms'); if (!target) return;
      history.replaceState(history.state,'',location.pathname + location.search + '#featured-platforms');
      const header = document.getElementById('iconex-header');
      window.scrollTo({top:Math.max(0,window.scrollY + target.getBoundingClientRect().top - (header ? header.offsetHeight : 80) - 16),behavior:'auto'});
    });
  }
  window.addEventListener('popstate', () => { closeDialog(false); if (location.hash === '#featured-platforms') restoreAnchor(); });
  window.addEventListener('pagehide', () => closeDialog(false));
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',initialise,{once:true}); else initialise();
})();
