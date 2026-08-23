# FB-2.1S — Supabase Persistent Cognitive Memory

Status: adapter/schema implemented; live database provisioning pending separate ForgeBrain Supabase project.

## Implemented
- Backend-only Supabase persistence adapter.
- Environment-only service-role configuration.
- Snapshot persistence with SHA-256 chain fields.
- Candidate persistence with pending-review default.
- Review persistence with promoted-memory and snapshot references.
- Append-only audit-event persistence.
- SQL schema for snapshots, candidates, reviews and audit events.
- Indexes for founder/version, review queue and audit history.
- RLS enabled on every cognitive table.

## Privacy boundary
Anon and authenticated roles receive no direct cognitive-table privileges. The service-role key must remain server-side and must never be shipped to ranjan.ideasforgeai.com or any other browser client.

## Required live configuration
FORGEBRAIN_SUPABASE_URL
FORGEBRAIN_SUPABASE_SERVICE_ROLE_KEY

The existing ForgeSocial Production database must not be reused for private ForgeBrain cognitive memory.
