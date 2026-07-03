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

async function apiPut(path, body) {
  const res = await fetch(API_BASE + path, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(path + " failed");
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(API_BASE + path, { method: "DELETE" });
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
      cards[1].querySelector("small").textContent = "â‚¹" + stats.pipeline_value + " pipeline";
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

function createLeadFormModal() {
  if (document.getElementById("leadFormModal")) return;

  const modal = document.createElement("div");
  modal.id = "leadFormModal";
  modal.style.position = "fixed";
  modal.style.inset = "0";
  modal.style.background = "rgba(2, 6, 23, 0.72)";
  modal.style.display = "none";
  modal.style.alignItems = "center";
  modal.style.justifyContent = "center";
  modal.style.zIndex = "9998";

  modal.innerHTML = `
    <form id="leadForm" style="width:min(460px,92vw);background:#111827;border:1px solid rgba(255,255,255,.14);border-radius:28px;padding:26px;color:white;box-shadow:0 28px 90px rgba(0,0,0,.45);font-family:Arial,sans-serif;">
      <h2 id="leadFormTitle" style="margin:0 0 16px;font-size:28px;">Add Lead</h2>
      <input type="hidden" name="id" />

      <label>Lead Name</label>
      <input name="name" required style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <label>Company</label>
      <input name="company" required style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <label>Stage</label>
      <select name="stage" style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;">
        <option value="new">New</option>
        <option value="qualified">Qualified</option>
        <option value="proposal">Proposal</option>
        <option value="won">Won</option>
      </select>

      <label>Deal Value</label>
      <input name="value" type="number" value="75000" style="width:100%;margin:8px 0 14px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <label>Next Follow-up</label>
      <input name="next_follow_up" placeholder="Tomorrow 10 AM" style="width:100%;margin:8px 0 20px;padding:14px;border-radius:14px;border:1px solid #334155;background:#020617;color:white;" />

      <div style="display:flex;gap:12px;justify-content:flex-end;">
        <button type="button" id="cancelLeadForm" style="padding:12px 18px;border-radius:999px;border:0;background:#374151;color:white;font-weight:800;">Cancel</button>
        <button type="submit" style="padding:12px 18px;border-radius:999px;border:0;background:white;color:#020617;font-weight:900;">Save Lead</button>
      </div>
    </form>
  `;

  document.body.appendChild(modal);

  document.getElementById("cancelLeadForm").onclick = () => {
    modal.style.display = "none";
  };

  document.getElementById("leadForm").onsubmit = async (event) => {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const existingId = formData.get("id");

    const lead = {
      id: existingId ? Number(existingId) : Date.now(),
      name: formData.get("name"),
      company: formData.get("company"),
      stage: formData.get("stage") || "new",
      value: Number(formData.get("value") || 0),
      next_follow_up: formData.get("next_follow_up") || null,
    };

    try {
      if (existingId) {
        await apiPut("/api/leads/" + existingId, lead);
        showBadge("Lead updated successfully", true);
      } else {
        await apiPost("/api/leads", lead);
        showBadge("Lead added successfully", true);
      }

      modal.style.display = "none";
      form.reset();
      await loadCRMData();
      await renderLeadManager();
    } catch (err) {
      console.error(err);
      showBadge("Lead save failed", false);
    }
  };
}

function openLeadForm(lead = null) {
  createLeadFormModal();

  const modal = document.getElementById("leadFormModal");
  const form = document.getElementById("leadForm");
  const title = document.getElementById("leadFormTitle");

  form.reset();

  if (lead) {
    title.textContent = "Edit Lead";
    form.elements.id.value = lead.id;
    form.elements.name.value = lead.name || "";
    form.elements.company.value = lead.company || "";
    form.elements.stage.value = lead.stage || "new";
    form.elements.value.value = lead.value || 0;
    form.elements.next_follow_up.value = lead.next_follow_up || "";
  } else {
    title.textContent = "Add Lead";
    form.elements.id.value = "";
    form.elements.stage.value = "new";
    form.elements.value.value = 75000;
  }

  modal.style.display = "flex";
}

function createLeadManagerModal() {
  if (document.getElementById("leadManagerModal")) return;

  const modal = document.createElement("div");
  modal.id = "leadManagerModal";
  modal.style.position = "fixed";
  modal.style.inset = "0";
  modal.style.background = "rgba(2, 6, 23, 0.72)";
  modal.style.display = "none";
  modal.style.alignItems = "center";
  modal.style.justifyContent = "center";
  modal.style.zIndex = "9997";

  modal.innerHTML = `
    <section style="width:min(980px,94vw);max-height:86vh;overflow:auto;background:#111827;border:1px solid rgba(255,255,255,.14);border-radius:28px;padding:26px;color:white;box-shadow:0 28px 90px rgba(0,0,0,.45);font-family:Arial,sans-serif;">
      <div style="display:flex;justify-content:space-between;gap:14px;align-items:center;margin-bottom:18px;">
        <div>
          <h2 style="margin:0;font-size:30px;">Manage Leads</h2>
          <p style="margin:6px 0 0;color:#cbd5e1;">Edit, delete, or move leads between stages.</p>
        </div>
        <div style="display:flex;gap:10px;">
          <button id="managerAddLead" style="padding:12px 18px;border-radius:999px;border:0;background:white;color:#020617;font-weight:900;">Add Lead</button>
          <button id="closeLeadManager" style="padding:12px 18px;border-radius:999px;border:0;background:#374151;color:white;font-weight:800;">Close</button>
        </div>
      </div>
      <div id="leadManagerList"></div>
    </section>
  `;

  document.body.appendChild(modal);

  document.getElementById("closeLeadManager").onclick = () => {
    modal.style.display = "none";
  };

  document.getElementById("managerAddLead").onclick = () => {
    openLeadForm();
  };
}

async function renderLeadManager() {
  const list = document.getElementById("leadManagerList");
  if (!list) return;

  try {
    const data = await apiGet("/api/leads");
    const leads = data.leads || [];

    if (!leads.length) {
      list.innerHTML = `<p style="color:#cbd5e1;">No leads yet.</p>`;
      return;
    }

    list.innerHTML = leads.map((lead) => `
      <div class="lead-row" data-lead-id="${lead.id}" style="display:grid;grid-template-columns:1.2fr 1.2fr .8fr .8fr 1fr auto;gap:12px;align-items:center;padding:14px;border:1px solid rgba(255,255,255,.12);border-radius:18px;margin-bottom:10px;background:#020617;">
        <strong>${lead.name || ""}</strong>
        <span>${lead.company || ""}</span>
        <span style="text-transform:capitalize;color:#93c5fd;">${lead.stage || "new"}</span>
        <span>â‚¹${lead.value || 0}</span>
        <small>${lead.next_follow_up || "No follow-up"}</small>
        <span style="display:flex;gap:8px;">
          <button data-action="edit" style="padding:9px 12px;border-radius:999px;border:0;background:white;color:#020617;font-weight:900;">Edit</button>
          <button data-action="delete" style="padding:9px 12px;border-radius:999px;border:0;background:#ef4444;color:white;font-weight:900;">Delete</button>
        </span>
      </div>
    `).join("");

    list.querySelectorAll("button[data-action='edit']").forEach((button) => {
      button.onclick = () => {
        const row = button.closest(".lead-row");
        const id = Number(row.dataset.leadId);
        const lead = leads.find((item) => item.id === id);
        openLeadForm(lead);
      };
    });

    list.querySelectorAll("button[data-action='delete']").forEach((button) => {
      button.onclick = async () => {
        const row = button.closest(".lead-row");
        const id = Number(row.dataset.leadId);
        const lead = leads.find((item) => item.id === id);

        if (!confirm("Delete lead: " + (lead?.name || id) + "?")) return;

        await apiDelete("/api/leads/" + id);
        await loadCRMData();
        await renderLeadManager();
        showBadge("Lead deleted successfully", true);
      };
    });
  } catch (err) {
    console.error(err);
    list.innerHTML = `<p style="color:#fecaca;">Unable to load leads.</p>`;
  }
}

function openLeadManager() {
  createLeadManagerModal();
  document.getElementById("leadManagerModal").style.display = "flex";
  renderLeadManager();
}

function wireButtons() {
  createLeadFormModal();
  createLeadManagerModal();

  const buttons = Array.from(document.querySelectorAll("button, a"));

  const addLeadButton = buttons.find((button) =>
    button.textContent.trim().toLowerCase() === "add lead"
  );

  if (addLeadButton && addLeadButton.dataset.boundAddLead !== "true") {
    addLeadButton.dataset.boundAddLead = "true";
    addLeadButton.onclick = (event) => {
      event.preventDefault();
      openLeadForm();
    };
  }

  const importButton = buttons.find((button) =>
    button.textContent.trim().toLowerCase() === "import leads"
  );

  if (importButton && importButton.dataset.boundLeadManager !== "true") {
    importButton.dataset.boundLeadManager = "true";
    importButton.textContent = "Manage Leads";
    importButton.onclick = (event) => {
      event.preventDefault();
      openLeadManager();
    };
  }
}

window.addEventListener("load", () => {
  loadCRMData();
  wireButtons();
});
'''

def write_file(relative_path, content):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


write_file("backend/agents/lead_crud_agent.py", """
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class LeadCRUDAgent(BaseAgent):
    name = "lead_crud_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        template_data = context.get("template_selection_agent", {})
        template_id = template_data.get("template_id", "startup_landing")

        if template_id == "crm_tool":
            return self.success(
                summary="Generated edit, delete, and stage movement plan for CRM leads.",
                data={
                    "features": [
                        "edit_lead",
                        "delete_lead",
                        "move_stage",
                        "refresh_dashboard",
                        "persist_to_json",
                    ]
                },
            )

        return self.success(
            summary="No CRM lead CRUD actions needed for this template.",
            data={"features": []},
        )
""")

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
            summary="Generated frontend API connector with add, edit, delete lead actions.",
            data={{"files": {{"app.js": app_js}}}},
        )

    def _crm_js(self) -> str:
        return {CRM_APP_JS!r}
''')

# Patch orchestrator so future apps show lead_crud_agent.
orchestrator_path = ROOT / "backend" / "agents" / "orchestrator_agent.py"
if orchestrator_path.exists():
    s = orchestrator_path.read_text(encoding="utf-8")

    if "lead_crud_agent" not in s:
        s = s.replace(
            "from backend.agents.html_builder_agent import HTMLBuilderAgent",
            "from backend.agents.html_builder_agent import HTMLBuilderAgent\nfrom backend.agents.lead_crud_agent import LeadCRUDAgent",
        )

    if "LeadCRUDAgent()," not in s:
        s = s.replace(
            "DatabasePersistenceAgent(),",
            "DatabasePersistenceAgent(),\n            LeadCRUDAgent(),",
        )

    orchestrator_path.write_text(s, encoding="utf-8")

# Patch future generated backend code with PUT/DELETE endpoints.
generator_path = ROOT / "backend" / "agents" / "backend_code_generator_agent.py"
if generator_path.exists():
    s = generator_path.read_text(encoding="utf-8")

    if "/api/leads/{lead_id}" not in s:
        needle = '            "@app.get(\\\'/api/pipeline\\\')",'
        if needle not in s:
            needle = '            "@app.get(\'/api/pipeline\')",'

        insert = '''            "@app.put('/api/leads/{lead_id}')",
            "def update_lead(lead_id: int, updated_lead: Lead):",
            "    for index, existing in enumerate(leads):",
            "        if existing.id == lead_id:",
            "            updated_lead.id = lead_id",
            "            leads[index] = updated_lead",
            "            save_leads(leads)",
            "            return {'status': 'success', 'lead': updated_lead}",
            "    return {'status': 'error', 'message': 'Lead not found'}",
            "",
            "@app.delete('/api/leads/{lead_id}')",
            "def delete_lead(lead_id: int):",
            "    for index, existing in enumerate(leads):",
            "        if existing.id == lead_id:",
            "            deleted = leads.pop(index)",
            "            save_leads(leads)",
            "            return {'status': 'success', 'deleted': deleted}",
            "    return {'status': 'error', 'message': 'Lead not found'}",
            "",
'''
        s = s.replace(needle, insert + needle)
        generator_path.write_text(s, encoding="utf-8")

# Patch current PersistCRM1 backend.
persist_main = ROOT / "generated-apps" / "persistcrm1" / "backend" / "main.py"
if persist_main.exists():
    s = persist_main.read_text(encoding="utf-8")

    if "@app.put('/api/leads/{lead_id}')" not in s:
        endpoint_code = '''
@app.put('/api/leads/{lead_id}')
def update_lead(lead_id: int, updated_lead: Lead):
    for index, existing in enumerate(leads):
        if existing.id == lead_id:
            updated_lead.id = lead_id
            leads[index] = updated_lead
            save_leads(leads)
            return {'status': 'success', 'lead': updated_lead}
    return {'status': 'error', 'message': 'Lead not found'}


@app.delete('/api/leads/{lead_id}')
def delete_lead(lead_id: int):
    for index, existing in enumerate(leads):
        if existing.id == lead_id:
            deleted = leads.pop(index)
            save_leads(leads)
            return {'status': 'success', 'deleted': deleted}
    return {'status': 'error', 'message': 'Lead not found'}


'''
        s = s.replace("@app.get('/api/pipeline')", endpoint_code + "@app.get('/api/pipeline')")
        persist_main.write_text(s, encoding="utf-8")
        print("PersistCRM1 backend CRUD endpoints added.")

# Patch current PersistCRM1 frontend.
persist_frontend = ROOT / "generated-apps" / "persistcrm1" / "frontend"
if persist_frontend.exists():
    (persist_frontend / "app.js").write_text(CRM_APP_JS.strip() + "\n", encoding="utf-8")

    index_path = persist_frontend / "index.html"
    html = index_path.read_text(encoding="utf-8")

    if "app-config.js" not in html:
        html = html.replace("</body>", '  <script src="./app-config.js"></script>\n  <script src="./app.js"></script>\n</body>')
    elif "app.js" not in html:
        html = html.replace("</body>", '  <script src="./app.js"></script>\n</body>')

    index_path.write_text(html, encoding="utf-8")
    print("PersistCRM1 frontend CRUD actions added.")

print("Edit/Delete Lead Agent patch applied successfully.")
