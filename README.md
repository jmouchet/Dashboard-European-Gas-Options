# Gas Intelligence

A personal European gas and gas-options workspace, built with Python, Streamlit,
Supabase/PostgreSQL and Plotly. This first increment implements the manual workflow
in section 37 of [the roadmap](GAS_INTELLIGENCE_PROJECT_ROADMAP.md).

## First run on Windows

Open PowerShell in this folder and run each command separately:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Open [the local dashboard](http://localhost:8501). No PowerShell activation script
is required. Without Supabase settings, the app opens in **session preview**.
Preview entries disappear when the session is lost; export them from Data / Admin.
There is no alternate local database and no automatic preview-to-Supabase import.

After the initial installation, double-click **Start Dashboard.cmd** to launch
the app again. Keep its terminal window open while using the dashboard.

Follow [SETUP.md](SETUP.md) to connect the existing Supabase project and publish to
the existing GitHub repository. Do not put keys or passwords in chat or Git.

## What is implemented

| Page | First-version behaviour |
| --- | --- |
| Morning | Sourced manual values, exact contract/region and source selection, point history, data-quality flags |
| Knowledge Wiki | 10 sourced introductory articles, search and category filters |
| Daily Learning | Fixed starter pack using units, storage and LNG, with one shared historical episode |
| Quiz & Review | 20 questions, answer before reveal, self-assessment, confidence and attempt history |
| Journal | Append-only morning theses, evening reviews and falsifiable predictions |
| Data / Admin | Connection instructions, record inspection and complete JSON export |

Supabase sign-in uses the user's email/password and a public project key. Clients
and read caches are scoped to the browser session. Private tables have row-level
security and allow users to select and append only their own records. There are
no app-level update or delete operations. See [Supabase's RLS documentation](https://supabase.com/docs/guides/database/postgres/row-level-security).

No live market data, market feeds, paid sources, automated trades or generated
market observations are included. All numbers in learning examples are explicitly
illustrative. Primary references appear inside each article.

## Data and calculation conventions

- Every manual observation retains raw text, normalized numeric value, unit,
  source name/URL, observation time, optional publication time, original UTC offset,
  entry time and quality status. For manual entry, `retrieved_at` means the time
  entered into this application; it is not an API download timestamp.
- Blank numeric input remains null. NaN/infinity and ambiguous decimal formats
  are rejected. Out-of-range storage and negative physical flows/volatility are
  retained and flagged, then excluded from metric cards/charts. Negative TTF
  prices are not automatically rejected.
- Storage sanity range is 0–100%; physical flows and volatility must be nonnegative
  to qualify as `ok`. No undocumented upper bounds are invented for those series.
- Corrections append a new observation and require a note. Chart selection uses
  the latest entry for the same metric, exact instrument/scope, source and observed
  time. A missing/flagged revision does not resurrect an older value.
- The history helper accepts an `as_of` time and excludes later observations,
  publications and entries. Backfilled data entered today is not treated as having
  been available in this app yesterday. Inputs remain manually asserted, not
  independently verified against a provider.
- All stored instants use UTC; input requires an explicit offset or `Z`. The
  original offset is preserved. Observation charts use UTC. Journal dates use
  Europe/Paris. Gas-day transformations are deferred until a provider's convention
  is documented.
- Contracts and sources are never silently stitched. A point chart avoids implying
  observations between irregular manual entries. No daily returns, percentiles,
  continuous M1 series or automated gap/jump alerts are calculated yet.
- An observation older than 48 elapsed hours is labelled as such. This is a simple
  age indication, not an exchange-calendar freshness rule.
- Energy conversion: 1 TWh = 1,000 GWh = 1,000,000 MWh. Volume conversion requires
  an explicit calorific value: GWh = mcm × kWh/m³. Document HHV/LHV and reference
  conditions whenever using this conversion with actual data.
- Quiz score is self-assessed: 0, 0.5 or 1. The displayed average is the arithmetic
  mean across attempts, including repeat attempts. Wrong + confidence 4 is tracked
  separately. No automated scoring or mastery claim is made. Response time measures
  elapsed time since the question opened and can include idle time.

## Database

[001_initial.sql](database/migrations/001_initial.sql) creates six tables plus a
`learning_progress` view. The view derives progress from attempts using
`security_invoker = true`; it avoids a second mutable copy drifting out of sync.
This is the only schema deviation from the first-build list: a derived view instead
of a stored progress table, plus a manual-observations table needed by Morning.

The migration is for a new project, is transactional and changes no existing
application objects. It fails if a named object already exists. Inspect such a
conflict instead of deleting or replacing existing objects. No migration has been
applied remotely by this build.

[seed.sql](database/seed.sql) inserts the curriculum with stable IDs. Re-running
the seed does not overwrite existing articles or questions. Connected mode reads
the database curriculum; preview mode reads its bundled source. Future content
changes require an explicit migration so references remain reproducible.

Regenerate the SQL after editing `learning/content.py`:

```powershell
python scripts/build_seed.py
```

## Tests and current verification

Full suite after installation:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The same test cases can run through Python's standard-library runner:

```powershell
python -m unittest discover -s tests -v
```

Validation on 2026-09-14: dependencies installed successfully into `.venv` using
Python 3.14.2. **48 tests passed, 0 failed, 0 skipped**, including all nine Streamlit
smoke/workflow tests (and 27 passing subtests). `pip check` reported no broken
requirements. The first sandboxed test run had temporary-file permission errors
and a startup timeout; the approved unrestricted run passed in 2.73 seconds.
Streamlit started successfully on `127.0.0.1:8501`.

Supabase setup: the user reports applying the schema/seed and creating an Auth
account. The locally configured public key passed a live Auth service check;
anonymous reads were denied on all six tables and the progress view. The app was
restarted with network access for Supabase sign-in. These read-only checks can be
repeated with `.venv\Scripts\python.exe scripts/check_supabase.py` and never print
keys or response bodies.

The user confirmed successful sign-in, the requested app checks and records
persisting after signing out and back in on 2026-09-14.

Pending: independent authenticated curriculum counts, desktop/mobile visual review
and two-account RLS checks. The initial version is published on the repository's
`main` branch. See
[the database verification procedure](database/VERIFY.md).

## Project layout

```text
app.py                   Streamlit navigation
views/                   Six initial pages
components/session.py    Per-session auth, repository selection and read cache
data/validation.py       Manual observation normalization and revision selection
database/                Repository, initial migration, seed and verification guide
learning/                Sourced curriculum and descriptive progress calculation
utils/                   Settings, dates and explicit unit conversions
tests/                   Data, security-boundary, curriculum and Streamlit tests
```

The app follows [Streamlit's multipage API](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation).
Read results are cached for 30 seconds per session; writes and the refresh button
invalidate the cache. An API failure shows a sanitized error and the last successful
read time where available, without substituting preview data. Dependency ranges
are bounded but not locked; record a tested lock set after the first successful
installation.

## Next increment

Use the manual workflow for several days, then build the GIE storage connector
with documented API fields, units and ingestion tests.
Provider access details will be requested when that work begins. Predictions use
evening-review references for post-mortems in V0.1; structured outcome scoring,
adaptive learning and additional market pages follow the roadmap.
