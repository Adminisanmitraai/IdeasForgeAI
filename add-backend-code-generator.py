from pathlib import Path

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path, content):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


write_file("backend/agents/backend_code_generator_agent.py", '''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class BackendCodeGeneratorAgent(BaseAgent):
    name = "backend_code_generator_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        template_data = context.get("template_selection_agent", {})

        project_name = idea_data.get("project_name", "Generated Product")
        template_id = template_data.get("template_id", "startup_landing")
        template_name = template_data.get("template_name", "Startup Landing Page")

        main_py = self._build_main_py(project_name, template_id, template_name)
        requirements = self._requirements()
        env_example = self._env_example(project_name)
        readme = self._readme(project_name, template_name)

        return self.success(
            summary=f"Generated backend starter code for {template_name}.",
            data={
                "files": {
                    "main.py": main_py,
                    "requirements.txt": requirements,
                    ".env.example": env_example,
                    "README.md": readme,
                },
                "run_command": "uvicorn main:app --reload --port 8200",
            },
        )

    def _requirements(self) -> str:
        return """fastapi
uvicorn[standard]
pydantic
python-dotenv
"""

    def _env_example(self, project_name: str) -> str:
        return f"""APP_NAME={project_name}
APP_ENV=development
DATABASE_URL=
JWT_SECRET=
"""

    def _readme(self, project_name: str, template_name: str) -> str:
        return f"""# {project_name} Backend

Generated backend starter for: {template_name}

## Run

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8200
