# FORGE-ATL.1A-R1D

Adds nine Student projection profiles, each with nine domain competencies, evidence-backed learning ratings, and a pure School Dashboard aggregate projector.

Rules:
- A learning rating is not displayed unless the latest mastery event carries evidence_refs.
- Each displayed rating retains score kind, confidence, evidence references and source event ID.
- Unmeasured competencies remain null; no synthetic percentages are invented.
- Dashboard activation remains disabled.
- No training, Teacher API/model, GPU/cloud provider, ForgeWa runtime or ForgeCommander production binding exists in this slice.

Fixed certification: apps/forgeatl/test_r1d.py.
