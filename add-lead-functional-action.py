from pathlib import Path
from textwrap import dedent

ROOT = Path(r"D:\APPS\IdeasForgeAI")


CRM_APP_JS = r'''
const API_BASE =
  (window.GENERATED_APP_CONFIG && window.GENERATED_APP_CONFIG.apiBase) ||
  "http://127.0.0.1:8300";

function showBadge(text, ok) {
  let badge = document.getElementById("apiStatusBadge");
  if (!badge) {
    badge = document.createElement("div");
    badge.id = "apiStatusBadge";
    badge.style.position = "fixed";
    badge.style.right = "18px";
    badge.style.bottom = "18px";
    badge.style.zIndex = "9999";
    badge.style.padding = "10px 14px";
    badge.style.borderRadius = "999px";
    badge.style.fontWeight = "900";
    document.body.appendChild(badge);
  }

  badge.textContent = text;
  badge.style.background = ok ? "#22c55e" : "#ef4444";
  badge.style.color = ok ? "#052e16" : "#450a0a";
}

async function apiGet(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(path + " failed");
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error(path + " failed");
  return res.json();
}

async function loadCRMData() {
  try {
    const statsData = await apiGet("/api/stats");
    const stats = statsData.stats || {};
    const cards = document.querySelectorAll(".stat-card");

    if (cards[0]) {
      cards[0].querySelector("strong").textContent = stats.total_leads;
      cards[0].querySelector("small").textContent = "Live from backend";
    }

    if (cards[1]) {
      cards[1].querySelector("small").textContent = "₹" + stats.pipeline_value + " pipeline";
    }

    if (cards[2]) {
      cards[2].querySelector("strong").textContent = stats.followups_due;
      cards[2].querySelector("small").textContent = "Due from backend";
    }

    if (cards[3]) {
      cards[3].querySelector("strong").textContent = stats.conversion_rate;
      cards[3].querySelector("small").textContent = "Live CRM metric";
    }

    showBadge("Live API connected", true);
  } catch (err) {
    console.error(err);
    showBadge("Backend not connected", false);
  }
}

function createAddLeadModal() {
  if (document.getElementById("addLeadModal")) return;

  const modal = document.createElement("div");
  modal.id = "addLeadModal";
  modal.style.position = "fixed";
  modal.style.inset = "0";
  modal.style.background = "rgba(2, 6, 23, 0.72)";
  modal.style.display = "none";
  modal.style.alignItems = "center";
  modal.style.justifyContent = "center";
  modal.style.zIndex = "9998";

  modal.innerHTML = `
    <form id="addLeadForm" style="
      width: min(460px, 92vw);
      background: #111827;
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 28px;
      padding: 26px;
      color: white;
      box-shadow: 0 28px 90px rgba(0,0,0,0.45);
      font-family: Arial, sans-serif;
    ">
      <h2 style="margin: 0 0 16px; font-size: 28px;">Add New Lead</h2>

      <label>Lead Name</label>
      <input name="name" required placeholder="Example: Riya Sharma" style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <label>Company</label>
      <input name="company" required placeholder="Example: Bright Foods" style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <label>Stage</label>
      <select name="stage" style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;">
        <option value="new">New</option>
        <option value="qualified">Qualified</option>
        <option value="proposal">Proposal</option>
        <option value="won">Won</option>
      </select>

      <label>Deal Value</label>
      <input name="value" type="number" value="50000" style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <label>Next Follow-up</label>
      <input name="next_follow_up" placeholder="Tomorrow 11:00 AM" style="width:100%;margin:8px 0 20px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <div style="display:flex;gap:12px;justify-content:flex-end;">
        <button type="button" id="cancelLeadModal" style="padding:12px 18px;border-radius:999px;border:0;background:#374151;color:white;font-weight:800;">Cancel</button>
        <button type="submit" style="padding:12px 18px;border-radius:999px;border:0;background:white;color:#020617;font-weight:900;">Save Lead</button>
      </div>
    </form>
  `;

  document.body.appendChild(modal);

  document.getElementById("cancelLeadModal").addEventListener("click", () => {
    modal.style.display = "none";
  });

  document.getElementById("addLeadForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const lead = {
      id: Date.now(),
      name: formData.get("name"),
      company: formData.get("company"),
      stage: formData.get("stage") || "new",
      value: Number(formData.get("value") || 0),
      next_follow_up: formData.get("next_follow_up") || null,
    };

    try {
      await apiPost("/api/leads", lead);
      modal.style.display = "none";
      form.reset();
      await loadCRMData();
      showBadge("Lead added successfully", true);
    } catch (err) {
      console.error(err);
      showBadge("Lead save failed", false);
    }
  });
}

function wireAddLeadButton() {
  createAddLeadModal();

  const buttons = Array.from(document.querySelectorAll("button, a"));
  const addLeadButton = buttons.find((button) =>
    button.textContent.trim().toLowerCase() === "add lead"
  );

  if (!addLeadButton || addLeadButton.dataset.boundAddLead === "true") return;

  addLeadButton.dataset.boundAddLead = "true";
  addLeadButton.addEventListener("click", (event) => {
    event.preventDefault();
    document.getElementById("addLeadModal").style.display = "flex";
  });
}

window.addEventListener("load", () => {
  loadCRMData();
  wireAddLeadButton();
});
'''


def write_file(relative_path, content):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


write_file("backend/agents/frontend_api_connector_agent.py", f'''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class FrontendAPIConnectorAgent(BaseAgent):
    name = "frontend_api_connector_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        template_data = context.get("template_selection_agent", {{}})
        template_id = template_data.get("template_id", "startup_landing")

        if template_id == "crm_tool":
            app_js = self._crm_js()
        else:
            app_js = "console.log('IdeasForgeAI connector loaded.');\\n"

        return self.success(
            summary="Generated frontend API connector with Add Lead action.",
            data={{"files": {{"app.js": app_js}}}},
        )

    def _crm_js(self) -> str:
        return r{CRM_APP_JS!r}
''')

runtimecrm3_app_js = ROOT / "generated-apps" / "runtimecrm3" / "frontend" / "app.js"
if runtimecrm3_app_js.exists():
    runtimecrm3_app_js.write_text(CRM_APP_JS.strip() + "\n", encoding="utf-8")
    print("RuntimeCRM3 app.js updated.")

print("Add Lead Functional Action patch applied successfully.")