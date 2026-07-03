# IdeasForgeAI Backend

Phase 26B adds backend-only OpenAI chat for the existing FastAPI API.

## Endpoints

- `GET /api/health`
- `GET /api/contract`
- `POST /api/chat`

`POST /api/chat` accepts a JSON object with a required `message` string and an optional `sessionId` string. Unknown JSON fields are ignored. File, image, audio, and upload payloads remain disabled.

## Environment

Set `OPENAI_API_KEY` on the backend service only. For Render, add it to the `ideasforgeai-api` service environment variables. Do not add it to `ideasforgeai-web`, and do not commit `.env` files.

If `OPENAI_API_KEY` is missing:

- `GET /api/health` still works.
- `GET /api/contract` still works.
- `POST /api/chat` returns a safe not-configured response.

## Local Testing

Without a key:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8011
```

With a key for the current PowerShell session only:

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "set-the-key-in-your-shell-only", "Process")
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8011
Remove-Item Env:\OPENAI_API_KEY
```

## Live Testing

```powershell
$live = "https://ideasforgeai-api.onrender.com"
Invoke-RestMethod "$live/api/health"
Invoke-RestMethod "$live/api/contract"
$body = @{ sessionId = "phase26b-live"; message = "Create a polished app idea for a wedding venue booking platform"; client = "mobile"; intent = "chat" } | ConvertTo-Json
Invoke-RestMethod "$live/api/chat" -Method Post -ContentType "application/json" -Body $body
```

## Phase 26B Safety Boundaries

This phase enables backend chat only. The API reports these capabilities as disabled:

- Product generation
- Preview generation
- Code generation
- Database
- Auth
- Billing
- File upload processing
- OCR
- Image analysis
- Voice transcription
- Deployment

No database, auth, billing, upload processing, OCR, image analysis, voice transcription, frontend connector, preview generation, or code generation is added in Phase 26B.

