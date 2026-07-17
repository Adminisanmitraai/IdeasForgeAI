from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from threading import RLock
from typing import Generator, List, Optional

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/ideasforge", tags=["IdeasForgeAI Chat"])

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MAX_ATTACHMENT_COUNT = 5
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
ATTACHMENT_TTL_SECONDS = 60 * 60

ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}

ALLOWED_TEXT_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
}

ALLOWED_ATTACHMENT_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_TEXT_TYPES


@dataclass(frozen=True)
class AttachmentRecord:
    attachment_id: str
    filename: str
    mime_type: str
    size: int
    content: bytes
    created_at: float


_ATTACHMENT_LOCK = RLock()
_ATTACHMENTS: dict[str, AttachmentRecord] = {}


class ChatMessage(BaseModel):
    role: str = Field(default="user")
    content: str = Field(default="")


class IdeasForgeChatRequest(BaseModel):
    mode: str = Field(default="chat")
    message: str = Field(default="")
    messages: List[ChatMessage] = Field(default_factory=list)
    local_time: Optional[str] = None
    attachment_ids: List[str] = Field(default_factory=list)


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
    mode = (mode or "chat").lower().strip()

    shared = """
You are IdeasForgeAI inside the user's own AI product platform.

Important style:
- Sound human, calm, intelligent, and practical.
- Keep replies short unless the user asks for detail.
- Use simple words.
- Prefer small messages and clear next steps.
- Ask only one useful question at a time.
- Do not sound robotic.
- Do not overpromise.
- Do not claim you edited files, controlled a computer, connected GitHub, deployed, or read private files unless that action really happened through an approved tool.
- Public product names are ForgeStudio, ForgeCode, and ForgeWork.
- Never call ForgeWork "ForgePilot" in public.
- When attachments are provided, inspect only those attachments and explain uncertainty clearly.
""".strip()

    chat = """
Brain: IdeasForgeAI Chat Router
Purpose:
Help the user decide whether they need ForgeStudio, ForgeCode, or ForgeWork.
Guide vague ideas into a clear starting point.
Be friendly and direct.
""".strip()

    studio = """
Brain: ForgeStudio
Purpose:
Act like a creative product architect.
Help create apps, websites, UI/UX, dashboards, logos, images, presentations, documents, branding, marketing materials, and preview flows.
Convert rough ideas into screens, sections, content, features, and a clean build plan.
Keep the tone visual, polished, and founder-friendly.
""".strip()

    code = """
Brain: ForgeCode
Purpose:
Act like a senior software engineering partner.
Help analyze projects, explain architecture, plan code changes, debug errors, write frontend/backend logic, prepare tests, and guide deployment.
Always protect the user with approval gates.
When unsure, ask for the exact file, screenshot, log, repository, or error.
""".strip()

    work = """
Brain: ForgeWork
Purpose:
Act like a professional workspace intelligence layer.
Help with documents, research, reports, tasks, workflows, calculations, planning, and professional software work.
For desktop/computer work, require a trusted connection and user approval.
Never imply hidden control.
""".strip()

    if mode in {"studio", "forgestudio"}:
        return shared + "\n\n" + studio

    if mode in {"code", "forgecode"}:
        return shared + "\n\n" + code

    if mode in {"work", "forgework"}:
        return shared + "\n\n" + work

    return shared + "\n\n" + chat


def _expected_founder_token() -> str:
    return os.getenv("IF_FOUNDER_ADMIN_TOKEN", "").strip()


def _provided_founder_token(request: Request) -> str:
    return str(
        request.headers.get("X-IF-Founder-Token")
        or request.headers.get("x-if-founder-token")
        or ""
    ).strip()


def _founder_access_error(request: Request) -> JSONResponse | None:
    expected = _expected_founder_token()

    if not expected:
        return JSONResponse(
            status_code=403,
            content={
                "ok": False,
                "error": "founder_access_not_configured",
                "detail": "Founder attachment access is not configured.",
            },
        )

    if _provided_founder_token(request) != expected:
        return JSONResponse(
            status_code=401,
            content={
                "ok": False,
                "error": "founder_unauthorized",
                "detail": "A valid Founder token is required.",
            },
        )

    return None


def _normalize_mime_type(upload: UploadFile) -> str:
    value = (upload.content_type or "").lower().strip()

    if value:
        return value

    filename = (upload.filename or "").lower()

    if filename.endswith(".md"):
        return "text/markdown"

    if filename.endswith(".csv"):
        return "text/csv"

    if filename.endswith(".json"):
        return "application/json"

    if filename.endswith(".txt"):
        return "text/plain"

    return "application/octet-stream"


def _cleanup_expired_attachments() -> None:
    cutoff = time.time() - ATTACHMENT_TTL_SECONDS

    with _ATTACHMENT_LOCK:
        expired_ids = [
            attachment_id
            for attachment_id, record in _ATTACHMENTS.items()
            if record.created_at < cutoff
        ]

        for attachment_id in expired_ids:
            _ATTACHMENTS.pop(attachment_id, None)


def _resolve_attachments(
    attachment_ids: List[str],
) -> tuple[List[AttachmentRecord], List[str]]:
    _cleanup_expired_attachments()

    resolved: List[AttachmentRecord] = []
    missing: List[str] = []

    with _ATTACHMENT_LOCK:
        for attachment_id in attachment_ids:
            record = _ATTACHMENTS.get(attachment_id)

            if record is None:
                missing.append(attachment_id)
            else:
                resolved.append(record)

    return resolved, missing


def _decode_text_attachment(record: AttachmentRecord) -> str:
    return record.content.decode("utf-8", errors="replace")


def _conversation_text(
    req: IdeasForgeChatRequest,
    attachments: List[AttachmentRecord] | None = None,
) -> str:
    lines: List[str] = []

    if req.local_time:
        lines.append(f"User local time: {req.local_time}")

    recent = req.messages[-14:] if req.messages else []

    for message in recent:
        role = (
            "User"
            if (message.role or "").lower() == "user"
            else "Assistant"
        )
        content = _clean_text(message.content)

        if content:
            lines.append(f"{role}: {content}")

    latest = _clean_text(req.message)

    if latest:
        lines.append(f"User: {latest}")

    for attachment in attachments or []:
        if attachment.mime_type not in ALLOWED_TEXT_TYPES:
            continue

        text = _clean_text(_decode_text_attachment(attachment))

        if len(text) > 40_000:
            text = text[:40_000] + "\n[Attachment truncated]"

        lines.append(
            "\n".join(
                [
                    f"Attached file: {attachment.filename}",
                    f"Content type: {attachment.mime_type}",
                    "File content:",
                    text,
                ]
            )
        )

    if not lines:
        lines.append("User: Start the conversation naturally.")

    return "\n".join(lines)


def _openai_input(
    req: IdeasForgeChatRequest,
    attachments: List[AttachmentRecord],
) -> str | list[dict]:
    text = _conversation_text(req, attachments)

    image_attachments = [
        attachment
        for attachment in attachments
        if attachment.mime_type in ALLOWED_IMAGE_TYPES
    ]

    if not image_attachments:
        return text

    content: List[dict] = [
        {
            "type": "input_text",
            "text": text,
        }
    ]

    for attachment in image_attachments:
        encoded = base64.b64encode(attachment.content).decode("ascii")

        content.append(
            {
                "type": "input_image",
                "image_url": (
                    f"data:{attachment.mime_type};base64,{encoded}"
                ),
            }
        )

    return [
        {
            "role": "user",
            "content": content,
        }
    ]


def _openai_payload(
    req: IdeasForgeChatRequest,
    stream: bool,
    attachments: List[AttachmentRecord] | None = None,
) -> dict:
    selected_attachments = attachments or []

    return {
        "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        "instructions": _instructions(req.mode),
        "input": _openai_input(req, selected_attachments),
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

    parts: List[str] = []

    for item in data.get("output", []) or []:
        for content in item.get("content", []) or []:
            if not isinstance(content, dict):
                continue

            text = content.get("text") or content.get("value")

            if isinstance(text, str):
                parts.append(text)

    return _clean_text("\n".join(parts))


def _request_openai_json(
    req: IdeasForgeChatRequest,
    attachments: List[AttachmentRecord] | None = None,
) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "output_text": (
                "I am almost ready. Please add the OpenAI API key "
                "on the backend first, then I can reply intelligently."
            )
        }

    payload = json.dumps(
        _openai_payload(
            req,
            stream=False,
            attachments=attachments,
        )
    ).encode("utf-8")

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
        exc.read()

        return {
            "output_text": (
                "I could not reach the AI properly yet. "
                f"Backend received OpenAI error {exc.code}. "
                "Please check the API key, model, and Render environment."
            )
        }

    except Exception as exc:
        return {
            "output_text": (
                "I could not connect to the AI service yet. "
                "Please check the backend and API configuration. "
                f"Error: {type(exc).__name__}"
            )
        }


def _stream_openai(
    req: IdeasForgeChatRequest,
    attachments: List[AttachmentRecord] | None = None,
) -> Generator[bytes, None, None]:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        yield (
            b"I am almost ready. Please add the OpenAI API key "
            b"on the backend first."
        )
        return

    payload = json.dumps(
        _openai_payload(
            req,
            stream=True,
            attachments=attachments,
        )
    ).encode("utf-8")

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
                line = raw.decode(
                    "utf-8",
                    errors="replace",
                ).strip()

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

                elif (
                    event_type == "response.completed"
                    and not emitted
                ):
                    response_object = event.get("response") or {}
                    text = _extract_text(response_object)

                    if text:
                        emitted = True
                        yield text.encode("utf-8")

                elif event_type == "response.error":
                    error = event.get("error") or {}
                    message = (
                        error.get("message")
                        or "The AI service returned an error."
                    )
                    yield message.encode("utf-8")
                    return

        if not emitted:
            fallback = _request_openai_json(
                req,
                attachments=attachments,
            )
            text = (
                _extract_text(fallback)
                or "I am here. Please tell me what you want to build."
            )
            yield text.encode("utf-8")

    except urllib.error.HTTPError as exc:
        exc.read()

        yield (
            "I could not reach the AI properly yet. "
            f"OpenAI error {exc.code}. "
            "Please check the API key, model, and Render environment."
        ).encode("utf-8")

    except Exception as exc:
        yield (
            "I could not connect to the AI service yet. "
            "Please check the backend. "
            f"Error: {type(exc).__name__}"
        ).encode("utf-8")


@router.get("/chat/health")
def chat_health():
    return {
        "ok": True,
        "configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        "attachments": {
            "enabled": True,
            "maximum_files": MAX_ATTACHMENT_COUNT,
            "maximum_bytes_per_file": MAX_ATTACHMENT_BYTES,
            "allowed_types": sorted(ALLOWED_ATTACHMENT_TYPES),
        },
    }


@router.post("/attachments")
async def upload_attachments(
    request: Request,
    files: List[UploadFile] = File(...),
):
    access_error = _founder_access_error(request)

    if access_error is not None:
        return access_error

    _cleanup_expired_attachments()

    if not files:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "attachments_required",
            },
        )

    if len(files) > MAX_ATTACHMENT_COUNT:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "too_many_attachments",
                "maximum": MAX_ATTACHMENT_COUNT,
            },
        )

    prepared: List[AttachmentRecord] = []

    for upload in files:
        filename = (upload.filename or "attachment").strip()
        mime_type = _normalize_mime_type(upload)

        if mime_type not in ALLOWED_ATTACHMENT_TYPES:
            return JSONResponse(
                status_code=415,
                content={
                    "ok": False,
                    "error": "unsupported_attachment_type",
                    "filename": filename,
                    "mime_type": mime_type,
                },
            )

        content = await upload.read(MAX_ATTACHMENT_BYTES + 1)

        if len(content) > MAX_ATTACHMENT_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "ok": False,
                    "error": "attachment_too_large",
                    "filename": filename,
                    "maximum_bytes": MAX_ATTACHMENT_BYTES,
                },
            )

        if not content:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": "empty_attachment",
                    "filename": filename,
                },
            )

        prepared.append(
            AttachmentRecord(
                attachment_id=uuid.uuid4().hex,
                filename=filename,
                mime_type=mime_type,
                size=len(content),
                content=content,
                created_at=time.time(),
            )
        )

    with _ATTACHMENT_LOCK:
        for record in prepared:
            _ATTACHMENTS[record.attachment_id] = record

    return {
        "ok": True,
        "attachments": [
            {
                "id": record.attachment_id,
                "name": record.filename,
                "mime_type": record.mime_type,
                "size": record.size,
                "expires_in_seconds": ATTACHMENT_TTL_SECONDS,
            }
            for record in prepared
        ],
    }


@router.post("/chat")
def chat(
    req: IdeasForgeChatRequest,
    request: Request,
):
    attachments, missing_ids = _resolve_attachments(
        req.attachment_ids
    )

    if req.attachment_ids:
        access_error = _founder_access_error(request)

        if access_error is not None:
            return access_error

    if missing_ids:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "attachments_not_found",
                "attachment_ids": missing_ids,
            },
        )

    data = _request_openai_json(
        req,
        attachments=attachments,
    )

    text = (
        _extract_text(data)
        or "I am here. Please tell me what you want to build."
    )

    return JSONResponse(
        {
            "ok": True,
            "mode": req.mode,
            "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            "reply": _clean_text(text),
            "attachment_count": len(attachments),
        }
    )


@router.post("/chat/stream")
def chat_stream(
    req: IdeasForgeChatRequest,
    request: Request,
):
    attachments, missing_ids = _resolve_attachments(
        req.attachment_ids
    )

    if req.attachment_ids:
        access_error = _founder_access_error(request)

        if access_error is not None:
            return access_error

    if missing_ids:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "attachments_not_found",
                "attachment_ids": missing_ids,
            },
        )

    return StreamingResponse(
        _stream_openai(
            req,
            attachments=attachments,
        ),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )