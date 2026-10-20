# Public Gauri product guide

POST `/api/ideasforge/forgehr/public-demo/chat` answers product questions through the existing server-only OpenAI Responses helper. No Supabase/workspace identity, data lookup, external links or mutation tools are accepted. The approved catalogue distinguishes signed-in pilot features from planned autonomous execution. User history is untrusted, bounded to four exchanges; provider storage is disabled. Text is rendered as text, never HTML.

Both frontend and backend must explicitly set `FORGEHR_PUBLIC_DEMO_ENABLED=true` and share a separately generated `FORGEHR_PUBLIC_DEMO_PROXY_SECRET` (at least 32 characters, server-only). Reuse the approved Render OpenAI credential. Never set a NEXT_PUBLIC secret. Neither configuration nor deployment is performed by this change. Default is disabled, with an explicitly labelled offline guide.

Two concurrent provider calls and six admitted requests/minute, 100/day **per backend process** limit exposure. These counters reset on restart and do not coordinate replicas; they are not a durable spend budget or individual visitor limit. The public frontend proxy can be called by bots; same-origin checking is not authentication. Before broad traffic, add edge bot/rate protection and provider project spending controls. The shared secret authenticates the proxy, not the visitor. Errors and request text are not logged here.

The model can suggest only a local section enum. The visitor clicks Show to navigate/highlight; no model output triggers decisions or saves. Optional speech remains browser device TTS, not live microphone voice. Browser, provider integration and configured production smoke testing remain rollout checks.
