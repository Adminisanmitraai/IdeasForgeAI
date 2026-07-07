from pathlib import Path
import json
import time
from playwright.sync_api import sync_playwright

URL = "http://localhost:5173/frontend/pages/studio-v4.html"
OUT_DIR = Path("backend/agent_audit_reports/pixel_icon_pseudo_lock")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def stamp():
    return time.strftime("%Y%m%d-%H%M%S")

def main():
    created = stamp()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 853, "height": 1844}, device_scale_factor=1)
        page.goto(URL, wait_until="networkidle", timeout=30000)

        data = page.evaluate("""
        () => {
          function clean(v) {
            return String(v || '').replace(/\\s+/g, ' ').trim().slice(0, 140);
          }

          function box(el) {
            const r = el.getBoundingClientRect();
            return {
              x: Math.round(r.x),
              y: Math.round(r.y),
              width: Math.round(r.width),
              height: Math.round(r.height)
            };
          }

          function styles(el, pseudo = null) {
            const s = getComputedStyle(el, pseudo);
            return {
              content: s.content,
              display: s.display,
              position: s.position,
              width: s.width,
              height: s.height,
              background: s.background,
              backgroundColor: s.backgroundColor,
              color: s.color,
              borderRadius: s.borderRadius,
              boxShadow: s.boxShadow,
              filter: s.filter,
              opacity: s.opacity,
              transform: s.transform,
              fontSize: s.fontSize,
              fontWeight: s.fontWeight,
              lineHeight: s.lineHeight
            };
          }

          return Array.from(document.querySelectorAll('button.if-card')).map((card, index) => {
            const icon = card.querySelector('.if-card-icon');
            const copy = card.querySelector('.if-card-copy');
            const arrow = card.querySelector('.if-card-arrow');

            return {
              index: index + 1,
              cardText: clean(card.innerText || card.textContent),
              icon: icon ? {
                className: icon.className || '',
                text: clean(icon.innerText || icon.textContent),
                html: clean(icon.innerHTML),
                box: box(icon),
                style: styles(icon),
                before: styles(icon, '::before'),
                after: styles(icon, '::after')
              } : null,
              copy: copy ? {
                className: copy.className || '',
                text: clean(copy.innerText || copy.textContent),
                html: clean(copy.innerHTML),
                box: box(copy),
                style: styles(copy)
              } : null,
              arrow: arrow ? {
                className: arrow.className || '',
                text: clean(arrow.innerText || arrow.textContent),
                html: clean(arrow.innerHTML),
                box: box(arrow),
                style: styles(arrow),
                before: styles(arrow, '::before'),
                after: styles(arrow, '::after')
              } : null
            };
          });
        }
        """)

        screenshot = OUT_DIR / f"icon-pseudo-lock-{created}.png"
        page.screenshot(path=str(screenshot), full_page=True)
        browser.close()

    report = OUT_DIR / f"icon-pseudo-lock-{created}.json"
    report.write_text(json.dumps({
        "phase": "PIXEL-MAP-PERFECT-17U",
        "screenshot": str(screenshot),
        "cards": data
    }, indent=2), encoding="utf-8")

    parts = []
    for item in data:
        icon = item.get("icon") or {}
        before = (icon.get("before") or {}).get("content", "")
        after = (icon.get("after") or {}).get("content", "")
        text = icon.get("text", "")
        cls = icon.get("className", "")
        parts.append(f"CARD{item['index']} cls={cls} text={text} before={before} after={after}")

    line = "17U ICON LOCK | " + " | ".join(parts) + f" | REPORT {report}"
    Path("frontend/design-reference/PASTE-17U-ICON-LOCK.txt").write_text(line, encoding="utf-8")
    print(line)

if __name__ == "__main__":
    main()
