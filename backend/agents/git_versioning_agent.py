import subprocess
from pathlib import Path
from typing import Any, Dict, List

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult
from backend.core.project_paths import PROJECT_ROOT


class GitVersioningAgent(BaseAgent):
    name = "GitVersioningAgent"

    risky_patterns = [".env", "key", "token", "__pycache__", ".pyc", "secret"]

    def run(self, context: Dict[str, Any]) -> AgentResult:
        repo_root = Path(context.get("repo_root") or PROJECT_ROOT)
        is_git_repo = (repo_root / ".git").exists()
        git_status = self._git(repo_root, ["status", "--short"]) if is_git_repo else "Not a Git repository."
        git_branch = self._git(repo_root, ["branch", "--show-current"]) if is_git_repo else ""
        git_diff_stat = self._git(repo_root, ["diff", "--stat"]) if is_git_repo else ""
        risky_files = self._find_risky_files(repo_root)

        return self.success(
            summary="Git/GitHub readiness dry run completed. No commit or push was performed.",
            data={
                "mode": "dry_run_only",
                "is_git_repository": is_git_repo,
                "git_status": git_status,
                "git_branch": git_branch,
                "git_diff_stat": git_diff_stat,
                "suggested_branch": "feature/kisanmitraai-premium-home",
                "suggested_commit_message": "Add premium KisanMitraAI homepage and live app workflow",
                "risky_files": risky_files,
                "warnings": [
                    "Do not commit .env files, keys, tokens, __pycache__, .pyc, or generated secrets.",
                    "Stage only reviewed and approved files.",
                    "No Git commit was created.",
                    "No GitHub push was attempted.",
                ],
                "commit_performed": False,
                "push_performed": False,
            },
        )

    @staticmethod
    def _git(cwd: Path, args: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            return (result.stdout or result.stderr).strip()
        except Exception as exc:
            return f"Unable to run git {' '.join(args)}: {exc}"

    def _find_risky_files(self, root: Path) -> List[str]:
        risky: List[str] = []
        ignored_dirs = {".venv", "node_modules", ".git"}
        for path in root.rglob("*"):
            if any(part in ignored_dirs for part in path.parts):
                continue
            text = str(path).lower()
            if any(pattern in text for pattern in self.risky_patterns):
                risky.append(str(path))
            if len(risky) >= 80:
                risky.append("Risky file scan truncated at 80 entries.")
                break
        return risky
