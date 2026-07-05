# Pixel Agent Multi-Screenshot Benchmarks

Directory:
backend/agent_auditor/pixel_benchmarks/screenshots

Current required screenshot:
chat-mobile-current.png

Optional future screenshots:
chat-mobile-after-message.png
chat-mobile-keyboard-active.png
chat-desktop-current.png
chat-small-mobile-current.png

Rules:
- Required cases must pass.
- Optional missing cases are skipped.
- Optional cases become stronger benchmarks after screenshots and expected boxes are calibrated.
- Pixel Agent should not patch UI unless the debug report and UI patch gate pass.

Run:
python backend\agent_auditor\pixel_benchmarks\pixel_real_accuracy.py
python backend\agent_auditor\forge_agent_auditor.py --agent pixel_matched_page_converter_agent
