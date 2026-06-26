from pathlib import Path
from textwrap import dedent

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path, content):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


# Ensure dependencies
req_path = ROOT / "backend" / "requirements.txt"
existing = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
needed = ["fastapi", "uvicorn[standard]", "pydantic", "python-dotenv", "openai"]
lines = [line.strip() for line in existing.splitlines() if line.strip()]
for item in needed:
    if item not in lines:
        lines.append(item)
req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


write_file("backend/core/ai_provider.py", r'''
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class OpenAIProvider:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        if not self.is_configured():
            return {
                "status": "not_configured",
                "message": "OPENAI_API_KEY is missing. Add it to D:\\APPS\\IdeasForgeAI\\.env",
            }

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role.upper()}: {content}\n\n"

            response = client.responses.create(
                model=self.model,
                input=prompt,
            )

            return {
                "status": "success",
                "model": self.model,
                "message": response.output_text,
            }

        except Exception as exc:
            return {
                "status": "error",
                "model": self.model,
                "message": str(exc),
            }
''')


write_file("backend/main.py", r'''
import json
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.agents.orchestrator_agent import create_default_builder_pipeline
from backend.api.health import router as health_router
from backend.core.ai_provider import OpenAIProvider
from backend.core.project_paths import GENERATED_APPS_DIR, PROJECT_ROOT, ensure_project_folders

ensure_project_folders()

app = FastAPI(
    title="IdeasForgeAI",
    description="AI Product Factory backend.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)

if GENERATED_APPS_DIR.exists():
    app.mount(
        "/generated-apps",
        StaticFiles(directory=str(GENERATED_APPS_DIR)),
        name="generated-apps",
    )

frontend_dir = PROJECT_ROOT / "frontend"
if frontend_dir.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(frontend_dir)),
        name="frontend",
    )


class GenerateRequest(BaseModel):
    idea: str
    app_name: Optional[str] = None
    preferred_style: Optional[str] = None
    target_platforms: List[str] = Field(default_factory=lambda: ["web"])


class AIChatRequest(BaseModel):
    message: str
    app_name: Optional[str] = None
    idea: Optional[str] = None


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


@app.post("/api/ai/assistant")
def ai_assistant(request: AIChatRequest):
    provider = OpenAIProvider()

    system_prompt = """
You are IdeasForgeAI Studio Assistant.

You help the user build apps step by step.
Be practical and product-focused.
When the user asks for an app, break it into:
1. pages
2. dashboards
3. backend APIs
4. database tables or JSON files
5. user actions
6. next build step

Do not expose secrets.
Do not ask for the OpenAI API key in chat.
For KisanMitraLite, focus on farmers, FPOs, buyers, farms, crops, mandi deals, weather, accounts, and dashboards.
"""

    user_context = f"""
Current app name: {request.app_name or ""}
Current idea: {request.idea or ""}
User message: {request.message}
"""

    return provider.chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context},
        ]
    )


@app.get("/api/projects")
def list_projects():
    projects = []

    if not GENERATED_APPS_DIR.exists():
        return {"status": "success", "projects": []}

    for app_dir in sorted(GENERATED_APPS_DIR.iterdir()):
        if not app_dir.is_dir():
            continue

        slug = app_dir.name
        plan_path = app_dir / "docs" / "product-plan.json"
        preview_path = app_dir / "frontend" / "index.html"

        project_name = slug
        original_idea = ""
        template_name = ""

        if plan_path.exists():
            try:
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                project_name = plan.get("project_name", slug)
                original_idea = plan.get("idea", {}).get("raw_idea", "")
                template_name = plan.get("template", {}).get("template_name", "")
            except Exception:
                pass

        projects.append(
            {
                "slug": slug,
                "project_name": project_name,
                "template_name": template_name,
                "original_idea": original_idea,
                "has_preview": preview_path.exists(),
                "preview_url": f"http://127.0.0.1:8100/generated-apps/{slug}/frontend/index.html",
                "folder_path": str(app_dir),
            }
        )

    return {"status": "success", "projects": projects}
''')


write_file("frontend/pages/studio-v2.html", r'''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IdeasForgeAI Studio V2</title>
  <link rel="stylesheet" href="./studio-v2.css" />
</head>
<body>
  <main class="studio">
    <aside class="assistant-panel">
      <div class="brand">
        <div class="mark">IF</div>
        <div>
          <p>AI Product Factory</p>
          <h1>IdeasForgeAI</h1>
        </div>
      </div>

      <div class="app-inputs">
        <label>
          App Name
          <input id="appName" value="KisanMitraLite" />
        </label>

        <label>
          Idea
          <textarea id="ideaText">Create an agriculture management platform with farmer dashboard, FPO dashboard, buyer dashboard, farm records, crop records, mandi deals, weather insights and account records.</textarea>
        </label>

        <div class="button-row">
          <button id="generateBtn">Generate App</button>
          <button id="kisanBtn" class="secondary">KisanMitraLite</button>
        </div>
      </div>

      <section class="chat-box">
        <div id="chatMessages" class="chat-messages"></div>

        <div class="chat-input">
          <input id="chatInput" placeholder="Ask the builder assistant..." />
          <button id="sendChatBtn">Send</button>
        </div>
      </section>
    </aside>

    <section class="workspace">
      <header class="workspace-top">
        <div>
          <p class="eyebrow">Live Builder Workspace</p>
          <h2 id="workspaceTitle">KisanMitraLite Development</h2>
        </div>

        <div class="top-actions">
          <button id="refreshProjectsBtn">Refresh Apps</button>
          <button id="openPreviewBtn">Open Preview</button>
        </div>
      </header>

      <section class="status-grid">
        <article>
          <span>Backend</span>
          <strong id="backendStatus">Waiting</strong>
        </article>
        <article>
          <span>Generated App</span>
          <strong id="generatedStatus">Waiting</strong>
        </article>
        <article>
          <span>AI Assistant</span>
          <strong id="aiStatus">Checking</strong>
        </article>
      </section>

      <section class="preview-shell">
        <iframe id="previewFrame" title="Generated App Preview"></iframe>
      </section>

      <section class="build-output">
        <div class="output-card">
          <h3>Agent Steps</h3>
          <div id="agentRows" class="agent-rows">No generation yet.</div>
        </div>

        <div class="output-card">
          <h3>Generated Apps</h3>
          <div id="projectsGallery" class="projects-gallery">Loading...</div>
        </div>
      </section>
    </section>
  </main>

  <script src="./studio-v2.js"></script>
</body>
</html>
''')


write_file("frontend/pages/studio-v2.css", r'''
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #050816;
  color: white;
}

.studio {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 420px 1fr;
}

.assistant-panel {
  height: 100vh;
  overflow: auto;
  padding: 22px;
  border-right: 1px solid rgba(255,255,255,.1);
  background:
    radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 28%),
    rgba(255,255,255,.045);
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 22px;
}

.mark {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: 18px;
  background: linear-gradient(135deg, #38bdf8, #8b5cf6);
  font-weight: 900;
}

.brand p,
.eyebrow {
  margin: 0;
  color: #93c5fd;
  text-transform: uppercase;
  letter-spacing: .12em;
  font-size: 12px;
  font-weight: 900;
}

.brand h1,
.workspace h2 {
  margin: 4px 0 0;
}

.app-inputs,
.chat-box,
.output-card,
.status-grid article,
.preview-shell {
  border: 1px solid rgba(255,255,255,.1);
  background: rgba(255,255,255,.07);
  border-radius: 24px;
}

.app-inputs {
  padding: 18px;
}

label {
  display: grid;
  gap: 8px;
  margin-bottom: 14px;
  color: #dbeafe;
  font-weight: 800;
}

input,
textarea {
  width: 100%;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(2,6,23,.72);
  color: white;
  border-radius: 16px;
  padding: 13px 14px;
  outline: none;
}

textarea {
  min-height: 150px;
  resize: vertical;
  line-height: 1.45;
}

button {
  border: 0;
  border-radius: 999px;
  padding: 12px 16px;
  font-weight: 900;
  cursor: pointer;
  background: white;
  color: #020617;
}

button.secondary {
  background: rgba(255,255,255,.12);
  color: white;
}

.button-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.chat-box {
  margin-top: 16px;
  padding: 14px;
}

.chat-messages {
  height: 310px;
  overflow: auto;
  display: grid;
  gap: 10px;
  align-content: start;
  padding-right: 6px;
}

.message {
  padding: 12px 14px;
  border-radius: 18px;
  line-height: 1.45;
  color: #dbeafe;
  background: rgba(15,23,42,.92);
}

.message.user {
  background: rgba(56,189,248,.16);
  color: white;
}

.message.ai {
  background: rgba(139,92,246,.16);
}

.chat-input {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  margin-top: 12px;
}

.workspace {
  height: 100vh;
  overflow: auto;
  padding: 24px;
}

.workspace-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.top-actions {
  display: flex;
  gap: 10px;
}

.status-grid {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.status-grid article {
  padding: 18px;
}

.status-grid span {
  color: #cbd5e1;
  display: block;
  margin-bottom: 8px;
}

.status-grid strong {
  font-size: 22px;
}

.preview-shell {
  margin-top: 18px;
  height: 52vh;
  overflow: hidden;
}

iframe {
  width: 100%;
  height: 100%;
  border: 0;
  background: white;
}

.build-output {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.output-card {
  padding: 18px;
}

.agent-rows {
  display: grid;
  gap: 8px;
}

.agent-row,
.project-card {
  padding: 12px;
  border-radius: 16px;
  background: rgba(2,6,23,.6);
  border: 1px solid rgba(255,255,255,.08);
}

.agent-row strong,
.project-card strong {
  display: block;
}

.agent-row small,
.project-card small {
  color: #cbd5e1;
}

.projects-gallery {
  display: grid;
  gap: 10px;
}

.project-card button {
  margin-top: 10px;
}

@media (max-width: 980px) {
  .studio {
    grid-template-columns: 1fr;
  }

  .assistant-panel,
  .workspace {
    height: auto;
  }

  .build-output,
  .status-grid {
    grid-template-columns: 1fr;
  }
}
''')


write_file("frontend/pages/studio-v2.js", r'''
const API_BASE = "http://127.0.0.1:8100";

const appNameInput = document.getElementById("appName");
const ideaText = document.getElementById("ideaText");
const generateBtn = document.getElementById("generateBtn");
const kisanBtn = document.getElementById("kisanBtn");
const chatInput = document.getElementById("chatInput");
const sendChatBtn = document.getElementById("sendChatBtn");
const chatMessages = document.getElementById("chatMessages");
const agentRows = document.getElementById("agentRows");
const projectsGallery = document.getElementById("projectsGallery");
const previewFrame = document.getElementById("previewFrame");
const openPreviewBtn = document.getElementById("openPreviewBtn");
const refreshProjectsBtn = document.getElementById("refreshProjectsBtn");
const backendStatus = document.getElementById("backendStatus");
const generatedStatus = document.getElementById("generatedStatus");
const aiStatus = document.getElementById("aiStatus");

let currentPreviewUrl = "";

function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "generated-product";
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = "message " + role;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function checkBackend() {
  try {
    const res = await fetch(API_BASE + "/health");
    if (!res.ok) throw new Error("offline");
    backendStatus.textContent = "Online";
  } catch {
    backendStatus.textContent = "Offline";
  }
}

async function askAI(message) {
  addMessage("user", message);
  aiStatus.textContent = "Thinking...";

  try {
    const res = await fetch(API_BASE + "/api/ai/assistant", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        message,
        app_name: appNameInput.value.trim(),
        idea: ideaText.value.trim(),
      }),
    });

    const data = await res.json();
    aiStatus.textContent = data.status === "success" ? "Connected" : data.status;
    addMessage("ai", data.message || "No response.");
  } catch (err) {
    aiStatus.textContent = "Error";
    addMessage("ai", "AI assistant is not reachable. Check backend and OPENAI_API_KEY.");
  }
}

async function generateApp() {
  const app_name = appNameInput.value.trim();
  const idea = ideaText.value.trim();

  generatedStatus.textContent = "Generating...";
  agentRows.textContent = "Running builder agents...";

  try {
    const res = await fetch(API_BASE + "/api/generate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        app_name,
        idea,
        target_platforms: ["web", "mobile"],
      }),
    });

    const data = await res.json();
    generatedStatus.textContent = data.status || "Done";

    agentRows.innerHTML = "";
    (data.results || []).forEach((item) => {
      const row = document.createElement("div");
      row.className = "agent-row";
      row.innerHTML = `<strong>${item.agent_name}</strong><small>${item.status} — ${item.summary}</small>`;
      agentRows.appendChild(row);
    });

    const slug = slugify(data.project_name || app_name);
    currentPreviewUrl = `${API_BASE}/generated-apps/${slug}/frontend/index.html?v=${Date.now()}`;
    previewFrame.src = currentPreviewUrl;

    addMessage("ai", `${data.project_name || app_name} generated. I opened the preview on the right side.`);
    await loadProjects();
  } catch (err) {
    generatedStatus.textContent = "Error";
    agentRows.textContent = err.message;
  }
}

async function loadProjects() {
  try {
    const res = await fetch(API_BASE + "/api/projects");
    const data = await res.json();
    const projects = data.projects || [];

    projectsGallery.innerHTML = "";

    if (!projects.length) {
      projectsGallery.textContent = "No generated apps yet.";
      return;
    }

    projects.reverse().slice(0, 8).forEach((project) => {
      const card = document.createElement("div");
      card.className = "project-card";
      card.innerHTML = `
        <strong>${project.project_name}</strong>
        <small>${project.template_name || "Generated App"}</small>
        <button data-url="${project.preview_url}?v=${Date.now()}">Open Preview</button>
      `;

      card.querySelector("button").onclick = () => {
        currentPreviewUrl = card.querySelector("button").dataset.url;
        previewFrame.src = currentPreviewUrl;
      };

      projectsGallery.appendChild(card);
    });
  } catch (err) {
    projectsGallery.textContent = "Unable to load generated apps.";
  }
}

generateBtn.onclick = generateApp;

kisanBtn.onclick = () => {
  appNameInput.value = "KisanMitraLite";
  ideaText.value = "Create an agriculture management platform with farmer dashboard, FPO dashboard, buyer dashboard, farm records, crop records, mandi deals, weather insights and account records.";
  generateApp();
};

sendChatBtn.onclick = () => {
  const text = chatInput.value.trim();
  if (!text) return;
  chatInput.value = "";
  askAI(text);
};

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendChatBtn.click();
  }
});

openPreviewBtn.onclick = () => {
  if (currentPreviewUrl) window.open(currentPreviewUrl, "_blank");
};

refreshProjectsBtn.onclick = loadProjects;

window.addEventListener("load", async () => {
  addMessage("ai", "Welcome. I am your IdeasForgeAI builder assistant. Generate KisanMitraLite and I will show development steps here.");
  await checkBackend();
  await loadProjects();
  askAI("Check if OpenAI is configured and suggest the first KisanMitraLite build steps.");
});
''')


print("OpenAI provider and Studio V2 added successfully.")
print("Open: http://127.0.0.1:8100/frontend/pages/studio-v2.html")