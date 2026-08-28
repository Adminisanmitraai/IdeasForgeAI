from pathlib import Path
import pytest

from backend.forge_commander import production_agent_runtime as runtime


def _allow(monkeypatch, root: Path):
    monkeypatch.setattr(runtime, "_allowed_read_roots", lambda: (root.resolve(),))


def test_file_read_text_exact_path(monkeypatch, tmp_path):
    _allow(monkeypatch, tmp_path)
    target = tmp_path / "safe.md"
    target.write_text("forge-read-ok", encoding="utf-8")
    data = runtime._file_or_terminal_payload("file.read_text", {"path": str(target)})
    assert data["path"] == str(target.resolve())
    assert data["content"] == "forge-read-ok"


def test_file_read_text_blocks_sensitive(monkeypatch, tmp_path):
    _allow(monkeypatch, tmp_path)
    target = tmp_path / ".env"
    target.write_text("SECRET=nope", encoding="utf-8")
    with pytest.raises(PermissionError):
        runtime._file_or_terminal_payload("file.read_text", {"path": str(target)})


def test_file_read_text_enforces_64k(monkeypatch, tmp_path):
    _allow(monkeypatch, tmp_path)
    target = tmp_path / "large.txt"
    target.write_text("x" * 65537, encoding="utf-8")
    with pytest.raises(ValueError, match="file_too_large"):
        runtime._file_or_terminal_payload("file.read_text", {"path": str(target)})