from pathlib import Path
from typing import Any, Dict, List

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult
from backend.core.project_paths import GENERATED_APPS_DIR


class KisanMitraProductionSyncAgent(BaseAgent):
    name = "KisanMitraProductionSyncAgent"

    production_targets = [
        Path("D:/APPS/KisanMitraAI"),
        Path("D:/APPS/KisanMitraAI_GITHUB_CLEAN"),
    ]

    def run(self, context: Dict[str, Any]) -> AgentResult:
        app_slug = context.get("app_slug") or "kisanmitralite"
        source_dir = GENERATED_APPS_DIR / app_slug / "frontend"
        source_files = [
            source_dir / "home.html",
            source_dir / "home.css",
            source_dir / "home.js",
        ]

        planned_targets: List[Dict[str, Any]] = []
        files_to_create: List[str] = []
        files_to_update: List[str] = []
        files_to_skip: List[str] = []

        for target_root in self.production_targets:
            target_exists = target_root.exists()
            for source in source_files:
                target_file = target_root / "frontend" / source.name
                planned_targets.append(
                    {
                        "production_root": str(target_root),
                        "production_root_exists": target_exists,
                        "source_file": str(source),
                        "target_file": str(target_file),
                        "source_exists": source.exists(),
                        "target_exists": target_file.exists(),
                    }
                )
                if not source.exists():
                    files_to_skip.append(str(source))
                elif target_file.exists():
                    files_to_update.append(str(target_file))
                else:
                    files_to_create.append(str(target_file))

        return self.success(
            summary="Dry run completed. Manual approval is required before any production sync.",
            data={
                "mode": "dry_run_only",
                "source_files": [str(path) for path in source_files],
                "target_files": planned_targets,
                "files_to_create": files_to_create,
                "files_to_update": files_to_update,
                "files_to_skip": files_to_skip,
                "secret_safety_warnings": [
                    "Do not copy .env files, keys, tokens, service role keys, or private credentials.",
                    "Review generated HTML/CSS/JS before any manual production copy.",
                    "Frontend files must not contain OpenAI, Supabase service role, GitHub, Render, or private keys.",
                ],
                "manual_approval_required": True,
                "production_write_performed": False,
            },
        )
