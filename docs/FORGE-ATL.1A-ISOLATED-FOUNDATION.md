# FORGE-ATL.1A — Isolated Autonomous Training Lab Foundation

## Objective
Create ForgeATL as a serious ForgeWa-adjacent module without changing ForgeWa production behavior.

## Hard boundaries
1. No ForgeWa production activation.
2. No ForgeCommander production mutation.
3. No Student may hard-code a GPU, host, or cloud provider.
4. Teacher assistance must be disabled and auditable during examinations.
5. UI must distinguish DATA GENERATION, TRAINING, EXAMINATION, EVALUATION and IDLE truthfully.
6. Subjective ratings must identify evaluator/rubric; deterministic truth checks remain separate.
7. Medical/Ayurveda research students are research systems, not autonomous clinical decision makers.

## V1 dashboard contract
Each Student cockpit exposes identity/version/state, current feed, teacher lesson, student response, tool actions, live examination, ForgeTruth results, competency ratings, failure clusters, timeline, GPU telemetry/cost, checkpoints and replay.

## Compute architecture
Student -> ComputeRequest -> Scheduler -> Provider Adapter -> Physical/Cloud Node -> Telemetry -> Checkpoint Registry.

Initial adapters planned:
- local_nvidia
- forgepc_node
- cloud_adapter
- cluster_adapter

## Teacher architecture
Teacher Router -> Curriculum Engine -> Lesson/Task Generator -> Student -> Examiner -> ForgeTruth -> Failure Analyzer -> targeted curriculum.

## Initial acceptance gate
Foundation passes only when contracts are parseable, nine students are registered IDLE, no production imports/actions exist, and no GPU/cloud job can start from this slice.
