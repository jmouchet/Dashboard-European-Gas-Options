-- Run once after 002. Adds AI briefs only; existing tables and history stay intact.
-- Claims and results are append-only. A unique daily attempt prevents simultaneous
-- dashboard/worker calls; a second attempt requires an explicit manual retry.
begin;

create table public.market_brief_runs (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    brief_date date not null,
    attempt smallint not null check (attempt between 1 and 2),
    started_at timestamptz not null default now(),
    unique (user_id, brief_date, attempt),
    unique (id, user_id, brief_date)
);

create table public.market_briefs (
    id uuid primary key,
    run_id uuid not null unique,
    user_id uuid not null default auth.uid() references auth.users(id),
    brief_date date not null,
    as_of timestamptz not null,
    generated_at timestamptz not null default now(),
    status text not null check (status in ('success', 'failed')),
    model text not null,
    prompt_version text not null,
    body text not null default '',
    citations jsonb not null default '[]' check (jsonb_typeof(citations) = 'array'),
    input_context jsonb not null,
    raw_response jsonb,
    usage jsonb not null default '{}',
    error_message text not null default '',
    foreign key (run_id, user_id, brief_date)
        references public.market_brief_runs(id, user_id, brief_date),
    check (generated_at >= as_of),
    check (status <> 'success' or (length(trim(body)) > 0 and jsonb_array_length(citations) > 0))
);
create index brief_latest on public.market_briefs(user_id, brief_date desc, generated_at desc);

alter table public.market_brief_runs enable row level security;
alter table public.market_briefs enable row level security;
create policy brief_runs_read on public.market_brief_runs for select to authenticated using ((select auth.uid()) = user_id);
create policy brief_runs_insert on public.market_brief_runs for insert to authenticated with check ((select auth.uid()) = user_id);
create policy briefs_read on public.market_briefs for select to authenticated using ((select auth.uid()) = user_id);
create policy briefs_insert on public.market_briefs for insert to authenticated with check ((select auth.uid()) = user_id);
revoke all on public.market_brief_runs, public.market_briefs from anon, authenticated;
grant select, insert on public.market_brief_runs, public.market_briefs to authenticated;
commit;
