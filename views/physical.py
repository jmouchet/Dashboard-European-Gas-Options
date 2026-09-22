import pandas as pd
import streamlit as st
from components.session import page_header, read_rows, save_row
from components.market_data import load_feed, records, feed_status
from data.market_entries import make_asset

page_header("Physical System", "European gas infrastructure · GIE datasets and your sourced asset profiles.")
platform = st.radio("GIE directory", ["AGSI", "ALSI"], horizontal=True, format_func=lambda x: "Storage" if x == "AGSI" else "LNG")
result = load_feed("GIE Directory", platform, st.button("Refresh directory"))
catalog = records(result)
st.caption("Source: GIE. Entries identify operator/facility datasets, which may be storage groups or operator shares of an asset. Historical datasets are included; this is not a count of unique active physical facilities.")
if catalog:
    countries = ["All"] + sorted({r["country"] for r in catalog})
    country_filter = st.selectbox("Country", countries)
    query = st.text_input("Find a facility, operator or EIC").strip().lower()
    filtered = [r for r in catalog if (country_filter == "All" or r["country"] == country_filter) and
                (not query or query in " ".join(str(r.get(k, "")) for k in ("name", "operator", "facility_eic", "operator_eic")).lower())]
    st.write(f"{len(filtered)} datasets")
    st.dataframe(pd.DataFrame(filtered), hide_index=True, width="stretch")
feed_status(result, f"GIE {platform} directory")

st.subheader("Asset profiles")
assets = read_rows("assets")
if assets:
    chosen = st.selectbox("Asset profile", assets, format_func=lambda a: f"{a['name']} · {a['country']} · {a['operator']}")
    st.write(chosen["description"])
    st.caption(f"{chosen['asset_type']} · Operator: {chosen['operator']} · Connected market: {chosen['connected_market'] or 'unspecified'}")
    if chosen["capacity"] is not None:
        st.write(f"Capacity: {chosen['capacity']:,.2f} {chosen['capacity_unit']}")
    st.link_button("Profile source", chosen["source_url"])
    if chosen["latitude"] is not None:
        st.map(pd.DataFrame([{"lat": chosen["latitude"], "lon": chosen["longitude"]}]))
else:
    st.write("No sourced profiles added yet. The GIE directory above is available independently.")

with st.expander("Add an asset profile"):
    with st.form("asset_profile"):
        name = st.text_input("Asset name")
        asset_type = st.selectbox("Asset type", ["Storage", "LNG terminal", "Pipeline", "Interconnector", "Production field", "Processing plant", "Gas hub"])
        country = st.text_input("Asset country")
        operator = st.text_input("Operator")
        capacity = st.text_input("Capacity (optional)")
        unit = st.text_input("Capacity unit (if provided)")
        market = st.text_input("Connected market")
        description = st.text_area("Description / market importance / capacity basis")
        source = st.text_input("Public source URL")
        lat = st.text_input("Latitude (optional)")
        lon = st.text_input("Longitude (optional)")
        submitted = st.form_submit_button("Save asset profile", type="primary")
    if submitted:
        try:
            row = make_asset(name, asset_type, country, operator, capacity, unit, market, description, source, lat, lon)
        except ValueError as exc:
            st.error(str(exc))
        else:
            if save_row("assets", row):
                st.rerun()
