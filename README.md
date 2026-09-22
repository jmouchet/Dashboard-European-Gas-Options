# Gas Intelligence

A personal European gas and gas-options workspace built with Python, Streamlit,
Supabase/PostgreSQL and Plotly. The **Market Dashboard** implements the first
live-data increment of [roadmap sections 2–9](GAS_INTELLIGENCE_PROJECT_ROADMAP.md).

## Run locally

On this computer, double-click **Start Dashboard.cmd**, then open
[the dashboard](http://127.0.0.1:8501) and sign in. The terminal must remain open.
For a fresh environment, run each command separately in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

No activation script is necessary. [SETUP.md](SETUP.md) explains Supabase, local
secrets and GitHub. Migration **002 is already applied** on the user's project;
do not rerun it. GIE access is configured in the ignored local secrets file.

Without sign-in, the app uses session preview. Preview entries disappear when
the session is lost; export them in Data / Admin. Live ingestion requires sign-in
so fetched data can be archived. There is no automatic preview import.

## Pages

| Group / page | Implemented behavior |
| --- | --- |
| Market Dashboard / Morning | EU storage, net injection, LNG send-out, exact previous-gas-day changes, seasonal storage comparison, city weather outlook and feed status |
| Markets | Exact-contract, source-separated manual TTF price explorer; automatic price feed awaits a provider |
| Fundamentals | GIE regional storage history and seasonal bands, LNG send-out, 15-day weather forecasts and HDD |
| Physical System | Searchable GIE storage/LNG dataset directories and sourced asset profiles with optional coordinates |
| Options & Volatility | Manual ATM, 25D RR and BF marks with expiry, quote convention, source and history |
| Events | GIE service announcements plus a structured, sourced personal event log |
| Knowledge Wiki | 10 sourced introductory articles, search and categories |
| Daily Learning | Starter pack on units, storage and LNG with a chart investigation |
| Quiz & Review | 20 questions, answer before reveal, self-assessment and confidence |
| Workspace / Journal | Append-only theses, reviews and falsifiable predictions |
| Data / Admin | Manual observation entry, personal record inspection/export, feed status and loaded raw/normalized snapshot export |

The previous Morning investigation prompts, observation-history block and manual
input form have been removed from Morning. Existing records are preserved.

## Automatic data

GIE AGSI supplies storage, GIE ALSI supplies LNG send-out, and Open-Meteo supplies
city forecasts. GIE also supplies infrastructure datasets and platform notices.
See [data sources, units, methods and limitations](docs/MARKET_DATA.md).

Feeds check on access. Morning also checks every 30 minutes while its session
remains active: GIE gas data refreshes after six hours, weather after one hour,
directories after 24 hours. Buttons can refresh immediately. This is **not an
unattended background service**; nothing runs when Streamlit is stopped.

Every changed provider payload is archived with normalized records, retrieval
time, source request and quality notes. Ingestion runs record successful and
failed checks. Missing data stays missing; errors show the last saved snapshot
from the same source when available. No invented or silently substituted data.

TTF futures and options have no connected provider. Norway/pipeline flows, power,
European weather weighting/revisions and full market-price analytics are pending.
GIE service announcements are not a classified market-outage feed.

## Storage and security

Apply [001_initial.sql](database/migrations/001_initial.sql),
[seed.sql](database/seed.sql), then
[002_market_dashboard.sql](database/migrations/002_market_dashboard.sql) for a
fresh project. Migrations are additive, transactional and intended to run once.
Seed inserts stable curriculum IDs without overwriting existing rows.

Supabase Auth uses a public project key and the user's email/password. Auth clients
and caches are session-scoped. User-owned tables have row-level security and
select/insert permissions only. Keys stay in local secrets or environment
variables. No service-role credentials, mutable history or app-level delete
operations are used. See [database verification](database/VERIFY.md).

Manual observations retain raw text, normalized value, explicit unit/source,
observation/publication/retrieval times and quality. Revisions append; historical
selection excludes information observed, published or entered after `as_of`.
Quiz scores are self-assessed, not an automated mastery claim. Learning examples
are clearly illustrative and reference primary sources.

## Tests and verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/check_market_feeds.py --full
.\.venv\Scripts\python.exe scripts/check_supabase.py
```

The test suite covers calculation edge cases, API schema/units/pagination,
failure fallback, archive retries, owner filtering, and all eleven Streamlit
pages including input workflows. Public live feed checks pass; new tables deny
anonymous access. Signed-in feed archive persistence still needs the user's app
verification. A GitHub Actions workflow runs the tests without credentials.

Local verification on 2026-09-22: **83 tests and 36 subtests passed, 0 failed**;
`pip check` reported no broken requirements. Streamlit starts on port 8501.

PyArrow is pinned to the tested 24.0.0 wheel: Windows Smart App Control blocked
the 25.0.1 compute DLL on this computer. The compatible official wheel loads
successfully without changing Windows security settings.

## Layout

```text
app.py                   Streamlit navigation
views/                   Market, learning and workspace pages
components/              Session auth, feed refresh, shared views and manual entry
data/loaders/            Isolated GIE and Open-Meteo connectors
data/                    Manual observation and market-entry validation
analytics/               Pure, tested gas/weather/volatility calculations
database/                Repositories, migrations, seed and verification guide
learning/                Sourced curriculum and review calculations
scripts/                 Read-only provider/Supabase checks and seed generation
tests/                   Unit, ingestion, repository and Streamlit workflows
```
