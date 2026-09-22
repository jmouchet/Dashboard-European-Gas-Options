-- Additive Market Dashboard migration. Run after 001; preserves all existing data.
-- Provider batches retain raw and normalized data in separate fields; analytics
-- remain derived in Python. Private records use the existing Supabase Auth model.
begin;

create table public.market_feed_batches (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null default auth.uid() references auth.users(id),
    source text not null,
    scope text not null,
    source_url text not null check (source_url ~ '^https://'),
    retrieved_at timestamptz not null,
    payload_hash text not null,
    raw_payload jsonb not null,
    clean_records jsonb not null check (jsonb_typeof(clean_records) = 'array'),
    quality_notes jsonb not null default '[]',
    created_at timestamptz not null default now(),
    unique (user_id, source, scope, payload_hash)
);
create index feed_latest on public.market_feed_batches(user_id, source, scope, retrieved_at desc);

create table public.ingestion_runs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null default auth.uid() references auth.users(id),
    source text not null,
    scope text not null,
    started_at timestamptz not null,
    finished_at timestamptz not null default now(),
    status text not null check (status in ('success', 'failed')),
    record_count integer not null default 0 check (record_count >= 0),
    message text not null default ''
);
create index run_latest on public.ingestion_runs(user_id, source, scope, finished_at desc);

create table public.assets (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    name text not null check (length(trim(name)) > 0),
    asset_type text not null,
    country text not null,
    operator text not null,
    capacity double precision check (capacity >= 0 and capacity < 'Infinity'::float8),
    capacity_unit text,
    connected_market text not null default '',
    description text not null default '',
    source_url text not null check (source_url ~ '^https?://'),
    latitude double precision check (latitude between -90 and 90),
    longitude double precision check (longitude between -180 and 180),
    created_at timestamptz not null default now(),
    check ((capacity is null) = (capacity_unit is null)),
    check ((latitude is null) = (longitude is null))
);

create table public.option_marks (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    observation_date date not null,
    underlying text not null check (length(trim(underlying)) > 0),
    expiry date not null,
    atm_vol double precision check (atm_vol >= 0 and atm_vol < 'Infinity'::float8),
    risk_reversal double precision check (risk_reversal > '-Infinity'::float8 and risk_reversal < 'Infinity'::float8),
    butterfly double precision check (butterfly > '-Infinity'::float8 and butterfly < 'Infinity'::float8),
    convention text not null check (length(trim(convention)) > 0),
    source_url text not null check (source_url ~ '^https?://'),
    notes text not null default '',
    created_at timestamptz not null default now(),
    check (expiry >= observation_date)
);

create table public.market_events (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    timestamp timestamptz not null,
    category text not null,
    entity text not null,
    headline text not null check (length(trim(headline)) > 0),
    description text not null,
    source_url text not null check (source_url ~ '^https?://'),
    physical_impact double precision check (physical_impact > '-Infinity'::float8 and physical_impact < 'Infinity'::float8),
    impact_unit text,
    expected_duration text not null default '',
    affected_tenors text not null default '',
    confidence smallint not null check (confidence between 1 and 4),
    interpretation text not null default '',
    created_at timestamptz not null default now(),
    check ((physical_impact is null) = (impact_unit is null))
);

alter table public.market_feed_batches enable row level security;
alter table public.ingestion_runs enable row level security;
alter table public.assets enable row level security;
alter table public.option_marks enable row level security;
alter table public.market_events enable row level security;

create policy feeds_read on public.market_feed_batches for select to authenticated using ((select auth.uid()) = user_id);
create policy feeds_insert on public.market_feed_batches for insert to authenticated with check ((select auth.uid()) = user_id);
create policy runs_read on public.ingestion_runs for select to authenticated using ((select auth.uid()) = user_id);
create policy runs_insert on public.ingestion_runs for insert to authenticated with check ((select auth.uid()) = user_id);
create policy assets_read on public.assets for select to authenticated using ((select auth.uid()) = user_id);
create policy assets_insert on public.assets for insert to authenticated with check ((select auth.uid()) = user_id);
create policy marks_read on public.option_marks for select to authenticated using ((select auth.uid()) = user_id);
create policy marks_insert on public.option_marks for insert to authenticated with check ((select auth.uid()) = user_id);
create policy events_read on public.market_events for select to authenticated using ((select auth.uid()) = user_id);
create policy events_insert on public.market_events for insert to authenticated with check ((select auth.uid()) = user_id);

revoke all on public.market_feed_batches, public.ingestion_runs, public.assets, public.option_marks, public.market_events from anon, authenticated;
grant select, insert on public.market_feed_batches, public.ingestion_runs, public.assets, public.option_marks, public.market_events to authenticated;
commit;
