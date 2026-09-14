import json
from pathlib import Path
import pandas as pd
import streamlit as st
from components.session import page_header, read_rows

page_header("Data / Admin", "Connection, source records and exports.")
connected = bool(st.session_state.get("db_user"))
st.subheader("Connection")
st.write("Supabase account connected." if connected else "Session preview. Persistent storage is not connected.")
st.caption("No provider APIs are connected. Market observations are entered manually; Wiki content has linked primary references.")
tables = ["manual_observations", "journal_entries", "predictions", "quiz_attempts"]
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

with st.expander("Connect your Supabase project", expanded=not connected):
    st.markdown("""
1. Open your Supabase project's **SQL Editor** and run `database/migrations/001_initial.sql` once.
2. Run `database/seed.sql` to install the 10 articles and 20 questions.
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
with st.expander("Planned next steps"):
    st.write("Verify Supabase persistence and access controls, use the manual workflow for several days, then add GIE storage ingestion. Weather, flows and options analytics follow the roadmap.")
