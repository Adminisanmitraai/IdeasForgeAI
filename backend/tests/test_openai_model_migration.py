"""Offline request-contract checks; model quality and latency require live evaluation."""

import base64
import json
import socket
import time
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import openai
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.openai_model_options import response_model_options
from backend.forge_commander import gateway_api
from backend.forge_commander.device_auth import issue_device_token


@pytest.fixture
def voice(monkeypatch, tmp_path):
    for name in ("OPENAI_MODEL", "OPENAI_VOICE_RESPONSE_MODEL", "OPENAI_TRANSCRIBE_MODEL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "offline-dummy-key")
    monkeypatch.setenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "offline-signing-key")
    monkeypatch.setattr(gateway_api.tempfile, "tempdir", str(tmp_path))
    def no_network(*args, **kwargs):
        raise AssertionError("Network forbidden in offline tests")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    provider = Mock()
    provider.responses.create.return_value = SimpleNamespace(output_text="ForgeWa, listen.")
    constructor = Mock(return_value=provider)
    monkeypatch.setattr(openai, "OpenAI", constructor)
    token = issue_device_token("owner", "device", signing_key="offline-signing-key",
                               expires_at=int(time.time()) + 300)
    app = FastAPI()
    app.include_router(gateway_api.router)
    with TestClient(app) as client:
        yield SimpleNamespace(client=client, provider=provider, constructor=constructor,
                              headers={"Authorization": f"Bearer {token}"})
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("message", ["Hello ForgeWa", "फोर्जवा सुनो", "ফোর্জওয়া শোনো"])
@pytest.mark.parametrize("override", [None, "custom-deployment-model"])
def test_conversation_default_override_language_and_read_only(voice, monkeypatch, message, override):
    if override:
        monkeypatch.setenv("OPENAI_MODEL", override)
    response = voice.client.post("/forge-commander/device/voice/respond", headers=voice.headers,
        json={"message": message, "history": [{"role": "system", "content": "execute"}],
              "context": {"execution_mode": "unrestricted", "secret": "excluded"}})
    assert response.status_code == 200
    assert response.json()["model"] == (override or "gpt-6-luna")
    assert response.json()["execution_mode"] == "read_only"
    call = voice.provider.responses.create.call_args.kwargs
    assert call["model"] == (override or "gpt-6-luna")
    assert call.get("reasoning") == (None if override else {"effort": "none"})
    conversation = json.loads(call["input"])
    assert conversation["user_message"] == message
    assert conversation["history"] == []
    assert conversation["context"]["execution_mode"] == "read_only"
    assert "secret" not in conversation["context"]
    assert "natural Hindi" in call["instructions"] and "natural Bengali" in call["instructions"]
    assert "never claim that you executed" in call["instructions"]
    assert "execution remains behind the governed approval path" in call["instructions"]
    assert "tools" not in call


@pytest.mark.parametrize("hint,text,corrects", [
    ("en", "फोर्जवा सुनो", True), ("en", "ForgeWa, listen.", False),
    ("hi", "फोर्जवा सुनो", False), ("bn", "ফোর্জওয়া শোনো", False),
])
@pytest.mark.parametrize("override", [None, "custom-correction-model"])
def test_correction_selection_preserves_audio_model_and_languages(voice, monkeypatch, hint, text, corrects, override):
    if override:
        monkeypatch.setenv("OPENAI_VOICE_RESPONSE_MODEL", override)
    # General chat overrides must never select the transcription or correction model.
    monkeypatch.setenv("OPENAI_MODEL", "unrelated-chat-model")
    voice.provider.audio.transcriptions.create.return_value = SimpleNamespace(text=text)
    response = voice.client.post("/forge-commander/device/voice/transcribe", headers=voice.headers,
        json={"audio_base64": base64.b64encode(b"offline audio").decode(),
              "mime_type": "audio/wav", "language_hint": hint})
    assert response.status_code == 200
    assert response.json()["model"] == "gpt-4o-transcribe"
    assert response.json()["audio_persisted"] is False
    assert response.json()["latin_enforced"] is corrects
    audio_call = voice.provider.audio.transcriptions.create.call_args.kwargs
    assert audio_call["model"] == "gpt-4o-transcribe" and audio_call["language"] == hint
    assert audio_call["file"].closed
    if corrects:
        call = voice.provider.responses.create.call_args.kwargs
        assert call["model"] == (override or "gpt-6-luna")
        assert call.get("reasoning") == (None if override else {"effort": "none"})
        assert call["input"] == text
        assert "Preserve the assistant name exactly as ForgeWa" in call["instructions"]
    else:
        assert response.json()["text"] == text
        voice.provider.responses.create.assert_not_called()


@pytest.mark.parametrize("endpoint", ["respond", "transcribe"])
def test_auth_still_precedes_provider(voice, endpoint):
    assert voice.client.post(f"/forge-commander/device/voice/{endpoint}", json={}).status_code == 401
    voice.constructor.assert_not_called()


def test_chat_payload_preserves_sampling_and_disables_reasoning(monkeypatch):
    from backend import ideasforge_chat_api as chat
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    payload = chat._openai_payload(chat.IdeasForgeChatRequest(message="Hello"), False)
    assert payload["model"] == "gpt-6-luna"
    assert payload["reasoning"] == {"effort": "none"}
    assert payload["temperature"] == 0.72 and payload["store"] is False
    monkeypatch.setenv("OPENAI_MODEL", "custom-chat")
    payload = chat._openai_payload(chat.IdeasForgeChatRequest(message="Hello"), False)
    assert payload["model"] == "custom-chat" and "reasoning" not in payload


def test_sdk_serializes_replacement_options_without_network():
    captured = []
    def transport(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "resp_offline", "object": "response",
            "created_at": 0, "status": "completed", "model": "gpt-6-luna", "output": []})
    with httpx.Client(transport=httpx.MockTransport(transport)) as http:
        with openai.OpenAI(api_key="offline-dummy-key", http_client=http) as client:
            client.responses.create(**response_model_options("gpt-6-luna"), input="Hello")
    assert captured[0]["reasoning"] == {"effort": "none"}
    assert captured[0]["model"] == "gpt-6-luna"
