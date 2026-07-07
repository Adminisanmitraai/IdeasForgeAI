from __future__ import annotations

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_card_structure"
URL = "http://localhost:5173/frontend/pages/studio-v4.html"

def stamp():
    return time.strftime("%Y%m%d-%H%M%S")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    created = stamp()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 853, "height": 1844},
            device_scale_factor=1,
        )

        page.goto(URL, wait_until="networkidle", timeout=30000)

        data = page.evaluate("""
        () => {
          function box(el) {
            const r = el.getBoundingClientRect();
            return {
              x: Math.round(r.x),
              y: Math.round(r.y),
              width: Math.round(r.width),
              height: Math.round(r.height),
              right: Math.round(r.right),
              bottom: Math.round(r.bottom)
            };
          }

          function style(el) {
            const s = getComputedStyle(el);
            return {
              display: s.display,
              position: s.position,
              flexDirection: s.flexDirection,
              gridTemplateColumns: s.gridTemplateColumns,
              alignItems: s.alignItems,
              justifyContent: s.justifyContent,
              gap: s.gap,
              padding: s.padding,
              margin: s.margin,
              fontSize: s.fontSize,
              fontWeight: s.fontWeight,
              lineHeight: s.lineHeight,
              letterSpacing: s.letterSpacing,
              borderRadius: s.borderRadius,
              background: s.background,
              boxShadow: s.boxShadow
            };
          }

          function node(el, depth = 0) {
            return {
              tag: el.tagName.toLowerCase(),
              className: el.className || "",
              text: (el.innerText || el.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 160),
              box: box(el),
              style: style(el),
              children: depth < 3 ? Array.from(el.children).map(child => node(child, depth + 1)) : []
            };
          }

          return Array.from(document.querySelectorAll("button.if-card")).map(card => node(card));
        }
        """)

        screenshot_path = OUT_DIR / f"card-structure-{created}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        browser.close()

    report_path = OUT_DIR / f"card-structure-{created}.json"
    report_path.write_text(json.dumps({
        "phase": "PIXEL-MAP-PERFECT-17G",
        "cards_found": len(data),
        "screenshot": str(screenshot_path),
        "cards": data
    }, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-17G",
        "cards_found": len(data),
        "report": str(report_path),
        "screenshot": str(screenshot_path)
    }, indent=2))

if __name__ == "__main__":
    main()
