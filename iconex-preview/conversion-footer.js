/* Footer markup is shared with the homepage renderer. Newsletter submission is handled separately. */
(function () {
  'use strict';

  const destinations = [
    ['Home', '/'], ['About Us', '/about'],
    ['Upcoming Events', '/events/upcoming-events'], ['All Events', '/events/all-events'],
    ['Global Presence', '/global-presence'], ['Gallery', '/gallery'],
    ['Career', '/career'], ['Contact', '/contact']
  ];

  const icons = {
    linkedin: '<path fill="currentColor" d="M4.5 8.4h3.1V20H4.5zM6 3.2A1.85 1.85 0 1 1 6 6.9a1.85 1.85 0 0 1 0-3.7ZM10 8.4h3v1.7h.05c.48-.91 1.52-1.95 3.46-1.95 3.25 0 4 1.98 4 5.04V20h-3.14v-6.07c0-1.55-.03-2.88-1.8-2.88-1.78 0-2.4 1.38-2.4 2.8V20H10Z"/>',
    x: '<path fill="currentColor" d="M17.76 3.5h2.79l-6.1 6.97 7.18 10.03h-5.62l-4.41-6.11-5.35 6.11H3.46L10.32 12 3.43 3.5h5.75l4.16 5.58zm-.98 15.37h1.54L8.35 5.05H6.7z"/>',
    instagram: '<g fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.6" y="3.6" width="16.8" height="16.8" rx="5"/><circle cx="12" cy="12" r="4.1"/></g><circle fill="currentColor" cx="17.6" cy="6.8" r="1.1"/>',
    youtube: '<path fill="currentColor" fill-rule="evenodd" d="M21.08 7.19a2.8 2.8 0 0 0-1.96-1.97C17.37 4.75 12 4.75 12 4.75s-5.37 0-7.12.47a2.8 2.8 0 0 0-1.96 1.97A28.94 28.94 0 0 0 2.45 12c0 1.63.15 3.23.47 4.8a2.8 2.8 0 0 0 1.96 1.98c1.75.47 7.12.47 7.12.47s5.37 0 7.12-.47a2.8 2.8 0 0 0 1.96-1.97c.32-1.58.47-3.18.47-4.81 0-1.63-.15-3.23-.47-4.81ZM10.07 15.08V8.92L15.4 12Z"/>',
    phone: '<path d="m6.4 3 2.1 4.9-2.1 1.9a14.8 14.8 0 0 0 7.8 7.8l1.9-2.1 4.9 2.1v2.3c0 1-1 1.8-2 1.7C10.7 20.8 3.2 13.3 2.4 5c-.1-1 .7-2 1.7-2z"/>',
    mail: '<rect x="2.75" y="5" width="18.5" height="14" rx="2.1"/><path d="m3.5 6 8.5 6.5L20.5 6"/>'
  };

  function icon(name) {
    return '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="' + (name === 'phone' || name === 'mail' ? 'currentColor' : 'none') + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" focusable="false" aria-hidden="true">' + icons[name] + '</svg>';
  }

  function socialLinks() {
    const profiles = {
      linkedin: 'https://www.linkedin.com/company/iconexglobal',
      x: 'https://twitter.com/iconexglobal',
      instagram: 'https://www.instagram.com/iconexglobal/',
      youtube: 'https://www.youtube.com/channel/UCiTcbfKHVgQskgTh2cgfTWQ'
    };
    const labels = {linkedin: 'iCONEX on LinkedIn', x: 'iCONEX on X (Twitter)', instagram: 'iCONEX on Instagram', youtube: 'Global HSE on YouTube'};
    return Object.entries(labels).map(function ([key, name]) {
      if (!profiles[key]) return '';
      let url;
      try { url = new URL(profiles[key]); } catch (_) { return ''; }
      if (url.protocol !== 'https:') return '';
      const href = url.href.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
      return '<a href="' + href + '" aria-label="' + name + '" title="' + name + '" class="ixf-social-link">' + icon(key) + '</a>';
    }).join('');
  }

  function desk(title, number, tel, email) {
    return '<div class="ixf-desk"><h4>' + title + '</h4><address>' +
      '<a href="tel:' + tel + '">' + icon('phone') + '<span>' + number + '</span></a>' +
      '<a href="mailto:' + email + '">' + icon('mail') + '<span>' + email + '</span></a></address></div>';
  }

  const logo = '<img class="ixf-logo" src="./iconex-header-logo-transparent.png" width="480" height="88" loading="lazy" decoding="async" alt=""><span class="ixf-logo-company">Exhibitions Private Limited</span>';

  const motif = '<svg class="ixf-motif" viewBox="0 0 360 360" width="360" height="360" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor"><circle cx="180" cy="180" r="154"/><circle cx="180" cy="180" r="136" stroke-dasharray="1 8"/><path d="M180 26 289 71 334 180 289 289 180 334 71 289 26 180 71 71Z M180 26 334 180 180 334 26 180Z M71 71H289V289H71Z"/><circle cx="180" cy="180" r="109"/><circle cx="180" cy="180" r="54" stroke-dasharray="2 7"/></g></svg>';

  window.iconexConversionFooter = function () {
    const socials = socialLinks();
    return `<footer class="ixf" id="partner-with-iconex" aria-label="Partner with iCONEX and company information">
      <div class="ixf-wrap">
        <section class="ixf-invite" aria-labelledby="ixf-invite-heading">
          <div class="ixf-panel">${motif}
            <div class="ixf-panel-copy">
              <p class="ixf-kicker">ONE PARTNER, EVERY STAGE</p>
              <h2 id="ixf-invite-heading">Ready to Inspire, Innovate, and Implement Your Next Global Platform?</h2>
              <p class="ixf-lead">Partner with one accountable team across Discover, Design, Develop, and Deliver—from initial strategic brief to the exhibition floor.</p>
              <div class="ixf-actions">
                <a class="ixf-primary" href="/contact" data-ix-route>Partner With Us</a>
                <a class="ixf-secondary" href="/career" data-ix-route>Explore Careers <span aria-hidden="true">→</span></a>
              </div>
            </div>
          </div>
        </section>
        <div class="ixf-grid">
          <div class="ixf-brand">
            <a class="ixf-brand-home" href="/" data-ix-route aria-label="iCONEX Exhibitions Private Limited — home">${logo}</a>
            <p class="ixf-mission">Specializing in international conferences, exhibitions, summits, workshops, and training programmes for governments and major industries—accelerating a paradigm shift for a sustainable future across borders.</p>
            <p class="ixf-doctrine">INSPIRE · INNOVATE · IMPLEMENT</p>
            ${socials ? '<nav class="ixf-socials" aria-label="iCONEX social media">' + socials + '</nav>' : ''}
          </div>
          <nav class="ixf-links" aria-labelledby="ixf-links-heading">
            <h3 id="ixf-links-heading">Quick Links</h3>
            <ul>${destinations.map(([name, path]) => '<li><a href="' + path + '" data-ix-route>' + name + '</a></li>').join('')}</ul>
          </nav>
          <section class="ixf-contacts" aria-labelledby="ixf-contact-heading">
            <h3 id="ixf-contact-heading">Global Contact</h3>
            ${desk('For India Operations', '+91 11 4912 2344', '+911149122344', 'connect@iconex.in')}
            ${desk('For Middle East Operations', '+973 1740 2889', '+97317402889', 'info@iconexgulf.com')}
          </section>
          <section class="ixf-news" aria-labelledby="ixf-news-heading">
            <h3 id="ixf-news-heading">Subscribe Our Newsletter</h3>
            <p>Don't miss our feature updates, upcoming global summits, and industry insights.</p>
            <form class="ixf-form" data-ixf-subscribe action="https://iconexglobal.com/subscribe" method="post">
              <input type="hidden" name="subscribe" value="Subscribe">
              <label class="ixf-sr" for="ixf-email">Email address</label>
              <input id="ixf-email" name="email" type="email" autocomplete="email" inputmode="email" autocapitalize="none" spellcheck="false" maxlength="254" required placeholder="Your email address">
              <button type="submit">Subscribe</button>
              <p class="ixf-status" data-ixf-status role="status" aria-live="polite" aria-atomic="true"></p>
            </form>
          </section>
        </div>
        <div class="ixf-base">
          <p>Copyright © 2015 – 2026 iCONEX Exhibitions Private Limited (iCONEX Global). All Rights Reserved.</p>
          <nav aria-label="Legal"><a href="/page/terms-conditions">Terms &amp; Conditions</a><span aria-hidden="true">·</span><a href="/page/privacy-policy">Privacy Policy</a></nav>
        </div>
      </div>
    </footer>`;
  };
})();
