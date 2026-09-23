"""Only normalized public provider data can enter the AI prompt."""
from datetime import date
from analytics.market import snapshot, seasonal_reference, net_injection, weather_window
from utils.dates import market_today


def build_context(feeds, now):
    context = {"as_of_utc": now.isoformat(), "ttf_exchange_feed": "not configured",
               "options_quotes": "not configured", "public_feeds": []}
    for source, scope, result in feeds:
        if (source, scope) not in {("GIE AGSI", "EU"), ("GIE ALSI", "EU"), ("Open-Meteo", "Paris")}:
            continue
        saved = result.get("batch")
        item = {"source": source, "scope": scope, "available": bool(saved),
                "refresh_failed": bool(result.get("error"))}
        if saved:
            rows = saved["clean_records"]
            item["retrieved_at"] = saved["retrieved_at"]
            item["source_url"] = {"GIE AGSI": "https://agsi.gie.eu/", "GIE ALSI": "https://alsi.gie.eu/",
                                  "Open-Meteo": "https://open-meteo.com/en/docs"}[source]
            # Do not send arbitrary DB raw payloads, user notes, credentials or errors.
            if source == "GIE AGSI":
                item["metrics"] = {name: {**snapshot(rows, name, as_of=market_today(now)), "unit": unit} for name, unit in
                                   [("storage_full", "%"), ("storage_energy", "TWh")]}
                item["metrics"]["net_injection"] = {**snapshot(net_injection(rows), "net_injection", as_of=market_today(now)), "unit": "GWh/d"}
                day = item["metrics"]["storage_full"]["date"]
                if day:
                    item["storage_5y_same_date"] = seasonal_reference(rows, "storage_full", date.fromisoformat(day))
            elif source == "GIE ALSI":
                item["metrics"] = {"lng_sendout": {**snapshot(rows, "lng_sendout", as_of=market_today(now)), "unit": "GWh/d"}}
            else:
                item["forecast_7d"] = weather_window(rows, market_today(now))
                item["forecast_basis"] = "Paris city forecast only; HDD base 18 C; mean C, HDD C.day; no European weighting or revision series"
        context["public_feeds"].append(item)
    return context
