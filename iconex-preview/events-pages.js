/* Dedicated iCONEX Create / Execute routes. No fabricated delivery status. */
(function(){
'use strict';
const create={
eyebrow:'iCONEX CREATE · OUR VISION, OUR STAGE',
headline:'Conferences, Summits & Forums Originated by iCONEX',
lead:'We conceive, brand, curate, and host our own flagship industry platforms—bringing together policymakers, global thought leaders, and enterprise stakeholders across borders.',
strip:['Concept & Theme Development','Speaker & Exhibitor Curation','Branding & Marketing','Venue & Logistics','Audience Building'],
label:'Flagship iCONEX Platforms',
cards:[
{tag:'FLAGSHIP SUMMIT · INDIA',title:'GEMS 2026 — Global Summit on Emergency Medical Services',details:'20 – 21 November 2026 · Vivanta Hyderabad, Begumpet, India',desc:'Uniting international health leaders, emergency response pioneers, and policymakers to advance intelligent, resilient emergency medical systems.',cta:'Explore Summit',href:'https://www.iconexglobal.com/events/all-events'},
{tag:'INTERNATIONAL CONFERENCE · MIDDLE EAST',title:'AI-HSSE 2027',details:'Kingdom of Bahrain',desc:'An international platform exploring artificial intelligence, operational excellence, and next-generation health, safety, security, and environmental standards.',cta:'Explore Summit',href:'https://www.iconexglobal.com/events/all-events'}],
closing:'Want to Speak, Exhibit, or Partner at an iCONEX Platform?',action:'Get in Touch'
};
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
window.iconexEventsPage=function(kind){
const data=kind==='execute'?execute:create;
const cards=data.cards.map((c,i)=>'<article class="ixe-card"><span class="ixe-card-tag">'+esc(c.tag)+'</span>'+(kind==='execute'?'<p class="ixe-concept-tag">DESIGN CONCEPT · NOT A VERIFIED COMPLETED BUILD</p>':'')+'<div class="ixe-index">'+String(i+1).padStart(2,'0')+'</div><h3>'+esc(c.title)+'</h3><p class="ixe-details">'+esc(c.details)+'</p><p class="ixe-desc">'+esc(c.desc)+'</p>'+(c.cta?'<a class="ixe-card-action" href="'+esc(c.href)+'" target="_blank" rel="noopener noreferrer">'+esc(c.cta)+' <span aria-hidden="true">↗</span></a>':'')+'</article>').join('');
return '<div class="ixe-page"><section class="ixe-hero"><div class="ixe-wrap"><div class="ixe-watermark" aria-hidden="true"><span></span></div><p class="ixe-eyebrow">'+esc(data.eyebrow)+'</p><h1>'+esc(data.headline)+'</h1><p class="ixe-lead">'+esc(data.lead)+'</p></div></section><section class="ixe-cover"><div class="ixe-wrap"><h2 class="ixe-small-heading">'+(kind==='create'?'What iCONEX Create Covers':'End-to-End Execution Capabilities')+'</h2><div class="ixe-pills">'+data.strip.map(x=>'<span class="ixe-capability">'+esc(x)+'</span>').join('')+'</div></div></section><section class="ixe-showcase"><div class="ixe-wrap"><p class="ixe-eyebrow">'+(kind==='create'?'OUR PLATFORMS':'OUR DESIGN WORK')+'</p><h2>'+esc(data.label)+'</h2>'+(kind==='execute'?'<p class="ixe-disclosure">The projects below are presented as proposed design concepts. Execution, fabrication and completed handover have not been independently verified.</p>':'')+'<div class="ixe-grid">'+cards+'</div></div></section><section class="ixe-end"><div class="ixe-wrap"><div class="ixe-panel"><h2>'+esc(data.closing)+'</h2><a href="/contact" data-ix-route class="ixe-close-cta">'+esc(data.action)+'</a></div></div></section></div>';
};
})();