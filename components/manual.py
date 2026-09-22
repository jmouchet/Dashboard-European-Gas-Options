import streamlit as st
from components.session import read_rows, save_row
from data.validation import SERIES, make_observation, utc_now


def observation_form():
    rows = read_rows("manual_observations")
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
