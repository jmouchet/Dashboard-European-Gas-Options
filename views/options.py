from datetime import timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from components.session import page_header, read_rows, save_row
from data.market_entries import make_mark
from utils.dates import market_today

page_header("Options & Volatility", "Sourced option marks · Exact underlying, expiry and quote convention.")
st.info("No options provider is connected. You can build a history from publicly sourced manual marks below.")
st.caption("All volatility inputs are in volatility points: enter 50 for 50% annualized volatility. Record the delta, premium adjustment, ATM definition, and RR/BF sign conventions used by the source.")
rows = read_rows("option_marks")
if rows:
    identities = sorted({(r["underlying"], r["expiry"], r["convention"], r["source_url"]) for r in rows})
    chosen = st.selectbox("Underlying · Expiry · Convention · Source", identities, format_func=lambda x: " · ".join(x))
    selected = [r for r in rows if (r["underlying"], r["expiry"], r["convention"], r["source_url"]) == chosen]
    frame = pd.DataFrame(selected).sort_values(["observation_date", "created_at"] if "created_at" in selected[0] else ["observation_date"])
    frame = frame.drop_duplicates("observation_date", keep="last")
    metric = st.selectbox("Volatility measure", ["atm_vol", "risk_reversal", "butterfly"], format_func=lambda k: {"atm_vol": "ATM", "risk_reversal": "25D risk reversal", "butterfly": "25D butterfly"}[k])
    latest = frame.iloc[-1]
    st.metric("Latest mark", f"{latest[metric]:.2f} vol pts" if pd.notna(latest[metric]) else "—")
    st.caption(f"Observation {latest['observation_date']} · Expiry {latest['expiry']}. Latest saved revision per date is shown; original records remain in Data / Admin.")
    fig = px.scatter(frame, x="observation_date", y=metric, labels={"observation_date": "Observation date", metric: "Volatility points"})
    st.plotly_chart(fig, width="stretch")
    st.dataframe(frame[["observation_date", "atm_vol", "risk_reversal", "butterfly", "notes"]], hide_index=True)
else:
    st.write("No option marks recorded yet.")

with st.expander("Add a sourced option mark", expanded=not rows):
    with st.form("option_mark"):
        observed = st.date_input("Observation date", market_today(), max_value=market_today())
        underlying = st.text_input("Exact underlying", placeholder="TTF Oct-2026 futures · Exchange")
        expiry = st.date_input("Option expiry", market_today() + timedelta(days=30))
        a, b, c = st.columns(3)
        atm = a.text_input("ATM (vol pts)")
        rr = b.text_input("25D risk reversal (vol pts)")
        bf = c.text_input("25D butterfly (vol pts)")
        convention = st.text_input("Quote and delta convention", placeholder="Source's ATM / delta / premium / RR and BF definitions")
        source = st.text_input("Public source URL")
        notes = st.text_area("Notes / mark revision")
        submitted = st.form_submit_button("Save option mark", type="primary")
    if submitted:
        try:
            row = make_mark(observed, underlying, expiry, atm, rr, bf, convention, source, notes)
            revisions = [r for r in rows if all(r[k] == row[k] for k in ("observation_date", "underlying", "expiry", "convention", "source_url"))]
            if revisions and not notes.strip():
                raise ValueError("Add a note explaining the revised mark; earlier marks will be preserved.")
        except ValueError as exc:
            st.error(str(exc))
        else:
            if save_row("option_marks", row):
                st.rerun()
st.caption("Realized volatility and implied/realized comparisons await a verified sequence of fixed-contract daily settlements.")
