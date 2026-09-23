import json
from pathlib import Path
import pandas as pd
import streamlit as st
from components.session import page_header, read_rows
from components.manual import observation_form
from components.market_data import setting
from briefing.openai_client import DEFAULT_MODEL

page_header("Data / Admin", "Connection, source records and exports.")
connected = bool(st.session_state.get("db_user"))
st.subheader("Connection")
st.write("Supabase account connected." if connected else "Session preview. Persistent storage is not connected.")
st.caption("GIE AGSI / ALSI and Open-Meteo refresh on page access. TTF futures and options providers are not configured.")
st.write("GIE key configured." if setting("GIE_API_KEY") else "GIE key missing: add GIE_API_KEY to local secrets.")
st.caption("Les flux du dashboard se rafraîchissent pendant la consultation. Le brief de 6 h peut être préparé indépendamment par GitHub Actions après configuration.")
tables = ["manual_observations", "journal_entries", "predictions", "quiz_attempts", "assets", "option_marks", "market_events"]
export = {table: read_rows(table) for table in tables}
st.download_button("Export my records (JSON)", json.dumps(export, ensure_ascii=False, indent=2),
                   "gas-intelligence-export.json", "application/json", type="primary")
st.caption("Export includes source metadata and all revisions. Preview exports are not automatically imported into Supabase in V0.1.")
table = st.selectbox("Inspect saved records", [t for t in tables if t not in {"quiz_attempts", "option_marks"}])
rows = export[table]
st.write(f"{len(rows)} records")
if rows:
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
else:
    st.info("No records saved in this table.")

observation_form()

st.subheader("Brief TTF · OpenAI + actualités")
st.write("Clé OpenAI locale configurée." if setting("OPENAI_API_KEY") else "Clé OpenAI locale à configurer pour une génération depuis le dashboard.")
st.caption(f"Modèle prévu : {setting('OPENAI_BRIEF_MODEL') or DEFAULT_MODEL}. Une clé présente uniquement dans GitHub permet de lire ici le brief planifié.")
with st.expander("Activer le brief quotidien à 6 h Paris"):
    st.markdown("""
1. Crée une clé dans [OpenAI Platform](https://platform.openai.com/api-keys) et active la facturation API.
2. Exécute **une fois** `database/migrations/003_market_briefs.sql` dans Supabase.
3. Dans ton dépôt GitHub, ouvre **Settings → Secrets and variables → Actions → Secrets**.
   Ajoute `OPENAI_API_KEY`, `GIE_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
   `SUPABASE_BRIEF_EMAIL` et `SUPABASE_BRIEF_PASSWORD`.
   Les deux derniers correspondent au **même compte de connexion au dashboard**,
   pour que ses règles d'accès privées s'appliquent aussi au brief. N'utilise pas de clé service-role.
4. Dans **Variables**, ajoute `MARKET_BRIEF_ENABLED` avec la valeur `true`.
5. Dans **Actions → Morning TTF brief**, lance **Run workflow** pour vérifier le premier brief.

La tâche démarre vers **6 h Europe/Paris**, ordinateur éteint compris. GitHub peut retarder
le lancement ; l'heure réelle reste visible sur le brief. Les appels OpenAI et la recherche
web sont facturés séparément de ChatGPT. Le brief utilise des données publiques, jamais ton journal.
""")
    st.code('OPENAI_API_KEY = "ta-cle-locale"\nOPENAI_BRIEF_MODEL = "gpt-5.6-terra"', language="toml")
    path = Path(__file__).resolve().parents[1] / "database/migrations/003_market_briefs.sql"
    st.download_button("Télécharger la migration 003", path.read_text(encoding="utf-8"), path.name, "text/plain")
    st.link_button("Configurer les secrets GitHub", "https://github.com/jmouchet/Dashboard-European-Gas-Options/settings/secrets/actions")

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
2. Run `database/migrations/002_market_dashboard.sql` once to add market feed storage, then `003_market_briefs.sql` for the AI brief.
3. In **Authentication → Users**, create your user with an email and password. Keep public sign-ups disabled for this personal app.
4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` locally.
5. Enter your project URL and **publishable key** (or legacy **anon** key) in that file. Never use a service-role key.
6. Restart Streamlit, then sign in from the sidebar. Add one observation and reload to confirm persistence.
""")
    st.code('SUPABASE_URL = "https://gxnliymqvplnwoahxscf.supabase.co"\nSUPABASE_ANON_KEY = "your-publishable-key"', language="toml")
    root = Path(__file__).resolve().parents[1]
    for label, filename in [("Download schema SQL", "database/migrations/001_initial.sql"), ("Download market SQL", "database/migrations/002_market_dashboard.sql")]:
        path = root / filename
        if path.exists():
            st.download_button(label, path.read_text(encoding="utf-8"), path.name, "text/plain")
with st.expander("Data methods and remaining connections"):
    st.write("GIE history uses gas-day dates, explicit TWh / GWh/d units and confirmed/estimated status. Daily deltas require consecutive gas days. Missing and flagged data is retained but excluded from derived metrics.")
    st.write("The five-year storage comparison uses the five preceding calendar years at the same date, based on currently retrieved history. City HDD uses an 18°C base. Weather revisions, Norway/pipeline flows, power data and exchange price analytics are later connections.")
