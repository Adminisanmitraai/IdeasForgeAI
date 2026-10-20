Backend half of the pilot. Frontend and proposed SQL activation live in Ranjanhore/hr-management-saas.

# Demo checklist agent pilot

Divyansh's linked employee login can explicitly start one bounded AI checklist draft for an open assigned Demo task. Gauri's project manager login can review that draft as a different human. This is not autonomous staffing, human impersonation, background execution or an employee performance assessment.

## Surfaces

- Projects links to `/app/projects/agent` in the Demo workspace.
- The pilot page shows start, stop, persistent run history, a proposed checklist and separate human draft review.
- `/api/task-agent` accepts only fixed actions and IDs. Active workspace/caller identity is derived on the server.
- The existing model service receives only the selected task title, description and expected outcome, using caller JWT reads and its existing server-held OpenAI configuration. No new key is created or exposed.
- The backend adds `/forgehr/task-agent/draft` and must be released together with the reviewed database SQL before enabling this frontend.

## Controls

The SQL in `supabase/demo_task_agent_pilot.sql` is a **proposed activation script**, not an applied migration. Register it as a versioned migration during approved activation. The Supabase CLI was previously rejected for unrequested telemetry in this workspace, so it was not rerun. No production schema activation is claimed.

RLS requires the active `forgehr-demo` workspace, linked active `DEMO-007` employee, organization employee role, explicit project membership and current task assignment. Manager reads/reviews require existing project management access. Anonymous access and peer draft access are denied. No service-role key or user-editable metadata grants access.

Five starts per caller per database day; one running run per caller/task; one atomic provider-generation claim per run. Cancellation is terminal and later output is discarded. A provider request already sent may still consume tokens. Server interruptions can leave a running row; stop it explicitly before retrying.

Submitted drafts and human reviews are immutable through authenticated grants. Reviews require a different authorized human, current task assignee/version and a submitted draft. Draft review does not write employee daily reports, alter task state or certify execution. A new run is required for rework. Task changes invalidate output submission/review. No external message, deployment, financial action, credential change or computer execution tool exists.

Run records attribute **who initiated** a request and record its draft; they are not cryptographic attestation that a provider produced text. An authenticated caller can exercise their permitted Data API writes. All artifact content is untrusted, rendered as escaped text and cannot authorize execution. Do not use these records as independently verified work or employee evidence.

## Verification

- Ten backend unit-test methods cover role/identity/task boundaries, cancelled/stale runs, caller-scoped reads, bounded model payloads and invalid/incomplete responses.
- Twelve frontend boundary/handler tests cover strict actions, authentication, scoped output and cancellation races.
- Typecheck and focused lint are required before publication.
- The activation SQL and `supabase/tests/demo_task_agent_pilot.sql` have passed in one transaction followed by ROLLBACK: own start, duplicate running denial, one provider claim, peer read/start denial, self-review denial, manager review, unchanged employee task, immutable terminal output, cancellation and anonymous denial. Test fixture is an isolated new Demo task; all changes roll back.
- Live signed-in generation, stop races, model output quality, task reassignment/revocation/suspension across organizations, UI review and provider latency remain release checks. Mocked provider tests and role-switched SQL are not live JWT/browser certification.

The existing Phase 3 completion percentage is unchanged until its outstanding acceptance checks pass. This pilot adds no training/fine-tuning requirement. Scheduled autonomous work and additional employees are separate future milestones.
