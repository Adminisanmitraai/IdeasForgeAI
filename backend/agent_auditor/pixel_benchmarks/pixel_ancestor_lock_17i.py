from __future__ import annotations

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_ancestor_lock"
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
          function cleanText(el) {
            return (el.innerText || el.textContent || "")
              .trim()
              .replace(/\\s+/g, " ")
              .slice(0, 140);
          }

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
              rowGap: s.rowGap,
              columnGap: s.columnGap,
              padding: s.padding,
              margin: s.margin,
              width: s.width,
              height: s.height,
              minHeight: s.minHeight,
              fontSize: s.fontSize,
              lineHeight: s.lineHeight,
              borderRadius: s.borderRadius,
              overflow: s.overflow
            };
          }

          function node(el) {
            return {
              tag: el.tagName.toLowerCase(),
              id: el.id || "",
              className: el.className || "",
              text: cleanText(el),
              box: box(el),
              style: style(el)
            };
          }

          function chainFrom(el, limit = 10) {
            const chain = [];
            let current = el;
            let i = 0;

            while (current && current !== document.documentElement && i < limit) {
              chain.push(node(current));
              current = current.parentElement;
              i++;
            }

            return chain;
          }

          const firstCard = document.querySelector("button.if-card");
          const hero = document.querySelector("section.if-hero");
          const heroTitle = document.querySelector("section.if-hero h1");
          const cards = Array.from(document.querySelectorAll("button.if-card")).map(node);

          return {
            viewport: {
              width: window.innerWidth,
              height: window.innerHeight,
              dpr: window.devicePixelRatio
            },
            hero_chain: hero ? chainFrom(hero, 10) : [],
            hero_title_chain: heroTitle ? chainFrom(heroTitle, 10) : [],
            card_chain: firstCard ? chainFrom(firstCard, 10) : [],
            cards: cards
          };
        }
        """)

        screenshot_path = OUT_DIR / f"ancestor-lock-{created}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        browser.close()

    report_path = OUT_DIR / f"ancestor-lock-{created}.json"
    report_path.write_text(json.dumps({
        "phase": "PIXEL-MAP-PERFECT-17I",
        "screenshot": str(screenshot_path),
        "data": data
    }, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-17I",
        "report": str(report_path),
        "screenshot": str(screenshot_path),
        "hero_chain_count": len(data["hero_chain"]),
        "card_chain_count": len(data["card_chain"]),
        "cards_found": len(data["cards"])
    }, indent=2))

if __name__ == "__main__":
    main()
