
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Generator, List, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/ideasforge", tags=["IdeasForgeAI Chat"])

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class ChatMessage(BaseModel):
    role: str = Field(default="user")
    content: str = Field(default="")


class IdeasForgeChatRequest(BaseModel):
    mode: str = Field(default="chat")
    message: str = Field(default="")
    messages: List[ChatMessage] = Field(default_factory=list)
    local_time: Optional[str] = None


def _clean_text(value: str) -> str:
    value = (value or "").strip()
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    while "\n\n\n" in value:
        value = value.replace("\n\n\n", "\n\n")
    return value


def _mode_name(mode: str) -> str:
    mode = (mode or "chat").lower().strip()
    if mode in {"studio", "forgestudio"}:
        return "ForgeStudio"
    if mode in {"code", "forgecode"}:
        return "ForgeCode"
    if mode in {"work", "forgework"}:
        return "ForgeWork"
    return "IdeasForgeAI Chat"


def _instructions(mode: str) -> str:
    product = _mode_name(mode)

    base = f"""
You are IdeasForgeAI, a premium AI product assistant inside the user's IdeasForgeAI app.

Current section: {product}

Style:
- Speak like a helpful human product partner, not a robotic chatbot.
- Keep messages short, simple, warm, and clear.
- Use small paragraphs only.
- Do not write long essays unless the user asks.
- Ask one useful next question when needed.
- Be practical and action-focused.
- Avoid overpromising.
- Never claim files, computer, GitHub, or desktop access unless the user has connected/approved that capability.
- Public product names are ForgeStudio, ForgeCode, ForgeWork.
- Never call ForgeWork "ForgePilot" in public UI.
""".strip()

    mode = (mode or "chat").lower().strip()

    if mode in {"studio", "forgestudio"}:
        extra = """
ForgeStudio helps the user create apps, websites, UI screens, dashboards, logos, images, presentations, documents, brand systems, and preview flows.
When the user shares an idea, help shape it into a clear product concept, screens, features, flow, and next action.
""".strip()
    elif mode in {"code", "forgecode"}:
        extra = """
ForgeCode helps the user understand projects, plan code changes, debug errors, generate frontend/backend code, prepare tests, and guide deployment.
Keep safety gates clear. Do not say code was changed unless an approved code action actually happened.
""".strip()
    elif mode in {"work", "forgework"}:
        extra = """
ForgeWork helps professionals work with documents, research, reports, tasks, workflows, and professional software.
Computer control requires a trusted desktop connection and user approval. Do not claim live desktop access unless connected.
""".strip()
    else:
        extra = """
Chat helps the user decide whether to create with ForgeStudio, build with ForgeCode, or work professionally with ForgeWork.
Guide them gently to the right section.
""".strip()

    return base + "\n\n" + extra


def _conversation_text(req: IdeasForgeChatRequest) -> str:
    lines = []
    if req.local_time:
        lines.append(f"User local time: {req.local_time}")

    recent = req.messages[-14:] if req.messages else []
    for m in recent:
        role = "User" if (m.role or "").lower() == "user" else "Assistant"
        content = _clean_text(m.content)
        if content:
            lines.append(f"{role}: {content}")

    latest = _clean_text(req.message)
    if latest:
        lines.append(f"User: {latest}")

    if not lines:
        lines.append("User: Start the conversation naturally.")

    return "\n".join(lines)


def _openai_payload(req: IdeasForgeChatRequest, stream: bool) -> dict:
    return {
        "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        "instructions": _instructions(req.mode),
        "input": _conversation_text(req),
        "stream": stream,
        "store": False,
        "temperature": 0.72,
        "max_output_tokens": 520,
    }


def _extract_text(data: dict) -> str:
    if not isinstance(data, dict):
        return ""

    direct = data.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    parts = []
    for item in data.get("output", []) or []:
        for content in item.get("content", []) or []:
            if isinstance(content, dict):
                text = content.get("text") or content.get("value")
                if isinstance(text, str):
                    parts.append(text)

    return _clean_text("\n".join(parts))


def _request_openai_json(req: IdeasForgeChatRequest) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "output_text": "I am almost ready. Please add the OpenAI API key on the backend first, then I can reply intelligently."
        }

    payload = json.dumps(_openai_payload(req, stream=False)).encode("utf-8")

    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=75) as response:
            body = response.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        return {
            "output_text": f"I could not reach the AI properly yet. Backend received OpenAI error {exc.code}. Please check the API key, model, and Render environment."
        }
    except Exception as exc:
        return {
            "output_text": f"I could not connect to the AI service yet. Please check the backend and API configuration. Error: {type(exc).__name__}"
        }


def _stream_openai(req: IdeasForgeChatRequest) -> Generator[bytes, None, None]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        yield b"I am almost ready. Please add the OpenAI API key on the backend first."
        return

    payload = json.dumps(_openai_payload(req, stream=True)).encode("utf-8")

    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    emitted = False

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            for raw in response:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line or not line.startswith("data:"):
                    continue

                payload_text = line[5:].strip()
                if payload_text == "[DONE]":
                    break

                try:
                    event = json.loads(payload_text)
                except Exception:
                    continue

                event_type = event.get("type", "")

                if event_type == "response.output_text.delta":
                    delta = event.get("delta", "")
                    if delta:
                        emitted = True
                        yield delta.encode("utf-8")

                elif event_type == "response.completed" and not emitted:
                    response_obj = event.get("response") or {}
                    text = _extract_text(response_obj)
                    if text:
                        emitted = True
                        yield text.encode("utf-8")

                elif event_type == "response.error":
                    error = event.get("error") or {}
                    message = error.get("message") or "The AI service returned an error."
                    yield message.encode("utf-8")
                    return

        if not emitted:
            fallback = _request_openai_json(req)
            text = _extract_text(fallback) or "I am here. Please tell me what you want to build."
            yield text.encode("utf-8")

    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        yield f"I could not reach the AI properly yet. OpenAI error {exc.code}. Please check the API key, model, and Render environment.".encode("utf-8")
    except Exception as exc:
        yield f"I could not connect to the AI service yet. Please check the backend. Error: {type(exc).__name__}".encode("utf-8")


@router.get("/chat/health")
def chat_health():
    return {
        "ok": True,
        "configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
    }


@router.post("/chat")
def chat(req: IdeasForgeChatRequest):
    data = _request_openai_json(req)
    text = _extract_text(data) or "I am here. Please tell me what you want to build."
    return JSONResponse(
        {
            "ok": True,
            "mode": req.mode,
            "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            "reply": _clean_text(text),
        }
    )


@router.post("/chat/stream")
def chat_stream(req: IdeasForgeChatRequest):
    return StreamingResponse(
        _stream_openai(req),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
