from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:5173/frontend/pages/studio-v4.html"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 853, "height": 1844}, device_scale_factor=1)
        page.goto(URL, wait_until="networkidle", timeout=30000)

        data = page.evaluate("""
        () => {
          function text(el){ return (el.innerText || el.textContent || '').trim().replace(/\\s+/g,' '); }
          function box(el){
            const r = el.getBoundingClientRect();
            return `${Math.round(r.x)},${Math.round(r.y)},${Math.round(r.width)}x${Math.round(r.height)}`;
          }
          function name(el){ return `${el.tagName.toLowerCase()}.${el.className || ''}`; }

          const all = Array.from(document.querySelectorAll('body *'));
          const ideas = all.find(el => text(el).includes('IdeasForgeAI'));
          const modes = all.find(el => text(el).includes('Create') && text(el).includes('Code') && text(el).includes('Work'));

          return {
            ideas: ideas ? `${name(ideas)}@${box(ideas)}` : 'missing',
            ideasParent: ideas && ideas.parentElement ? `${name(ideas.parentElement)}@${box(ideas.parentElement)}` : 'missing',
            modes: modes ? `${name(modes)}@${box(modes)}` : 'missing',
            modesParent: modes && modes.parentElement ? `${name(modes.parentElement)}@${box(modes.parentElement)}` : 'missing'
          };
        }
        """)

        browser.close()

    line = f"17N HEADER LOCK | IDEAS {data['ideas']} | IDEAS_PARENT {data['ideasParent']} | MODES {data['modes']} | MODES_PARENT {data['modesParent']}"
    out = Path("frontend/design-reference/PASTE-17N-RESULT.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(line, encoding="utf-8")
    print(line)

if __name__ == "__main__":
    main()
