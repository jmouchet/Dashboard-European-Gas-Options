from datetime import datetime, timezone, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from components.session import page_header, read_rows, save_row
from data.validation import SERIES, latest_revisions, make_observation, parse_timestamp, utc_now

page_header("Morning", "What changed? What matters? What deserves investigation?")
rows = read_rows("manual_observations")
eligible = latest_revisions(rows)
st.subheader("Market & fundamentals")

for col, series in zip(st.columns(4), ["ttf", "storage", "norway", "lng"]):
    with col:
        spec = SERIES[series]
        candidates = [r for r in eligible if r["series"] == series]
        if not candidates:
            st.metric(spec["label"], "—")
            st.caption(f"{spec['unit']} · No observation")
            continue
        identities = sorted({(r["instrument"], r["source"]) for r in candidates})
        identity = st.selectbox(spec["label"] + " series", identities,
                                format_func=lambda x: f"{x[0]} · {x[1]}", key=f"metric_{series}")
        history = [r for r in candidates if (r["instrument"], r["source"]) == identity]
        latest = history[-1]
        value = latest["clean_value"] if latest["quality_status"] == "ok" else None
        st.metric(spec["label"], f"{value:,.2f}" if value is not None else "—")
        st.caption(f"{spec['unit']} · {latest['observation_timestamp']}")
        st.markdown(f"[Source]({latest['source_url']})")
        if latest["quality_status"] != "ok":
            st.warning(f"Latest entry: {latest['quality_status']}. See the observation register.")
        elif datetime.now(timezone.utc) - parse_timestamp(latest["observation_timestamp"]) > timedelta(hours=48):
            st.caption("⚠ Observation is older than 48 hours")

left, right = st.columns([2, 1])
with left:
    st.subheader("Observation history")
    if eligible:
        identities = sorted({(r["series"], r["instrument"], r["source"]) for r in eligible})
        chosen = st.selectbox("Series, exact contract/region and source", identities,
                              format_func=lambda x: f"{SERIES[x[0]]['label']} · {x[1]} · {x[2]}")
        history = [r for r in eligible if (r["series"], r["instrument"], r["source"]) == chosen]
        clean = [r for r in history if r["quality_status"] == "ok"]
        if clean:
            frame = pd.DataFrame(clean)
            frame["observation_timestamp"] = pd.to_datetime(frame["observation_timestamp"], utc=True)
            chart = px.scatter(frame, x="observation_timestamp", y="clean_value",
                               labels={"observation_timestamp": "Observation time (UTC)", "clean_value": SERIES[chosen[0]]["unit"]},
                               color_discrete_sequence=["#087F8C"])
            chart.update_traces(marker_size=9)
            chart.update_layout(margin=dict(l=0, r=10, t=10, b=0), height=300)
            st.plotly_chart(chart, width="stretch")
        else:
            st.info("No valid values for this series. Missing or flagged observations are retained below.")
        st.caption("Observed points only. Missing values and flagged entries are excluded; source histories are kept separate.")
        with st.expander("Observation register and lineage"):
            st.dataframe(pd.DataFrame(history), hide_index=True, width="stretch")
    else:
        st.info("Add your first sourced observation below to start a history.")
with right:
    st.subheader("Today's investigation")
    st.markdown("1. Which fact changed your view?\n2. Is it a supply, demand or timing change?\n3. What evidence would contradict your interpretation?")
    st.caption("Fixed prompts for the first version; no market signals are inferred from empty data.")
    st.page_link("views/journal.py", label="Write a morning thesis →")
    st.page_link("views/daily_learning.py", label="Open the learning pack →")

with st.expander("Add a manual observation", expanded=not rows):
    series = st.selectbox("Metric", list(SERIES), format_func=lambda k: SERIES[k]["label"], key="input_series")
    st.caption(f"Unit: {SERIES[series]['unit']}. Enter public data only. Leave a missing value blank.")
    with st.form("manual_observation"):
        instrument = st.text_input("Exact contract or geographic scope", placeholder="e.g. TTF Oct-2026 (ICE Endex), or EU aggregate")
        raw = st.text_input("Value", placeholder="Decimal point, no thousands separators")
        observed = st.text_input("Observation timestamp with timezone", value=utc_now())
        source = st.text_input("Source name")
        url = st.text_input("Public source URL")
        published = st.text_input("Publication timestamp with timezone (optional)")
        notes = st.text_area("Notes / methodology", placeholder="Scope, measurement basis, reason for a correction, or missing-data explanation")
        submitted = st.form_submit_button("Save observation", type="primary")
    if submitted:
        try:
            row = make_observation(series, instrument, raw, source, url, observed, published, notes)
        except ValueError as exc:
            st.error(str(exc))
        else:
            same = [r for r in rows if all(r.get(k) == row.get(k) for k in
                    ("series", "instrument", "source", "observation_timestamp", "raw_value", "source_url", "source_timestamp", "notes"))]
            revisions = [r for r in rows if all(r.get(k) == row.get(k) for k in ("series", "instrument", "source", "observation_timestamp"))]
            if same:
                st.warning("That exact observation is already recorded.")
            elif revisions and not notes.strip():
                st.error("Add a note explaining this revision. The original observation will be preserved.")
            elif save_row("manual_observations", row):
                st.rerun()
