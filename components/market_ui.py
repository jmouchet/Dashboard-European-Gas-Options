"""Compact views of normalized data; provider JSON stays inside connectors."""
from datetime import date
import plotly.express as px
import streamlit as st
from analytics.market import snapshot, history_frame, seasonal_reference
from utils.dates import market_today


def metric_card(rows, metric, label, unit, delta_unit=None):
    value = snapshot(rows, metric)
    delta = f"{value['delta']:+,.2f} {delta_unit or unit}" if value["delta"] is not None else None
    st.metric(label, f"{value['value']:,.2f}" if value["value"] is not None else "—", delta, delta_color="off")
    st.caption(f"{unit} · Gas day {value['date'] or 'unavailable'}")
    if value["date"]:
        if value["delta"] is not None:
            st.caption(f"Change vs {value['previous_date']}")
        else:
            st.caption("Daily comparison unavailable")
        if value.get("source_status") == "E":
            st.caption("Estimated by GIE")
        if value["status"] != "ok":
            st.caption(f"Latest value: {value['status']}")
        age = (market_today() - date.fromisoformat(value["date"])).days
        if age > 2:
            st.warning(f"Latest gas day is {age} days old.")
    return value


def history_chart(rows, metric, unit, title, start=None):
    frame = history_frame(rows, metric)
    if start is not None and not frame.empty:
        frame = frame[frame["date"].dt.date >= start]
    if frame.empty:
        st.info(f"{title}: data unavailable.")
        return
    chart = px.line(frame, x="date", y="value", title=title,
                    labels={"date": "Gas day / forecast date", "value": unit}, color_discrete_sequence=["#087F8C"])
    chart.update_traces(connectgaps=False)
    chart.update_layout(height=320, margin=dict(l=0, r=10, t=45, b=0))
    st.plotly_chart(chart, width="stretch")


def storage_comparison(rows):
    latest = snapshot(rows, "storage_full")
    if not latest["date"]:
        st.info("Seasonal storage comparison awaits GIE history.")
        return
    day = date.fromisoformat(latest["date"])
    reference = seasonal_reference(rows, "storage_full", day)
    previous = seasonal_reference(rows, "storage_full", day, years=1)
    for col, label, result in zip(st.columns(2), ["vs 5-year mean", "vs previous year"], [reference, previous]):
        with col:
            delta = latest["value"] - result["mean"] if latest["value"] is not None and result["mean"] is not None else None
            st.metric(label, f"{delta:+.2f} pp" if delta is not None else "—")
    st.caption(f"Same calendar date as gas day {day}. Five-year mean requires all 5 prior years; {reference['years_available']}/5 available. Uses today's retrieved history, including provider revisions and coverage changes.")
