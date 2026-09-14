-- V0.1, new Supabase project only. Transactional and additive.
-- If any named object already exists, STOP and review instead of overwriting it.
-- No public/anonymous data access; personal rows are append-only for app users.
begin;

create table public.knowledge_articles (
    id uuid primary key,
    slug text unique not null,
    title text not null,
    category text not null,
    difficulty smallint not null check (difficulty between 1 and 5),
    summary text not null,
    content_markdown text not null,
    source_urls jsonb not null,
    importance_score smallint not null,
    curriculum_order integer not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.questions (
    id uuid primary key,
    article_id uuid not null references public.knowledge_articles(id),
    topic text not null,
    question_type text not null,
    difficulty smallint not null check (difficulty between 1 and 5),
    question text not null,
    answer text not null,
    explanation text not null,
    importance smallint not null,
    curriculum_order integer not null,
    created_at timestamptz not null default now()
);

create table public.manual_observations (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    series text not null check (series in ('ttf', 'storage', 'norway', 'lng', 'atm_vol')),
    instrument text not null check (length(trim(instrument)) > 0),
    raw_value text not null,
    clean_value double precision,
    unit text not null,
    source text not null check (length(trim(source)) > 0),
    source_url text not null check (source_url ~ '^https?://'),
    source_timestamp timestamptz,
    observation_timestamp timestamptz not null,
    source_timezone text not null,
    retrieved_at timestamptz not null,
    quality_status text not null check (quality_status in ('ok', 'missing', 'flagged')),
    notes text not null default '',
    created_at timestamptz not null default now(),
    check (clean_value is null or clean_value not in ('NaN'::float8, 'Infinity'::float8, '-Infinity'::float8)),
    check ((clean_value is null) = (quality_status = 'missing')),
    check ((series = 'ttf' and unit = 'EUR/MWh') or
           (series = 'storage' and unit = '%') or
           (series = 'norway' and unit = 'mcm/d') or
           (series = 'lng' and unit = 'GWh/d') or
           (series = 'atm_vol' and unit = 'volatility points')),
    check (quality_status <> 'ok' or series = 'ttf' or
           (clean_value >= 0 and (series <> 'storage' or clean_value <= 100)))
);
create index observations_owner_time on public.manual_observations(user_id, observation_timestamp desc);

create table public.journal_entries (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    entry_date date not null,
    entry_type text not null check (entry_type in ('Morning thesis', 'Evening review')),
    sections jsonb not null,
    created_at timestamptz not null default now()
);
create index journal_owner_date on public.journal_entries(user_id, entry_date desc);

create table public.predictions (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    prediction_date date not null,
    prediction text not null check (length(trim(prediction)) > 0),
    horizon date not null,
    confidence smallint not null check (confidence between 1 and 4),
    reasoning text not null check (length(trim(reasoning)) > 0),
    expected_outcome text not null check (length(trim(expected_outcome)) > 0),
    created_at timestamptz not null default now(),
    check (horizon >= prediction_date)
);
create index predictions_owner_date on public.predictions(user_id, prediction_date desc);

create table public.quiz_attempts (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users(id),
    question_id uuid not null references public.questions(id),
    attempt_date timestamptz not null,
    user_answer text not null check (length(trim(user_answer)) > 0),
    score double precision not null check (score in (0, 0.5, 1)),
    confidence smallint not null check (confidence between 1 and 4),
    grading_method text not null default 'self_assessed' check (grading_method = 'self_assessed'),
    response_time double precision check (response_time >= 0 and response_time < 'Infinity'::float8),
    created_at timestamptz not null default now()
);
create index quiz_owner_date on public.quiz_attempts(user_id, attempt_date desc);

-- Derived rather than a second mutable copy: attempts are the authoritative inputs.
-- security_invoker ensures the caller's underlying RLS policies apply.
create view public.learning_progress with (security_invoker = true) as
select a.user_id, q.article_id, count(*) as times_seen,
       count(*) filter (where a.score = 1) as times_correct,
       count(*) filter (where a.score = 0) as times_wrong,
       avg(a.score) as average_self_assessed_score,
       count(*) filter (where a.score = 0 and a.confidence = 4) as confident_errors,
       max(a.attempt_date) as last_seen
from public.quiz_attempts a join public.questions q on q.id = a.question_id
group by a.user_id, q.article_id;

alter table public.knowledge_articles enable row level security;
alter table public.questions enable row level security;
alter table public.manual_observations enable row level security;
alter table public.journal_entries enable row level security;
alter table public.predictions enable row level security;
alter table public.quiz_attempts enable row level security;

create policy curriculum_read on public.knowledge_articles for select to authenticated using (true);
create policy questions_read on public.questions for select to authenticated using (true);

create policy observations_read on public.manual_observations for select to authenticated using ((select auth.uid()) = user_id);
create policy observations_insert on public.manual_observations for insert to authenticated with check ((select auth.uid()) = user_id);
create policy journal_read on public.journal_entries for select to authenticated using ((select auth.uid()) = user_id);
create policy journal_insert on public.journal_entries for insert to authenticated with check ((select auth.uid()) = user_id);
create policy predictions_read on public.predictions for select to authenticated using ((select auth.uid()) = user_id);
create policy predictions_insert on public.predictions for insert to authenticated with check ((select auth.uid()) = user_id);
create policy attempts_read on public.quiz_attempts for select to authenticated using ((select auth.uid()) = user_id);
create policy attempts_insert on public.quiz_attempts for insert to authenticated with check ((select auth.uid()) = user_id);

revoke all on public.knowledge_articles, public.questions, public.manual_observations,
    public.journal_entries, public.predictions, public.quiz_attempts, public.learning_progress from anon, authenticated;
grant select on public.knowledge_articles, public.questions, public.learning_progress to authenticated;
grant select, insert on public.manual_observations, public.journal_entries, public.predictions, public.quiz_attempts to authenticated;
commit;
