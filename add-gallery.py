from pathlib import Path

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path: str, content: str):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip(), encoding="utf-8")


write_file("backend/main.py", r'''
import json
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.agents.orchestrator_agent import create_default_builder_pipeline
from backend.api.health import router as health_router
from backend.core.project_paths import GENERATED_APPS_DIR, ensure_project_folders

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

app.mount(
    "/generated-apps",
    StaticFiles(directory=str(GENERATED_APPS_DIR)),
    name="generated-apps",
)


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


@app.get("/api/projects")
def list_projects():
    projects = []

    if not GENERATED_APPS_DIR.exists():
        return {"status": "success", "projects": []}

    for app_dir in sorted(GENERATED_APPS_DIR.iterdir()):
        if not app_dir.is_dir():
            continue

        slug = app_dir.name
        readme_path = app_dir / "README.md"
        plan_path = app_dir / "docs" / "product-plan.json"
        preview_path = app_dir / "frontend" / "index.html"

        project_name = slug
        original_idea = ""

        if plan_path.exists():
            try:
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                project_name = plan.get("project_name", slug)
                original_idea = plan.get("idea", {}).get("raw_idea", "")
            except Exception:
                pass

        projects.append(
            {
                "slug": slug,
                "project_name": project_name,
                "original_idea": original_idea,
                "has_preview": preview_path.exists(),
                "preview_url": f"http://127.0.0.1:8100/generated-apps/{slug}/frontend/index.html",
                "folder_path": str(app_dir),
                "readme_path": str(readme_path),
                "plan_path": str(plan_path),
            }
        )

    return {"status": "success", "projects": projects}
''')


studio_html = (ROOT / "frontend/pages/studio.html").read_text(encoding="utf-8")

studio_html = studio_html.replace(
    '<pre id="rawOutput"></pre>',
    '''
      <div class="gallery-header">
        <h2>Generated Apps</h2>
        <button id="refreshProjectsBtn" class="small-btn">Refresh</button>
      </div>

      <div id="projectsGallery" class="projects-gallery">
        No generated apps loaded yet.
      </div>

      <pre id="rawOutput"></pre>
    '''
)

write_file("frontend/pages/studio.html", studio_html)


studio_css = (ROOT / "frontend/pages/studio.css").read_text(encoding="utf-8")

studio_css += r'''

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 22px;
}

.gallery-header h2 {
  margin: 0;
  font-size: 20px;
}

.small-btn {
  padding: 10px 14px;
  font-size: 13px;
}

.projects-gallery {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.project-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.project-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
}

.project-card p {
  margin: 0 0 12px;
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.45;
}

.project-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.project-actions a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 9px 12px;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
}

.project-actions span {
  color: #93c5fd;
  font-size: 12px;
  align-self: center;
}
'''

write_file("frontend/pages/studio.css", studio_css)


studio_js = (ROOT / "frontend/pages/studio.js").read_text(encoding="utf-8")

studio_js += r'''

const refreshProjectsBtn = document.getElementById("refreshProjectsBtn");
const projectsGallery = document.getElementById("projectsGallery");

async function loadProjects() {
  if (!projectsGallery) return;

  projectsGallery.textContent = "Loading generated apps...";

  try {
    const response = await fetch("http://127.0.0.1:8100/api/projects");

    if (!response.ok) {
      throw new Error(`Project list API error: ${response.status}`);
    }

    const data = await response.json();
    const projects = data.projects || [];

    if (!projects.length) {
      projectsGallery.textContent = "No generated apps yet.";
      return;
    }

    projectsGallery.innerHTML = "";

    projects.forEach((project) => {
      const card = document.createElement("div");
      card.className = "project-card";

      const idea = project.original_idea
        ? project.original_idea.slice(0, 160)
        : "Generated app folder created by IdeasForgeAI.";

      card.innerHTML = `
        <h3>${project.project_name}</h3>
        <p>${idea}${idea.length >= 160 ? "..." : ""}</p>
        <div class="project-actions">
          ${
            project.has_preview
              ? `<a href="${project.preview_url}" target="_blank">Open Preview</a>`
              : `<span>No preview yet</span>`
          }
          <span>${project.folder_path}</span>
        </div>
      `;

      projectsGallery.appendChild(card);
    });
  } catch (error) {
    projectsGallery.textContent = error.message;
  }
}

if (refreshProjectsBtn) {
  refreshProjectsBtn.addEventListener("click", loadProjects);
}

window.addEventListener("load", loadProjects);
'''

write_file("frontend/pages/studio.js", studio_js)

print("Generated Apps Gallery added successfully.")
print("Restart backend, then reopen Studio.")