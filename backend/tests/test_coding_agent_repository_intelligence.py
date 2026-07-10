from pathlib import Path

import pytest

from backend.coding_agent_repository_intelligence import (
    WorkspaceValidationError,
    analyze_repository,
    detect_language,
    is_sensitive,
    validate_workspace,
)


def test_validate_workspace_accepts_directory(tmp_path: Path):
    resolved = validate_workspace(
        str(tmp_path),
        approved_root=str(tmp_path),
    )

    assert resolved == tmp_path.resolve()


def test_validate_workspace_rejects_missing_directory(
    tmp_path: Path,
):
    missing = tmp_path / "missing"

    with pytest.raises(WorkspaceValidationError):
        validate_workspace(
            str(missing),
            approved_root=str(tmp_path),
        )


def test_validate_workspace_rejects_file(tmp_path: Path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("test", encoding="utf-8")

    with pytest.raises(WorkspaceValidationError):
        validate_workspace(
            str(file_path),
            approved_root=str(tmp_path),
        )


def test_validate_workspace_rejects_outside_root(
    tmp_path: Path,
):
    approved = tmp_path / "approved"
    outside = tmp_path / "outside"

    approved.mkdir()
    outside.mkdir()

    with pytest.raises(WorkspaceValidationError):
        validate_workspace(
            str(outside),
            approved_root=str(approved),
        )


def test_sensitive_detection(tmp_path: Path):
    assert is_sensitive(tmp_path / ".env")
    assert is_sensitive(tmp_path / ".env.production")
    assert is_sensitive(tmp_path / "server.pem")
    assert not is_sensitive(tmp_path / "main.py")


def test_language_detection():
    assert detect_language(Path("main.py")) == "Python"
    assert detect_language(Path("app.tsx")) == "TypeScript"
    assert detect_language(Path("index.html")) == "HTML"


def test_repository_analysis_is_read_only(tmp_path: Path):
    (tmp_path / "main.py").write_text(
        '@app.get("/health")\n'
        "def health():\n"
        "    return {'ok': True}\n",
        encoding="utf-8",
    )

    (tmp_path / "requirements.txt").write_text(
        "fastapi==1.0\npytest==1.0\n",
        encoding="utf-8",
    )

    secret = tmp_path / ".env"
    secret.write_text(
        "SECRET=do-not-read",
        encoding="utf-8",
    )

    result = analyze_repository(
        str(tmp_path),
        approved_root=str(tmp_path),
    )

    assert result.summary.total_files == 3
    assert result.summary.api_count == 1
    assert "fastapi" in result.dependency_inventory
    assert any(file.is_sensitive for file in result.files)
    assert secret.read_text(encoding="utf-8") == "SECRET=do-not-read"


def test_repository_analysis_truncates(tmp_path: Path):
    for index in range(5):
        (tmp_path / f"file_{index}.py").write_text(
            "value = 1\n",
            encoding="utf-8",
        )

    result = analyze_repository(
        str(tmp_path),
        approved_root=str(tmp_path),
        max_files=2,
    )

    assert result.summary.truncated is True
    assert result.summary.total_files == 2