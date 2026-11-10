/* Section 4: company-supplied institutional metrics, approved in the website brief.
 * Load after philosophy.js and before header-navigation.js.
 * No analytics, storage, API requests, or changes to other sections.
 */
(function () {
  'use strict';
  const VERSION = '20261110-impact-v1';
  const originalHero = window.heroSlider;
  if (typeof originalHero !== 'function' || window.__iconexImpactMetrics === VERSION) return;
  window.__iconexImpactMetrics = VERSION;

  const DURATION = 2200;
  const THRESHOLD = 0.25;
  const metrics = [
    { value: 30, label: 'Global Events Organized', context: 'Across international markets' },
    { value: 1000, label: 'Industry & Government Stakeholders', context: 'Public & private sector leaders' },
    { value: 55000, unit: 'sq.mtr', label: 'Managed Exhibition Footprint', context: 'Turnkey spatial engineering' },
    { value: 30000, label: 'Participating Delegates', context: 'Global industry attendees' },
    { value: 42000, label: 'Event Visitors', context: 'Cross-border attendance' },
    { value: 3000, label: 'VIPs & Keynote Speakers', context: 'Ministers, CXOs & thought leaders' }
  ];
  const formatter = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 });
  const escapeText = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let completed = false;
  let started = false;
  let section = null;
  let observer = null;
  let frame = null;
  let counters = [];
  let mainObserver = null;

  function impactSection() {
    const cards = metrics.map((metric, index) => {
      const final = formatter.format(metric.value);
      const accessible = `${final}+${metric.unit ? ' square metres' : ''}`;
      return `<div class="ix-impact-stat" data-metric-index="${index}">
        <dt class="ix-impact-label">${escapeText(metric.label)}</dt>
        <dd class="ix-impact-value">
          <span class="ix-impact-figure" aria-hidden="true"><span class="ix-impact-number" data-final="${final}"><span class="ix-impact-current" data-count-target="${metric.value}">${final}</span></span><span class="ix-impact-plus">+</span></span>${metric.unit ? `<span class="ix-impact-unit" aria-hidden="true">${metric.unit}</span>` : ''}
          <span class="ix-impact-sr">${accessible}</span>
        </dd>
        <dd class="ix-impact-context">${escapeText(metric.context)}</dd>
      </div>`;
    }).join('');
    return `<section id="iconex-impact-metrics" class="ix-impact" data-ix-section="impact-metrics" data-count-state="static" aria-labelledby="ix-impact-title">
      <div class="ix-impact-inner">
        <header class="ix-impact-intro"><p class="ix-impact-overline">THE PROOF OF SCALE</p><h2 id="ix-impact-title">Impact at a Glance</h2></header>
        <div class="ix-impact-panel"><dl class="ix-impact-grid">${cards}</dl></div>
      </div>
    </section>`;
  }
  function heroWithImpact() {
    const html = originalHero.apply(this, arguments);
    const template = document.createElement('template');
    template.innerHTML = html;
    if (template.content.querySelector('#iconex-impact-metrics')) return html;
    const philosophy = template.content.querySelector('#iconex-philosophy');
    if (!philosophy) return html;
    const markup = document.createElement('template');
    markup.innerHTML = impactSection();
    const slot = template.content.querySelector('#ix-impact-metrics-slot');
    if (slot) slot.replaceWith(markup.content.firstElementChild);
    else philosophy.after(markup.content.firstElementChild);
    return template.innerHTML;
  }
  Object.assign(heroWithImpact, originalHero);
  heroWithImpact.iconexImpactVersion = VERSION;
  window.heroSlider = heroWithImpact;

  function stopFrame() {
    if (frame !== null) window.cancelAnimationFrame(frame);
    frame = null;
  }
  function finish() {
    stopFrame();
    if (observer) { observer.disconnect(); observer = null; }
    counters.forEach(counter => { counter.node.textContent = formatter.format(counter.target); });
    if (section) section.dataset.countState = 'complete';
    completed = true;
  }
  function cleanup() {
    stopFrame();
    if (observer) { observer.disconnect(); observer = null; }
    // A route change during the count must not replay it when returning home.
    if (started) completed = true;
    section = null;
    counters = [];
  }
  function startCount() {
    if (!section || started || completed) { if (section) finish(); return; }
    started = true;
    section.dataset.countState = 'running';
    if (observer) { observer.disconnect(); observer = null; }
    let firstTimestamp = null;
    const tick = timestamp => {
      if (!section || !section.isConnected) { cleanup(); return; }
      if (motion.matches || document.hidden) { finish(); return; }
      if (firstTimestamp === null) firstTimestamp = timestamp;
      const progress = Math.min(1, Math.max(0, (timestamp - firstTimestamp) / DURATION));
      const eased = progress === 0 ? 0 : progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      counters.forEach(counter => {
        const value = Math.floor(counter.target * eased);
        if (value !== counter.lastValue) {
          counter.node.textContent = formatter.format(value);
          counter.lastValue = value;
        }
      });
      if (progress < 1) frame = window.requestAnimationFrame(tick);
      else finish();
    };
    frame = window.requestAnimationFrame(tick);
  }
  function mount() {
    const next = document.getElementById('iconex-impact-metrics');
    if (next === section) return;
    cleanup();
    section = next;
    if (!section) return;
    counters = Array.from(section.querySelectorAll('[data-count-target]')).map(node => ({ node, target: Number(node.dataset.countTarget), lastValue: 0 }));
    if (completed || motion.matches || !('IntersectionObserver' in window) || typeof window.requestAnimationFrame !== 'function') {
      finish();
      return;
    }
    section.dataset.countState = 'ready';
    counters.forEach(counter => { counter.node.textContent = '0'; });
    observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= THRESHOLD)) startCount();
    }, { threshold: THRESHOLD });
    observer.observe(section.querySelector('.ix-impact-panel'));
  }
  function initialise() {
    const main = document.getElementById('main');
    if (!main || mainObserver) return;
    // Observe only page replacements, not counter text changes. One observer for this module.
    mainObserver = new MutationObserver(mount);
    mainObserver.observe(main, { childList: true });
    mount();
  }
  motion.addEventListener('change', () => { if (motion.matches && section) finish(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden && started && !completed) finish(); });
  window.addEventListener('pagehide', cleanup);
  window.addEventListener('pageshow', event => { if (event.persisted) mount(); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialise, { once: true });
  else initialise();
})();
