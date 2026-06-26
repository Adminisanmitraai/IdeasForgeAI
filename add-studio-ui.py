from pathlib import Path

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path: str, content: str):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


write_file("backend/main.py", r'''
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agents.orchestrator_agent import create_default_builder_pipeline
from backend.api.health import router as health_router
from backend.core.project_paths import ensure_project_folders

ensure_project_folders()

app = FastAPI(
    title="IdeasForgeAI",
    description="AI Product Factory backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


class GenerateRequest(BaseModel):
    idea: str
    app_name: Optional[str] = None
    preferred_style: Optional[str] = None
    target_platforms: List[str] = Field(default_factory=lambda: ["web"])


@app.post("/api/generate")
def generate_product(request: GenerateRequest):
    pipeline = create_default_builder_pipeline()

    result = pipeline.run(
        {
            "idea": request.idea,
            "app_name": request.app_name,
            "preferred_style": request.preferred_style,
            "target_platforms": request.target_platforms,
        }
    )

    return result.model_dump()
'''.strip())


write_file("frontend/pages/studio.html", r'''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IdeasForgeAI Studio</title>
  <link rel="stylesheet" href="./studio.css" />
</head>
<body>
  <main class="studio-shell">
    <section class="hero-panel">
      <div class="brand-row">
        <div class="brand-mark">IF</div>
        <div>
          <p class="eyebrow">AI Product Factory</p>
          <h1>IdeasForgeAI Studio</h1>
        </div>
      </div>

      <p class="hero-text">
        Write a simple product idea. IdeasForgeAI will convert it into a structured builder plan and export a starter app folder.
      </p>

      <div class="form-grid">
        <label>
          App Name
          <input id="appName" value="IdeasForgeAI" placeholder="Example: ShopPilotAI" />
        </label>

        <label>
          Product Idea
          <textarea id="ideaText" placeholder="Write your idea here...">Create an app where anyone can write a simple idea and instantly generate a web tool, backend, database and mobile app package.</textarea>
        </label>

        <button id="generateBtn">Generate App</button>
      </div>
    </section>

    <section class="result-panel">
      <div class="result-header">
        <h2>Generation Result</h2>
        <span id="statusBadge">Waiting</span>
      </div>

      <div id="summaryBox" class="summary-box">
        No generation started yet.
      </div>

      <div class="agent-table-wrap">
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Status</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody id="agentRows"></tbody>
        </table>
      </div>

      <pre id="rawOutput"></pre>
    </section>
  </main>

  <script src="./studio.js"></script>
</body>
</html>
'''.strip())


write_file("frontend/pages/studio.css", r'''
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, sans-serif;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.2), transparent 34%),
    radial-gradient(circle at bottom right, rgba(168, 85, 247, 0.18), transparent 30%),
    #070b18;
  color: #ffffff;
}

.studio-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: 22px;
  padding: 28px;
}

.hero-panel,
.result-panel {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.07);
  border-radius: 28px;
  box-shadow: 0 28px 90px rgba(0, 0, 0, 0.35);
}

.hero-panel {
  padding: 34px;
}

.result-panel {
  padding: 26px;
  overflow: hidden;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-mark {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #38bdf8, #8b5cf6);
  font-weight: 900;
  color: white;
}

.eyebrow {
  margin: 0;
  color: #aeb9d4;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

h1 {
  margin: 4px 0 0;
  font-size: clamp(34px, 5vw, 58px);
  line-height: 1;
}

.hero-text {
  margin: 28px 0;
  max-width: 720px;
  color: #d8def0;
  font-size: 17px;
  line-height: 1.55;
}

.form-grid {
  display: grid;
  gap: 18px;
}

label {
  display: grid;
  gap: 8px;
  color: #cbd5e1;
  font-weight: 700;
}

input,
textarea {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.16);
  outline: none;
  border-radius: 18px;
  padding: 15px 16px;
  background: rgba(3, 7, 18, 0.65);
  color: #ffffff;
  font-size: 15px;
}

textarea {
  min-height: 190px;
  resize: vertical;
  line-height: 1.5;
}

button {
  width: fit-content;
  border: 0;
  border-radius: 999px;
  padding: 15px 24px;
  font-weight: 900;
  color: #07111f;
  background: #ffffff;
  cursor: pointer;
  box-shadow: 0 16px 34px rgba(255, 255, 255, 0.12);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.result-header h2 {
  margin: 0;
}

#statusBadge {
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(148, 163, 184, 0.2);
  color: #dbeafe;
  font-size: 13px;
  font-weight: 800;
}

.summary-box {
  margin: 22px 0;
  padding: 18px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.75);
  color: #dbeafe;
  line-height: 1.5;
}

.agent-table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  text-align: left;
  padding: 13px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  vertical-align: top;
}

th {
  color: #93c5fd;
  font-size: 13px;
}

td {
  color: #e2e8f0;
  font-size: 14px;
}

pre {
  max-height: 280px;
  overflow: auto;
  margin: 22px 0 0;
  padding: 16px;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.45);
  color: #bbf7d0;
  font-size: 12px;
  white-space: pre-wrap;
}

@media (max-width: 960px) {
  .studio-shell {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .hero-panel,
  .result-panel {
    border-radius: 22px;
    padding: 22px;
  }
}
'''.strip())


write_file("frontend/pages/studio.js", r'''
const generateBtn = document.getElementById("generateBtn");
const appNameInput = document.getElementById("appName");
const ideaText = document.getElementById("ideaText");
const statusBadge = document.getElementById("statusBadge");
const summaryBox = document.getElementById("summaryBox");
const agentRows = document.getElementById("agentRows");
const rawOutput = document.getElementById("rawOutput");

const API_URL = "http://127.0.0.1:8100/api/generate";

function setStatus(text, mode = "neutral") {
  statusBadge.textContent = text;

  if (mode === "success") {
    statusBadge.style.background = "rgba(34, 197, 94, 0.18)";
    statusBadge.style.color = "#bbf7d0";
  } else if (mode === "error") {
    statusBadge.style.background = "rgba(239, 68, 68, 0.18)";
    statusBadge.style.color = "#fecaca";
  } else {
    statusBadge.style.background = "rgba(148, 163, 184, 0.2)";
    statusBadge.style.color = "#dbeafe";
  }
}

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || "generated-product";
}

function renderAgents(results) {
  agentRows.innerHTML = "";

  results.forEach((item) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${item.agent_name || ""}</td>
      <td>${item.status || ""}</td>
      <td>${item.summary || ""}</td>
    `;

    agentRows.appendChild(row);
  });
}

generateBtn.addEventListener("click", async () => {
  const idea = ideaText.value.trim();
  const app_name = appNameInput.value.trim();

  if (!idea) {
    setStatus("Missing idea", "error");
    summaryBox.textContent = "Please write a product idea first.";
    return;
  }

  generateBtn.disabled = true;
  generateBtn.textContent = "Generating...";
  setStatus("Generating", "neutral");
  summaryBox.textContent = "IdeasForgeAI agents are building the product plan...";
  agentRows.innerHTML = "";
  rawOutput.textContent = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        idea,
        app_name,
        target_platforms: ["web", "mobile"],
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    const folderName = slugify(data.project_name || app_name || "generated-product");

    setStatus(data.status || "Done", data.status === "success" ? "success" : "error");

    summaryBox.innerHTML = `
      <strong>Project:</strong> ${data.project_name || "Untitled"}<br/>
      <strong>Status:</strong> ${data.status || "unknown"}<br/>
      <strong>Export:</strong> D:\\APPS\\IdeasForgeAI\\generated-apps\\${folderName}
    `;

    renderAgents(data.results || []);
    rawOutput.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    setStatus("Error", "error");
    summaryBox.textContent = error.message;
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "Generate App";
  }
});
'''.strip())


print("IdeasForgeAI Studio UI added successfully.")
print(r"Open: D:\APPS\IdeasForgeAI\frontend\pages\studio.html")