from pathlib import Path
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult
from backend.core.project_paths import GENERATED_APPS_DIR


class IdeasForgeAILandingTemplateAgent(BaseAgent):
    name = "IdeasForgeAILandingTemplateAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        app_slug = context.get("app_slug") or "IdeasForgeAIProduct"
        frontend_dir = GENERATED_APPS_DIR / app_slug / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)

        html_path = frontend_dir / "home.html"
        css_path = frontend_dir / "home.css"
        js_path = frontend_dir / "home.js"

        html_path.write_text(self.home_html(), encoding="utf-8")
        css_path.write_text(self.home_css(), encoding="utf-8")
        js_path.write_text(self.home_js(), encoding="utf-8")

        return self.success(
            summary="Generated premium IdeasForgeAI homepage locally.",
            data={
                "mode": "local_generated_output",
                "html_file": str(html_path),
                "css_file": str(css_path),
                "js_file": str(js_path),
                "preview_url": f"http://127.0.0.1:8100/generated-apps/{app_slug}/frontend/home.html",
                "production_safety": [
                    "No production folders were touched.",
                    "No Git commit was created.",
                    "No GitHub push was attempted.",
                    "No secrets were added to frontend files.",
                ],
            },
        )

    @staticmethod
    def home_html() -> str:
        return """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IdeasForgeAI - Precision Farming</title>
  <link rel="stylesheet" href="./home.css" />
</head>
<body>
  <header class="site-header">
    <a class="brand" href="./home.html" aria-label="IdeasForgeAI home">
      <span class="brand-mark">KM</span>
      <span><strong>IdeasForgeAI</strong><small>AI for farms and markets</small></span>
    </a>
    <button id="menuBtn" class="menu-btn" type="button">Menu</button>
    <nav id="siteNav" class="site-nav" aria-label="Primary navigation">
      <a href="./home.html">Home</a>
      <a href="./farmers.html">Farmers</a>
      <a href="./fpos.html">FPO</a>
      <a href="./buyers.html">Buyer</a>
      <a href="#ai-engine">AI Engine</a>
      <a href="#trust">Trust</a>
      <a href="#contact">Contact</a>
      <select aria-label="Language selector">
        <option>English</option>
        <option>Hindi</option>
        <option>Marathi</option>
      </select>
      <a class="nav-cta" href="./index.html">Talk to AI</a>
      <a class="nav-login" href="./index.html">Login</a>
    </nav>
  </header>

  <main>
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Smart agriculture intelligence</p>
        <h1>Precision Farming. Stronger Market Connection.</h1>
        <p class="hero-text">IdeasForgeAI helps farmers, FPOs and buyers with AI-powered crop guidance, trusted market linkage, local-language support and smart farm intelligence.</p>
        <div class="hero-actions">
          <a class="primary-btn" href="./farmers.html">I'm a Farmer</a>
          <a class="secondary-btn" href="./buyers.html">I'm a Buyer</a>
          <a class="ghost-btn" href="#how-it-works">See How It Works</a>
        </div>
      </div>

      <div class="hero-visual" aria-label="IdeasForgeAI intelligence cards">
        <article class="floating-card crop-card">
          <span>AI Crop Insight</span>
          <strong>Tomato flowering risk reduced</strong>
          <p>Spray window adjusted using local weather and crop stage signals.</p>
        </article>
        <article class="floating-card weather-card">
          <span>Weather Update</span>
          <strong>Moderate rain in 18 hrs</strong>
          <p>Delay pesticide spray and protect open harvest lots.</p>
        </article>
        <article class="floating-card market-card">
          <span>Market Linkage</span>
          <strong>3 verified buyers matched</strong>
          <p>FPO lot ready for mandi and direct buyer negotiation.</p>
        </article>
      </div>
    </section>

    <section id="how-it-works" class="feature-strip">
      <article><span>AI-Powered Insights</span><p>Crop guidance shaped by farm records, stage, and weather risk.</p></article>
      <article id="trust"><span>Trust & Transparency</span><p>Traceable records for farmers, FPOs, buyers, and accounts.</p></article>
      <article><span>Global Market Linkage</span><p>Connect local produce with demand, quantity, price, and buyer status.</p></article>
      <article id="ai-engine"><span>Voice & Language Support</span><p>Built for local-language workflows and field-team adoption.</p></article>
    </section>
  </main>

  <footer id="contact" class="site-footer">
    <span>IdeasForgeAI local preview</span>
    <a href="./index.html">Open live dashboard</a>
  </footer>

  <script src="./home.js"></script>
</body>
</html>
"""

    @staticmethod
    def home_css() -> str:
        return """:root {
  --bg: #06110d;
  --panel: rgba(12, 31, 22, .86);
  --panel-strong: #10291d;
  --text: #f3fff6;
  --muted: #a9c9b5;
  --line: rgba(219, 255, 229, .14);
  --accent: #63e083;
  --accent-2: #40bac6;
  --gold: #f5c86a;
}

* { box-sizing: border-box; }
html, body { margin: 0; max-width: 100%; overflow-x: hidden; }
body {
  min-height: 100vh;
  font-family: Inter, Segoe UI, Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at 78% 14%, rgba(64, 186, 198, .22), transparent 24rem),
    radial-gradient(circle at 8% 16%, rgba(99, 224, 131, .18), transparent 28rem),
    linear-gradient(180deg, #06110d 0%, #030806 100%);
}

.site-header {
  position: fixed;
  inset: 0 0 auto;
  z-index: 10;
  min-height: 76px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 14px clamp(16px, 4vw, 52px);
  background: rgba(4, 12, 8, .78);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(18px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text);
  text-decoration: none;
}
.brand-mark {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  color: #04130a;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  font-weight: 950;
}
.brand strong, .brand small { display: block; }
.brand small { color: var(--muted); font-size: 12px; }

.menu-btn { display: none; }
.site-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.site-nav a, .site-nav select, .menu-btn {
  min-height: 42px;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 10px 11px;
  color: var(--muted);
  background: transparent;
  text-decoration: none;
  font-weight: 800;
}
.site-nav select {
  color: var(--text);
  background: rgba(255,255,255,.07);
  border-color: var(--line);
}
.site-nav a:hover { color: var(--text); background: rgba(255,255,255,.07); }
.site-nav .nav-cta, .primary-btn {
  color: #04130a;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
}
.site-nav .nav-login, .secondary-btn, .ghost-btn {
  border: 1px solid var(--line);
  color: var(--text);
  background: rgba(255,255,255,.07);
}

.hero {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(320px, .95fr);
  align-items: center;
  gap: clamp(24px, 5vw, 72px);
  padding: 128px clamp(16px, 5vw, 72px) 54px;
}
.eyebrow {
  margin: 0 0 14px;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: .08em;
  font-size: 12px;
  font-weight: 950;
}
h1 {
  max-width: 820px;
  margin: 0;
  font-size: clamp(42px, 6.4vw, 86px);
  line-height: .96;
  letter-spacing: 0;
}
.hero-text {
  max-width: 720px;
  margin: 24px 0 0;
  color: var(--muted);
  font-size: clamp(16px, 2vw, 20px);
  line-height: 1.7;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 30px;
}
.primary-btn, .secondary-btn, .ghost-btn {
  min-height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  padding: 13px 16px;
  text-decoration: none;
  font-weight: 950;
}

.hero-visual {
  min-height: 540px;
  position: relative;
  border: 1px solid var(--line);
  border-radius: 12px;
  background:
    linear-gradient(135deg, rgba(99, 224, 131, .12), transparent 42%),
    linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
  overflow: hidden;
}
.hero-visual::before {
  content: "";
  position: absolute;
  inset: 12%;
  border-radius: 50%;
  border: 1px solid rgba(99, 224, 131, .2);
  box-shadow: 0 0 120px rgba(99, 224, 131, .16);
}
.floating-card {
  position: absolute;
  width: min(78%, 360px);
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: rgba(8, 24, 16, .9);
  box-shadow: 0 22px 70px rgba(0, 0, 0, .28);
}
.floating-card span {
  color: var(--accent);
  font-size: 12px;
  text-transform: uppercase;
  font-weight: 950;
}
.floating-card strong { display: block; margin: 8px 0; font-size: 22px; }
.floating-card p { margin: 0; color: var(--muted); line-height: 1.55; }
.crop-card { top: 12%; left: 8%; }
.weather-card { top: 42%; right: 7%; }
.market-card { bottom: 10%; left: 14%; }

.feature-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 0 clamp(16px, 5vw, 72px) 54px;
}
.feature-strip article {
  min-height: 150px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
}
.feature-strip span {
  display: block;
  margin-bottom: 10px;
  color: var(--text);
  font-weight: 950;
}
.feature-strip p {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}
.site-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 20px clamp(16px, 5vw, 72px);
  border-top: 1px solid var(--line);
  color: var(--muted);
}
.site-footer a { color: var(--accent); text-decoration: none; font-weight: 900; }

@media (max-width: 980px) {
  .site-header { align-items: flex-start; flex-wrap: wrap; }
  .menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--text);
    background: rgba(255,255,255,.08);
    border-color: var(--line);
  }
  .site-nav {
    width: 100%;
    display: none;
    align-items: stretch;
    flex-direction: column;
  }
  .site-nav.open { display: flex; }
  .site-nav a, .site-nav select { width: 100%; }
  .hero {
    min-height: auto;
    grid-template-columns: 1fr;
    padding-top: 140px;
  }
  .hero-visual { min-height: 480px; }
  .feature-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 520px) {
  .site-header { padding: 12px; }
  .brand-mark { width: 42px; height: 42px; }
  .hero { padding: 132px 12px 34px; gap: 22px; }
  h1 { font-size: 42px; }
  .hero-actions { display: grid; grid-template-columns: 1fr; }
  .hero-visual {
    min-height: auto;
    display: grid;
    gap: 12px;
    padding: 12px;
  }
  .hero-visual::before { display: none; }
  .floating-card {
    position: static;
    width: 100%;
  }
  .feature-strip {
    grid-template-columns: 1fr;
    padding: 0 12px 34px;
  }
  .site-footer { align-items: flex-start; flex-direction: column; padding: 18px 12px; }
}
"""

    @staticmethod
    def home_js() -> str:
        return """const menuBtn = document.getElementById("menuBtn");
const siteNav = document.getElementById("siteNav");

if (menuBtn && siteNav) {
  menuBtn.addEventListener("click", () => siteNav.classList.toggle("open"));
  siteNav.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => siteNav.classList.remove("open"));
  });
}
"""

