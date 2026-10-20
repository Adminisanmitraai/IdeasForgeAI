# Gauri demo voice

The public demo's Listen control now connects to the same `gpt-live-1` read-aloud session configuration used by the signed-in assistant. Browser speech synthesis has been removed. The original configuration uses the provider's default voice; this change does not introduce a new named voice or a voice clone.

The displayed answer's script selects English, Hindi or Bangla. Playback uses a silent input clock and never requests the microphone. Stop, a new question, navigation, closing the assistant and unmounting close the peer and cancel pending requests. A separate Play voice button and native audio controls support browsers that block autoplay.

Deployment requires the paired backend public-demo speak endpoint. Enable `FORGEHR_PUBLIC_DEMO_VOICE_ENABLED=true` on the backend only when releasing public voice. Existing public-demo enablement and the server-only proxy secret remain required. No new API key is needed.

The public speech request excludes workspace IDs and user credentials. It accepts at most 1,800 characters plus bounded SDP. It shares the existing demo quota (six requests/minute, 100/day per process) and two concurrent setup slots. These are process-local controls, not durable spending limits. The browser ends sessions after two minutes, but a modified client can keep a provider connection open; the setup quota does not limit ongoing provider-session duration. Review provider billing controls before enabling this new public surface.

Validation covers proxy access, strict schemas, language selection, shared backend voice configuration, stopping playback and stale connection responses. Mocked browser/provider tests cannot certify actual voice timbre, audible output or mobile autoplay. A live device comparison with the signed-in assistant remains required after deployment.
