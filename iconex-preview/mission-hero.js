/* Section 2 only: mission-led hero. The existing header, routes and lower pages remain intact. */
(function () {
  'use strict';
  const VERSION = '20261110-mission-v1';
  if (window.__iconexMissionHero === VERSION || typeof window.heroSlider !== 'function') return;
  window.__iconexMissionHero = VERSION;
  const initialAnchor = location.hash;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let entered = false;

  function methodology() {
    return `<section id="methodology" class="ix-methodology" aria-labelledby="ix-methodology-title" tabindex="-1">
      <div class="ix-methodology-inner">
        <div class="ix-methodology-intro">
          <span class="ix-methodology-overline">OUR APPROACH</span>
          <h2 id="ix-methodology-title">The 4D methodology of iCONEX.</h2>
          <p>Our engineered framework transforms event briefs into reality. From clarifying audience priorities to coordinating structures and executing on the exhibition floor, we ensure every stage delivers measurable impact.</p>
        </div>
        <ol class="ix-methodology-stages" aria-label="The four methodology stages in order">
          <li><span class="ix-methodology-number">01</span><strong>DISCOVER</strong><span class="ix-methodology-arrow" aria-hidden="true">→</span></li>
          <li><span class="ix-methodology-number">02</span><strong>DESIGN</strong><span class="ix-methodology-arrow" aria-hidden="true">→</span></li>
          <li><span class="ix-methodology-number">03</span><strong>DEVELOP</strong><span class="ix-methodology-arrow" aria-hidden="true">→</span></li>
          <li><span class="ix-methodology-number">04</span><strong class="ix-methodology-deliver">DELIVER</strong></li>
        </ol>
      </div>
    </section>`;
  }

  function missionHero() {
    const entrance = !entered;
    entered = true;
    return `<section id="iconex-mission-hero" class="ix-mission-hero" aria-labelledby="ix-mission-title" data-entrance="${entrance}">
      <div class="ix-mission-content">
        <p class="ix-mission-badge">WE BELIEVE IN THE 3 I'S — INSPIRE, INNOVATE &amp; IMPLEMENT</p>
        <h1 id="ix-mission-title" class="ix-mission-title">Connecting Businesses<br> Creating Opportunities<br> for a <span>Sustainable Future</span></h1>
        <p class="ix-mission-lead">At iCONEX, we specialize in organizing international conferences, exhibitions, summits, workshops, and training programmes tailored for governments and major industries—accelerating a paradigm shift through collaborative global platforms.</p>
        <div class="ix-mission-actions">
          <a class="ix-mission-button ix-mission-primary" href="/events/all-events" data-ix-route>Explore All Events</a>
          <a class="ix-mission-button ix-mission-secondary" href="#methodology" data-ix-hero-scroll>Discover Our 4D Approach <span aria-hidden="true">↓</span></a>
        </div>
      </div>
      <a class="ix-mission-scroll" href="#methodology" data-ix-hero-scroll aria-label="Scroll to our 4D methodology">
        <span class="ix-mission-scroll-label">SCROLL TO DISCOVER</span>
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
      </a>
    </section>${methodology()}`;
  }
  missionHero.iconexMissionVersion = VERSION;
  window.heroSlider = missionHero;
  // app.js owns routing and cleanup. Its setupHeroSlider safely returns when
  // there is no carousel, so replacing this function creates no extra timers.

  function scrollToMethodology(writeHistory, instant) {
    const target = document.getElementById('methodology');
    if (!target) return;
    const header = document.getElementById('iconex-header');
    const headerHeight = header ? header.getBoundingClientRect().height : 80;
    target.style.scrollMarginTop = (headerHeight + 20) + 'px';
    if (writeHistory && location.hash !== '#methodology') {
      history.pushState(Object.assign({}, history.state, {iconexAnchor: 'methodology'}), '', location.pathname + location.search + '#methodology');
    }
    target.focus({preventScroll: true});
    window.scrollTo({top: Math.max(0, window.scrollY + target.getBoundingClientRect().top - headerHeight - 20), behavior: reduceMotion.matches || instant ? 'auto' : 'smooth'});
  }
  // Capture prevents the legacy hash router from mistaking an in-page anchor
  // for a page route. Default behaviour is retained for modified/new-tab clicks.
  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target instanceof Element ? event.target.closest('a[data-ix-hero-scroll]') : null;
    if (!link || !document.getElementById('methodology')) return;
    event.preventDefault();
    scrollToMethodology(true, false);
  }, true);
  // Header navigation resolves clean URLs after this deferred module executes.
  // Preserve direct anchor visits and back/forward anchor restoration afterward.
  const restoreAnchor = function () {
    requestAnimationFrame(function () {
      if (!document.getElementById('methodology')) return;
      history.replaceState(history.state, '', location.pathname + location.search + '#methodology');
      scrollToMethodology(false, true);
    });
  };
  if (initialAnchor === '#methodology') {
    document.addEventListener('DOMContentLoaded', function () {
      if (document.getElementById('methodology')) {
        history.replaceState(history.state, '', location.pathname + location.search + '#methodology');
        restoreAnchor();
      }
    }, {once: true});
  }
  window.addEventListener('popstate', function () {
    if (location.hash === '#methodology') restoreAnchor();
  });
})();
