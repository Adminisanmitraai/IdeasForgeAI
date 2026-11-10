# Section 6 — Featured Platforms & Events Showcase

Implemented 10 November 2026. Scoped to the homepage, after #methodology.

## Integration
- Load featured-platforms.css after methodology.css.
- Load featured-platforms.js after methodology.js and before header-navigation.js.
- Keep the root and seven static navigation HTML shells synchronised.
- Existing header, hero, philosophy, metrics, methodology and routes are not modified.
- The module replaces #ix-featured-events-slot and reserves the non-rendering #ix-global-presence-slot for future Section 7. It does not create an unapproved Global Presence section.

## Content provenance and publication limits
- GEMS: https://www.globalems.in/ and https://www.globalems.in/about-conference checked 10 November 2026. Official date: 20–21 November 2026. Venue: Vivanta Hyderabad, Begumpet. Sixth edition. 500+ leaders and 50+ exhibitors are advertised expectations, not completed attendance totals.
- Registration button: https://www.globalems.in/registration?sub=Delegate-Registration. This opens the official registration-enquiry page; no local registration, payment or form integration is claimed.
- GEMS card artwork is typographic HTML/SVG, not another event's photograph. Status changes based on India-local event dates and removes the registration CTA after 21 November 2026. Editorial revalidation is still required if organisers change the schedule.
- DGH image: embedded visual from Iconex_High_Resolution_Master.pptx slide 8. The supplied deck calls DGH delivered, while other project context describes concepts. Completion status and the newly supplied 19.5m × 11m footprint have not been independently reconciled. The card and case-study preview explicitly flag scope/delivery confirmation; they do not claim endorsement, measured outcomes or completion dates.
- Hindalco image: supplied master presentation slide 13, explicitly marked proposed pavilion concept. The card and case-study preview preserve that status.
- IMR: reuse the previously supplied pavilion concept image at assets/imr-slide3-background.avif. It remains a design proposal, not built-project evidence.
- Client permissions, final project scopes and image publication rights remain company approval items for production-domain use.
- No workshop record was supplied. That category uses a useful empty state rather than fabricated listings.

## Interactions
Four category filters use native buttons, aria-pressed and a polite result-count status. Arrow keys/Home/End navigate filter focus; Enter/Space activate the focused filter. Incoming matching cards use a brief fade/scale animation; reduced motion disables it.

Three case-study buttons open a native dialog with project metadata, evidence notes, Escape/backdrop/close controls, focus containment/restoration and body-scroll cleanup on route changes. No dead links or fictional case-study URLs are used.

The archive button uses the existing /events/all-events route. Its existing preview-directory content has not been changed into a complete archive by this section.

## Testing
541 offline Chromium component assertions passed across 320, 375, 540, 767, 768, 900, 1023, 1024, 1280, 1366 and 1920 pixels. Checks cover content/order, filters, empty state, responsive columns, equal card heights, clipped text, local media, official link targets, modal focus/Escape/cleanup, repeat rendering, reduced motion, hover and date-aware status.

These are offline component tests using local media and the declared Arial fallback, not full-site/cross-browser/live-server verification. Earlier-section rendered HTML was compared in the test fixture. External fonts and live-site delivery require a separate browser check.

## Deployment safety
New files/assets and HTML imports only. Publish to the existing preview branch; the official iconexglobal.com site is outside this change. Revert the section commit to roll back. No secrets, databases, analytics, mail delivery or tracking added.
