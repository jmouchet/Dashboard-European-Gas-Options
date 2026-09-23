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
secrets and GitHub. Migrations **002 and 003 are already applied** on the user's
project; do not rerun them. GIE and OpenAI keys are configured locally. API billing
and GitHub scheduling still need activation; follow [the brief guide](docs/MARKET_BRIEF.md).

Without sign-in, the app uses session preview. Preview entries disappear when
the session is lost; export them in Data / Admin. Live ingestion requires sign-in
so fetched data can be archived. There is no automatic preview import.

## Pages

| Group / page | Implemented behavior |
| --- | --- |
| Market Dashboard / Morning | Colored EU storage/LNG cards, exact previous-gas-day changes, sparklines, seasonal storage bands, Paris weather and a sourced TTF brief |
| Markets | Exact-contract, source-separated manual TTF price explorer; automatic price feed awaits a provider |
| Fundamentals | GIE regional storage history and seasonal bands, LNG send-out, 15-day weather forecasts and HDD |
| Physical System | Searchable GIE storage/LNG dataset directories and sourced asset profiles with optional coordinates |
| Events | GIE service announcements plus a structured, sourced personal event log |
| Workspace / Journal | Append-only theses, reviews and falsifiable predictions |
| Data / Admin | Manual observation entry, personal record inspection/export, feed status and loaded raw/normalized snapshot export |

Navigation contains only **Market Dashboard** and **Workspace**, seven pages in
total. Build Understanding and Options & Volatility are removed from navigation;
their historical records remain in the database and personal exports. Morning
contains market data and the brief; manual observation entry stays in Data / Admin.

## Automatic data

GIE AGSI supplies storage, GIE ALSI supplies LNG send-out, and Open-Meteo supplies
city forecasts. GIE also supplies infrastructure datasets and platform notices.
See [data sources, units, methods and limitations](docs/MARKET_DATA.md).

Feeds check on access. Morning also checks every 30 minutes while its session
remains active: GIE gas data refreshes after six hours, weather after one hour,
directories after 24 hours. Buttons can refresh immediately. These checks need an
active app. Once configured, the separate GitHub worker refreshes EU storage,
EU LNG and Paris weather before preparing the daily brief with the app closed.

Every changed provider payload is archived with normalized records, retrieval
time, source request and quality notes. Ingestion runs record successful and
failed checks. Missing data stays missing; errors show the last saved snapshot
from the same source when available. No invented or silently substituted data.

TTF futures and options have no connected provider. Norway/pipeline flows, power,
European weather weighting/revisions and full market-price analytics are pending.
GIE service announcements are not a classified market-outage feed.

## Daily TTF brief

The OpenAI Responses API performs live web search and combines sourced news with
dated public dashboard metrics. The French brief targets 180–260 words: key point,
TTF drivers, conditional options implications and catalysts. Clickable citations,
the actual generation time, model and input context are archived in Supabase.
Journal entries and other personal records are excluded from the prompt.

GitHub Actions is configured for **06:00 Europe/Paris**, including daylight saving
changes and days when the computer is off. GitHub can delay scheduled runs; the
brief shows the actual time. The job stays disabled until `MARKET_BRIEF_ENABLED`
is set to `true` and its six secrets are configured. Opening Morning reads the
saved brief without a paid call. One explicit retry is available after failure;
the database prevents simultaneous attempts from generating duplicate briefs.

The first live API check received HTTP 429. The user confirmed billing/credits
still need activation. No successful live brief or unattended run is claimed yet.
See [configuration, costs controls and limitations](docs/MARKET_BRIEF.md).

## Storage and security

For a fresh project apply [001_initial.sql](database/migrations/001_initial.sql),
[002_market_dashboard.sql](database/migrations/002_market_dashboard.sql), then
[003_market_briefs.sql](database/migrations/003_market_briefs.sql). Migrations are
additive, transactional and intended to run once. The old curriculum seed is
optional and is no longer required by any registered page.

Supabase Auth uses a public project key and the user's email/password. Auth clients
and caches are session-scoped. User-owned tables have row-level security and
select/insert permissions only. Keys stay in local secrets or environment
variables. No service-role credentials, mutable history or app-level delete
operations are used. See [database verification](database/VERIFY.md).

Manual observations retain raw text, normalized value, explicit unit/source,
observation/publication/retrieval times and quality. Revisions append; historical
selection excludes information observed, published or entered after `as_of`.

## Tests and verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/check_market_feeds.py --full
.\.venv\Scripts\python.exe scripts/check_supabase.py
```

The test suite covers calculation edge cases, API schema/units/pagination,
failure fallback, archive retries, owner filtering, seven Streamlit pages and
input workflows. Brief tests cover citations, public-only context, Paris/DST
dates, simultaneous requests, paid-call limits and save recovery. Public live
feeds respond; new brief tables deny anonymous access. Authenticated brief writes
and the complete scheduled run still require verification after API billing and
GitHub configuration. A separate GitHub workflow runs tests without credentials.

Local verification on 2026-09-23: **102 tests and 45 subtests passed, 0 failed**.
The running Streamlit server returned HTTP 200 on its health endpoint. Automated
page rendering passed; a browser connection for visual/mobile review was unavailable.

PyArrow is pinned to the tested 24.0.0 wheel: Windows Smart App Control blocked
the 25.0.1 compute DLL on this computer. The compatible official wheel loads
successfully without changing Windows security settings.

## Layout

```text
app.py                   Streamlit navigation
views/                   Market and workspace pages; unregistered legacy pages
components/              Session auth, feed refresh, shared views and manual entry
briefing/                Public context, OpenAI connector and daily brief workflow
data/loaders/            Isolated GIE and Open-Meteo connectors
data/                    Manual observation and market-entry validation
analytics/               Pure, tested gas/weather/volatility calculations
database/                Repositories, migrations, seed and verification guide
learning/                Preserved legacy curriculum and review calculations
scripts/                 Provider checks and scheduled brief worker
.github/workflows/       Credential-free tests and opt-in daily brief
tests/                   Unit, ingestion, repository and Streamlit workflows
```
