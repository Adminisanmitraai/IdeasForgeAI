/* Section 5: the complete 4D methodology. Load after impact-metrics.js and
 * before header-navigation.js. Only replaces #methodology inside the homepage.
 * No timers, observers, route listeners, external dependencies or other edits.
 */
(function () {
  'use strict';
  const VERSION = '20261113-methodology-v2';
  const originalHero = window.heroSlider;
  if (typeof originalHero !== 'function' || originalHero.iconexMethodologyVersion === VERSION) return;

  const stages = [
    {
      number: '01', title: 'DISCOVER', headline: 'First, We Understand The Why',
      description: 'Before developing a concept, we clarify what the brand needs to communicate, who it needs to engage, and what the exhibition must achieve.',
      output: 'OUTPUT: A CLEAR STRATEGIC BRIEF'
    },
    {
      number: '02', title: 'DESIGN', headline: 'Then, We Give The Vision A Form',
      description: 'We translate strategy into a distinctive physical environment, connecting brand storytelling with architecture, visitor flow, product presentation, and engagement.',
      output: 'OUTPUT: AN EXPERIENCE CONCEPT'
    },
    {
      number: '03', title: 'DEVELOP', headline: 'We Engineer The Experience Behind The Image',
      description: 'Design becomes reality through technical planning, material selection, fabrication detailing, and coordination of the elements that make the exhibition work.',
      output: 'OUTPUT: AN EXECUTION-READY PLAN'
    },
    {
      number: '04', title: 'DELIVER', headline: 'Bring The Experience To Life',
      description: 'Seamless execution and complete on-floor accountability—managing builds, operations, stakeholder logistics, and live transitions from first VIP arrivals to final debrief.',
      output: 'OUTPUT: FLAWLESS ON-FLOOR EXECUTION'
    }
  ];
  const escapeText = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));

  function methodologySection() {
    const cards = stages.map(stage => `<li class="ix-4d-stage">
      <div class="ix-4d-track" aria-hidden="true"><span class="ix-4d-node">${stage.number}</span><span class="ix-4d-arrow">➔</span></div>
      <article class="ix-4d-card" aria-labelledby="ix-4d-stage-${stage.number}">
        <span class="ix-4d-watermark" aria-hidden="true">${stage.number}</span>
        <header class="ix-4d-card-header"><p class="ix-4d-stage-tag">STAGE ${stage.number} — THE 4D METHOD</p><h3 id="ix-4d-stage-${stage.number}">${stage.title}</h3></header>
        <h4 class="ix-4d-headline">${escapeText(stage.headline)}</h4>
        <p class="ix-4d-description">${escapeText(stage.description)}</p>
        <p class="ix-4d-output">${escapeText(stage.output)}</p>
      </article>
    </li>`).join('');
    return `<section id="methodology" class="ix-4d-method" aria-labelledby="ix-4d-title" tabindex="-1" data-ix-section="methodology" data-methodology-version="${VERSION}">
      <div class="ix-4d-inner">
        <header class="ix-4d-intro">
          <p class="ix-4d-overline">ONE PARTNER, EVERY STAGE</p>
          <h2 id="ix-4d-title">The iCONEX Methodology — 4D</h2>
          <p class="ix-4d-subtitle">FROM VISION TO EXPERIENCE</p>
          <p class="ix-4d-lead">Four Connected Stages: One accountable approach from brief to exhibition floor.</p>
        </header>
        <div class="ix-4d-pipeline">
          <ol class="ix-4d-grid" role="list" aria-label="The four methodology stages in order">${cards}</ol>
          <div class="ix-4d-row-bridge" aria-hidden="true"><span>02</span><svg viewBox="0 0 120 20" preserveAspectRatio="none" focusable="false"><path d="M118 2v7H3v8"/><path d="m0 14 3 3 3-3"/></svg><span>03</span></div>
        </div>
      </div>
    </section>`;
  }

  function heroWithMethodology() {
    const html = originalHero.apply(this, arguments);
    const template = document.createElement('template');
    template.innerHTML = html;
    const current = template.content.querySelector('#methodology');
    if (!current) return html;
    const replacement = document.createElement('template');
    replacement.innerHTML = methodologySection();
    const section = replacement.content.firstElementChild;
    current.replaceWith(section);
    const metrics = template.content.querySelector('[data-ix-section="impact-metrics"]');
    if (metrics && metrics.nextElementSibling !== section) metrics.after(section);
    return template.innerHTML;
  }
  Object.assign(heroWithMethodology, originalHero);
  heroWithMethodology.iconexMethodologyVersion = VERSION;
  window.heroSlider = heroWithMethodology;
  // header-navigation.js performs the existing final render after this module.
})();
