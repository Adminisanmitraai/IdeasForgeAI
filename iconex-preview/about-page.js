(function(){
'use strict';
const metrics=[
['30+','Global Events','Across international markets'],
['1,000+','Stakeholders','Public & private sector leaders'],
['55,000+ sq.mtr','Exhibition Area','Turnkey spatial engineering'],
['30,000+','Delegates','Global industry attendees'],
['42,000+','Visitors','Cross-border attendance'],
['3,000+','VIPs & Speakers','Ministers, CXOs & thought leaders']
];
const purpose=[
['OUR VISION','An Inspiring After-Feel for Every Participant','Top-notch visualization to ensure that everyone who attends the event—whether an exhibitor, visitor, delegate, speaker, or sponsor—leaves with a truly inspiring after-feel. We visualize to enlighten each moment of the event through our warm hospitality and dedicated services.'],
['OUR MISSION','Zero-Risk Execution & Policy Advocacy','We ensure risks are taken care of so that our clients don’t have to—promoting awareness, policy advocacy, and business development by connecting stakeholders across health, safety, environment, energy, and technology for sustainable societal development.'],
["THE 3 I'S OF iCONEX",'Inspire · Innovate · Implement','With a highly experienced team bringing cumulative decades of expertise, we create platforms for thought leaders and industry stakeholders to network and inspire each other with innovative ideas that spring into measurable business excellence and sustainability.']
];
const capabilities=[
['PLANNING & RESEARCH','Event management, exhibition planning, and sector-specific market research tailored to strategic briefs.'],
['PROMOTION & SPEAKERS','Targeted stakeholder outreach, international promotion, and high-level speaker and VIP coordination.'],
['VENUE & SUPPLIERS','End-to-end venue management, architectural spatial design, and vetted global supplier liaising.'],
['ONSITE DELIVERY','Precision onsite coordination, technical production, and seamless hospitality from opening to teardown.']
];
const partners=['Tamkeen','Tatweer Petroleum','ASSP','Bahrain Management Society','BCSP','GPA GCC','RECSO','Shespro'];
const tag=t=>'<p class="ixa-overline">'+t+'</p>';
const section=(cl,content)=>'<section class="ixa-section '+cl+'"><div class="ixa-container">'+content+'</div></section>';
const number=i=>String(i+1).padStart(2,'0');
window.iconexAboutPage=function(){
const hero=section('ixa-hero','<div class="ixa-emblem" aria-hidden="true"><span></span></div><div class="ixa-hero-content">'+tag('ABOUT iCONEX · ESTABLISHED 2013')+'<h1>More Than Events — We Create Platforms for Progress</h1><p class="ixa-lead">iCONEX is an international business events and exhibition company, creating platforms that connect industry, government, experts, and communities. Through exhibitions, conferences, summits, and industry events, we bring people and ideas together to encourage knowledge sharing, collaboration, innovation, and business development.</p><div class="ixa-actions"><a class="ixa-button primary" href="/events/all-events" data-ix-route>Explore Our Events</a><a class="ixa-button secondary" href="/contact" data-ix-route>Partner With Us</a></div></div>');
const story=section('ixa-story','<div class="ixa-split"><div>'+tag('WHO WE ARE')+'<h2>Passionate Execution at Par With International Standards</h2><p>We design and create meetings, conferences, and exhibitions that are enlightening, and our team effort ensures they are memorable too. Working with iCONEX is more than using skills to manage conferences or exhibitions or simply coordinating at par with international standards—it comes from our team\'s passion to execute, reconfirmed by the testimonials of our clients.</p><p>For each conference or exhibition, we remain as passionate and honest as we were for our very first event, keeping us enthusiastic from planning through delivery. With a global presence across the Middle East, Asia Pacific, Europe, USA, and India, iCONEX has been dedicated since 2013 to promoting a paradigm shift for a sustainable future, technology intervention, and connecting stakeholders across industries.</p></div><aside class="ixa-identity"><span class="ixa-pill">OUR CATALYST ROLE</span><p>iCONEX is an international specialist in organizing conferences, events, seminars, workshops, and training programs—acting as a catalyst organization pursuing business objectives toward the promotion and facilitation of tools and technologies for a resilient and sustainable future.</p><dl><div><dt>Global Footprint</dt><dd>Middle East, Asia Pacific, Europe, USA &amp; India</dd></div><div><dt>Core Sectors</dt><dd>Health, Safety, Environment, Energy, Technology &amp; Industry</dd></div><div><dt>Track Record</dt><dd>Connecting global communities &amp; policymakers since 2013</dd></div></dl></aside></div>');
const impact=section('ixa-impact','<div class="ixa-heading">'+tag('OUR IMPACT')+'<h2>Impact at a Glance</h2></div><div class="ixa-metrics">'+metrics.map(m=>'<article class="ixa-metric"><strong>'+m[0]+'</strong><h3>'+m[1]+'</h3><p>'+m[2]+'</p></article>').join('')+'</div>');
const philosophy=section('ixa-purpose','<div class="ixa-heading">'+tag('PURPOSE & DIRECTION')+'<h2>Our Vision, Mission &amp; Philosophy</h2><p>Guided by warm hospitality, risk-free delivery, and our core belief in Inspire, Innovate, and Implement.</p></div><div class="ixa-grid three">'+purpose.map((p,i)=>'<article class="ixa-card"><span class="ixa-pill">'+p[0]+'</span><h3>'+p[1]+'</h3><p>'+p[2]+'</p><span class="ixa-watermark" aria-hidden="true">'+number(i)+'</span></article>').join('')+'</div>');
const how=section('ixa-how','<div class="ixa-heading">'+tag('HOW WE DO')+'<h2>Focused Personal Attention Backed by Global Depth</h2><p>With the help of our resources, in-depth industry knowledge, and vast experience, iCONEX manages and organizes events worldwide across sectors. Our focused and effective team ensures a deeply personal approach to every client—supported by a top-notch industry network, venue management, supplier liaising, and onsite coordination from planning through delivery.</p></div><div class="ixa-grid four">'+capabilities.map((p,i)=>'<article class="ixa-card"><span class="ixa-pill">'+number(i)+' — '+p[0]+'</span><p>'+p[1]+'</p><span class="ixa-watermark" aria-hidden="true">'+number(i)+'</span></article>').join('')+'</div>');
const trust=section('ixa-trust','<div class="ixa-heading">'+tag('INSTITUTIONAL TRUST')+'<h2>Our Clients &amp; Strategic Partners</h2><p>Collaborating with government bodies, national energy enterprises, and international safety and management councils.</p></div><div class="ixa-partners" aria-label="Client and partner names">'+partners.map(p=>'<div class="ixa-partner">'+p+'</div>').join('')+'</div>');
return '<div class="ixa-about">'+hero+story+impact+philosophy+how+trust+'</div>';
};
})();