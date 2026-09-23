# Market data: sources, methods and operations

Implemented from 2026-09-22; Morning updated on 2026-09-23. Scope: the first useful Market Dashboard
increment from roadmap sections 2–9. TTF prices, a full European gas balance and
an options surface remain later increments.

## Sources

| Source | Data | Coverage requested | Refresh on access |
| --- | --- | --- | --- |
| GIE AGSI | Fullness %, inventory/capacity TWh, injection/withdrawal GWh/d | EU, DE, FR, IT, NL, AT; Jan 1 five calendar years ago through yesterday | 6 hours |
| GIE ALSI | Send-out and technical send-out capacity, GWh/d | EU, DE, FR, IT, NL; past year through yesterday | 6 hours |
| GIE directories | Facility/operator dataset names, countries, EICs, provider operational dates | AGSI storage and ALSI LNG directories | 24 hours |
| GIE announcements | Reporting, coverage and platform notices | Returned AGSI news collection; latest 20 displayed | 6 hours |
| Open-Meteo | Daily mean 2m temperature, °C | 15 days; Berlin, Paris, Amsterdam or Milan | 1 hour |

Primary documentation: [GIE API manual v007](https://www.gie.eu/transparency-platform/GIE_API_documentation_v007.pdf),
[AGSI data definitions](https://agsi.gie.eu/data-definition),
[ALSI data definitions](https://alsi.gie.eu/data-definition),
[Open-Meteo forecast API](https://open-meteo.com/en/docs).
GIE attribution appears in the UI. The public Open-Meteo endpoint is used for this
personal application; review its licence/terms before commercial deployment.

GIE authentication uses an `x-key` header, never a URL parameter. Store
`GIE_API_KEY` in ignored `.streamlit/secrets.toml` or an environment variable.
Weather needs no key for this public endpoint. API requests have timeouts,
sanitized errors and bounded retries for throttling/temporary service failures.
GIE history uses 300-row pages, a 30-page safety bound, stable pagination checks
and a 1.1-second pause between pages.

Observed schema details: ALSI inventory is now a nested structure, so the initial
connector uses the separately documented `sendOut`/`dtrs` energy-flow fields only.
The directory repeats some EIC pairs for pre/post-Brexit country datasets (GB and
GB*); country and operational dates remain part of the identity. The news endpoint
currently ignores the requested page size and returns 306 notices. Raw payloads
are retained; only the latest 20 normalized notices are rendered. No comprehensive
outage history is claimed. Notice HTML is rendered as plain text.

## Refresh and persistence

Sign-in is required before live ingestion. Each user's authenticated Supabase
client and Streamlit cache belong to that browser session. `load_feed` first
checks that user's latest batch and ingestion run, then calls the provider only
when due or explicitly refreshed. A new session uses the remaining refresh
interval, rather than resetting it. Failed refreshes wait 15 minutes before an
automatic retry; manual refresh bypasses this delay.

Morning uses a [Streamlit fragment](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment)
that checks every 30 minutes while the session remains active. Other pages check
on access. These app refreshes stop when the application is closed. A separate
GitHub workflow can refresh EU AGSI, EU ALSI and Paris weather at 06:00 Europe/Paris
before generating the daily brief, even with the computer off. It requires explicit
configuration and activation; see [MARKET_BRIEF.md](MARKET_BRIEF.md). Other scopes
continue to refresh on app access.

`market_feed_batches` stores the source, exact non-secret request URL, UTC
retrieval time, raw response, normalized records and quality notes. Analytics are
derived in Python, never written over the raw data. Every changed payload is a
new retrieval vintage, including when a provider reverts A → B → A. Identical
successive raw responses reuse their saved batch and append a successful check
to `ingestion_runs`. The `payload_hash` is SHA-256 over the JSON retrieval envelope
(`retrieved_at` plus `raw_payload`), not the bare raw payload. Retrying the same
batch object is idempotent. Historical batches are never overwritten.

A failed provider refresh logs a failed run and displays the last saved snapshot
from that same source/scope, with the error. A failed database save does not
silently switch to session-preview storage or display an unsaved new batch.
An audit-write failure is also shown. Supabase/API outage can prevent recording
the failure itself; the error remains visible. The displayed last successful
check is distinct from the snapshot's original retrieval time.

History snapshots retain full requested windows, so database size grows. Monitor
Supabase storage as scopes and vintages accumulate. No automatic deletion or
retention policy is enabled. Data / Admin exports loaded raw/clean snapshots;
older vintages and audit runs remain in Supabase.

## Time, units and quality

- GIE gas days remain calendar labels from `gasDayStart`, not invented midnight
  timestamps. They describe the provider's gas day. `updatedAt`, when present,
  is preserved as supplied with unknown timezone; it is not assumed to be UTC.
- `retrieved_at` is a UTC instant. Open-Meteo dates use the selected city timezone.
  No model issue time is supplied: retrieval time identifies the stored forecast
  vintage. A current forecast is never presented as realized weather.
- GIE C = confirmed, E = estimated, N = no data. C and E may be displayed;
  estimates are labelled. N overrides numeric values to missing. Blank/dash,
  malformed and non-finite values remain missing; raw values stay intact.
- Negative physical values, fullness outside 0–100%, or unknown statuses are
  flagged and excluded from analytics. Fullness jumps exceeding 5 percentage
  points on consecutive gas days are flagged as a review heuristic, not deleted.
- Duplicate gas days, unexpected scopes, invalid dates and pagination changes
  reject the batch. Missing dates are recorded in quality notes. Chart gaps
  contain nulls and are not interpolated.
- Data over two calendar gas days old is labelled with its age. This is a simple
  age indication, not a claim about a publication or trading calendar.

## Calculations

- Daily delta = latest value minus the value on the immediately preceding gas
  day. Either missing or flagged input makes the delta unavailable. Fullness
  differences are **percentage points**, not percent returns.
- Net injection = injection − withdrawal on the same gas day/instrument, GWh/d.
  Positive means filling. This is not a full European supply-demand residual.
- Seasonal reference = arithmetic mean/min/max across the five preceding
  calendar years on the same month/day. All five valid observations are required.
  Leap-day references are often unavailable. Historical coverage and revisions
  affect this comparison: it is based on currently retrieved history, not a
  backtest of information available at each historical date.
- HDD = max(18°C − daily mean temperature, 0). Seven-day HDD sums the exact seven
  forecast dates starting today; mean temperature also requires all seven dates.
  Units: °C·day. City forecasts are not weighted European demand estimates.
- The tested realized-volatility helper uses sample standard deviation of N log
  returns × sqrt(252) × 100 and requires N+1 positive fixed-contract settlements.
  Missing/nonpositive prices invalidate affected windows. It is not exposed on
  manual observations because consecutive exchange sessions are not verified.
- Historical manual options use volatility points (50 means 50% annualized),
  exact underlying/expiry, source URL and explicit quote/delta/sign conventions.
  The Options & Volatility page is now unregistered; saved records remain in
  Supabase and personal exports.

Morning combines four physical metric cards, 30-day sparklines, current-year
storage against the previous year and five-year seasonal band, 45-day LNG bars,
and a 15-day Paris weather chart. Blue/amber arrows indicate a physical increase
or decrease, not bullish/bearish TTF signals. Dates, units and estimated status
remain visible. Missing values are never rendered as zero.

Manual observations, option marks, events and assets remain editable only by
appending records; no app-level update/delete exists. Event source facts and
personal interpretations have separate fields. Physical impact requires a unit.
Coordinates and capacities are never invented from a facility name.

## Verification

Run `python -m pytest -q` for the complete unit, ingestion, repository and Streamlit
workflow suite. Use the virtual environment's Python on Windows.

`python scripts/check_market_feeds.py --full` performs read-only provider checks
without printing secrets. The full EU AGSI check returned 10,445 normalized
records covering 2021-01-01–2026-09-20; ALSI returned 730 records covering
2025-09-21–2026-09-20. The latest checked values included 69.94% storage fullness
and 3,816.7 GWh/d LNG send-out, both estimated for gas day 2026-09-20. These are
verification results, never seeded or hard-coded dashboard values.

`python scripts/check_supabase.py` checks Auth and confirms anonymous access is
denied, including the five migration-002 and two migration-003 tables. This does not prove authenticated
writes or two-account isolation. The user has applied migration 002; sign-in,
feed persistence across sign-out/in and account-isolation checks must use the
user's own app account. Migration 003 is also confirmed applied. Browser visual/mobile review was not available in the
agent's browser connection; automated page rendering and workflows are tested.

## Remaining roadmap work

No futures/options price feed, EUA/JKM/power feed, verified Norway/pipeline flow
aggregation, weighted weather index, archived forecast-revision analysis,
automated physical-outage classification, complete balance model or event-return
study is implemented yet. None is inferred from unavailable inputs. Next steps
are signed-in archive verification, a verified Norway-flow mapping, and choosing
an exchange-data provider when access becomes available.
