from datetime import timedelta
from uuid import uuid4
import streamlit as st
from components.session import page_header, read_rows, save_row
from data.validation import utc_now
from utils.dates import market_today

page_header("Journal", "Separate facts, interpretation and falsifiable hypotheses. Public information and personal study notes only.")
entries = read_rows("journal_entries")
predictions = read_rows("predictions")
write_tab, predictions_tab, history_tab = st.tabs(["Daily journal", "Predictions", "Past entries"])
with write_tab:
    kind = st.radio("Entry type", ["Morning thesis", "Evening review"], horizontal=True)
    fields = (["Observed facts and sources", "Market regime", "Bull / base / bear scenarios", "Important variables", "Expected volatility and skew", "Main risk", "Confidence and reasoning"]
              if kind == "Morning thesis" else
              ["What happened?", "What surprised me?", "What did I misunderstand?", "What did I predict correctly?", "What would I watch next time?", "What should I add to the Wiki?"])
    with st.form("journal_" + kind):
        entry_date = st.date_input("Journal date", value=market_today(), max_value=market_today())
        sections = {field: st.text_area(field, key=f"journal_{kind}_{field}") for field in fields}
        submit = st.form_submit_button("Save journal entry", type="primary")
    if submit:
        if not any(v.strip() for v in sections.values()):
            st.error("Write at least one section before saving.")
        elif save_row("journal_entries", {"id": str(uuid4()), "entry_date": entry_date.isoformat(),
                                         "entry_type": kind, "sections": sections, "created_at": utc_now()}):
            st.rerun()
    st.caption("Entries are appended. Add a new entry for a correction; the original remains in history.")
with predictions_tab:
    with st.form("prediction"):
        prediction = st.text_area("Falsifiable prediction")
        horizon = st.date_input("Evaluate by", value=market_today() + timedelta(days=7), min_value=market_today())
        confidence = st.select_slider("Confidence", options=[1, 2, 3, 4], value=2)
        reasoning = st.text_area("Reasoning / public evidence")
        outcome = st.text_area("Measurable expected outcome and invalidation condition")
        submit = st.form_submit_button("Record prediction", type="primary")
    if submit:
        if not all(v.strip() for v in [prediction, reasoning, outcome]):
            st.error("Prediction, reasoning and expected outcome are required.")
        elif save_row("predictions", {"id": str(uuid4()), "prediction_date": market_today().isoformat(),
                                      "prediction": prediction.strip(), "horizon": horizon.isoformat(),
                                      "confidence": confidence, "reasoning": reasoning.strip(),
                                      "expected_outcome": outcome.strip(), "created_at": utc_now()}):
            st.rerun()
    st.caption("Predictions are immutable. Record the result and post-mortem in a new evening review, referring to the prediction ID.")
    for p in sorted(predictions, key=lambda p: p["created_at"], reverse=True):
        with st.expander(f"{p['prediction_date']} → {p['horizon']} · {p['prediction'][:80]}"):
            st.write(p["prediction"])
            st.write(p["reasoning"])
            st.write(p["expected_outcome"])
            st.caption(f"Confidence {p['confidence']}/4 · ID {p['id']} · Recorded {p['created_at']}")
with history_tab:
    if not entries:
        st.info("No journal entries yet.")
    for entry in sorted(entries, key=lambda e: (e["entry_date"], e["created_at"]), reverse=True):
        with st.expander(f"{entry['entry_date']} · {entry['entry_type']} · {entry['created_at']}"):
            for label, value in entry["sections"].items():
                if value.strip():
                    st.markdown(f"**{label}**")
                    st.write(value)
