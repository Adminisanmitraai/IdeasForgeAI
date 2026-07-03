# IdeasForgeAI Travel Dev With GitHub Codespaces

Use this workflow when you want to work on IdeasForgeAI from an iPhone browser without laptop PowerShell or a local server.

## Start From iPhone

1. Open the GitHub repo on iPhone.
2. Tap **Code**.
3. Tap **Codespaces**.
4. Create or open a codespace.
5. Open the terminal.
6. Run:

```bash
bash scripts/dev-start.sh
```

7. Open the **PORTS** tab.
8. Open the forwarded frontend port, **8088**.
9. Test Studio V4 at:

```text
/frontend/pages/studio-v4.html
```

The backend runs on port **8000** and the frontend static preview runs on port **8088**.

## Stop Dev Servers

```bash
bash scripts/dev-stop.sh
```

## Commit And Push From Codespaces

```bash
git status
git add ...
git commit -m "..."
git push origin main
```

## Notes

- Studio V4 uses the forwarded Codespaces backend URL when opened from `*.app.github.dev`.
- Local laptop testing still uses `http://127.0.0.1:8000`.
- Production still uses `https://ideasforgeai-api.onrender.com`.
- No frontend API keys or backend secrets are needed for this travel setup.

