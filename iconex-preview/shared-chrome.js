/* Single source of truth for the iCONEX site header/footer and route metadata.
   No main element is created, replaced, or mutated here. */
(function () {
  "use strict";
  const labels = [
    ["Home", "/"],
    ["About Us", "/about"],
    ["iCONEX Create", "/events/iconex-create"],
    ["iCONEX Execute", "/events/iconex-execute"],
    ["Gallery", "/gallery"],
    ["Career", "/career"],
    ["Contact Us", "/contact"]
  ];
  const descriptions = {
    "/": ["iCONEX | International Exhibitions, Conferences & Business Events", "iCONEX connects industries, governments and businesses through international conferences, exhibitions, summits and business events."],
    "/about": ["About Us | iCONEX Exhibitions Private Limited", "Learn about iCONEX Exhibitions Private Limited and its international exhibitions, summits and conferences."],
    "/events/iconex-create": ["iCONEX Create | Flagship Conferences, Summits & Forums", "Explore the international conferences, summits and forums originated by iCONEX."],
    "/events/iconex-execute": ["iCONEX Execute | Turnkey Exhibition Stalls, Pavilions & Client Events", "Discover iCONEX exhibition design, pavilion and client event experience."],
    "/gallery": ["Event Gallery | iCONEX Exhibitions Private Limited", "Explore iCONEX event photography and gallery albums from international conferences and exhibitions."],
    "/career": ["Career | Join the iCONEX Team", "Explore professional disciplines and career opportunities across the iCONEX events and exhibitions team."],
    "/contact": ["Contact Us | iCONEX Exhibitions Private Limited", "Contact iCONEX about international exhibitions, conferences, event services and business partnerships."]
  };
  const normalize = (v) => {
    try { v = decodeURIComponent(v); } catch (_) { return "/"; }
    return v.replace(/\/index\.html$/, "").replace(/\/+$/, "") || "/";
  };
  function currentRoute() {
    return normalize(location.hash.startsWith("#/") ? location.hash.slice(1) : location.pathname);
  }
  function syncMetadata(route) {
    const path = normalize(route || currentRoute());
    const values = descriptions[path] || (path.startsWith("/gallery/") ? descriptions["/gallery"] : null);
    if (!values) return;
    if (!path.startsWith("/gallery/")) document.title = values[0];
    let meta = document.querySelector('meta[name="description"]');
    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "description";
      document.head.appendChild(meta);
    }
    meta.content = values[1];
    // Preview indexing policy is deliberately untouched.
  }
  window.iconexSyncMeta = syncMetadata;

  const createIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16M5 15h14v4H5zM8 15V7h8v8M12 2v3M6 5l-2-2M18 5l2-2"/></svg>';
  const executeIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 2 9 5-9 5-9-5 9-5ZM3 7v10l9 5 9-5V7M12 12v10"/></svg>';
  function eventLink(name, subtitle, href, icon) {
    return '<li><a class="ix-event-link" href="' + href + '" data-ix-route><span class="ix-event-icon" aria-hidden="true">' + icon + '</span><span class="ix-event-copy"><strong>' + name + '</strong><small>' + subtitle + '</small></span></a></li>';
  }
  const events =
    eventLink("iCONEX Create", "Internal conferences, summits & forums originated by us", "/events/iconex-create", createIcon) +
    eventLink("iCONEX Execute", "Custom exhibition stalls, pavilions & client events built by us", "/events/iconex-execute", executeIcon);
  const chev = '<svg class="ix-chevron" viewBox="0 0 16 16" aria-hidden="true"><path d="m3 6 5 5 5-5"/></svg>';
  const menuIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>';
  const closeIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>';
  const headerHTML =
    '<header class="ixc-header" id="iconex-header">' +
      '<div class="ix-nav-bar"><a class="ix-brand" href="/" data-ix-route aria-label="iCONEX Exhibitions Private Limited — home">' +
        '<img src="/iconex-header-logo-transparent.png" alt="iCONEX Exhibitions Private Limited" width="480" height="88"></a>' +
      '<nav id="links" class="ix-desktop-nav" aria-label="Main navigation"><ul class="ix-nav-items">' +
        '<li class="ix-nav-item"><a class="ix-nav-link" href="/" data-ix-route>Home</a></li>' +
        '<li class="ix-nav-item"><a class="ix-nav-link" href="/about" data-ix-route>About Us</a></li>' +
        '<li class="ix-nav-item" id="ix-events-item"><button id="ix-events-toggle" class="ix-nav-link" type="button" aria-expanded="false" aria-controls="ix-events-links">Events ' + chev + '</button><ul id="ix-events-links" class="ix-dropdown" hidden>' + events + '</ul></li>' +
        '<li class="ix-nav-item"><a class="ix-nav-link" href="/gallery" data-ix-route>Gallery</a></li>' +
        '<li class="ix-nav-item"><a class="ix-nav-link" href="/career" data-ix-route>Career</a></li>' +
      '</ul></nav>' +
      '<div class="ix-nav-actions"><a class="ix-contact" href="/contact" data-ix-route>Contact Us <span aria-hidden="true">↗</span></a>' +
      '<button type="button" id="menu" class="ix-menu-toggle" aria-label="Open navigation menu" aria-expanded="false" aria-controls="iconex-nav-drawer" aria-haspopup="dialog">' + menuIcon + '</button></div></div></header>' +
    '<dialog class="ixc-drawer" id="iconex-nav-drawer" aria-labelledby="ix-drawer-title">' +
      '<div class="ix-drawer-top"><h2 id="ix-drawer-title">Explore iCONEX</h2><button class="ix-close" type="button" aria-label="Close navigation menu">' + closeIcon + '</button></div>' +
      '<nav aria-label="Mobile navigation"><ul class="ix-drawer-links">' +
        '<li><a href="/" data-ix-route>Home</a></li><li><a href="/about" data-ix-route>About Us</a></li>' +
        '<li><details id="ix-mobile-events"><summary>Events ' + chev + '</summary><ul>' + events + '</ul></details></li>' +
        '<li><a href="/gallery" data-ix-route>Gallery</a></li><li><a href="/career" data-ix-route>Career</a></li>' +
      '</ul></nav><div class="ix-drawer-bottom"><a class="ix-contact" href="/contact" data-ix-route>Contact Us <span aria-hidden="true">↗</span></a></div></dialog>';

  const footerLinks = labels.map(([name, href]) => '<li><a href="' + href + '">' + name + '</a></li>').join("");
  const footerHTML = '<footer class="ixc-footer" aria-label="iCONEX corporate footer">' +
    '<div class="ixc-footer-grid">' +
      '<div class="ixc-footer-brand"><a href="/" aria-label="iCONEX home"><img src="/iconex-header-logo-transparent.png" alt="iCONEX Exhibitions Private Limited" width="480" height="88"></a>' +
        '<p>Conferences, exhibitions and industry connections across India and the Middle East.</p></div>' +
      '<nav class="ixc-footer-links" aria-label="Footer quick links"><h2>Quick Links</h2><ul>' + footerLinks + '</ul></nav>' +
      '<section class="ixc-footer-connect" aria-labelledby="ixc-connect-title"><h2 id="ixc-connect-title">Connect</h2>' +
        '<p>New Delhi, India<br><a href="mailto:connect@iconex.in">connect@iconex.in</a></p>' +
        '<p>Middle East Operations<br><a href="mailto:info@iconexgulf.com">info@iconexgulf.com</a></p></section>' +
    '</div><div class="ixc-footer-base">© 2026 iCONEX Exhibitions Private Limited. All rights reserved.</div></footer>';

  const head = document.getElementById("ix-shared-header");
  const foot = document.getElementById("ix-shared-footer");
  if (head && foot) {
    head.innerHTML = headerHTML;
    foot.innerHTML = footerHTML;
  }
  const header = document.getElementById("iconex-header");
  const drawer = document.getElementById("iconex-nav-drawer");
  if (header && drawer) {
    const menu = header.querySelector("#menu");
    const close = drawer.querySelector(".ix-close");
    const eventBtn = header.querySelector("#ix-events-toggle");
    const eventPanel = header.querySelector("#ix-events-links");
    let trigger = null;
    // The existing SPA navigation bridge owns these listeners on SPA pages;
    // standalone Career/Gallery use the same chrome with this fallback handler.
    const standalone = () => typeof window.render !== "function";
    const toggleEvents = (open) => { eventPanel.hidden = !open; eventBtn.setAttribute("aria-expanded", String(open)); };
    eventBtn.addEventListener("click", () => { if (standalone()) toggleEvents(eventPanel.hidden); });
    eventBtn.addEventListener("keydown", e => {
      if (!standalone()) return;
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault(); toggleEvents(true);
        const links = eventPanel.querySelectorAll("a");
        links[e.key === "ArrowUp" ? links.length - 1 : 0]?.focus();
      }
      if (e.key === "Escape") { toggleEvents(false); eventBtn.focus(); }
    });
    document.addEventListener("pointerdown", e => {
      if (standalone() && !header.querySelector("#ix-events-item").contains(e.target)) toggleEvents(false);
    });
    const setMobile = (open) => {
      if (open) {
        trigger = document.activeElement;
        drawer.showModal();
        drawer.classList.add("is-open");
        menu.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";
        close.focus();
      } else if (drawer.open) {
        drawer.classList.remove("is-open");
        drawer.close();
        menu.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
        if (trigger?.isConnected) trigger.focus();
      }
    };
    menu.addEventListener("click", () => { if (standalone()) setMobile(true); });
    close.addEventListener("click", () => { if (standalone()) setMobile(false); });
    drawer.addEventListener("cancel", e => { if (standalone()) { e.preventDefault(); setMobile(false); } });
    drawer.addEventListener("click", e => { if (standalone() && e.target === drawer) setMobile(false); });
    header.addEventListener("keydown", e => { if (standalone() && e.key === "Escape") toggleEvents(false); });
  }

  // Shared chrome uses real HTTP paths, bypassing older hash-route interceptors;
  // main-page components and their own interactions are not touched.
  document.addEventListener("click", function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const anchor = event.target.closest("#ix-shared-header a[href], #ix-shared-footer a[href]");
    if (!anchor) return;
    // Preserve normal native browser link behavior (including email links).
    event.stopPropagation();
  }, true);

  document.addEventListener("DOMContentLoaded", function () {
    syncMetadata();
    const page = currentRoute();
    const active = page.startsWith("/events/") ? "/events" : page.startsWith("/gallery/") ? "/gallery" : page;
    document.querySelectorAll("#ix-shared-header [aria-current]").forEach(a => a.removeAttribute("aria-current"));
    document.querySelectorAll("#ix-shared-header a[data-ix-route]").forEach(a => {
      if (a.getAttribute("href") === active) a.setAttribute("aria-current","page");
    });
    const btn = document.querySelector("#ix-events-toggle");
    if (btn) btn.dataset.current = String(active === "/events");
    const summary = document.querySelector("#ix-mobile-events summary");
    if (summary) summary.dataset.current = String(active === "/events");
  });
})();
