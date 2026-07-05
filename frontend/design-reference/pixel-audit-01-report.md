# PIXEL-AUDIT-01 — Chat Screen Pixel Mapping Audit

Audit time: 2026-07-05T09:44:54

## Verdict

**Status: FAIL / PARTIAL**

The Pixel Mapping Agent is not behaving as a true pixel mapping agent yet. It is applying CSS overrides, but it is not measuring and enforcing the reference screenshot layout precisely.

## Evidence

- CSS file exists: `True`
- JS file exists: `True`
- Pixel map JSON exists: `True`
- Composer CSS rule count: `26`

## Patch markers found

- AI-02B: CSS=`True`, JS=`True`
- AI-02C: CSS=`False`, JS=`False`
- AI-02D: CSS=`False`, JS=`False`
- AI-02E: CSS=`False`, JS=`False`
- PIXEL-01: CSS=`False`, JS=`False`
- PIXEL-01B: CSS=`False`, JS=`False`

## Composer bottom rules found

1. `var(--mobile-composer-bottom, 52px)`
2. `128px`
3. `42px`
4. `38px`
5. `24px`
6. `22px`
7. `max(0px, calc(24px - 25px))`
8. `max(0px, calc(22px - 25px))`
9. `0`
10. `0`
11. `var(--pixel02-composer-bottom)`
12. `165px`

## Composer transform rules found

1. `uppercase`
2. `translateY(1px)`
3. `uppercase`
4. `scale(0.985)`
5. `none`
6. `translateX(min(var(--ifai-drawer-width), var(--ifai-drawer-max)))`
7. `translateX(0)`
8. `translateX(-101%)`
9. `translateX(0)`
10. `translateX(75vw)`
11. `none`

## Pixel map file

```json
{
  "phase": "PIXEL-02",
  "name": "Single Source Composer Layout Lock",
  "updated_at": "2026-07-05T09:44:26",
  "status": "composer visual source of truth consolidated",
  "reference_rule": "screenshot is reference only; not used as background",
  "composer": {
    "bottom_mobile": "calc(env(safe-area-inset-bottom, 0px) + 34px)",
    "bottom_small": "calc(env(safe-area-inset-bottom, 0px) + 30px)",
    "height": "68px",
    "input_height": "48px",
    "send_button_size": "46px",
    "mic_button_size": "34px",
    "plus_width": "40px",
    "submit_color": "linear-gradient(135deg, #6f55ff, #2f7bff)",
    "typing_behavior": "body.ifai-pixel02-typing hides mic and expands input"
  },
  "removed_conflicts": [
    "AI-02C composer visual/runtime block",
    "AI-02D composer visual/runtime block",
    "AI-02E composer visual/runtime block",
    "PIXEL-01 composer visual/runtime block",
    "PIXEL-01B transform runtime block"
  ]
}
```

## Root cause

1. The current Pixel Mapping Agent created a static JSON and CSS block, but it did not detect actual pixel positions from the reference image.
2. The composer has many older CSS overrides from AI-02B / AI-02C / AI-02D / AI-02E / PIXEL-01 / PIXEL-01B.
3. Because many rules use `!important`, the last-loaded or runtime-applied rule wins.
4. The submit color changed, so the CSS is loading, but the final y-position is still controlled by another composer rule or runtime layout.
5. This means the live layout is not being locked from a single measured source of truth.

## Required correction

Create PIXEL-02 as a real measured layout lock:

- Remove competing composer overrides or neutralize them.
- Keep one final composer block only.
- Store measured values as CSS variables.
- Apply final position using one source of truth.
- Use JS only for typing behavior, not visual position.
- Freeze the chat screen after matching reference.

## Recommendation

Do not continue adding small composer patches. First consolidate the composer CSS into one final PIXEL-02 block.