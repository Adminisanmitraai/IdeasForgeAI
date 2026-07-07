from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_computed_styles"
URL = "http://localhost:5173/frontend/pages/studio-v4.html"


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    created = stamp()

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            browser_name = "chromium"
        except Exception:
            browser = p.chromium.launch(channel="msedge", headless=True)
            browser_name = "msedge"

        page = browser.new_page(
            viewport={"width": 853, "height": 1844},
            device_scale_factor=1,
        )

        page.goto(URL, wait_until="networkidle", timeout=30000)

        data = page.evaluate(
            """
            () => {
              function cleanText(el) {
                return (el.innerText || el.textContent || "")
                  .trim()
                  .replace(/\\s+/g, " ")
                  .slice(0, 180);
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

              function styles(el) {
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
                  fontFamily: s.fontFamily,
                  fontSize: s.fontSize,
                  fontWeight: s.fontWeight,
                  lineHeight: s.lineHeight,
                  letterSpacing: s.letterSpacing,
                  color: s.color,
                  background: s.background,
                  backgroundColor: s.backgroundColor,
                  borderRadius: s.borderRadius,
                  boxShadow: s.boxShadow,
                  overflow: s.overflow
                };
              }

              function summarize(el) {
                return {
                  tag: el.tagName.toLowerCase(),
                  id: el.id || "",
                  className: el.className || "",
                  text: cleanText(el),
                  box: box(el),
                  styles: styles(el)
                };
              }

              function findByText(term) {
                const all = Array.from(document.querySelectorAll("body *"));
                return all
                  .filter(el => cleanText(el).includes(term))
                  .slice(0, 12)
                  .map(summarize);
              }

              function ancestorChainForText(term) {
                const all = Array.from(document.querySelectorAll("body *"));
                const el = all.find(node => cleanText(node).includes(term));
                if (!el) return [];

                const chain = [];
                let current = el;
                let depth = 0;

                while (current && current !== document.body && depth < 8) {
                  chain.push(summarize(current));
                  current = current.parentElement;
                  depth++;
                }

                return chain;
              }

              function likelyCards() {
                const all = Array.from(document.querySelectorAll("body *"));
                return all
                  .map(el => summarize(el))
                  .filter(item => {
                    const b = item.box;
                    const br = parseFloat(item.styles.borderRadius || "0");
                    const bg = item.styles.backgroundColor || "";
                    const text = item.text || "";
                    return (
                      b.width > 220 &&
                      b.height > 55 &&
                      br >= 16 &&
                      bg !== "rgba(0, 0, 0, 0)" &&
                      (
                        text.includes("ForgeStudio") ||
                        text.includes("ForgeCode") ||
                        text.includes("ForgeWork") ||
                        text.includes("Create apps") ||
                        text.includes("Analyze projects") ||
                        text.includes("AI workspace")
                      )
                    );
                  });
              }

              function likelyHero() {
                return Array.from(document.querySelectorAll("h1, h2, p, div, section"))
                  .map(el => summarize(el))
                  .filter(item =>
                    item.text.includes("What do you want") ||
                    item.text.includes("Choose a mode")
                  )
                  .slice(0, 20);
              }

              return {
                url: location.href,
                viewport: {
                  width: window.innerWidth,
                  height: window.innerHeight,
                  devicePixelRatio: window.devicePixelRatio
                },
                body: summarize(document.body),
                terms: {
                  IdeasForgeAI: findByText("IdeasForgeAI"),
                  hero_title: findByText("What do you want"),
                  hero_subtitle: findByText("Choose a mode"),
                  ForgeStudio: findByText("ForgeStudio"),
                  ForgeCode: findByText("ForgeCode"),
                  ForgeWork: findByText("ForgeWork"),
                  Ask: findByText("Ask")
                },
                ancestor_chains: {
                  ForgeStudio: ancestorChainForText("ForgeStudio"),
                  ForgeCode: ancestorChainForText("ForgeCode"),
                  ForgeWork: ancestorChainForText("ForgeWork"),
                  hero_title: ancestorChainForText("What do you want")
                },
                likely_cards: likelyCards(),
                likely_hero: likelyHero()
              };
            }
            """
        )

        screenshot_path = OUT_DIR / f"computed-style-screenshot-{created}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)

        browser.close()

    report = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-17D",
        "created_at": created,
        "browser": browser_name,
        "url": URL,
        "screenshot": str(screenshot_path),
        "frontend_write_status": "no_frontend_files_modified",
        "data": data,
        "next_step": "Use exact DOM selectors/classes from this report for the next card/hero repair pass."
    }

    report_path = OUT_DIR / f"computed-style-report-{created}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "phase": report["phase"],
        "report": str(report_path),
        "screenshot": str(screenshot_path),
        "viewport": data["viewport"],
        "likely_cards_count": len(data["likely_cards"]),
        "likely_hero_count": len(data["likely_hero"]),
        "next_step": report["next_step"]
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
