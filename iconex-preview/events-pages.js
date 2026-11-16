/* Dedicated iCONEX Create / Execute routes. No fabricated delivery status. */
(function(){
'use strict';
const create={"eyebrow":"iCONEX CREATE · OUR VISION, OUR STAGE","headline":"Conferences, Summits & Forums Originated by iCONEX","lead":"We conceive, brand, curate, and host our own flagship international platforms—bringing together policymakers, industry leaders, and global communities across borders.","strip":["Concept & Theme Development","Speaker & Exhibitor Curation","Branding & Marketing","Venue & Logistics","Audience Building"],"label":"Flagship iCONEX Platforms","cards":[{"filter":"Healthcare & EMS","tag":"HEALTHCARE & EMS · 6TH EDITION","title":"GEMS 2026 — Global Summit on Emergency Medical Services","details":"20 – 21 November 2026 · Vivanta Hyderabad, Begumpet, India","href":"https://globalems.in/","image":"./assets/iconex-conference-audience.avif","alt":"GEMS 2026 Emergency Medical Services Summit"},{"filter":"HSE & Artificial Intelligence","tag":"AI & SAFETY-CRITICAL SECTORS · MIDDLE EAST","title":"AI-HSSE 2027 — International Conference & Exhibition on AI in Health, Safety, Security & Environment","details":"20 – 22 April 2027 · Gulf Convention Centre, Kingdom of Bahrain","href":"https://aihsse.com/","image":"./assets/ai-hsse-event.avif","alt":"AI-HSSE 2027 International Conference & Exhibition"},{"filter":"HSE & Artificial Intelligence","tag":"HEALTH, SAFETY & ENVIRONMENT · FLAGSHIP SERIES","title":"Global HSE — International Conference & Exhibition on Health, Safety and Environment","details":"Kingdom of Bahrain & GCC","href":"https://www.globalhse.org/","image":"./assets/global-hse-event.avif","alt":"Global HSE Conference & Exhibition"},{"filter":"Energy & Digitalisation","tag":"ENERGY & DIGITAL TRANSFORMATION · 6TH EDITION","title":"GEDC 2026 — Global Energy Digitalisation Conclave","details":"20 – 21 August 2026 · Pride Plaza Hotel, Aerocity, New Delhi, India","href":"https://www.gedcevent.com/","image":"./assets/gedc-event.avif","alt":"GEDC 2026 Global Energy Digitalisation Conclave"},{"filter":"Hospitality & Destinations","tag":"DESTINATION WEDDINGS & HOSPITALITY · MICE","title":"GDEC — Global Destinations Expo & Conference","details":"India Expo Centre & Mart, Greater Noida, India","href":"https://gdecevents.com/home","image":"./assets/gdec-event.avif","alt":"GDEC Global Destinations Expo & Conference"}],"closing":"Want to Speak, Exhibit, or Partner at an iCONEX Create Platform?","action":"Get in Touch"};
const execute={
eyebrow:'iCONEX EXECUTE · YOUR VISION, OUR CRAFT',
headline:'Turnkey Exhibition Stalls, Pavilions & Client Events Built by Us',
lead:'We partner with governments, enterprise brands, and organizers to design, engineer, fabricate, and deliver high-impact physical experiences from initial brief to final handover.',
strip:['Exhibition Stand Design & Visualisation','Fabrication & Installation','Pavilion Concepts','On-Site Project Coordination','Dismantling'],
label:'Client Project Concepts',
cards:[
{tag:'GOVERNMENT PAVILION · ENERGY & INFRASTRUCTURE',title:'DGH — High-Tech Integrated Exhibition Stall',details:'Ministry of Petroleum & Natural Gas, Govt. of India · 19.5m × 11m Turnkey Pavilion',desc:'Spatial architecture integrating curved LED columns, holographic exploration zones, interactive kiosks, and dedicated VVIP bilateral meeting suites.'},
{tag:'PAVILION ARCHITECTURE · MINING & METALS',title:'Hindalco — Engineering Better Futures',details:'Four-Side Open Experiential Pavilion',desc:'A four-side open architectural showcase structuring industrial storytelling around intelligent mining, advanced materials, and circularity.'},
{tag:'CORPORATE TRADE EXPERIENCE · MULTI-SECTOR',title:'IMR Resources — One Brand, Six Sectors',details:'Connected Multi-Vertical Exhibition Environment',desc:'Unifying six business divisions under one cohesive canopy with executive hospitality lounges and structured B2B engagement zones.'}],
closing:'Have an Exhibition Stall, Pavilion, or Corporate Event in Mind?',action:'Discuss a Project'
};
const esc=v=>String(v).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

const ixFilters=['All Platforms (5)','Healthcare & EMS','HSE & Artificial Intelligence','Energy & Digitalisation','Hospitality & Destinations'];
document.addEventListener('click',event=>{
 const control=event.target.closest('button[data-ixe-filter]');
 if(!control)return;
 const page=control.closest('.ixe-create');
 if(!page)return;
 const selected=control.dataset.ixeFilter;
 page.querySelectorAll('button[data-ixe-filter]').forEach(btn=>{
  const active=btn.dataset.ixeFilter===selected;
  btn.classList.toggle('is-active',active);btn.setAttribute('aria-pressed',String(active));
 });
 page.querySelectorAll('.ixe-event-card').forEach(card=>{
  card.hidden=selected!=='all'&&card.dataset.sector!==selected;
 });
});
window.iconexEventsPage=function(kind){
 if(kind==='execute' && typeof window.iconexExecuteCatalogue==='function') return window.iconexExecuteCatalogue();
 const data=kind==='execute'?execute:create, isCreate=kind==='create';
 const cards=data.cards.map((c,i)=> isCreate
  ? '<article class="ixe-card ixe-event-card" data-sector="'+esc(c.filter)+'">'+
    '<span class="ixe-card-tag">'+esc(c.tag)+'</span>'+
    '<div class="ixe-event-media"><img src="'+esc(c.image)+'" alt="'+esc(c.alt)+'" width="960" height="540" loading="lazy" decoding="async"></div>'+
    '<h3>'+esc(c.title)+'</h3>'+
    '<p class="ixe-details">'+esc(c.details)+'</p>'+
    '<div class="ixe-index" aria-hidden="true">'+String(i+1).padStart(2,'0')+'</div>'+
    '<a class="ixe-card-action" href="'+esc(c.href)+'" target="_blank" rel="noopener noreferrer">Visit Official Website <span aria-hidden="true">↗</span></a>'+
    '</article>'
  : '<article class="ixe-card"><span class="ixe-card-tag">'+esc(c.tag)+'</span>'+
    '<p class="ixe-concept-tag">DESIGN CONCEPT · NOT A VERIFIED COMPLETED BUILD</p>'+
    '<div class="ixe-index" aria-hidden="true">'+String(i+1).padStart(2,'0')+'</div>'+
    '<h3>'+esc(c.title)+'</h3><p class="ixe-details">'+esc(c.details)+'</p>'+
    '<p class="ixe-desc">'+esc(c.desc)+'</p></article>').join('');
 const filters=isCreate?'<div class="ixe-filters" role="group" aria-label="Filter platforms by sector">'+ixFilters.map((f,i)=>'<button type="button" class="ixe-filter'+(i===0?' is-active':'')+'" data-ixe-filter="'+(i===0?'all':esc(f))+'" aria-pressed="'+(i===0?'true':'false')+'">'+esc(f)+'</button>').join('')+'</div>':'';
 return '<div class="ixe-page'+(isCreate?' ixe-create':'')+'"><section class="ixe-hero"><div class="ixe-wrap"><div class="ixe-watermark" aria-hidden="true"><span></span></div><p class="ixe-eyebrow">'+esc(data.eyebrow)+'</p><h1>'+esc(data.headline)+'</h1><p class="ixe-lead">'+esc(data.lead)+'</p></div></section><section class="ixe-cover"><div class="ixe-wrap"><h2 class="ixe-small-heading">'+(isCreate?'What iCONEX Create Covers':'End-to-End Execution Capabilities')+'</h2><div class="ixe-pills">'+data.strip.map(x=>'<span class="ixe-capability">'+esc(x)+'</span>').join('')+'</div></div></section><section class="ixe-showcase"><div class="ixe-wrap"><p class="ixe-eyebrow">'+(isCreate?'OUR PLATFORMS':'OUR DESIGN WORK')+'</p><h2>'+esc(data.label)+'</h2>'+filters+(!isCreate?'<p class="ixe-disclosure">The projects below are presented as proposed design concepts. Execution, fabrication and completed handover have not been independently verified.</p>':'')+'<div class="ixe-grid">'+cards+'</div></div></section>'+(!isCreate?'<section class="ixe-end"><div class="ixe-wrap"><div class="ixe-panel"><h2>'+esc(data.closing)+'</h2><div class="ixe-closing-actions"><a href="/contact" data-ix-route class="ixe-close-cta">'+esc(data.action)+'</a></div></div></div></section>':'')+'</div>';
};

})();