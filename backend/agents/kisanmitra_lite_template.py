import json


PAGES = [
    ("dashboard", "Dashboard", "index.html"),
    ("farmers", "Farmers", "farmers.html"),
    ("fpos", "FPOs", "fpos.html"),
    ("buyers", "Buyers", "buyers.html"),
    ("farms", "Farms", "farms.html"),
    ("crops", "Crops", "crops.html"),
    ("mandi-deals", "Mandi Deals", "mandi-deals.html"),
    ("weather", "Weather", "weather.html"),
    ("accounts", "Accounts", "accounts.html"),
    ("settings", "Settings", "settings.html"),
]


def html_page(project_name: str, page_id: str = "dashboard") -> str:
    title = next((label for pid, label, _ in PAGES if pid == page_id), "Dashboard")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{project_name} - {title}</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body data-page="{page_id}">
  <div class="app-shell">
    <aside class="sidebar">
      <a class="brand" href="./index.html">
        <span class="brand-mark">KM</span>
        <span><strong>{project_name}</strong><small>Agri command center</small></span>
      </a>
      <button class="mobile-menu" id="mobileMenuBtn">Menu</button>
      <nav class="nav-list" id="mainNav"></nav>
      <div class="assistant-card">
        <span>AI Assistant</span>
        <strong>Ready</strong>
        <p>Use recommendations to prioritize farmers, crops, weather risks, and buyer follow-ups.</p>
      </div>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">Live API workspace</p>
          <h1 id="pageTitle">{title}</h1>
        </div>
        <div class="top-actions">
          <button id="refreshDashboardBtn">Refresh Dashboard</button>
          <a class="button ghost" href="./index.html">Home</a>
        </div>
      </header>

      <section id="statusBadge" class="status-badge">Checking backend...</section>
      <section id="pageContent" class="page-content"></section>
    </main>
  </div>
  <script src="./app-config.js"></script>
  <script src="./app.js"></script>
</body>
</html>
"""


def frontend_files(project_name: str) -> dict:
    files = {}
    for page_id, _, filename in PAGES:
        files[filename] = html_page(project_name, page_id)
    files["dashboard.html"] = html_page(project_name, "dashboard")
    return files


def styles_css() -> str:
    return """:root {
  --bg: #07120f;
  --panel: #102019;
  --panel-2: #142a20;
  --line: rgba(222, 247, 229, 0.13);
  --text: #f3fff6;
  --muted: #a8c7b3;
  --accent: #52d273;
  --accent-2: #3bb4c1;
  --warn: #f4c95d;
  --danger: #fb7185;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: Inter, Segoe UI, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
}

button, .button {
  border: 0;
  border-radius: 12px;
  padding: 11px 14px;
  background: var(--accent);
  color: #06240f;
  cursor: pointer;
  font-weight: 800;
  text-decoration: none;
}

button.ghost, .button.ghost {
  background: rgba(255,255,255,.08);
  color: var(--text);
  border: 1px solid var(--line);
}

input, select, textarea {
  width: 100%;
  border: 1px solid var(--line);
  background: #091510;
  color: var(--text);
  border-radius: 12px;
  padding: 12px;
  outline: none;
}

label { display: grid; gap: 7px; color: var(--muted); font-size: 13px; font-weight: 800; }

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 20px;
  border-right: 1px solid var(--line);
  background: #0b1712;
  overflow: auto;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  color: var(--text);
  text-decoration: none;
  margin-bottom: 18px;
}

.brand-mark {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #05220d;
  font-weight: 950;
}

.brand strong, .brand small { display: block; }
.brand small, .eyebrow, .muted { color: var(--muted); }

.mobile-menu { display: none; width: 100%; margin-bottom: 12px; }

.nav-list { display: grid; gap: 8px; }
.nav-list a {
  color: var(--muted);
  text-decoration: none;
  padding: 11px 12px;
  border-radius: 12px;
  border: 1px solid transparent;
}
.nav-list a.active, .nav-list a:hover {
  color: var(--text);
  background: rgba(82, 210, 115, .12);
  border-color: rgba(82, 210, 115, .28);
}

.assistant-card, .card, .table-card, .form-panel {
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 8px;
}

.assistant-card {
  margin-top: 18px;
  padding: 16px;
}

.assistant-card p { color: var(--muted); line-height: 1.5; }
.workspace { min-width: 0; padding: 22px; }

.topbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}

.top-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.eyebrow { margin: 0 0 5px; text-transform: uppercase; letter-spacing: .08em; font-size: 12px; font-weight: 900; }
h1 { margin: 0; font-size: 34px; line-height: 1.1; }
h2, h3 { margin-top: 0; }

.status-badge {
  display: inline-flex;
  margin-bottom: 16px;
  padding: 9px 12px;
  border-radius: 999px;
  background: rgba(244, 201, 93, .15);
  color: #ffe5a3;
  border: 1px solid rgba(244, 201, 93, .28);
  font-weight: 900;
}
.status-badge.ok { background: rgba(82,210,115,.16); color: #b8ffc9; border-color: rgba(82,210,115,.35); }
.status-badge.error { background: rgba(251,113,133,.16); color: #fecdd3; border-color: rgba(251,113,133,.35); }

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.card { padding: 16px; }
.card span { display: block; color: var(--muted); font-size: 13px; }
.card strong { display: block; margin: 8px 0; font-size: 28px; }

.section-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.table-card { padding: 16px; overflow: auto; }
.table-card table { width: 100%; border-collapse: collapse; min-width: 540px; }
th, td { padding: 11px 8px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); font-size: 12px; text-transform: uppercase; }

.toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
.form-panel { padding: 16px; margin-bottom: 14px; display: grid; gap: 12px; }
.form-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.danger { background: var(--danger); color: white; }
.mini-list { display: grid; gap: 10px; }
.mini-row { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--line); }

@media (max-width: 1080px) {
  .app-shell { grid-template-columns: 230px minmax(0, 1fr); }
  .stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .section-grid, .form-grid { grid-template-columns: 1fr; }
}

@media (max-width: 720px) {
  .app-shell { display: block; }
  .sidebar { position: relative; height: auto; }
  .mobile-menu { display: block; }
  .nav-list { display: none; }
  .nav-list.open { display: grid; }
  .workspace { padding: 16px; }
  .topbar { align-items: flex-start; flex-direction: column; }
  .stat-grid { grid-template-columns: 1fr; }
  h1 { font-size: 28px; }
  button, .button { min-height: 44px; }
}
"""


def app_js() -> str:
    return """const API_BASE = (window.GENERATED_APP_CONFIG && window.GENERATED_APP_CONFIG.apiBase) || "http://127.0.0.1:8300";

const pages = [
  ["dashboard", "Dashboard", "index.html"],
  ["farmers", "Farmers", "farmers.html"],
  ["fpos", "FPOs", "fpos.html"],
  ["buyers", "Buyers", "buyers.html"],
  ["farms", "Farms", "farms.html"],
  ["crops", "Crops", "crops.html"],
  ["mandi-deals", "Mandi Deals", "mandi-deals.html"],
  ["weather", "Weather", "weather.html"],
  ["accounts", "Accounts", "accounts.html"],
  ["settings", "Settings", "settings.html"],
];

const resourceConfig = {
  farmers: { title: "Farmers", path: "/api/farmers", fields: ["name", "village", "phone", "crop", "acres"] },
  fpos: { title: "FPOs", path: "/api/fpos", fields: ["name", "district", "members", "focus"] },
  buyers: { title: "Buyers", path: "/api/buyers", fields: ["name", "company", "phone", "interest", "status"] },
  farms: { title: "Farms", path: "/api/farms", fields: ["farmer", "village", "acres", "soil", "water_source"] },
  crops: { title: "Crops", path: "/api/crops", fields: ["crop", "farmer", "stage", "health", "expected_yield"] },
  "mandi-deals": { title: "Mandi Deals", path: "/api/mandi-deals", fields: ["crop", "buyer", "quantity", "price", "stage"] },
};

function $(id) { return document.getElementById(id); }
function pageId() { return document.body.dataset.page || "dashboard"; }
function setStatus(text, state = "") { const el = $("statusBadge"); el.textContent = text; el.className = "status-badge " + state; }

async function api(path, options = {}) {
  const res = await fetch(API_BASE + path, { headers: { "Content-Type": "application/json" }, ...options });
  if (!res.ok) throw new Error(path + " failed");
  return res.json();
}

function wireNav() {
  const nav = $("mainNav");
  nav.innerHTML = pages.map(([id, label, href]) => `<a class="${id === pageId() ? "active" : ""}" href="./${href}">${label}</a>`).join("");
  $("mobileMenuBtn").onclick = () => nav.classList.toggle("open");
  $("refreshDashboardBtn").onclick = loadPage;
}

function statCard(label, value, note) {
  return `<article class="card"><span>${label}</span><strong>${value}</strong><small class="muted">${note}</small></article>`;
}

function table(title, rows, columns) {
  const body = rows.map(row => `<tr>${columns.map(col => `<td>${row[col] ?? ""}</td>`).join("")}</tr>`).join("");
  return `<section class="table-card"><h2>${title}</h2><table><thead><tr>${columns.map(col => `<th>${col.replace("_", " ")}</th>`).join("")}</tr></thead><tbody>${body || `<tr><td colspan="${columns.length}">No records yet.</td></tr>`}</tbody></table></section>`;
}

async function loadDashboard() {
  const [statsData, farmersData, cropsData, dealsData, weatherData, accountsData, buyersData, farmsData] = await Promise.all([
    api("/api/stats"), api("/api/farmers"), api("/api/crops"), api("/api/mandi-deals"),
    api("/api/weather-summary"), api("/api/accounts-summary"), api("/api/buyers"), api("/api/farms")
  ]);
  const stats = statsData.stats || {};
  $("pageContent").innerHTML = `
    <section class="stat-grid">
      ${statCard("Total Farmers", stats.total_farmers, "Registered growers")}
      ${statCard("Total Farms", stats.total_farms, "Mapped farm records")}
      ${statCard("Active Crops", stats.active_crops, "Live crop cycles")}
      ${statCard("Buyer Leads", stats.buyer_leads, "Procurement contacts")}
      ${statCard("Mandi Deals", stats.mandi_deals, "Open and won deals")}
      ${statCard("Weather Alerts", stats.weather_alerts, "Local risk signals")}
      ${statCard("Payments Due", stats.payments_due, "Account follow-up")}
      ${statCard("AI Recommendations", stats.ai_recommendations, "Generated actions")}
    </section>
    <section class="section-grid">
      ${table("Recent Farmers", farmersData.farmers || [], ["name", "village", "crop", "acres"])}
      ${table("Crop Health Summary", cropsData.crops || [], ["crop", "stage", "health", "expected_yield"])}
      ${table("Mandi Deal Pipeline", dealsData["mandi-deals"] || dealsData.mandi_deals || [], ["crop", "buyer", "quantity", "price", "stage"])}
      ${table("Weather Intelligence", weatherData.weather || [], ["district", "condition", "alert", "advice"])}
      ${table("Farm Records", farmsData.farms || [], ["farmer", "village", "acres", "soil"])}
      ${table("Buyer Follow-ups", buyersData.buyers || [], ["name", "company", "interest", "status"])}
    </section>`;
  if (accountsData.accounts) console.log("Accounts summary", accountsData.accounts);
}

function blankRecord(fields) {
  const record = { id: Date.now() };
  fields.forEach(field => record[field] = "");
  return record;
}

async function loadResource(id) {
  const config = resourceConfig[id];
  const data = await api(config.path);
  const records = data[id] || data[id.replace("-", "_")] || [];
  const fields = config.fields;
  const formInputs = fields.map(field => `<label>${field.replace("_", " ")}<input name="${field}" /></label>`).join("");
  $("pageContent").innerHTML = `
    <section class="form-panel">
      <h2>Add ${config.title.slice(0, -1)}</h2>
      <form id="recordForm" class="form-grid">${formInputs}<button type="submit">Save</button></form>
    </section>
    <section class="table-card">
      <div class="toolbar"><button id="reloadBtn">Refresh</button></div>
      <table><thead><tr>${fields.map(f => `<th>${f.replace("_", " ")}</th>`).join("")}<th>Actions</th></tr></thead>
      <tbody>${records.map(record => `<tr data-id="${record.id}">${fields.map(f => `<td>${record[f] ?? ""}</td>`).join("")}<td class="actions"><button data-edit="${record.id}">Edit</button><button class="danger" data-delete="${record.id}">Delete</button></td></tr>`).join("")}</tbody></table>
    </section>`;

  $("reloadBtn").onclick = loadPage;
  $("recordForm").onsubmit = async event => {
    event.preventDefault();
    const payload = blankRecord(fields);
    new FormData(event.target).forEach((value, key) => payload[key] = value);
    await api(config.path, { method: "POST", body: JSON.stringify(payload) });
    setStatus("Data saved successfully", "ok");
    await loadPage();
  };

  document.querySelectorAll("[data-edit]").forEach(button => button.onclick = async () => {
    const record = records.find(item => String(item.id) === String(button.dataset.edit));
    fields.forEach(field => $("recordForm").elements[field].value = record[field] ?? "");
    $("recordForm").onsubmit = async event => {
      event.preventDefault();
      const payload = { id: record.id };
      new FormData(event.target).forEach((value, key) => payload[key] = value);
      await api(config.path + "/" + record.id, { method: "PUT", body: JSON.stringify(payload) });
      setStatus("Data saved successfully", "ok");
      await loadPage();
    };
  });

  document.querySelectorAll("[data-delete]").forEach(button => button.onclick = async () => {
    if (!confirm("Delete this record?")) return;
    await api(config.path + "/" + button.dataset.delete, { method: "DELETE" });
    setStatus("Data saved successfully", "ok");
    await loadPage();
  });
}

async function loadSimplePage(id) {
  const weather = id === "weather" ? await api("/api/weather-summary") : null;
  const accounts = id === "accounts" ? await api("/api/accounts-summary") : null;
  $("pageContent").innerHTML = `
    <section class="section-grid">
      <article class="card"><h2>${pages.find(p => p[0] === id)[1]}</h2><p class="muted">Live workspace for ${id.replace("-", " ")} planning, reports, and operations.</p></article>
      <article class="card"><h2>API Status</h2><p class="muted">${weather || accounts ? "Loaded live backend data." : "This page is ready for the next generated workflow."}</p></article>
    </section>
    ${weather ? table("Weather Records", weather.weather || [], ["district", "condition", "alert", "advice"]) : ""}
    ${accounts ? table("Account Records", accounts.accounts || [], ["name", "type", "amount_due", "due_date"]) : ""}`;
}

async function loadPage() {
  try {
    setStatus("Checking backend...", "");
    const id = pageId();
    if (id === "dashboard") await loadDashboard();
    else if (resourceConfig[id]) await loadResource(id);
    else await loadSimplePage(id);
    setStatus("Live API connected", "ok");
  } catch (err) {
    console.error(err);
    setStatus("Backend not connected", "error");
  }
}

window.addEventListener("load", () => {
  wireNav();
  loadPage();
});
"""


def backend_main_py(project_name: str, template_name: str) -> str:
    return f'''import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="{project_name} Backend", description="Generated by IdeasForgeAI for {template_name}.", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class Record(BaseModel):
    id: int | None = None
    name: str | None = None
    village: str | None = None
    phone: str | None = None
    crop: str | None = None
    acres: str | None = None
    district: str | None = None
    members: str | None = None
    focus: str | None = None
    company: str | None = None
    interest: str | None = None
    status: str | None = None
    farmer: str | None = None
    soil: str | None = None
    water_source: str | None = None
    stage: str | None = None
    health: str | None = None
    expected_yield: str | None = None
    buyer: str | None = None
    quantity: str | None = None
    price: str | None = None
    type: str | None = None
    amount_due: str | None = None
    due_date: str | None = None


DEFAULTS: Dict[str, List[Dict[str, Any]]] = {json.dumps(default_data(), indent=4)}


def file_for(resource: str) -> Path:
    return DATA_DIR / (resource.replace("-", "_") + ".json")


def ensure_data(resource: str) -> List[Dict[str, Any]]:
    path = file_for(resource)
    if not path.exists():
        path.write_text(json.dumps(DEFAULTS.get(resource, []), indent=2), encoding="utf-8")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = DEFAULTS.get(resource, [])
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data


def save_data(resource: str, records: List[Dict[str, Any]]) -> None:
    file_for(resource).write_text(json.dumps(records, indent=2), encoding="utf-8")


def payload(record: Record) -> Dict[str, Any]:
    data = record.model_dump(exclude_none=True) if hasattr(record, "model_dump") else record.dict(exclude_none=True)
    if not data.get("id"):
        data["id"] = 0
    return data


def list_resource(resource: str) -> Dict[str, Any]:
    return {{"status": "success", resource: ensure_data(resource)}}


def create_resource(resource: str, record: Record) -> Dict[str, Any]:
    records = ensure_data(resource)
    data = payload(record)
    ids = [int(item.get("id", 0)) for item in records]
    if not data.get("id") or data["id"] in ids:
        data["id"] = max(ids or [0]) + 1
    records.append(data)
    save_data(resource, records)
    return {{"status": "success", "record": data}}


def update_resource(resource: str, record_id: int, record: Record) -> Dict[str, Any]:
    records = ensure_data(resource)
    data = payload(record)
    data["id"] = record_id
    for index, existing in enumerate(records):
        if int(existing.get("id", 0)) == record_id:
            records[index] = data
            save_data(resource, records)
            return {{"status": "success", "record": data}}
    return {{"status": "error", "message": "Record not found"}}


def delete_resource(resource: str, record_id: int) -> Dict[str, Any]:
    records = ensure_data(resource)
    for index, existing in enumerate(records):
        if int(existing.get("id", 0)) == record_id:
            deleted = records.pop(index)
            save_data(resource, records)
            return {{"status": "success", "deleted": deleted}}
    return {{"status": "error", "message": "Record not found"}}


@app.get("/health")
def health_check():
    return {{"status": "ok", "service": "{project_name} Backend", "persistence": "local_json"}}


@app.get("/api/stats")
def stats():
    farmers = ensure_data("farmers")
    farms = ensure_data("farms")
    crops = ensure_data("crops")
    buyers = ensure_data("buyers")
    deals = ensure_data("mandi-deals")
    weather = ensure_data("weather")
    accounts = ensure_data("accounts")
    return {{"status": "success", "stats": {{
        "total_farmers": len(farmers),
        "total_farms": len(farms),
        "active_crops": len(crops),
        "buyer_leads": len(buyers),
        "mandi_deals": len(deals),
        "weather_alerts": len([item for item in weather if item.get("alert")]),
        "payments_due": len(accounts),
        "ai_recommendations": 8,
    }}}}


@app.get("/api/weather-summary")
def weather_summary():
    return {{"status": "success", "weather": ensure_data("weather")}}


@app.get("/api/accounts-summary")
def accounts_summary():
    return {{"status": "success", "accounts": ensure_data("accounts")}}
'''


def crud_routes() -> str:
    blocks = []
    for resource in ["farmers", "fpos", "buyers", "farms", "crops", "mandi-deals"]:
        fn = resource.replace("-", "_")
        blocks.append(f'''
@app.get("/api/{resource}")
def list_{fn}():
    return list_resource("{resource}")


@app.post("/api/{resource}")
def create_{fn}(record: Record):
    return create_resource("{resource}", record)


@app.put("/api/{resource}/{{record_id}}")
def update_{fn}(record_id: int, record: Record):
    return update_resource("{resource}", record_id, record)


@app.delete("/api/{resource}/{{record_id}}")
def delete_{fn}(record_id: int):
    return delete_resource("{resource}", record_id)
''')
    return "".join(blocks)


def backend_code(project_name: str, template_name: str) -> str:
    return backend_main_py(project_name, template_name) + crud_routes()


def default_data() -> dict:
    return {
        "farmers": [
            {"id": 1, "name": "Ramesh Patil", "village": "Nashik", "phone": "9876543210", "crop": "Tomato", "acres": "4.5"},
            {"id": 2, "name": "Meena Rao", "village": "Mandya", "phone": "9876500011", "crop": "Paddy", "acres": "3.2"},
            {"id": 3, "name": "Gurpreet Singh", "village": "Ludhiana", "phone": "9876500022", "crop": "Wheat", "acres": "6.0"},
        ],
        "fpos": [
            {"id": 1, "name": "Green Valley FPO", "district": "Nashik", "members": "480", "focus": "Vegetables"},
            {"id": 2, "name": "Kaveri Farmers Collective", "district": "Mandya", "members": "320", "focus": "Paddy"},
        ],
        "buyers": [
            {"id": 1, "name": "Anika Foods", "company": "Anika Retail", "phone": "9000011111", "interest": "Tomato", "status": "follow-up"},
            {"id": 2, "name": "FreshKart", "company": "FreshKart Supply", "phone": "9000022222", "interest": "Wheat", "status": "quoted"},
        ],
        "farms": [
            {"id": 1, "farmer": "Ramesh Patil", "village": "Nashik", "acres": "4.5", "soil": "Black", "water_source": "Drip"},
            {"id": 2, "farmer": "Meena Rao", "village": "Mandya", "acres": "3.2", "soil": "Loamy", "water_source": "Canal"},
        ],
        "crops": [
            {"id": 1, "crop": "Tomato", "farmer": "Ramesh Patil", "stage": "Flowering", "health": "Good", "expected_yield": "78 qtl"},
            {"id": 2, "crop": "Paddy", "farmer": "Meena Rao", "stage": "Vegetative", "health": "Watch", "expected_yield": "42 qtl"},
        ],
        "mandi-deals": [
            {"id": 1, "crop": "Tomato", "buyer": "Anika Foods", "quantity": "90 qtl", "price": "Rs 1,650/qtl", "stage": "Negotiation"},
            {"id": 2, "crop": "Wheat", "buyer": "FreshKart", "quantity": "140 qtl", "price": "Rs 2,250/qtl", "stage": "Quoted"},
        ],
        "accounts": [
            {"id": 1, "name": "Ramesh Patil", "type": "Farmer payout", "amount_due": "Rs 42,000", "due_date": "2026-06-28"},
            {"id": 2, "name": "Green Valley FPO", "type": "Service fee", "amount_due": "Rs 18,500", "due_date": "2026-07-02"},
        ],
        "weather": [
            {"id": 1, "district": "Nashik", "condition": "Cloudy", "alert": "Moderate rain", "advice": "Delay pesticide spray"},
            {"id": 2, "district": "Mandya", "condition": "Humid", "alert": "Low", "advice": "Monitor fungal risk"},
        ],
    }


def data_files() -> dict:
    mapping = {
        "farmers": "data/farmers.json",
        "fpos": "data/fpos.json",
        "buyers": "data/buyers.json",
        "farms": "data/farms.json",
        "crops": "data/crops.json",
        "mandi-deals": "data/mandi_deals.json",
        "accounts": "data/accounts.json",
        "weather": "data/weather.json",
    }
    return {path: json.dumps(default_data()[resource], indent=2) + "\n" for resource, path in mapping.items()}


def env_example(project_name: str) -> str:
    return f"""APP_NAME={project_name}
APP_ENV=development
DATABASE_URL=
JWT_SECRET=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
"""


def supabase_schema() -> str:
    tables = ["farmers", "fpos", "buyers", "farms", "crops", "mandi_deals", "accounts", "weather_records", "users", "roles"]
    return "\n\n".join(
        f"""create table if not exists public.{table} (
  id bigint generated by default as identity primary key,
  payload jsonb not null default '{{}}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);"""
        for table in tables
    ) + "\n"


def supabase_plan() -> str:
    return """# Supabase Plan

IdeasForgeAIProduct currently uses local JSON persistence. Supabase is planned as the next storage layer without exposing service-role keys to the frontend.

Planned tables:
- farmers
- fpos
- buyers
- farms
- crops
- mandi_deals
- accounts
- weather_records
- users
- roles

Environment variables:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY

Frontend rule:
- The frontend may use only SUPABASE_URL and SUPABASE_ANON_KEY when public client access is added.
- SUPABASE_SERVICE_ROLE_KEY must stay server-side only.
"""

