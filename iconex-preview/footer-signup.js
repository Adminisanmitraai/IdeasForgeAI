/* A successful response represents a receipt from the official iCONEX newsletter. */
(function () {
  'use strict';

  const endpoint = 'https://iconex-newsletter-bridge.onrender.com/subscribe';
  const officialContact = 'https://iconexglobal.com/contact';

  function feedback(form, state, text, offerHelp = false) {
    const status = form.querySelector('[data-ixf-status]');
    status.dataset.state = state;
    status.textContent = text;
    if (!offerHelp) return;
    const link = document.createElement('a');
    link.href = officialContact;
    link.textContent = 'Check with iCONEX.';
    status.append(' ', link);
  }

  document.addEventListener('submit', async function (event) {
    const form = event.target;
    if (!form.matches('form[data-ixf-subscribe]')) return;
    if (typeof window.fetch !== 'function' || typeof AbortController !== 'function') return;
    event.preventDefault();
    if (form.hasAttribute('aria-busy') || !form.reportValidity()) return;

    const email = form.elements.namedItem('email');
    const button = form.querySelector('button[type="submit"]');
    form.setAttribute('aria-busy', 'true');
    button.disabled = true;
    email.readOnly = true;
    feedback(form, 'pending', 'Submitting your subscription…');
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 75_000);
    try {
      const reply = await window.fetch(endpoint, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, credentials: 'omit',
        body: JSON.stringify({email: email.value.trim()}), signal: controller.signal
      });
      const data = await reply.json();
      if (reply.ok && data.status === 'subscribed') {
        form.reset();
        feedback(form, 'success', 'Thank you for subscribing to iCONEX updates.');
      } else if (reply.status === 400 && data.status === 'invalid') {
        feedback(form, 'error', 'Please check your email address and try again.');
      } else if (reply.status === 429 && data.status === 'busy') {
        feedback(form, 'error', 'The signup service is busy. Please try again in a minute.');
      } else {
        feedback(form, 'error', 'We could not confirm your subscription.', true);
      }
    } catch {
      feedback(form, 'error', 'We could not confirm your subscription.', true);
    } finally {
      window.clearTimeout(timeout);
      form.removeAttribute('aria-busy');
      email.readOnly = false;
      button.disabled = false;
    }
  });
})();
