# iCONEX header/navigation refresh

Scope: header, navigation interactions and the requested clean navigation paths. Existing app.js, hero slide content, slide-specific styles and carousel timers are unchanged.

## Files
- index.html: semantic header, native mobile dialog, preserved body/footer, base URL.
- header-navigation.css: scoped navy/white/gold system; below-1024px drawer; reduced motion; focus states.
- header-navigation.js: disclosure interactions, native modal focus/scroll handling, clean-path adapter for the existing hash renderer.
- iconex-header-logo.webp: original user-supplied logo, transparent margin trimmed and resized to 480x88; white panel preserves readability without recolouring.
- Seven route directories contain the same index shell for direct navigation and refresh. Run `node iconex-preview/sync-navigation-shells.mjs` after any root index changes, then commit the regenerated shells.

## Content
Upcoming Events and All Events currently provide an honest link to the official event directory, not an invented schedule. Gallery reuses supplied event photographs; Global Presence reuses the existing capability page; Career states that no verified openings are published on this preview. The Contact page remains the existing demonstration form.

## Verification
Chromium offline component tests: widths 320,375,768,1023,1024,1280,1366,1920; no horizontal overflow/header overlap; dropdown pointer and keyboard interactions; drawer focus, Escape and accordion; sticky blur. History/location were simulated for route tests, not verified against the live CDN. Live-browser/cross-browser/accessibility testing remains required. The main site remains noindex staging.

White navigation text is retained over navy for contrast; gold is used for indicators and the CTA, whose dark text has contrast above 4.5:1.
