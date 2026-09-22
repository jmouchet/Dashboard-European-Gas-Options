from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analytics.market import history_frame, seasonal_reference, net_injection, hdd, valid_value
from components.session import page_header
from components.market_data import load_feed, feed_status, records
from components.market_ui import metric_card, storage_comparison, history_chart
from data.loaders.gie import SCOPES, LNG_SCOPES
from data.loaders.weather import LOCATIONS
from utils.dates import market_today

page_header("Fundamentals", "Storage, LNG send-out and weather · Source data and gas-day history.")
section = st.radio("Explore", ["Storage", "LNG", "Weather"], horizontal=True)
force = st.button("Refresh this feed")

if section == "Storage":
    scope = st.selectbox("Storage region", list(SCOPES), format_func=SCOPES.get)
    result = load_feed("GIE AGSI", scope, force)
    rows = records(result)
    for col, metric, label, unit in zip(st.columns(3), ["storage_full", "storage_energy", "storage_capacity"],
                                      ["Storage fullness", "Stored energy", "Working gas capacity"], ["%", "TWh", "TWh"]):
        with col:
            metric_card(rows, metric, label, unit, "pp" if unit == "%" else unit)
    storage_comparison(rows)
    frame = history_frame(rows, "storage_full")
    if not frame.empty:
        year = st.selectbox("Seasonal year", sorted(set(frame.date.dt.year), reverse=True))
        current = frame[frame.date.dt.year == year].copy()
        refs = [seasonal_reference(rows, "storage_full", d.date()) for d in current.date]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=current.date, y=[r["max"] for r in refs], name="5Y maximum", line=dict(width=0)))
        fig.add_trace(go.Scatter(x=current.date, y=[r["min"] for r in refs], name="5Y minimum", fill="tonexty", line=dict(width=0)))
        fig.add_trace(go.Scatter(x=current.date, y=[r["mean"] for r in refs], name="5Y mean", line=dict(dash="dot")))
        fig.add_trace(go.Scatter(x=current.date, y=current.value, name=str(year), line=dict(color="#087F8C", width=3)))
        fig.update_traces(connectgaps=False)
        fig.update_layout(title="Storage fullness · Same-date seasonal comparison", yaxis_title="%", height=370, margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, width="stretch")
        st.caption("Band and mean require all five preceding calendar years at each date. Earlier selected years may lack sufficient history. Revised history is not an as-published backtest.")
    days = st.selectbox("Flow history", [30, 90, 365], index=1, format_func=lambda d: f"Last {d} days")
    history_chart(net_injection(rows), "net_injection", "GWh/d", "Net storage injection", market_today() - timedelta(days=days))
    st.caption("Net injection is derived from reported injection minus withdrawal; it is not the full European supply-demand balance.")

elif section == "LNG":
    scope = st.selectbox("LNG region", list(LNG_SCOPES), format_func=LNG_SCOPES.get)
    result = load_feed("GIE ALSI", scope, force)
    rows = records(result)
    left, right = st.columns(2)
    with left:
        metric_card(rows, "lng_sendout", "LNG send-out", "GWh/d")
    with right:
        metric_card(rows, "lng_sendout_capacity", "Technical send-out capacity", "GWh/d")
    history_chart(rows, "lng_sendout", "GWh/d", "LNG send-out · GIE ALSI")
    st.caption("Send-out measures gas delivered from LNG terminals. It does not measure cargo arrivals or liquefaction output.")

else:
    scope = st.selectbox("Forecast location", list(LOCATIONS), index=1)
    result = load_feed("Open-Meteo", scope, force)
    rows = records(result)
    history_chart(rows, "temperature", "°C", "Daily mean temperature · Current forecast")
    if rows:
        st.dataframe(pd.DataFrame([{"Forecast date": r["observation_date"], "Mean temperature (°C)": valid_value(r),
                                    "HDD (18°C base)": hdd(valid_value(r)), "Quality": r["quality_status"]} for r in rows]), hide_index=True)
    st.caption("Open-Meteo · 15 forecast days in the selected city's timezone. Retrieval time identifies the stored vintage; no model issue timestamp is supplied. Historical forecast revisions and temperature anomalies are not yet calculated.")

feed_status(result, f"{section} · {scope}")
with st.expander("Normalized source records"):
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
st.caption("Norwegian/pipeline supply, power demand and a complete balance model await additional verified feeds.")
