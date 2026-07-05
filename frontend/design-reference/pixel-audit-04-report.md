# PIXEL-AUDIT-04 — Measured Composer Calibration Audit

Audit time: 2026-07-05T10:00:14

## Verdict

**Status: PASS FOR CALIBRATED SOURCE-OF-TRUTH / LIVE VISUAL TEST REQUIRED**

PIXEL-04 is now the last composer layout block and contains measured live-vs-reference correction values.

## Evidence

- PIXEL-04 CSS present: `True`
- PIXEL-04 JS present: `True`
- Composer CSS rule count: `21`

## Measured correction

- Live send center was around 0.807 of screenshot height.
- Target send center was around 0.852 of screenshot height.
- Estimated live correction needed: about 58px down.
- Live send center was also too far left, so composer width/right space was increased.

## Last bottom rules

- `10px`
- `1px solid rgba(20,22,30,0.055)`
- `var(--mobile-composer-bottom, 52px)`
- `128px`
- `42px`
- `38px`
- `0`
- `0`
- `var(--pixel04-composer-bottom)`
- `145px`

## Required live test

Open: https://ideasforgeai.com/?v=pixel04

Expected:
- Composer lower than PIXEL-03.
- Composer closer to reference image.
- Submit button remains purple-blue brand gradient.
- Plus icon has no extra circle.
- Mic hides when typing.
- Input expands toward submit button.