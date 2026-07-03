# ForgePilot Desktop Companion

## What FP-1 does

FP-1 creates the IdeasForgeAI Desktop Companion foundation inside `apps/desktop-companion`.

This phase includes:
- An Express + `ws` + `cors` WebSocket server on port `7070`
- A browser/mobile UI for connection status and safe test-task triggering
- A laptop agent that runs in `script-only` mode only
- One safe Desktop test file creation flow after a manual `Run Test Task` click

This phase intentionally does not include:
- Mouse control
- Keyboard control
- Screen capture or streaming
- Software launching
- Dangerous file access
- Auto-run commands

## How to install

```bash
npm install
```

## How to run server

```bash
node server.js
```

## How to run laptop agent

```bash
node laptop-agent.js
```

## How to test

1. Open `http://localhost:7070`
2. Confirm the laptop agent shows as online
3. Click `Run Test Task`
4. Check the Desktop for `ideasforgeai_connection_test.txt`
