from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st
from analytics.market import snapshot, net_injection, seasonal_reference, weather_window
from components.market_data import load_feed, feed_status, records
from components.morning_charts import STYLE, BLUE, AMBER, TEAL, PURPLE, card_html, spark_figure, storage_figure, flow_figure, weather_figure
from components.brief import render_brief
from utils.dates import market_today

st.html(STYLE)


@st.fragment(run_every="30m")
def morning():
    today = market_today()
    now = datetime.now(ZoneInfo("Europe/Paris"))
    st.html(f'<div class="morning-hero"><div class="eyebrow">MARKET DASHBOARD · EUROPEAN GAS</div><h2>Morning — le marché en un regard</h2><p>{now:%d.%m.%Y · %H:%M} Paris · Les variations, leur contexte et les risques pour le TTF.</p></div>')
    controls = st.columns([3, 1])
    controls[0].caption("Données GIE + météo Paris · Actualisation automatique pendant la consultation")
    force = controls[1].button("Actualiser les données", width="stretch")
    storage = load_feed("GIE AGSI", "EU", force)
    lng = load_feed("GIE ALSI", "EU", force)
    weather = load_feed("Open-Meteo", "Paris", force)
    gas_rows, lng_rows, weather_rows = records(storage), records(lng), records(weather)
    net_rows = net_injection(gas_rows)
    feeds = [("GIE AGSI", "EU", storage), ("GIE ALSI", "EU", lng), ("Open-Meteo", "Paris", weather)]

    if not st.session_state.get("db_user"):
        st.info("Connecte-toi dans la barre latérale pour charger les données et lire le brief.")
    else:
        for source, scope, result in feeds:
            if result.get("error"):
                st.warning(f"{source} : {result['error']} Dernier instantané conservé s'il est disponible.")

    cards = [(gas_rows, "storage_full", "Stockage UE", "%", "pp", BLUE),
             (gas_rows, "storage_energy", "Gaz en stock", "TWh", "TWh", TEAL),
             (net_rows, "net_injection", "Injection nette UE", "GWh/j", "GWh/j", PURPLE),
             (lng_rows, "lng_sendout", "Émission LNG UE", "GWh/j", "GWh/j", AMBER)]
    latest_storage = snapshot(gas_rows, "storage_full")
    for col, (rows, metric, label, unit, delta_unit, accent) in zip(st.columns(4), cards):
        value = snapshot(rows, metric)
        meta = f"Gas day {value['date']}" if value["date"] else "En attente de données"
        if value.get("previous_date"):
            meta += f" · Comparé au {value['previous_date']}"
        if value.get("source_status") == "E":
            meta += " · Estimation GIE"
        if value["status"] != "ok" and value["date"]:
            meta += " · Valeur manquante ou signalée"
        if value["date"] and (today - date.fromisoformat(value["date"])).days > 2:
            meta += f" · Attention : {(today - date.fromisoformat(value['date'])).days} jours de retard"
        with col:
            st.html(card_html(label, value["value"], unit, value["delta"], delta_unit, meta, accent))
            if rows:
                st.plotly_chart(spark_figure(rows, metric, accent, bars=metric == "net_injection"),
                                width="stretch", config={"displayModeBar": False}, key=f"spark_{metric}")
                st.caption("30 derniers gas days disponibles · " + unit)
    st.caption("↑ Bleu : hausse · ↓ Ambre : baisse. Ces couleurs décrivent la donnée physique, pas une prévision de prix. Source : GIE AGSI / ALSI.")
    st.html('<div class="morning-note"><strong>TTF :</strong> flux de prix non connecté. Le brief distingue les prix cités dans la presse des cotations de marché en direct.</div>')

    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.subheader("Stockage · Où en est-on ?")
        if gas_rows:
            st.plotly_chart(storage_figure(gas_rows), width="stretch", key="morning_seasonality")
            day = date.fromisoformat(latest_storage["date"])
            ref = seasonal_reference(gas_rows, "storage_full", day)
            last_year = seasonal_reference(gas_rows, "storage_full", day, years=1)
            for col, label, comparison in zip(st.columns(2), ["Écart à la moyenne 5 ans", "Écart à l'an dernier"], [ref, last_year]):
                delta = latest_storage["value"] - comparison["mean"] if latest_storage["value"] is not None and comparison["mean"] is not None else None
                col.metric(label, "—" if delta is None else f"{delta:+.2f} pp")
            st.caption(f"Même date calendaire · {ref['years_available']}/5 années valides. Historique révisé par GIE ; couverture susceptible d'évoluer.")
        else:
            st.info("La courbe de stockage et sa fourchette saisonnière apparaîtront après le chargement de GIE.")
    with right:
        with st.container(border=True):
            render_brief(feeds)

    st.divider()
    flow, outlook = st.columns(2, gap="large")
    with flow:
        st.subheader("LNG · Rythme des émissions")
        if lng_rows:
            st.plotly_chart(flow_figure(lng_rows, "lng_sendout", "Émission LNG", TEAL), width="stretch", key="morning_lng")
        else:
            st.info("Historique LNG indisponible.")
        st.caption("45 derniers gas days disponibles · Gaz émis vers le réseau, distinct des arrivées de cargaisons. Source : GIE ALSI.")
    with outlook:
        st.subheader("Météo · Pression sur le chauffage")
        forecast = weather_window(weather_rows, today)
        a, b = st.columns(2)
        a.metric("Paris · Moyenne 7 jours", "—" if forecast["mean"] is None else f"{forecast['mean']:.1f} °C")
        b.metric("Paris · HDD 7 jours", "—" if forecast["hdd"] is None else f"{forecast['hdd']:.1f} °C·j")
        if weather_rows:
            st.plotly_chart(weather_figure(weather_rows), width="stretch", key="morning_weather")
        st.caption(f"Prévision Open-Meteo · {today} → {today + timedelta(days=6)} : {forecast['available']}/7 jours. HDD base 18°C. Paris est un indicateur local, sans pondération de la demande européenne.")

    with st.expander("Fraîcheur, sources et qualité des données"):
        st.caption("GIE : contrôle toutes les 6 h ; météo : toutes les heures. Après activation dans GitHub, le brief est programmé à 6 h Paris et conservé dans Supabase.")
        for source, scope, result in feeds:
            feed_status(result, f"{source} · {scope}")
    st.page_link("views/fundamentals.py", label="Explorer les fondamentaux par pays →")


morning()
