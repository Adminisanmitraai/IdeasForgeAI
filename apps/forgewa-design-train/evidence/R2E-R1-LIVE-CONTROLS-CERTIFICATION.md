# FW-TRAIN.CADMAXD5.1A-R2E-R1 — User-started live control certification

Status: PASS.

The isolated Teacher Mode panel was opened idle and did not start observation. The user then performed live trials through the visible panel.

## AutoCAD live observation
A bounded live run detected AutoCAD 2024 and the title-derived drawing hint Eco_Park_Update_25_09_2026.dwg. One verified run completed 10 samples, 9 supported AutoCAD samples, source=live, stop_reason=sample_limit, session_closed=true. Its timeline included a balanced drawing session_start/session_end pair. The observer also encountered the AutoCAD child title "References - Not Found Files" and later returned to the drawing HWND; both recorded sessions were balanced.

A later live AutoCAD run also persisted Eco_Park_Update_25_09_2026.dwg with a balanced session pair and automatic bounded stop.

## Pause deadline trial
Run run_99b597ef6cb94953ab416cad82d4444a recorded start, two samples, pause, then stop:time_limit. pause_count=1, samples=2, session_closed=true. No Resume occurred before the original deadline. This certifies that Pause is live and does not extend the fixed safety deadline.

## Final Start/Pause/Resume/Stop trial
Run run_c3907548777e49e38c4604289c9b5b90 recorded, in order:
1. start
2. sample
3. sample
4. pause
5. resume
6. sample
7. sample
8. stop:user_stop

The run lasted 4.284100300021237 seconds, pause_count=1, samples=4, state=STOPPED, stop_reason=user_stop, session_closed=true, source=live, observe_only=true, autonomous_actions=false, production_activation=false. The Teacher Mode panel remained foreground for this control-only run, so supported_samples=0 and no teacher_timeline.jsonl was created. This is expected and is not represented as an AutoCAD observation trial.

## Isolation
After the final trial, Desktop Commander reported no active terminal sessions. The four protected ForgeCommander production SHA-256 values remained:
- bootstrap_security_patch_contract.py: 8c39f71d86b4bc027ff6bb21caeb697e74d0a2e32f720ad7b55f15ec8a44789a
- mcp_server.py: 480e91e8e0f6e40e7e4e8bff63a8d03388f17e42352da4cf3187ea993db01053
- production_agent_runtime.py: ae6a4367f98d86cf6ed3cfc02bb2910b946b3eb2157b24b30d9145a841ca72f7
- security_surface_patch_contract.py: db86c7dedbe4fe338d579cb3bafcd900e3db49adbab7fdc2ac9af339a50df9b8

No autonomous editing, screenshot capture, input injection, application focus control, production activation, production restart, or deployment was performed by these trials.

D5 remains deferred to the RTX machine and is not certified by R2E-R1.

R2E-R1 disposition: COMPLETE for the isolated AutoCAD live observation + visible Start/Pause/Resume/Stop + bounded automatic-stop controls. 3ds Max observation was previously live-certified in R2D; the R2E-R1 visible button-control sequence itself was exercised with AutoCAD selected / panel foreground.
