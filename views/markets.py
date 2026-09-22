import pandas as pd
import plotly.express as px
import streamlit as st
from components.session import page_header, read_rows
from data.validation import latest_revisions

page_header("Markets", "Price explorer · Keep exact contracts and sources separate.")
st.info("TTF futures provider not configured. Automatic futures curves, spreads and daily market returns await a price feed.")
rows = [r for r in latest_revisions(read_rows("manual_observations")) if r["series"] == "ttf"]
if rows:
    identities = sorted({(r["instrument"], r["source"]) for r in rows})
    chosen = st.selectbox("Exact contract and source", identities, format_func=lambda x: " · ".join(x))
    frame = pd.DataFrame([r for r in rows if (r["instrument"], r["source"]) == chosen])
    frame["date"] = pd.to_datetime(frame.observation_timestamp, utc=True)
    frame["value"] = frame.clean_value.where(frame.quality_status == "ok")
    dates = st.date_input("Date range (UTC)", (frame.date.min().date(), frame.date.max().date()))
    if len(dates) == 2:
        frame = frame[(frame.date.dt.date >= dates[0]) & (frame.date.dt.date <= dates[1])]
    if not frame.empty:
        fig = px.scatter(frame, x="date", y="value", labels={"date": "Observation time (UTC)", "value": "EUR/MWh"})
        fig.update_traces(marker_size=8)
        st.plotly_chart(fig, width="stretch")
    st.caption("Manually sourced points; these are not a verified sequence of daily exchange settlements. Missing/flagged revisions remain excluded.")
    st.dataframe(frame.drop(columns=["date", "value"]), hide_index=True, width="stretch")
else:
    st.write("No sourced TTF observations saved yet.")
st.page_link("views/admin.py", label="Manage manual price observations →")
