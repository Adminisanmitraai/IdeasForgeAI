import os, time
import base64
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import openai
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.forge_commander.gateway_api import router, session_manager
from backend.forge_commander.device_auth import issue_device_token
from backend.forge_commander.gateway_auth import issue_gateway_token

KEY = "test-signing-key"

def _client():
    os.environ["FORGE_COMMANDER_GATEWAY_SIGNING_KEY"] = KEY
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

def _token(subject="owner-1"):
    return issue_gateway_token(subject, signing_key=KEY, expires_at=int(time.time()) + 300)

def test_health_and_tool_auth():
    client = _client()
    assert client.get("/forge-commander/health").status_code == 200
    assert client.get("/forge-commander/mcp/tools").status_code == 401
    r = client.get("/forge-commander/mcp/tools", headers={"Authorization": f"Bearer {_token()}"})
    assert r.status_code == 200
    assert r.json()["owner_subject"] == "owner-1"

def test_websocket_attach_heartbeat_disconnect():
    client = _client()
    token = issue_device_token(
        "owner-1", "dev-1", signing_key=KEY, expires_at=int(time.time()) + 300
    )
    path = "/forge-commander/device/ws/dev-1?session_id=s1&instance_id=i1"
    with client.websocket_connect(
        path, headers={"Authorization": f"Bearer {token}"}
    ) as ws:
        live = session_manager.get("dev-1")
        assert live is not None
        assert live.session.owner_subject == "owner-1"
        ws.send_json({"type": "heartbeat", "at": "2026-08-27T04:00:00+00:00"})
        assert ws.receive_json() == {
            "type": "heartbeat_ack", "at": "2026-08-27T04:00:00+00:00"
        }
        assert session_manager.get("dev-1").last_heartbeat_at == "2026-08-27T04:00:00+00:00"
    assert session_manager.get("dev-1") is None


@pytest.fixture
def transcribe_request(monkeypatch, tmp_path):
    from backend.forge_commander import gateway_api

    monkeypatch.setenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", KEY)
    monkeypatch.setenv("OPENAI_API_KEY", "offline-test-key")
    monkeypatch.setenv("OPENAI_TRANSCRIBE_MODEL", "test-transcribe-model")
    monkeypatch.setenv("OPENAI_VOICE_RESPONSE_MODEL", "test-correction-model")
    monkeypatch.setattr(gateway_api.tempfile, "tempdir", str(tmp_path))
    provider = Mock()
    constructor = Mock(return_value=provider)
    monkeypatch.setattr(openai, "OpenAI", constructor)
    audio_bytes = b"offline audio fixture"
    uploaded_files = []

    def request(transcript, correction=""):
        def transcribe(**kwargs):
            audio_file = kwargs["file"]
            uploaded_files.append(audio_file)
            assert Path(audio_file.name).is_file()
            assert audio_file.read() == audio_bytes
            assert kwargs["language"] == "en"
            assert kwargs["model"] == "test-transcribe-model"
            return SimpleNamespace(text=transcript)

        provider.audio.transcriptions.create.side_effect = transcribe
        provider.responses.create.return_value = SimpleNamespace(output_text=correction)
        token = issue_device_token(
            "owner-1", "dev-1", signing_key=KEY, expires_at=int(time.time()) + 300
        )
        with _client() as client:
            response = client.post(
                "/forge-commander/device/voice/transcribe",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "audio_base64": base64.b64encode(audio_bytes).decode("ascii"),
                    "mime_type": "audio/wav",
                    "language_hint": "en",
                },
            )
        assert response.status_code == 200, response.text
        constructor.assert_called_once_with(timeout=45)
        provider.audio.transcriptions.create.assert_called_once()
        assert len(uploaded_files) == 1
        assert uploaded_files[0].closed
        assert not Path(uploaded_files[0].name).exists()
        assert list(tmp_path.iterdir()) == []
        body = response.json()
        assert body["ok"] is True
        assert body["device_id"] == "dev-1"
        assert body["language_hint"] == "en"
        assert body["audio_persisted"] is False
        return body, provider.responses.create

    return request


def test_transcribe_english_skips_correction(transcribe_request):
    original = "ForgeWa, open the drawing."
    body, correction = transcribe_request(original)
    assert body["text"] == original
    assert body["latin_enforced"] is False
    correction.assert_not_called()


def test_transcribe_non_latin_corrects_once(transcribe_request):
    original = "फोर्जवा ड्राइंग खोलो"
    corrected = "ForgeWa, open the drawing."
    body, correction = transcribe_request(original, corrected)
    assert body["text"] == corrected
    assert body["latin_enforced"] is True
    correction.assert_called_once()
    assert correction.call_args.kwargs["input"] == original
    assert correction.call_args.kwargs["model"] == "test-correction-model"


def test_transcribe_empty_correction_preserves_original(transcribe_request):
    original = "फोर्जवा ड्राइंग खोलो"
    body, correction = transcribe_request(original, " \n\t ")
    assert body["text"] == original
    assert body["latin_enforced"] is False
    correction.assert_called_once()
    assert correction.call_args.kwargs["input"] == original


def test_transcribe_correction_instruction_preserves_forgewa(transcribe_request):
    body, correction = transcribe_request("फोर्जवा सुनो", "ForgeWa, listen.")
    correction.assert_called_once()
    instructions = correction.call_args.kwargs["instructions"]
    assert "Preserve the assistant name exactly as ForgeWa when applicable." in instructions
    assert body["text"] == "ForgeWa, listen."
    assert body["latin_enforced"] is True
