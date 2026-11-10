/* Section 3: the 3 I's. Loaded after mission-hero.js and before header-navigation.js.
   Adds homepage content only; does not change hero, navigation, routes or timers. */
(function () {
  'use strict';
  const VERSION = '20261110-philosophy-v1';
  const originalHero = window.heroSlider;
  if (typeof originalHero !== 'function' || originalHero.iconexPhilosophyVersion === VERSION) return;

  const pillars = [
    {
      number: '01', title: 'INSPIRE',
      description: 'Connecting global thought leaders, government delegates, speakers, and industry stakeholders to spark meaningful cross-border dialogue and fresh perspectives on business excellence.',
      tag: 'Cross-Border Dialogue & Thought Leadership',
      icon: '<path d="m12 2 2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4L12 2Z"/><path d="M20 2v4M18 4h4"/>'
    },
    {
      number: '02', title: 'INNOVATE',
      description: 'Curating specialized international conferences, exhibitions, and summits that showcase cutting-edge tools, resilient technologies, and breakthrough industry solutions.',
      tag: 'Specialized Summits & Exhibitions',
      icon: '<path d="M7 6.5 10 10m4 0 3-3.5M7 17.5l3-3.5m4 0 3 3.5"/><circle cx="12" cy="12" r="3"/><circle cx="5" cy="4.5" r="2.5"/><circle cx="19" cy="4.5" r="2.5"/><circle cx="5" cy="19.5" r="2.5"/><circle cx="19" cy="19.5" r="2.5"/>'
    },
    {
      number: '03', title: 'IMPLEMENT',
      description: 'Translating ambition into measurable impact through hands-on technical workshops, corporate training programmes, and precision-engineered exhibition platforms.',
      tag: 'Workshops, Training & Turnkey Execution',
      icon: '<path d="m12 3 10 5-10 5L2 8l10-5Zm-10 9 10 5 10-5M2 16l10 5 10-5"/><path d="m9 8 2 2 4-4"/>'
    }
  ];
  const escapeText = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));
  function philosophySection() {
    const cards = pillars.map(pillar => `<article class="ix-pillar-card" aria-labelledby="ix-pillar-title-${pillar.number}">
      <span class="ix-pillar-watermark" aria-hidden="true">${pillar.number}</span>
      <div class="ix-pillar-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" focusable="false">${pillar.icon}</svg></div>
      <p class="ix-pillar-counter">PILLAR ${pillar.number}</p>
      <h3 id="ix-pillar-title-${pillar.number}">${pillar.title}</h3>
      <p class="ix-pillar-description">${escapeText(pillar.description)}</p>
      <div class="ix-pillar-tag"><span>${escapeText(pillar.tag)}</span></div>
    </article>`).join('');
    return `<section id="iconex-philosophy" class="ix-philosophy" aria-labelledby="ix-philosophy-title" data-ix-section="philosophy">
      <div class="ix-philosophy-inner">
        <header class="ix-philosophy-intro">
          <p class="ix-philosophy-overline">CORE PILLARS OF OUR PURPOSE</p>
          <h2 id="ix-philosophy-title">We Believe in the 3 I's</h2>
          <p class="ix-philosophy-lead">At iCONEX, our mission is anchored in connecting stakeholders and communities across borders and industries to accelerate a paradigm shift for a sustainable future.</p>
        </header>
        <div class="ix-philosophy-grid">${cards}</div>
      </div>
    </section>`;
  }
  function heroWithPhilosophy() {
    const html = originalHero.apply(this, arguments);
    const template = document.createElement('template');
    template.innerHTML = html;
    const hero = template.content.querySelector('#iconex-mission-hero');
    if (!hero || template.content.querySelector('#iconex-philosophy')) return html;
    const sectionTemplate = document.createElement('template');
    sectionTemplate.innerHTML = philosophySection();
    const section = sectionTemplate.content.firstElementChild;
    hero.after(section);
    const metrics = template.content.querySelector('[data-ix-section="impact-metrics"], #impact-metrics, #iconex-impact-metrics');
    if (metrics) {
      section.after(metrics);
    } else {
      // Reserved, non-rendering insertion point. Never publish invented impact figures.
      const metricsSlot = document.createElement('template');
      metricsSlot.id = 'ix-impact-metrics-slot';
      metricsSlot.dataset.ixSlot = 'impact-metrics';
      section.after(metricsSlot);
    }
    return template.innerHTML;
  }
  heroWithPhilosophy.iconexPhilosophyVersion = VERSION;
  heroWithPhilosophy.iconexMissionVersion = originalHero.iconexMissionVersion;
  window.heroSlider = heroWithPhilosophy;
  // The next deferred script (header-navigation.js) renders the homepage once
  // using its existing clean-URL bridge. No listeners, observers or timers added.
})();
