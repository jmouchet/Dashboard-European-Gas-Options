# Supabase verification before hosting

These checks require the schema and seed to be installed. Local mock tests do not
prove that a remote project's grants, policies and authentication are correct.
Never use a service-role key when testing access restrictions.

## Inspect setup

Run in SQL Editor as the project administrator:

```sql
select count(*) as articles from public.knowledge_articles;
select count(*) as questions from public.questions;
select tablename, rowsecurity
from pg_tables
where schemaname = 'public'
  and tablename in ('knowledge_articles', 'questions', 'manual_observations',
                    'journal_entries', 'predictions', 'quiz_attempts',
                    'market_feed_batches', 'ingestion_runs', 'assets',
                    'option_marks', 'market_events');
select tablename, policyname, roles, cmd
from pg_policies
where schemaname = 'public';
```

Expect 10 articles, 20 questions, RLS enabled on all eleven listed base tables, and
only the documented SELECT/INSERT policies. These are two curriculum tables and
nine private tables. `learning_progress` is a view, not a table.

## Anonymous access

The following read-only test temporarily changes role within a transaction:

```sql
begin;
set local role anon;
select * from public.journal_entries;
rollback;
```

Expect permission denied. The failed transaction must be rolled back (run
`rollback;` separately if the SQL editor stops on the error). Anonymous clients
have no privileges on the app tables or progress view.

## Account separation and persistence

1. Sign in as your normal app account A. Save one sourced observation, journal
   entry and quiz attempt. Record their IDs from Data / Admin.
2. Create a separate temporary Auth account B in the Supabase dashboard. Open the
   app in a private browser window and sign in as B.
3. B must see the curriculum but no A observations, journal entries, predictions,
   quiz attempts or progress. Export from Data / Admin to confirm it is empty.
4. Save one B journal entry. A must not see it, including after refresh.
5. Sign out and back in as A; A's records must persist.
6. Confirm that the application offers no editing/deleting of old predictions,
   attempts or journal entries. Corrections are new records.
7. While signed in as A, open Morning. Check that `market_feed_batches` and
   `ingestion_runs` contain A-owned records and show success or a useful failure
   status. Sign out/in and confirm saved snapshots can be reused.
8. B's feed batches/runs must use B's user ID; B may fetch the same public data,
   but cannot select A's batch IDs. Assets, option marks and market events must
   likewise remain isolated. Explicitly test each of these tables with B's JWT.

Keep test fixtures identifiable. Do not delete real records during verification.
For direct API tests, a request carrying B's JWT and A's `user_id` must fail on
INSERT; SELECT must return no A rows. The client owner override is also unit-tested,
but database RLS is the access-control boundary.

## Failure behaviour

After a successful read, disconnect the network and use Refresh saved data. The
app should show a sanitized unavailable message and the last successful read time,
without showing invented zero values or switching to preview storage. Reconnect
and refresh. A failed save is not reported as successful; inspect records before
retrying an ambiguous network failure to avoid creating a duplicate.

For provider failures, use the page's **Refresh market data** button after a
successful retrieval. Morning should keep the last saved same-source snapshot,
show its gas-day date and indicate the refresh failure. Saved-record refresh and
forced provider refresh are distinct actions.

## Migration compatibility

The initial SQL creates new objects in one transaction. It intentionally fails on
conflicting existing names. Seed insertion is repeatable with `on conflict (id) do
nothing`. Review future schema changes as separate additive migrations; do not
rerun the initial migration to update a live schema.

Migration 002 adds five owner-scoped market tables without changing prior data.
The user reports applying it on 2026-09-22. Do not edit or rerun that applied
migration to introduce later schema changes; create a new numbered migration.
