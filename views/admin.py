import json
from pathlib import Path
import pandas as pd
import streamlit as st
from components.session import page_header, read_rows
from components.manual import observation_form
from components.market_data import setting

page_header("Data / Admin", "Connection, source records and exports.")
connected = bool(st.session_state.get("db_user"))
st.subheader("Connection")
st.write("Supabase account connected." if connected else "Session preview. Persistent storage is not connected.")
st.caption("GIE AGSI / ALSI and Open-Meteo refresh on page access. TTF futures and options providers are not configured.")
st.write("GIE key configured." if setting("GIE_API_KEY") else "GIE key missing: add GIE_API_KEY to local secrets.")
st.caption("Scheduled refresh requires Streamlit and an active dashboard session. There is no unattended worker when the app is closed.")
tables = ["manual_observations", "journal_entries", "predictions", "quiz_attempts", "assets", "option_marks", "market_events"]
export = {table: read_rows(table) for table in tables}
st.download_button("Export my records (JSON)", json.dumps(export, ensure_ascii=False, indent=2),
                   "gas-intelligence-export.json", "application/json", type="primary")
st.caption("Export includes source metadata and all revisions. Preview exports are not automatically imported into Supabase in V0.1.")
table = st.selectbox("Inspect saved records", tables)
rows = export[table]
st.write(f"{len(rows)} records")
if rows:
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
else:
    st.info("No records saved in this table.")

observation_form()

st.subheader("Loaded market snapshots")
loaded = st.session_state.get("market_cache", {})
if loaded:
    statuses = [{"Source": source, "Scope": scope, "Last successful check": r.get("last_success"),
                 "State": r.get("error") or "Available", "Records": len(r["batch"]["clean_records"]) if r.get("batch") else 0}
                for (source, scope), r in loaded.items()]
    st.dataframe(pd.DataFrame(statuses), hide_index=True, width="stretch")
    batches = [r["batch"] for r in loaded.values() if r.get("batch")]
    st.download_button("Export loaded feed snapshots (raw + normalized)", json.dumps(batches, ensure_ascii=False, indent=2),
                       "gas-feed-snapshots.json", "application/json")
    st.caption("Exports the snapshots loaded in this session. Earlier retrieval vintages and all ingestion runs remain in Supabase.")
else:
    st.info("Open Morning or Fundamentals while signed in to load and archive feeds.")

with st.expander("Connect your Supabase project", expanded=not connected):
    st.markdown("""
1. Open your Supabase project's **SQL Editor** and run `database/migrations/001_initial.sql` once.
2. Run `database/seed.sql` to install the 10 articles and 20 questions.
   Run `database/migrations/002_market_dashboard.sql` once to add market feed storage and the new page tables.
3. In **Authentication → Users**, create your user with an email and password. Keep public sign-ups disabled for this personal app.
4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` locally.
5. Enter your project URL and **publishable key** (or legacy **anon** key) in that file. Never use a service-role key.
6. Restart Streamlit, then sign in from the sidebar. Add one observation and reload to confirm persistence.
""")
    st.code('SUPABASE_URL = "https://gxnliymqvplnwoahxscf.supabase.co"\nSUPABASE_ANON_KEY = "your-publishable-key"', language="toml")
    root = Path(__file__).resolve().parents[1]
    for label, filename in [("Download schema SQL", "database/migrations/001_initial.sql"), ("Download curriculum SQL", "database/seed.sql")]:
        path = root / filename
        if path.exists():
            st.download_button(label, path.read_text(encoding="utf-8"), path.name, "text/plain")
with st.expander("Data methods and remaining connections"):
    st.write("GIE history uses gas-day dates, explicit TWh / GWh/d units and confirmed/estimated status. Daily deltas require consecutive gas days. Missing and flagged data is retained but excluded from derived metrics.")
    st.write("The five-year storage comparison uses the five preceding calendar years at the same date, based on currently retrieved history. City HDD uses an 18°C base. Weather revisions, Norway/pipeline flows, power data and exchange price analytics are later connections.")
