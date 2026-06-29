# IdeasForgeAI Backend

Phase 26A adds a contract-only backend chat API surface for local validation.

## Endpoints

- `GET /api/health`
- `GET /api/contract`
- `POST /api/chat`

`POST /api/chat` accepts a JSON object with a required `message` string and an optional `sessionId` string. It returns a mock local assistant response only.

## Phase 26A Safety Boundaries

This phase does not connect real AI generation or external services. The API reports these capabilities as disabled:

- OpenAI chat
- Product generation
- Database
- Auth
- Billing
- File upload processing
- OCR
- Image analysis
- Voice transcription
- Deployment

Phase 26B approval is required before real backend-only OpenAI chat integration is added.

No `.env` file is required for Phase 26A. `backend/.env.example` contains local placeholders only.
