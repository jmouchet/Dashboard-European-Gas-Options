import pandas as pd
import streamlit as st
from components.session import page_header, read_rows, save_row
from components.market_data import load_feed, records, feed_status
from data.market_entries import make_event
from data.validation import utc_now

page_header("Events", "Source announcements and a structured record of market events.")
st.subheader("GIE service announcements")
result = load_feed("GIE Announcements", "AGSI", st.button("Refresh announcements"))
st.caption("GIE data and service notices, including reporting changes. These are not a verified outage feed. Displays the latest 20 returned notices; the API currently ignores the requested page size. Source notice times have no supplied timezone.")
for item in sorted(records(result), key=lambda r: r["timestamp"], reverse=True)[:20]:
    with st.expander(f"{item['timestamp']} · {item['headline']}"):
        st.text(item["description"])
        if item["details"]:
            st.text(item["details"])
        st.link_button("GIE announcement platform", "https://agsi.gie.eu/")
        st.caption(f"Source API reference: {item['source_url']}")
feed_status(result, "GIE announcements")

st.subheader("Market event log")
rows = read_rows("market_events")
if rows:
    category = st.selectbox("Filter category", ["All"] + sorted({r["category"] for r in rows}))
    chosen = sorted([r for r in rows if category == "All" or r["category"] == category], key=lambda r: r["timestamp"], reverse=True)
    for row in chosen:
        with st.expander(f"{row['timestamp']} · {row['headline']}"):
            st.write(row["description"])
            st.caption(f"{row['category']} · {row['entity']} · Confidence {row['confidence']}/4")
            if row["physical_impact"] is not None:
                st.write(f"Estimated physical impact: {row['physical_impact']:,.2f} {row['impact_unit']}")
            st.write(f"Expected duration: {row['expected_duration'] or 'unspecified'} · Affected tenors: {row['affected_tenors'] or 'unspecified'}")
            if row["interpretation"]:
                st.markdown("**Your interpretation**")
                st.write(row["interpretation"])
            st.link_button("Event source", row["source_url"])
else:
    st.write("No structured events saved yet.")

with st.expander("Record a market event"):
    with st.form("market_event"):
        timestamp = st.text_input("Reported timestamp with timezone", utc_now())
        category = st.selectbox("Event category", ["Norway outage", "LNG", "Pipeline", "Storage", "Weather", "Geopolitics", "Sanctions", "Regulation", "Power", "Nuclear", "Industrial demand", "Shipping", "Macro"])
        entity = st.text_input("Affected entity")
        headline = st.text_input("Headline")
        description = st.text_area("Sourced facts")
        source = st.text_input("Public source URL")
        impact = st.text_input("Estimated physical impact (optional)")
        unit = st.text_input("Impact unit (if provided)")
        duration = st.text_input("Expected duration")
        tenors = st.text_input("Affected tenors")
        confidence = st.select_slider("Confidence", [1, 2, 3, 4], value=2)
        interpretation = st.text_area("Your interpretation / sign of physical impact")
        submitted = st.form_submit_button("Save market event", type="primary")
    if submitted:
        try:
            row = make_event(timestamp, category, entity, headline, description, source, impact, unit, duration, tenors, confidence, interpretation)
        except ValueError as exc:
            st.error(str(exc))
        else:
            if save_row("market_events", row):
                st.rerun()
st.caption("Price and volatility reactions are not estimated until a corresponding market-data provider is connected.")
