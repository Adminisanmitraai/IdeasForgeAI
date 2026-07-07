from pathlib import Path
import json
import time
from playwright.sync_api import sync_playwright

URL = "http://localhost:5173/frontend/pages/studio-v4.html"
OUT_DIR = Path("backend/agent_audit_reports/pixel_asset_check")
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
          function text(el) {
            return (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 120);
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

          function style(el) {
            const s = getComputedStyle(el);
            return {
              backgroundImage: s.backgroundImage,
              backgroundColor: s.backgroundColor,
              filter: s.filter,
              opacity: s.opacity,
              transform: s.transform,
              boxShadow: s.boxShadow,
              borderRadius: s.borderRadius
            };
          }

          function assetNode(el) {
            const imgs = Array.from(el.querySelectorAll('img')).map(img => ({
              src: img.getAttribute('src') || '',
              currentSrc: img.currentSrc || '',
              alt: img.getAttribute('alt') || '',
              box: box(img)
            }));

            const svgs = Array.from(el.querySelectorAll('svg')).map(svg => ({
              outer: svg.outerHTML.slice(0, 260),
              box: box(svg)
            }));

            return {
              tag: el.tagName.toLowerCase(),
              className: el.className || '',
              text: text(el),
              box: box(el),
              style: style(el),
              imgs,
              svgs
            };
          }

          const cards = Array.from(document.querySelectorAll('button.if-card')).map(card => {
            const icon = card.querySelector('.if-card-icon');
            const copy = card.querySelector('.if-card-copy');
            const arrow = card.querySelector('.if-card-arrow');

            return {
              card: assetNode(card),
              icon: icon ? assetNode(icon) : null,
              copy: copy ? assetNode(copy) : null,
              arrow: arrow ? assetNode(arrow) : null
            };
          });

          const topCandidates = Array.from(document.querySelectorAll('body *'))
            .filter(el => {
              const b = el.getBoundingClientRect();
              return b.y >= 80 && b.y < 150 && b.width > 20 && b.height > 20;
            })
            .map(assetNode);

          return {
            cards,
            topCandidates
          };
        }
        """)

        screenshot = OUT_DIR / f"asset-check-{created}.png"
        page.screenshot(path=str(screenshot), full_page=True)
        browser.close()

    report = OUT_DIR / f"asset-check-{created}.json"
    report.write_text(json.dumps({
        "phase": "PIXEL-MAP-PERFECT-17T",
        "screenshot": str(screenshot),
        "data": data
    }, indent=2), encoding="utf-8")

    first = data["cards"][0]
    second = data["cards"][1]
    third = data["cards"][2]

    def icon_summary(item):
        icon = item["icon"] or {}
        cls = icon.get("className", "")
        bg = icon.get("style", {}).get("backgroundImage", "")
        imgs = icon.get("imgs", [])
        img_src = imgs[0]["src"] if imgs else "no-img"
        return f"{cls} img={img_src} bg={bg[:80]}"

    line = (
        "17T ASSET CHECK | "
        f"CARD1 {icon_summary(first)} | "
        f"CARD2 {icon_summary(second)} | "
        f"CARD3 {icon_summary(third)} | "
        f"REPORT {report}"
    )

    Path("frontend/design-reference/PASTE-17T-ASSET-CHECK.txt").write_text(line, encoding="utf-8")
    print(line)

if __name__ == "__main__":
    main()
