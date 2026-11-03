
const $=s=>document.querySelector(s);
const nav=[["Home","/"],["About","/about"],["Services","/services"],["Projects","/projects"],["Industries","/industries"],["Capabilities","/capabilities"],["Process","/process"],["Insights","/insights"],["Contact","/contact"]];
const services=[
{n:"Custom Exhibition Stands",d:"Exhibition stand layouts and design concepts tailored to brand objectives, audience engagement and venue requirements.",icon:"01"},
{n:"3D Design & Visualisation",d:"3D views and spatial layouts to support design evaluation, stakeholder review and informed project decisions.",icon:"02"},
{n:"Stand Fabrication & Build",d:"Fabrication planning, material coordination and booth construction support in accordance with the approved project scope.",icon:"03"},
{n:"Exhibition Branding",d:"Brand graphics, signage and display elements designed to communicate clearly across exhibition environments.",icon:"04"},
{n:"Corporate & Country Pavilions",d:"Integrated pavilion concepts with coordinated branding, exhibitor zones, meeting areas and visitor circulation.",icon:"05"},
{n:"Installation & Event Support",d:"Installation coordination, on-site readiness and dismantling support according to agreed responsibilities.",icon:"06"}
];
const concepts=[
{n:"The Industrial Forum",cat:"Industrial",type:"Pavilion",size:"Large",city:"Concept study",shade:"bronze",image:"./assets/concept-industrial.webp",alt:"AI-generated industrial exhibition pavilion concept",desc:"An illustrative industrial pavilion with product demonstration areas, clear visitor routes and dedicated meeting spaces."},
{n:"A New Energy Experience",cat:"Energy",type:"Custom stand",size:"Medium",city:"Concept study",shade:"sage",image:"./assets/concept-energy.webp",alt:"AI-generated energy exhibition stand concept",desc:"A proposed energy-sector stand combining thematic displays, digital presentation features and open discussion areas."},
{n:"The Future Interface",cat:"Technology",type:"Experience",size:"Large",city:"Concept study",shade:"blue",image:"./assets/concept-technology.webp",alt:"AI-generated technology exhibition booth concept",desc:"An illustrative technology showcase organised around product demonstrations, digital content and business meetings."},
{n:"Commerce in Motion",cat:"Manufacturing",type:"Custom stand",size:"Small",city:"Concept study",shade:"umber",image:"./assets/concept-manufacturing.webp",alt:"AI-generated booth fabrication and material detail concept",desc:"A proposed compact trade-show stand incorporating product displays, visible branding and a practical visitor layout."}
];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const href=p=>"#"+p;
const arrow='<span aria-hidden="true">↗</span>';
const button=(label,route,ghost=false)=>'<a class="action '+(ghost?'action-ghost':'')+'" href="'+href(route)+'"><span>'+label+'</span>'+arrow+'</a>';
const label=s=>'<span class="eyebrow"><span class="eyeline"></span>'+s+'</span>';
const tile=(p,i)=>'<article class="project-card" data-industry="'+esc(p.cat)+'" data-type="'+esc(p.type)+'" data-size="'+esc(p.size)+'"><div class="project-image concept-art '+p.shade+'"><img class="project-photo" src="'+p.image+'" alt="'+esc(p.alt)+'" loading="lazy" decoding="async" width="900" height="506"><span class="art-tag">AI-GENERATED CONCEPT · NOT BUILT WORK</span></div><div class="project-info"><div class="project-overline"><span>CONCEPT / '+String(i+1).padStart(2,'0')+'</span><span>'+p.cat+' · '+p.type+'</span></div><h3>'+p.n+'</h3><p>'+p.desc+'</p><span class="project-meta">'+p.city+' / Proposed creative direction</span><a class="case-link" href="#/project/'+(i+1)+'">Explore concept '+arrow+'</a></div></article>';
const intro=(eyebrow,heading,copy,number)=>'<section class="inner-hero"><div class="shell">'+label(eyebrow)+'<h1>'+heading+'</h1><p>'+copy+'</p><span class="hero-index">ICONEX / '+number+'</span></div></section>';
const closing=()=>'<section class="closing"><div class="shell closing-layout">'+label('Planning an exhibition?')+'<h2>Let’s plan<br><em>your exhibition space.</em></h2><p>Share your exhibition name, location, stand size and objectives so the requirements can be reviewed and discussed.</p>'+button('Request a project discussion','/quote')+'</div></section>';
const serviceCards=()=>'<div class="service-grid">'+services.map((s,i)=>'<article class="service-item"><div class="service-top"><span>'+s.icon+'</span><span aria-hidden="true">↗</span></div><h3>'+s.n+'</h3><p>'+s.d+'</p><a href="#/quote" class="mini-link">Discuss this service '+arrow+'</a></article>').join('')+'</div>';
const sectionVisuals={services:{src:"./assets/services.webp",alt:"AI-generated exhibition design capabilities montage in blue and white"},portfolio:{src:"./assets/portfolio.webp",alt:"AI-generated mining, energy and exhibition environment concept montage"},process:{src:"./assets/design-process.webp",alt:"AI-generated 3D exhibition design planning visual"},industry:{src:"./assets/concept-energy.webp",alt:"AI-generated renewable energy exhibition concept"},about:{src:"./assets/concept-lounge.webp",alt:"AI-generated exhibition meeting lounge concept"}};
const sectionImage=kind=>{const a=sectionVisuals[kind];return '<figure class="editorial-visual editorial-'+kind+'"><img src="'+a.src+'" alt="'+a.alt+'" loading="lazy" decoding="async" width="1200" height="675"><figcaption>Illustrative AI-generated exhibition concept · Not a completed ICONEX project</figcaption></figure>'};
const portfolio=(limited)=>'<div class="portfolio-grid">'+(limited?concepts.slice(0,3):concepts).map(tile).join('')+'</div>';

/* ICONEX three-slide hero: approved brand identity and 4D process */
function heroSlider(){
  const slides=[
    '<div class="iconex-slide active" id="iconex-slide-1" role="group" aria-roledescription="slide" aria-label="Slide 1 of 3" aria-hidden="false">'+
      '<div class="iconex-slide-inner shell"><div class="iconex-slide-copy">'+label("THE THREE I\u0027S OF iCONEX")+
        '<h1 class="iconex-hero-title three-i"><span><b class="initial-i">I</b>nspire, </span><span><b class="initial-i">I</b>nnovate, </span><span><b class="initial-i">I</b>mplement.</span></h1>'+
        '<p>We specialize in organizing international conferences, exhibitions, and summits for governments and major industries, connecting stakeholders across borders to accelerate a sustainable future.</p>'+
        '<div class="hero-actions">'+button("Contact Us","/contact")+
          '<a class="action action-ghost" href="https://www.iconexglobal.com/events/all-events" target="_blank" rel="noopener noreferrer"><span>Upcoming Events</span><span aria-hidden="true">↗</span></a></div>'+
      '</div><figure class="iconex-slide-visual"><img src="./assets/hero.webp" alt="Concept rendering of a blue-and-white exhibition pavilion, not a completed ICONEX project" width="1672" height="941" fetchpriority="high"><figcaption>Illustrative exhibition concept · AI-generated</figcaption></figure></div>'+
    '</div>',
    '<div class="iconex-slide" id="iconex-slide-2" role="group" aria-roledescription="slide" aria-label="Slide 2 of 3" aria-hidden="true" inert>'+
      '<div class="iconex-slide-inner shell iconex-slide-method"><div class="iconex-slide-copy iconex-method-copy">'+label("Our approach")+
        '<h2 class="iconex-hero-title method-heading">The 4D methodology <br><em>of iCONEX.</em></h2>'+
        '<p>Our engineered framework transforms event briefs into reality. From clarifying audience priorities to coordinating structures and executing on the exhibition floor, we ensure every stage delivers measurable impact.</p>'+
        '<ol class="methodology-stages" aria-label="The four methodology stages in order">'+
          '<li><span class="stage-num">01</span><strong>DISCOVER</strong></li>'+
          '<li><span class="stage-num">02</span><strong>DESIGN</strong></li>'+
          '<li><span class="stage-num">03</span><strong>DEVELOP</strong></li>'+
          '<li class="stage-deliver"><span class="stage-num">04</span><strong>DELIVER</strong></li>'+
        '</ol>'+
      '</div></div>'+
    '</div>',
    '<div class="iconex-slide" id="iconex-slide-3" role="group" aria-roledescription="slide" aria-label="Slide 3 of 3" aria-hidden="true" inert>'+
      '<div class="iconex-slide-inner shell"><div class="iconex-slide-copy">'+label("Integrated event services")+
        '<h2 class="iconex-hero-title one-partner">ONE PARTNER, <br><em>EVERY STAGE.</em></h2>'+
        '<p>Leverage our comprehensive capabilities. We seamlessly integrate high-impact architecture, immersive digital displays, and dedicated business interaction zones to elevate your global brand presence.</p>'+
        '<div class="hero-actions">'+button("Explore Services","/services")+button("Contact Us","/contact",true)+'</div>'+
      '</div><figure class="iconex-slide-visual"><img src="./assets/services.webp" alt="AI-generated exhibition spaces and services concept montage" width="1672" height="941" loading="lazy"><figcaption>Illustrative exhibition concepts · AI-generated</figcaption></figure></div>'+
    '</div>'
  ];
  return '<section class="iconex-carousel" id="iconex-carousel" aria-label="ICONEX featured messages" aria-roledescription="carousel">'+
    '<div class="iconex-slide-stack">'+slides.join("")+'</div>'+
    '<div class="shell iconex-carousel-controls" aria-label="Hero slideshow controls">'+
      '<span class="iconex-slide-counter" id="iconex-slide-counter" aria-live="off">01 / 03</span>'+
      '<div class="iconex-dots" role="group" aria-label="Choose a slide">'+
        [0,1,2].map(i=>'<button type="button" class="iconex-dot'+(i===0?' active':'')+'" aria-label="Show slide '+(i+1)+'" aria-current="'+(i===0?'true':'false')+'" data-slide="'+i+'"></button>').join("")+
      '</div>'+
      '<div class="iconex-arrows">'+
        '<button type="button" class="iconex-arrow" data-hero-prev aria-label="Previous slide">←</button>'+
        '<button type="button" class="iconex-arrow" data-hero-next aria-label="Next slide">→</button>'+
        '<button type="button" class="iconex-pause" data-hero-pause aria-label="Pause automatic slides" aria-pressed="false">Pause</button>'+
      '</div>'+
    '</div>'+
  '</section>';
}


/* Original market-led discovery blocks inspired by industry-site information architecture */
function discoverySection(){
 const cards=[
  {number:"01",tag:"Event environments",title:"Discover what we create.",copy:"Explore exhibition stand concepts, pavilion environments and visual communication designed around visitor needs.",image:"./assets/concept-industrial.webp",alt:"AI-generated industrial pavilion concept",url:"#/projects",cta:"Explore concepts"},
  {number:"02",tag:"Our expertise",title:"Understand our services.",copy:"Review the proposed scope of design, visualisation, branding and coordinated exhibition build support.",image:"./assets/services.webp",alt:"AI-generated exhibition design and services montage",url:"#/services",cta:"View services"},
  {number:"03",tag:"Event discovery",title:"Find upcoming industry events.",copy:"Browse the official ICONEX events directory for announced conferences, exhibitions and professional programmes.",image:"./assets/concept-energy.webp",alt:"AI-generated energy sector exhibition environment concept",url:"https://www.iconexglobal.com/events/all-events",cta:"View official events",external:true}
 ];
 return '<section class="iconex-discovery section" aria-labelledby="discovery-heading"><div class="shell">'+
   '<div class="discovery-intro">'+label("Explore ICONEX")+'<h2 id="discovery-heading">Different needs.<br><em>Clear ways forward.</em></h2><p>Find the right starting point, whether you are exploring exhibition environments, reviewing services or looking for an upcoming industry event.</p></div>'+
   '<div class="discovery-grid">'+cards.map(card=>'<article class="discovery-card">'+
      '<div class="discovery-photo"><img loading="lazy" decoding="async" width="900" height="506" src="'+card.image+'" alt="'+card.alt+'"><span>AI-generated visual concept</span></div>'+
      '<div class="discovery-card-content"><span class="discovery-index">'+card.number+' / '+card.tag+'</span>'+
      '<h3>'+card.title+'</h3><p>'+card.copy+'</p>'+
      '<a href="'+card.url+'" '+(card.external?'target="_blank" rel="noopener noreferrer"':'')+' class="discovery-link">'+card.cta+' <span aria-hidden="true">↗</span></a></div></article>').join('')+'</div></div></section>';
}
function eventDiscoverySection(){
 return '<section class="iconex-event-band" aria-labelledby="event-band-heading"><div class="shell iconex-event-layout">'+
  '<div>'+label("From spaces to industry connections")+'<h2 id="event-band-heading">The right environment.<br><em>The right audience.</em></h2>'+
  '<p>Industry events create opportunities for organisations to present ideas, meet peers and open meaningful conversations. Explore ICONEX’s publicly listed events or discuss the requirements of your next exhibition space.</p></div>'+
  '<div class="iconex-event-actions">'+
  '<a class="action" href="https://www.iconexglobal.com/events/all-events" target="_blank" rel="noopener noreferrer"><span>Discover Events</span><span aria-hidden="true">↗</span></a>'+
  '<a class="action action-ghost" href="#/contact"><span>Contact ICONEX</span><span aria-hidden="true">↗</span></a>'+
  '<p class="small-note">Event dates and registration details are maintained by the official event source. This staging site does not independently confirm availability.</p></div></div></section>';
}

function home(){return heroSlider()+discoverySection()+
'<section class="manifesto section"><div class="shell manifesto-grid"><div>'+label('Design for the exhibition floor')+'<span class="oversized-marker">01</span></div><div><h2>Exhibition design with<br><em>clear business purpose.</em></h2><p>An effective exhibition stand must communicate the brand, support product presentation and provide room for meaningful business conversations. Our proposed design approach considers these priorities alongside the practical requirements of the venue.</p><a class="underlink" href="#/about">About ICONEX '+arrow+'</a></div></div></section>'+
'<section class="section services-section"><div class="shell"><div class="section-heading">'+label('01 / What we do')+'<div class="heading-row"><h2>Services for every stage<br><em>of exhibition planning.</em></h2><p>Review the proposed design, visualisation, fabrication coordination, event branding and installation services for your next exhibition.</p></div></div>'+sectionImage('services')+serviceCards()+'</div></section>'+
'<section class="section projects-section"><div class="shell"><div class="section-heading">'+label('02 / Exhibition concept studies')+'<div class="heading-row"><h2>Exhibition concepts<br><em>with a clear purpose.</em></h2><p>Explore illustrative stand and pavilion concepts showing different approaches to layouts, branding, displays and visitor experience. These are not completed ICONEX projects.</p></div></div>'+portfolio(true)+'<div class="section-end">'+button('View concept studies','/projects',true)+'</div></div></section>'+
'<section class="statement-section"><div class="shell"><span class="statement-index">EXHIBITION DESIGN REQUIRES BOTH CREATIVITY AND PLANNING.</span><h2>Strong visibility.<br>Clear circulation.<br><em>Purposeful engagement.</em></h2><p>Design decisions should support the exhibitor’s objectives while accounting for venue specifications, budget and construction requirements.</p></div><span class="giant-x" aria-hidden="true">X</span></section>'+
'<section class="section process-section"><div class="shell"><div class="section-heading">'+label('03 / Project approach')+'<h2>A clear process.<br><em>From brief to handover.</em></h2></div><div class="steps">'+[['Discover','Review the exhibitor’s brand, stand size, audience, venue and project objectives.'],['Imagine','Develop spatial layouts, branding directions and concept visualisations for review.'],['Develop','Confirm materials, technical drawings, commercial scope and implementation schedule.'],['Deliver','Coordinate the agreed fabrication, installation and site handover activities.']].map((s,i)=>'<div class="step"><span>0'+(i+1)+'</span><h3>'+s[0]+'</h3><p>'+s[1]+'</p></div>').join('')+'</div><p class="small-note">Proposed process for review; actual contractual scope requires confirmation.</p></div></section>'+
'<section class="section audience-section"><div class="shell"><div class="section-heading">'+label('04 / Industry applications')+'<div class="heading-row"><h2>Exhibition solutions<br><em>for diverse industries.</em></h2><p>Different sectors need different display formats, technical features and visitor experiences.</p></div></div><div class="industry-list">'+['Energy & Sustainability','Industrial & Manufacturing','Technology & Innovation','Government & Institutions','Corporate Brands & Exporters'].map((x,i)=>'<a href="#/industries"><span>0'+(i+1)+'</span><strong>'+x+'</strong><span aria-hidden="true">↗</span></a>').join('')+'</div></div></section>'+eventDiscoverySection()+closing();}
function about(){return intro('01 / Studio & outlook','Exhibition design<br><em>with a practical focus.</em>','ICONEX Exhibitions Private Limited is presenting a proposed exhibition design and services offering for corporate brands, institutions and trade-show exhibitors. The precise scope of fabrication services and company project credentials must be approved before publication.','ABOUT')+'<section class="section"><div class="shell manifesto-grid"><div>'+label('Our point of view')+sectionImage('about')+'</div><div><h2>Creative design.<br><em>Practical execution.</em></h2><p>Each exhibition brief brings together brand communication, visitor requirements, spatial limitations and delivery conditions. A structured design process helps align these considerations before technical development.</p><div class="verification">VERIFICATION REQUIRED: Company history, leadership, workshops, locations, certifications and built-project evidence.</div></div></div></section>'+closing();}
function servicesPage(){return intro('02 / Services','Exhibition services<br><em>from concept to site.</em>','Review the proposed scope of custom stand design, 3D visualisation, exhibition branding, pavilion planning and build coordination.','SERVICES')+'<section class="section services-section"><div class="shell">'+sectionImage('services')+serviceCards()+'<div class="verification">Final approval required for which fabrication, installation and production services ICONEX provides directly or through delivery partners.</div></div></section>'+closing();}
function projectsPage(){return intro('03 / Work & exploration','Concept studies<br><em>for exhibition spaces.</em>','Browse illustrative exhibition stand and pavilion concepts. These samples demonstrate design approaches only; real case studies will be added after ICONEX supplies approved project documentation.','PROJECTS')+'<section class="section projects-section"><div class="shell">'+sectionImage('portfolio')+'<div class="gallery-toolbar"><div><label for="industryFilter">Industry</label><select id="industryFilter" data-gallery-filter="industry"><option>All</option><option>Industrial</option><option>Energy</option><option>Technology</option><option>Manufacturing</option></select></div><div><label for="typeFilter">Format</label><select id="typeFilter" data-gallery-filter="type"><option>All</option><option>Pavilion</option><option>Custom stand</option><option>Experience</option></select></div><div><label for="sizeFilter">Scale</label><select id="sizeFilter" data-gallery-filter="size"><option>All</option><option>Small</option><option>Medium</option><option>Large</option></select></div><button type="button" id="resetGallery" class="reset-gallery">Reset filters ↺</button></div><p id="galleryCount" class="gallery-count" role="status" aria-live="polite">4 concept studies</p><div id="portfolioResults">'+portfolio(false)+'</div><div class="verification">All images are original CSS-based visual concept studies. No clients, completed projects, locations or project metrics are claimed.</div></div></section>'+closing();}
function industries(){return intro('04 / Sectors','Exhibition environments<br><em>for different sectors.</em>','Explore potential applications of exhibition design across corporate, industrial, technology and institutional events. Claims of ICONEX’s sector experience require supporting project evidence.','INDUSTRIES')+'<section class="section audience-section"><div class="shell">'+sectionImage('industry')+'<div class="industry-list">'+['Energy & Sustainability','Industrial & Manufacturing','Technology & Innovation','Government & Institutions','Corporate Brands & Exporters','Healthcare & Life Sciences'].map((x,i)=>'<a href="#/quote"><span>0'+(i+1)+'</span><strong>'+x+'</strong><span aria-hidden="true">↗</span></a>').join('')+'</div></div></section>'+closing();}
function capabilities(){return intro('05 / Capabilities','Project planning<br><em>across exhibition venues.</em>','Exhibition projects can involve different venue regulations, contractors and logistics requirements. ICONEX can review prospective locations and determine whether the requested scope is feasible.','CAPABILITIES')+'<section class="section"><div class="shell"><div class="manifesto-grid"><div>'+label('Delivery considerations')+'</div><div><h2>Venue requirements.<br><em>Project requirements.</em></h2><p>Design development should consider stand regulations, access schedules, materials, electrical provisions, safety requirements and the responsibilities assigned in the project agreement.</p><div class="verification">VERIFICATION REQUIRED: Confirmed international offices, workshop or partner capabilities and country coverage. No global delivery guarantees.</div></div></div></section>'+closing();}
function process(){return intro('06 / How we work','A structured process<br><em>for exhibition projects.</em>','A proposed five-stage workflow for developing an exhibition brief, reviewing designs and coordinating agreed delivery activities.','PROCESS')+'<section class="section process-section"><div class="shell">'+sectionImage('process')+'<div class="steps tall">'+[['01 / Brief','Understand the brand, dates, venue and exhibition footprint.'],['02 / Direction','Develop layouts, concept options and visual narratives.'],['03 / Detail','Confirm technical drawings, materials and project boundaries.'],['04 / Preparation','Coordinate procurement, fabrication and logistics where contracted.'],['05 / Handover','Review installation, inspection, completion and dismantling scope.']].map(s=>'<article class="step"><span>'+s[0]+'</span><p>'+s[1]+'</p></article>').join('')+'</div><div class="verification">Process and direct delivery responsibilities subject to management approval.</div></div></section>'+closing();}
function insights(){return intro('07 / Journal','Insights on<br><em>exhibition design.</em>','A planned resource section covering stand design, event preparation, visitor experience and exhibition operations.','INSIGHTS')+'<section class="section"><div class="shell"><div class="service-grid">'+[['The stand starts with the visitor','How spatial planning affects first impressions.'],['From sketch to exhibition floor','The value of clear design review and technical development.'],['Designing for discovery','A practical approach to brand messaging in busy halls.']].map((x,i)=>'<article class="service-item"><span class="eyebrow">EDITORIAL IDEA 0'+(i+1)+'</span><h3>'+x[0]+'</h3><p>'+x[1]+'</p><span class="small-note">Article not yet published</span></article>').join('')+'</div></div></section>'+closing();}
function contact(){return intro('08 / Contact','Discuss your<br><em>exhibition requirements.</em>','Provide your exhibition dates, location, stand dimensions and intended uses so the requirements can be reviewed.','CONTACT')+'<section class="section"><div class="shell contact-layout"><div>'+label('Reach the team')+'<h2>Start with<br><em>your project brief.</em></h2><p>The contacts shown were published for ICONEX’s event-organising business. Please confirm the correct contact channels for exhibition design and fabrication enquiries before this page is launched.</p><div class="verification">New Delhi, India · Published contact: connect@iconex.in<br>Riffa, Bahrain · Published contact: info@iconexgulf.com<br>Both addresses require confirmation for fabrication enquiries.</div></div><div class="form-panel">'+quoteForm()+'</div></div></section>';}
function quoteForm(){return '<form id="quoteDemo" class="quote-form"><div class="form-eyebrow">PROJECT BRIEF / PREVIEW</div><h3>Tell us about your exhibition project.</h3><p>Design demonstration only. This form does not collect, send or store submissions.</p><div class="formrow"><label for="qname">Your name</label><input id="qname" name="name" autocomplete="name" placeholder="Full name"></div><div class="formrow"><label for="qorg">Organisation</label><input id="qorg" name="organization" autocomplete="organization" placeholder="Company or institution"></div><div class="formrow"><label for="qemail">Work email</label><input id="qemail" name="email" type="email" autocomplete="email" placeholder="name@company.com"></div><div class="formrow"><label for="qevent">Event / exhibition</label><input id="qevent" name="event" placeholder="Exhibition name and city"></div><div class="formrow two"><div><label for="qarea">Stand size (m²)</label><input id="qarea" name="area" inputmode="decimal" placeholder="e.g. 80"></div><div><label for="qdate">Event month</label><input id="qdate" type="month" name="date"></div></div><div class="formrow"><label for="qmessage">Project requirements</label><textarea id="qmessage" name="message" rows="4" placeholder="Describe the stand layout, displays, meeting areas and technical requirements."></textarea></div><button type="button" class="action disabled" disabled>Submission unavailable — preview</button><p class="small-note">A secure backend, privacy terms and monitored recipient are required before activation.</p></form>';}
function quote(){return intro('09 / Start a project','Request an exhibition<br><em>project consultation.</em>','Share your exhibition details and required services. Submission will be enabled after the enquiry system is securely configured.','QUOTE')+'<section class="section"><div class="shell quote-centered">'+quoteForm()+'</div></section>';}
function legal(){return intro('Legal & privacy','Responsible<br><em>by design.</em>','Publication requires approved legal notices covering the actual company entity, services, jurisdictions and data practices.','LEGAL')+'<section class="section"><div class="shell"><div class="verification">VERIFICATION REQUIRED: Privacy Policy, Terms of Use, Cookie Notice, data retention, processors and company legal disclosures. No legal compliance is claimed.</div></div></section>';}
function projectDetail(index){const i=Number(index)-1,p=concepts[i];if(!p)return intro('Project concept','Concept not found.','Return to the concept gallery.','404')+closing();return intro('Spatial studies / '+String(i+1).padStart(2,'0'),esc(p.n).replace(' ','<br><em>')+'</em>',esc(p.desc),'CONCEPT')+'<section class="section case-study"><div class="shell"><div class="case-back"><a href="#/projects">← Back to the concept gallery</a></div><div class="case-grid"><div class="case-visual concept-art '+p.shade+'"><img class="case-photo" src="'+p.image+'" alt="'+esc(p.alt)+'" loading="lazy" decoding="async" width="900" height="506"><span class="art-tag">AI-GENERATED CONCEPT — NOT A BUILT PROJECT</span></div><aside class="case-facts"><span class="eyebrow">Study notes</span><h2>Concept objectives and planning.</h2><dl><div><dt>Sector</dt><dd>'+esc(p.cat)+'</dd></div><div><dt>Format</dt><dd>'+esc(p.type)+'</dd></div><div><dt>Scale</dt><dd>'+esc(p.size)+' concept, dimensions unspecified</dd></div><div><dt>Status</dt><dd>Creative study only</dd></div></dl><p>'+esc(p.desc)+'</p></aside></div><div class="case-phases"><article><span>01 / INTENT</span><h3>Define the stand objectives.</h3><p>Identify priority audiences, product displays, meeting needs and intended visitor movement.</p></article><article><span>02 / SPACE</span><h3>Develop the spatial layout.</h3><p>Consider visibility, entry points, circulation, presentation areas and brand graphics.</p></article><article><span>03 / DEVELOPMENT</span><h3>Assess technical feasibility.</h3><p>Review relevant venue rules, technical drawings, materials and delivery scope if the concept advances.</p></article></div><div class="verification">This is an original design study for website demonstration. No client, venue, construction, delivery or project result is claimed. Approved ICONEX renders and site photographs must replace these assets before publication as completed work.</div></div></section>'+closing();}
const routes={'/':home,'/about':about,'/services':servicesPage,'/projects':projectsPage,'/industries':industries,'/capabilities':capabilities,'/process':process,'/insights':insights,'/contact':contact,'/quote':quote,'/legal':legal};

let heroSliderCleanup=()=>{};
function disposeHeroSlider(){heroSliderCleanup();heroSliderCleanup=()=>{};}
function setupHeroSlider(){
  const root=document.getElementById('iconex-carousel');
  if(!root)return;
  const slides=[...root.querySelectorAll('.iconex-slide')];
  const dots=[...root.querySelectorAll('.iconex-dot')];
  const counter=root.querySelector('#iconex-slide-counter');
  const pauseButton=root.querySelector('[data-hero-pause]');
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  let index=0,timer=null,userPaused=false,pointerPaused=false,focusPaused=false;
  function stop(){if(timer!==null){window.clearInterval(timer);timer=null;}}
  function canPlay(){return !userPaused&&!pointerPaused&&!focusPaused&&!document.hidden&&!motion.matches;}
  function show(n){
    index=(n+slides.length)%slides.length;
    slides.forEach((slide,i)=>{
      const active=i===index;
      slide.classList.toggle('active',active);
      slide.setAttribute('aria-hidden',String(!active));
      slide.inert=!active;
    });
    dots.forEach((dot,i)=>{
      dot.classList.toggle('active',i===index);
      dot.setAttribute('aria-current',i===index?'true':'false');
    });
    counter.textContent=String(index+1).padStart(2,'0')+' / 03';
  }
  function schedule(){stop();if(canPlay())timer=window.setInterval(()=>show(index+1),5000);}
  function select(n){show(n);schedule();}
  function prev(){select(index-1);}
  function next(){select(index+1);}
  const prevButton=root.querySelector('[data-hero-prev]');
  const nextButton=root.querySelector('[data-hero-next]');
  prevButton.addEventListener('click',prev);
  nextButton.addEventListener('click',next);
  const dotHandlers=dots.map((dot,i)=>{const cb=()=>select(i);dot.addEventListener('click',cb);return cb;});
  function togglePause(){
    userPaused=!userPaused;
    pauseButton.setAttribute('aria-pressed',String(userPaused));
    pauseButton.setAttribute('aria-label',userPaused?'Resume automatic slides':'Pause automatic slides');
    pauseButton.textContent=userPaused?'Play':'Pause';
    schedule();
  }
  function mouseEnter(){pointerPaused=true;schedule();}
  function mouseLeave(){pointerPaused=false;schedule();}
  function focusIn(){focusPaused=true;schedule();}
  function focusOut(event){if(!root.contains(event.relatedTarget)){focusPaused=false;schedule();}}
  function visibility(){schedule();}
  function motionChange(){schedule();}
  pauseButton.addEventListener('click',togglePause);
  root.addEventListener('mouseenter',mouseEnter);
  root.addEventListener('mouseleave',mouseLeave);
  root.addEventListener('focusin',focusIn);
  root.addEventListener('focusout',focusOut);
  document.addEventListener('visibilitychange',visibility);
  motion.addEventListener('change',motionChange);
  show(0);schedule();
  heroSliderCleanup=()=>{
    stop();
    prevButton.removeEventListener('click',prev);
    nextButton.removeEventListener('click',next);
    dots.forEach((dot,i)=>dot.removeEventListener('click',dotHandlers[i]));
    pauseButton.removeEventListener('click',togglePause);
    root.removeEventListener('mouseenter',mouseEnter);
    root.removeEventListener('mouseleave',mouseLeave);
    root.removeEventListener('focusin',focusIn);
    root.removeEventListener('focusout',focusOut);
    document.removeEventListener('visibilitychange',visibility);
    motion.removeEventListener('change',motionChange);
  };
}

const main=document.getElementById('main');
function render(){disposeHeroSlider();let path=decodeURIComponent(location.hash.replace(/^#/,'')||'/');const fn=routes[path];const detail=path.match(/^\/project\/(\d+)$/);main.innerHTML=detail?projectDetail(detail[1]):fn?fn():intro('404','Nothing here.','The page you requested is unavailable.','404')+'<div class="shell section">'+button('Back to home','/')+'</div>';document.title=(path==='/'?'Exhibition Design & Services':path.slice(1).replace(/^\w/,a=>a.toUpperCase()))+' | ICONEX Preview';document.querySelectorAll('#links a').forEach(a=>{if(a.getAttribute('href')==='#'+path)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});const menu=document.getElementById('links'),toggle=document.getElementById('menu');menu.classList.remove('open');toggle.setAttribute('aria-expanded','false');window.scrollTo(0,0);if(path==='/')setupHeroSlider();}
const navToggle=document.getElementById('menu');
const navPanel=document.getElementById('links');
function closeMobileNav(returnFocus=false){
 navPanel.classList.remove('open');
 navToggle.setAttribute('aria-expanded','false');
 if(returnFocus)navToggle.focus();
}
navToggle.addEventListener('click',()=>{
 const open=navPanel.classList.toggle('open');
 navToggle.setAttribute('aria-expanded',String(open));
 if(open)navPanel.querySelector('a')?.focus();
});
document.addEventListener('pointerdown',event=>{
 if(navPanel.classList.contains('open')&&!navPanel.contains(event.target)&&!navToggle.contains(event.target))closeMobileNav();
});
function applyGalleryFilters(){const filters={industry:document.getElementById('industryFilter')?.value||'All',type:document.getElementById('typeFilter')?.value||'All',size:document.getElementById('sizeFilter')?.value||'All'};let count=0;document.querySelectorAll('.project-card').forEach(card=>{const show=Object.entries(filters).every(([k,v])=>v==='All'||card.dataset[k]===v);card.hidden=!show;if(show)count++});const el=document.getElementById('galleryCount');if(el)el.textContent=count?count+' concept '+(count===1?'study':'studies'):'No matching concepts. Adjust the filters.';}
document.addEventListener('change',e=>{if(e.target.matches('[data-gallery-filter]'))applyGalleryFilters()});
document.addEventListener('click',e=>{if(e.target.id==='resetGallery'){document.querySelectorAll('[data-gallery-filter]').forEach(s=>s.value='All');applyGalleryFilters()}});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&navPanel.classList.contains('open')){closeMobileNav(true);}});
window.addEventListener('hashchange',()=>{render();main.focus({preventScroll:true});});render();
