/* iCONEX header enhancement and clean-URL bridge. No change to hero rendering or timers. */
(function () {
  'use strict';
  const header = document.getElementById('iconex-header');
  const drawer = document.getElementById('iconex-nav-drawer');
  if (!header || !drawer || typeof window.render !== 'function') return;
  // The legacy app owns #menu and #links. Replace their nodes to remove its
  // old click listeners, without touching app.js or carousel lifecycle code.
  const oldToggle = document.getElementById('menu');
  const oldPanel = document.getElementById('links');
  const toggle = oldToggle.cloneNode(true);
  const panel = oldPanel.cloneNode(true);
  oldToggle.replaceWith(toggle);
  oldPanel.replaceWith(panel);
  const eventsButton = document.getElementById('ix-events-toggle');
  const eventsPanel = document.getElementById('ix-events-links');
  const eventsItem = document.getElementById('ix-events-item');
  const mobileEvents = document.getElementById('ix-mobile-events');
  const closeButton = drawer.querySelector('.ix-close');
  const mainElement = document.getElementById('main');
  const desktop = window.matchMedia('(min-width: 1024px)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let hoverTimer = null;
  let closeTimer = null;
  let priorOverflow = '';
  let lastFocus = null;

  function setEvents(open, focusLink) {
    window.clearTimeout(hoverTimer);
    eventsButton.setAttribute('aria-expanded', String(open));
    eventsPanel.hidden = !open;
    if (open && focusLink) {
      const links = eventsPanel.querySelectorAll('a');
      links[focusLink === 'last' ? links.length - 1 : 0].focus();
    }
  }
  eventsButton.addEventListener('click', function () {
    setEvents(eventsButton.getAttribute('aria-expanded') !== 'true');
  });
  eventsButton.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      setEvents(true, event.key === 'ArrowUp' ? 'last' : 'first');
    }
  });
  eventsItem.addEventListener('pointerenter', function () {
    if (desktop.matches && finePointer.matches) setEvents(true);
  });
  eventsItem.addEventListener('pointerleave', function () {
    if (desktop.matches && finePointer.matches) {
      hoverTimer = window.setTimeout(function () {
        if (!eventsItem.contains(document.activeElement)) setEvents(false);
      }, 160);
    }
  });
  eventsItem.addEventListener('focusout', function (event) {
    if (!eventsItem.contains(event.relatedTarget)) setEvents(false);
  });
  document.addEventListener('pointerdown', function (event) {
    if (!eventsItem.contains(event.target)) setEvents(false);
  });
  eventsItem.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      event.preventDefault();
      setEvents(false);
      eventsButton.focus();
    }
  });

  function finishDrawerClose(returnFocus) {
    window.clearTimeout(closeTimer);
    closeTimer = null;
    if (drawer.open) drawer.close();
    drawer.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = priorOverflow;
    mobileEvents.open = false;
    if (returnFocus && lastFocus && lastFocus.isConnected) lastFocus.focus({preventScroll:true});
  }
  function closeDrawer(returnFocus, immediate) {
    if (!drawer.open) return;
    drawer.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    if (immediate || reduced.matches) finishDrawerClose(returnFocus);
    else {
      window.clearTimeout(closeTimer);
      closeTimer = window.setTimeout(function () { finishDrawerClose(returnFocus); }, 220);
    }
  }
  function openDrawer() {
    if (desktop.matches || drawer.open) return;
    setEvents(false);
    lastFocus = document.activeElement;
    priorOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    drawer.showModal();
    toggle.setAttribute('aria-expanded', 'true');
    requestAnimationFrame(function () { drawer.classList.add('is-open'); closeButton.focus(); });
  }
  toggle.addEventListener('click', openDrawer);
  closeButton.addEventListener('click', function () { closeDrawer(true, false); });
  drawer.addEventListener('cancel', function (event) { event.preventDefault(); closeDrawer(true, false); });
  // Explicit keyboard containment complements native dialog behavior and keeps
  // focus inside the drawer at both ends of its navigation sequence.
  drawer.addEventListener('keydown', function (event) {
    if (event.key !== 'Tab' || !drawer.open) return;
    const focusable = Array.from(drawer.querySelectorAll(
      'a[href], button:not([disabled]), summary, input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )).filter(function (element) {
      return element.tabIndex >= 0 && element.getClientRects().length > 0 &&
        getComputedStyle(element).visibility !== 'hidden' && !element.closest('[inert]');
    });
    if (!focusable.length) { event.preventDefault(); return; }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first || !drawer.contains(document.activeElement))) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !drawer.contains(document.activeElement))) {
      event.preventDefault(); first.focus();
    }
  });
  drawer.addEventListener('click', function (event) {
    if (event.target !== drawer) return;
    const rect = drawer.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) closeDrawer(true, false);
  });
  desktop.addEventListener('change', function () { closeDrawer(false, true); setEvents(false); });
  let scrollScheduled = false;
  function updateScroll() { header.classList.toggle('is-scrolled', window.scrollY > 12); scrollScheduled = false; }
  window.addEventListener('scroll', function () {
    if (!scrollScheduled) { scrollScheduled = true; requestAnimationFrame(updateScroll); }
  }, {passive:true});
  updateScroll();

  const publicPaths = new Set(['/', '/about', '/events/upcoming-events', '/events/all-events', '/global-presence', '/gallery', '/career', '/contact']);
  const titles = {'/':'Exhibition Design & Services','/about':'About Us','/events/upcoming-events':'Upcoming Events','/events/all-events':'All Events','/global-presence':'Global Presence','/gallery':'Gallery','/career':'Career','/contact':'Contact Us'};
  function normalise(path) {
    let result;
    try { result = decodeURIComponent(path); } catch (_) { return '/not-found'; }
    result = result.replace(/\/index\.html$/, '').replace(/\/+$/, '') || '/';
    return result.startsWith('/') && !result.startsWith('//') ? result : '/not-found';
  }
  function currentPath() {
    return normalise(location.hash.startsWith('#/') ? location.hash.slice(1) : location.pathname);
  }
  function routeURL(path) { return publicPaths.has(path) ? path : '/#' + path; }
  function updateActive(path) {
    header.querySelectorAll('[data-ix-route]').forEach(function (link) {
      if (link.getAttribute('href') === path) link.setAttribute('aria-current','page');
      else link.removeAttribute('aria-current');
    });
    drawer.querySelectorAll('[data-ix-route]').forEach(function (link) {
      if (link.getAttribute('href') === path) link.setAttribute('aria-current','page');
      else link.removeAttribute('aria-current');
    });
    const isEvent = path.startsWith('/events/');
    eventsButton.dataset.current = String(isEvent);
    mobileEvents.querySelector('summary').dataset.current = String(isEvent);
  }
  function eventDestination(upcoming) {
    const title = upcoming ? 'Upcoming Events' : 'All Events';
    return '<section class="ix-nav-destination"><h1>' + title + '</h1>' +
      '<p>Explore iCONEX conferences, exhibitions and industry programmes.</p>' +
      '<div class="ix-notice"><h2>Official event information</h2><p>This preview does not host a verified event schedule. Please check the official event directory for dates, locations and registration details.</p>' +
      '<a href="https://www.iconexglobal.com/events/all-events" target="_blank" rel="noopener noreferrer">View the official event directory <span aria-hidden="true">↗</span><span class="ix-sr"> (opens in a new tab)</span></a></div>' +
      '<p>For event enquiries, <a href="/contact" data-ix-route>contact iCONEX</a>.</p></section>';
  }
  // Add only destinations required by the new navigation. Reuse existing verified/review-labelled content.
  if (typeof routes !== 'undefined') {
    routes['/events/upcoming-events'] = function () { return eventDestination(true); };
    routes['/events/all-events'] = function () { return eventDestination(false); };
    routes['/global-presence'] = window.iconexGlobalPresencePage;
    routes['/gallery'] = function () { return typeof realEventGallery === 'function' ? '<h1 class="ix-sr">Gallery</h1>' + realEventGallery() : '<section class="ix-nav-destination"><h1>Gallery</h1><p>Event photography is being prepared.</p></section>'; };
    routes['/career'] = function () {
      return '<section class="ix-nav-destination"><h1>Career</h1><p>Interested in working with iCONEX?</p><div class="ix-notice"><p>No verified vacancies are published on this preview. For career enquiries, please use the contact page. Do not submit sensitive identity documents through the demonstration form.</p><a href="/contact" data-ix-route>Contact Us</a></div></section>';
    };
  }
  const originalRender = window.render;
  let rendering = false;
  function renderRoute() {
    if (rendering) return;
    rendering = true;
    const path = currentPath();
    const search = location.search;
    const marketAnchor = path === '/' && location.hash === '#global-markets' ? '#global-markets' : '';
    closeDrawer(false, true);
    setEvents(false);
    try {
      // Original renderer reads the hash. replaceState does not emit hashchange,
      // so no duplicate carousel timers or extra browser-history entries are created.
      history.replaceState(history.state, '', '/'+search+'#'+path);
      originalRender();
      history.replaceState(history.state, '', routeURL(path)+(publicPaths.has(path)?search:'')+marketAnchor);
      if (marketAnchor) requestAnimationFrame(function () {
        const markets = document.getElementById('global-markets');
        if (markets && location.hash === marketAnchor) markets.scrollIntoView();
      });
      updateActive(path);
      if (titles[path]) document.title = titles[path] + ' | iCONEX Preview';
    } finally { rendering = false; }
  }
  window.render = renderRoute;
  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href]');
    if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
    const href = link.getAttribute('href');
    if (href === '#main') {
      event.preventDefault();
      if (mainElement) {
        mainElement.focus({preventScroll:true});
        const targetTop = window.scrollY + mainElement.getBoundingClientRect().top - header.offsetHeight;
        window.scrollTo({top:Math.max(0,targetTop),behavior:'auto'});
      }
      return;
    }
    let url;
    try { url = new URL(link.href, location.href); } catch (_) { return; }
    if (url.origin !== location.origin) return;
    const hashRoute = url.hash.startsWith('#/');
    const path = normalise(hashRoute ? url.hash.slice(1) : url.pathname);
    if (!hashRoute && !publicPaths.has(path)) return;
    event.preventDefault();
    const destination = routeURL(path);
    if (location.pathname + location.hash !== destination) history.pushState({iconexRoute:path},'',destination);
    renderRoute();
    if (mainElement) mainElement.focus({preventScroll:true});
  });
  window.addEventListener('popstate', renderRoute);
  renderRoute();
})();
