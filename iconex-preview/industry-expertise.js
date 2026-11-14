/* Homepage-only Industry Expertise section: inserted after 4D, before market/event content. */
(function () {
  'use strict';
  const previousHero = window.heroSlider;
  if (typeof previousHero !== 'function' || previousHero.iconexIndustryExpertise) return;

  const sectors = [
    { number: '01', title: 'AGRICULTURE', subtitle: 'Agri-Tech, Food Security & Sustainable Farming', icon: 'wheat' },
    { number: '02', title: 'OIL & GAS', subtitle: 'Upstream Exploration, Refining & Energy Transition', icon: 'rig' },
    { number: '03', title: 'PETROCHEMICAL', subtitle: 'Downstream Processing, Polymers & Industrial Value Chains', icon: 'plant' },
    { number: '04', title: 'CHEMICAL', subtitle: 'Specialty Chemicals, Process Safety & Green Chemistry', icon: 'flask' },
    { number: '05', title: 'PHARMA', subtitle: 'Pharmaceuticals, Life Sciences & Healthcare Innovation', icon: 'pill' },
    { number: '06', title: 'INFORMATION TECHNOLOGY', subtitle: 'Digital Transformation, AI & Enterprise Tech Ecosystems', icon: 'chip' },
    { number: '07', title: 'TOURISM', subtitle: 'Global Destination Promotion, Hospitality & MICE Forums', icon: 'compass' },
    { number: '08', title: 'SHIPPING & MARINE', subtitle: 'Maritime Logistics, Port Infrastructure & Offshore Marine', icon: 'ship' }
  ];
  const iconPaths = {
    wheat: '<path d="M12 22V4M12 9 7 5M12 13 6 10M12 17 7 15M12 9 17 5M12 13 18 10M12 17 17 15"/><path d="M6 4q4 0 4 4M18 4q-4 0-4 4"/>',
    rig: '<path d="M4 21h16M7 21l5-17 5 17M9 14h6M10 10h4M12 4v-2M3 19l3-3 3 3M15 19l3-3 3 3"/>',
    plant: '<path d="M3 21h18M5 21V11h6v10M11 21V8h7v13M7 11V5l4-2v8M14 13h2M14 17h2M19 21V13l2-2"/>',
    flask: '<path d="M9 3h6M10 3v7L5 19a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3M8 16h8"/><circle cx="10" cy="19" r=".8"/><circle cx="14" cy="18" r=".8"/>',
    pill: '<rect x="4" y="8" width="16" height="9" rx="4.5" transform="rotate(-43 12 12.5)"/><path d="m9 10 5 5M18 19h4M20 17v4"/>',
    chip: '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    compass: '<circle cx="12" cy="12" r="9"/><path d="m15.9 8.1-2.5 5.3-5.3 2.5 2.5-5.3 5.3-2.5Z"/>',
    ship: '<path d="M3 16 12 20 21 16 18 11H6l-3 5ZM9 11V5h6v6M12 5V2M2 22q2-2 4 0t4 0t4 0t4 0t4 0"/>'
  };
  const escapeText = value => String(value).replace(/[&<>"]/g, character =>
    ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;'}[character]));
  const svgIcon = name => '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" focusable="false">' + iconPaths[name] + '</svg>';

  function card(sector, mirrored) {
    return '<article class="ix-industry-card' + (mirrored ? ' ix-industry-mirrored' : '') + '" aria-labelledby="ix-industry-' + sector.number + '">' +
      '<span class="ix-industry-number" aria-hidden="true">' + sector.number + '</span>' +
      '<div class="ix-industry-copy"><h3 id="ix-industry-' + sector.number + '">' + escapeText(sector.title) + '</h3><p>' + escapeText(sector.subtitle) + '</p></div>' +
      '<span class="ix-industry-icon">' + svgIcon(sector.icon) + '</span>' +
      '</article>';
  }

  function section() {
    return '<section class="ix-industry-expertise" id="industry-expertise" aria-labelledby="ix-industry-title" data-ix-section="industry-expertise">' +
      '<div class="ix-industry-inner">' +
        '<header class="ix-industry-heading"><p class="ix-industry-overline">OUR INDUSTRY EXPERTISE</p>' +
          '<h2 id="ix-industry-title">Building platforms across industries that shape the global economy.</h2></header>' +
        '<div class="ix-industry-frame">' +
          '<span class="ix-industry-rail ix-industry-rail-left" aria-hidden="true">INDUSTRY EXPERTISE</span>' +
          '<div class="ix-industry-columns">' +
            '<div class="ix-industry-column">' + sectors.slice(0,4).map(s => card(s,false)).join('') + '</div>' +
            '<div class="ix-industry-column">' + sectors.slice(4).map(s => card(s,true)).join('') + '</div>' +
          '</div>' +
          '<span class="ix-industry-rail ix-industry-rail-right" aria-hidden="true">INDUSTRY EXPERTISE</span>' +
        '</div>' +
      '</div></section>';
  }

  function heroWithIndustries() {
    const html = previousHero.apply(this, arguments);
    const template = document.createElement('template');
    template.innerHTML = html;
    const methodology = template.content.querySelector('#methodology');
    if (!methodology || template.content.querySelector('#industry-expertise')) return html;
    const addition = document.createElement('template');
    addition.innerHTML = section();
    methodology.after(addition.content);
    return template.innerHTML;
  }
  Object.assign(heroWithIndustries, previousHero);
  heroWithIndustries.iconexIndustryExpertise = true;
  window.heroSlider = heroWithIndustries;
})();