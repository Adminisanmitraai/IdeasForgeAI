create extension if not exists pgcrypto;

create table if not exists public.fb_cognitive_snapshots (
  snapshot_sha256 text primary key,
  founder_id text not null,
  version integer not null check (version > 0),
  stored_at timestamptz not null,
  schema_version text not null,
  profile_json jsonb not null,
  profile_sha256 text not null,
  previous_snapshot_sha256 text references public.fb_cognitive_snapshots(snapshot_sha256),
  created_at timestamptz not null default now(),
  unique(founder_id, version)
);

create table if not exists public.fb_cognitive_candidates (
  candidate_id text primary key,
  founder_id text not null,
  kind text not null,
  statement text not null,
  confidence double precision not null check (confidence >= 0 and confidence <= 1),
  source_type text not null,
  source_id text not null,
  observed_at timestamptz not null,
  project_ids text[] not null default '{}',
  duplicate_memory_ids text[] not null default '{}',
  contradiction_memory_ids text[] not null default '{}',
  review_status text not null default 'pending'
    check (review_status in ('pending','deferred','rejected','accepted')),
  created_at timestamptz not null default now()
);

create table if not exists public.fb_cognitive_reviews (
  review_id text primary key,
  candidate_id text not null references public.fb_cognitive_candidates(candidate_id),
  founder_id text not null,
  disposition text not null check (disposition in ('accept','reject','defer')),
  reviewer_id text not null,
  reviewed_at timestamptz not null,
  rationale text not null,
  conflict_resolution text not null default '',
  conflict_action text check (conflict_action is null or conflict_action in ('supersede','contextual_exception','retain_both','require_clarification')),
  conflict_target_memory_ids text[] not null default '{}',
  conflict_context_note text not null default '',
  promoted_memory_id text,
  snapshot_sha256 text references public.fb_cognitive_snapshots(snapshot_sha256),
  created_at timestamptz not null default now()
);

create table if not exists public.fb_cognitive_audit_log (
  event_id text primary key,
  founder_id text not null,
  event_type text not null,
  occurred_at timestamptz not null,
  subject_id text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists fb_snapshots_founder_version_idx
  on public.fb_cognitive_snapshots(founder_id, version desc);
create index if not exists fb_candidates_founder_status_idx
  on public.fb_cognitive_candidates(founder_id, review_status, created_at desc);
create index if not exists fb_reviews_candidate_idx
  on public.fb_cognitive_reviews(candidate_id, reviewed_at desc);
create index if not exists fb_audit_founder_time_idx
  on public.fb_cognitive_audit_log(founder_id, occurred_at desc);

alter table public.fb_cognitive_snapshots enable row level security;
alter table public.fb_cognitive_candidates enable row level security;
alter table public.fb_cognitive_reviews enable row level security;
alter table public.fb_cognitive_audit_log enable row level security;

revoke all on public.fb_cognitive_snapshots from anon, authenticated;
revoke all on public.fb_cognitive_candidates from anon, authenticated;
revoke all on public.fb_cognitive_reviews from anon, authenticated;
revoke all on public.fb_cognitive_audit_log from anon, authenticated;
