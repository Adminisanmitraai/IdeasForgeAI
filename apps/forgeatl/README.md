# ForgeATL — Forge Autonomous Training Lab

Status: isolated foundation candidate. No production activation.

ForgeATL is a standalone ForgeWa-adjacent module for continuously teaching, examining, benchmarking and certifying specialist AI students while keeping compute providers replaceable.

## V1 mandatory surfaces
- School dashboard
- Per-student cockpit
- Live Classroom feed
- Live Examination feed
- Student response/tool-action viewer
- Competency/mastery map
- Failure analysis
- Training timeline
- GPU telemetry and cost tracking
- Replay/audit
- Model/checkpoint registry
- Teacher, Examiner, ForgeTruth and ForgeChallenge boundaries

## Initial students
ForgeCreativeDirector, ForgeCAD, ForgeScience, ForgeMedical, ForgeAgri, ForgeRobot, ForgeAI, ForgeEducation, ForgeAyurveda.

## Isolation rule
ForgeATL does not import, mutate or activate ForgeWa production runtime. Integration is future API/event-boundary work only.

## Compute rule
Students request capabilities, never a named GPU/provider. The scheduler selects physical or cloud compute through provider adapters.
