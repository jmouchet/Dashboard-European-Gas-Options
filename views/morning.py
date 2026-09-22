from datetime import timedelta
import streamlit as st
from analytics.market import net_injection, weather_window
from components.session import page_header
from components.market_data import load_feed, feed_status, records
from components.market_ui import metric_card, storage_comparison
from data.loaders.weather import LOCATIONS
from utils.dates import market_today

page_header("Morning", "Market Dashboard · The latest gas balance and what changed since the previous gas day.")


@st.fragment(run_every="30m")
def morning():
    controls = st.columns([2, 1])
    location = controls[0].selectbox("Weather location", list(LOCATIONS), index=1)
    force = controls[1].button("Refresh market data", width="stretch")
    st.caption("Updates on opening and while this page remains active. GIE: every 6 hours; weather: hourly. The refresh button checks now.")
    storage = load_feed("GIE AGSI", "EU", force)
    lng = load_feed("GIE ALSI", "EU", force)
    weather = load_feed("Open-Meteo", location, force)
    gas_rows, lng_rows = records(storage), records(lng)

    st.subheader("European gas balance")
    for col, args in zip(st.columns(4), [
        (gas_rows, "storage_full", "EU storage", "%", "pp"),
        (gas_rows, "storage_energy", "Gas in storage", "TWh"),
        (net_injection(gas_rows), "net_injection", "Net injection", "GWh/d"),
        (lng_rows, "lng_sendout", "EU LNG send-out", "GWh/d"),
    ]):
        with col:
            metric_card(*args)
    st.caption("Sources: GIE AGSI (storage) and GIE ALSI (LNG). Positive net injection = injection minus withdrawal. Deltas require the immediately preceding gas day.")
    storage_comparison(gas_rows)

    st.subheader(f"Weather outlook · {location}")
    today = market_today()
    forecast = weather_window(records(weather), today)
    left, right = st.columns(2)
    left.metric("Next 7 days · Mean temperature", f"{forecast['mean']:.1f} °C" if forecast["mean"] is not None else "—")
    right.metric("Next 7 days · Heating degree days", f"{forecast['hdd']:.1f} °C·day" if forecast["hdd"] is not None else "—")
    st.caption(f"{today} to {today + timedelta(days=6)} · {forecast['available']}/7 days available. HDD = sum of max(18°C − daily mean temperature, 0). This is a city forecast, with no European demand weighting or forecast-revision estimate.")

    st.subheader("Prices & volatility")
    st.info("TTF futures and options: provider not configured. Live prices, calendar spreads and volatility changes are unavailable.")
    left, right = st.columns(2)
    left.page_link("views/markets.py", label="Markets →")
    right.page_link("views/options.py", label="Options & Volatility →")

    st.subheader("Feed status")
    feed_status(storage, "GIE AGSI · EU")
    feed_status(lng, "GIE ALSI · EU")
    feed_status(weather, f"Open-Meteo · {location}")


morning()
