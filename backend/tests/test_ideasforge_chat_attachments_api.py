from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import ideasforge_chat_api as chat_api


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(chat_api.router)
    return TestClient(app)


def test_attachment_upload_requires_founder_token(monkeypatch):
    monkeypatch.setenv("IF_FOUNDER_ADMIN_TOKEN", "test-founder-token")

    client = make_client()

    response = client.post(
        "/api/ideasforge/attachments",
        files={
            "files": (
                "notes.txt",
                b"Founder attachment test",
                "text/plain",
            )
        },
    )

    assert response.status_code == 401
    assert response.json()["error"] == "founder_unauthorized"


def test_text_attachment_upload_returns_attachment_id(monkeypatch):
    monkeypatch.setenv("IF_FOUNDER_ADMIN_TOKEN", "test-founder-token")

    client = make_client()

    response = client.post(
        "/api/ideasforge/attachments",
        headers={
            "X-IF-Founder-Token": "test-founder-token",
        },
        files={
            "files": (
                "notes.txt",
                b"Founder attachment test",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["ok"] is True
    assert len(payload["attachments"]) == 1
    assert payload["attachments"][0]["name"] == "notes.txt"
    assert payload["attachments"][0]["mime_type"] == "text/plain"
    assert payload["attachments"][0]["id"]


def test_chat_resolves_text_attachment(monkeypatch):
    monkeypatch.setenv("IF_FOUNDER_ADMIN_TOKEN", "test-founder-token")

    captured = {}

    def fake_openai(req, attachments=None):
        captured["attachments"] = attachments or []
        captured["conversation"] = chat_api._conversation_text(
            req,
            attachments or [],
        )
        return {"output_text": "Attachment received."}

    monkeypatch.setattr(
        chat_api,
        "_request_openai_json",
        fake_openai,
    )

    client = make_client()

    upload_response = client.post(
        "/api/ideasforge/attachments",
        headers={
            "X-IF-Founder-Token": "test-founder-token",
        },
        files={
            "files": (
                "project.txt",
                b"IdeasForgeAI attachment content",
                "text/plain",
            )
        },
    )

    attachment_id = upload_response.json()["attachments"][0]["id"]

    response = client.post(
        "/api/ideasforge/chat",
        headers={
            "X-IF-Founder-Token": "test-founder-token",
        },
        json={
            "message": "Read the attached project.",
            "mode": "chat",
            "attachment_ids": [attachment_id],
        },
    )

    assert response.status_code == 200
    assert response.json()["reply"] == "Attachment received."
    assert response.json()["attachment_count"] == 1
    assert "IdeasForgeAI attachment content" in captured["conversation"]


def test_chat_rejects_unknown_attachment_id(monkeypatch):
    monkeypatch.setenv("IF_FOUNDER_ADMIN_TOKEN", "test-founder-token")

    client = make_client()

    response = client.post(
        "/api/ideasforge/chat",
        headers={
            "X-IF-Founder-Token": "test-founder-token",
        },
        json={
            "message": "Read this.",
            "attachment_ids": ["missing-attachment"],
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "attachments_not_found"


def test_upload_rejects_unsupported_type(monkeypatch):
    monkeypatch.setenv("IF_FOUNDER_ADMIN_TOKEN", "test-founder-token")

    client = make_client()

    response = client.post(
        "/api/ideasforge/attachments",
        headers={
            "X-IF-Founder-Token": "test-founder-token",
        },
        files={
            "files": (
                "archive.zip",
                b"not-a-real-zip",
                "application/zip",
            )
        },
    )

    assert response.status_code == 415
    assert response.json()["error"] == "unsupported_attachment_type"