from __future__ import annotations

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_header_nav_lock"
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
              .slice(0, 160);
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
              alignItems: s.alignItems,
              justifyContent: s.justifyContent,
              gap: s.gap,
              padding: s.padding,
              margin: s.margin,
              width: s.width,
              height: s.height,
              fontSize: s.fontSize,
              fontWeight: s.fontWeight,
              lineHeight: s.lineHeight,
              borderRadius: s.borderRadius
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

          function chainFrom(el, limit = 8) {
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

          const all = Array.from(document.querySelectorAll("body *"));

          const navCandidates = all
            .map(node)
            .filter(item =>
              item.box.y >= 0 &&
              item.box.y < 180 &&
              item.box.width > 30 &&
              item.box.height > 10
            );

          const ideas = all.find(el => cleanText(el).includes("IdeasForgeAI"));
          const modes = all.find(el => cleanText(el).includes("Create") && cleanText(el).includes("Code") && cleanText(el).includes("Work"));

          return {
            viewport: {
              width: window.innerWidth,
              height: window.innerHeight,
              dpr: window.devicePixelRatio
            },
            nav_candidates: navCandidates,
            ideas_chain: ideas ? chainFrom(ideas, 8) : [],
            modes_chain: modes ? chainFrom(modes, 8) : []
          };
        }
        """)

        screenshot_path = OUT_DIR / f"header-nav-lock-{created}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        browser.close()

    report_path = OUT_DIR / f"header-nav-lock-{created}.json"
    report_path.write_text(json.dumps({
        "phase": "PIXEL-MAP-PERFECT-17N",
        "screenshot": str(screenshot_path),
        "data": data
    }, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-17N",
        "report": str(report_path),
        "screenshot": str(screenshot_path),
        "nav_candidates": len(data["nav_candidates"]),
        "ideas_chain_count": len(data["ideas_chain"]),
        "modes_chain_count": len(data["modes_chain"])
    }, indent=2))

if __name__ == "__main__":
    main()
