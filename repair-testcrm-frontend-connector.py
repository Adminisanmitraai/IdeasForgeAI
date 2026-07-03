from pathlib import Path

FRONTEND = Path(r"D:\APPS\IdeasForgeAI\generated-apps\testcrm\frontend")
index_path = FRONTEND / "index.html"
app_js_path = FRONTEND / "app.js"

html = index_path.read_text(encoding="utf-8")

if '<script src="./app.js"></script>' not in html:
    html = html.replace("</body>", '  <script src="./app.js"></script>\n</body>')

index_path.write_text(html, encoding="utf-8")

app_js_path.write_text("""
const API_BASE = "http://127.0.0.1:8300";

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
    badge.style.boxShadow = "0 14px 40px rgba(0,0,0,0.35)";
    document.body.appendChild(badge);
  }

  badge.textContent = text;
  badge.style.background = ok ? "#22c55e" : "#ef4444";
  badge.style.color = ok ? "#052e16" : "#450a0a";
}

async function loadCRMData() {
  try {
    const statsResponse = await fetch(API_BASE + "/api/stats");
    const pipelineResponse = await fetch(API_BASE + "/api/pipeline");
    const followupsResponse = await fetch(API_BASE + "/api/followups");

    if (!statsResponse.ok || !pipelineResponse.ok || !followupsResponse.ok) {
      throw new Error("API not reachable");
    }

    const statsData = await statsResponse.json();
    const pipelineData = await pipelineResponse.json();
    const followupsData = await followupsResponse.json();

    const stats = statsData.stats || {};
    const statCards = document.querySelectorAll(".stat-card");

    if (statCards[0]) {
      statCards[0].querySelector("strong").textContent = stats.total_leads;
      statCards[0].querySelector("small").textContent = "Live from backend";
    }

    if (statCards[1]) {
      statCards[1].querySelector("small").textContent = "â‚¹" + stats.pipeline_value + " pipeline";
    }

    if (statCards[2]) {
      statCards[2].querySelector("strong").textContent = stats.followups_due;
      statCards[2].querySelector("small").textContent = "Due from backend";
    }

    if (statCards[3]) {
      statCards[3].querySelector("strong").textContent = stats.conversion_rate;
      statCards[3].querySelector("small").textContent = "Live CRM metric";
    }

    const columns = document.querySelectorAll(".pipeline-column");
    const stages = [
      ["new", "New Leads"],
      ["qualified", "Qualified"],
      ["proposal", "Proposal"],
      ["won", "Won"]
    ];

    stages.forEach(([stage, label], index) => {
      const column = columns[index];
      if (!column) return;

      column.innerHTML = `<h3>${label}</h3>`;

      const leads = pipelineData.pipeline?.[stage] || [];
      leads.forEach((lead) => {
        const card = document.createElement("div");
        card.className = "lead-card";
        card.innerHTML = `
          <strong>${lead.company}</strong>
          <span>${lead.name}</span>
          <small>Value: â‚¹${lead.value}</small>
        `;
        column.appendChild(card);
      });
    });

    const reminderList = document.querySelector(".reminder-card ul");
    if (reminderList) {
      reminderList.innerHTML = "";
      (followupsData.followups || []).forEach((lead) => {
        const item = document.createElement("li");
        item.textContent = `${lead.next_follow_up}: ${lead.name} from ${lead.company}`;
        reminderList.appendChild(item);
      });
    }

    showBadge("Live API connected", true);
  } catch (error) {
    console.error(error);
    showBadge("Backend not connected", false);
  }
}

window.addEventListener("load", loadCRMData);
""", encoding="utf-8")

print("TestCRM frontend connector repaired successfully.")
print(FRONTEND)
