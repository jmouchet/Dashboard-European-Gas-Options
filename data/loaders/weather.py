"""Open-Meteo forecast: selected locations, not an invented European weighted index."""
from datetime import date
from urllib.parse import urlencode
from .base import FeedError, batch, get_json, number

LOCATIONS = {
    "Berlin": (52.52, 13.41, "Europe/Berlin"),
    "Paris": (48.86, 2.35, "Europe/Paris"),
    "Amsterdam": (52.37, 4.90, "Europe/Amsterdam"),
    "Milan": (45.46, 9.19, "Europe/Rome"),
}


def normalize(payload, location):
    if not isinstance(payload, dict):
        raise FeedError("Weather response schema changed.")
    daily, units = payload.get("daily"), payload.get("daily_units")
    if not isinstance(daily, dict) or not isinstance(units, dict):
        raise FeedError("Weather daily data or units are missing.")
    if units.get("temperature_2m_mean") != "°C":
        raise FeedError("Weather temperature unit changed; expected degrees Celsius.")
    dates, values = daily.get("time"), daily.get("temperature_2m_mean")
    if not isinstance(dates, list) or not isinstance(values, list) or len(dates) != len(values):
        raise FeedError("Weather daily arrays are missing or misaligned.")
    if not all(isinstance(day, str) for day in dates):
        raise FeedError("Weather response contains an invalid date.")
    if len(set(dates)) != len(dates):
        raise FeedError("Weather response contains duplicate dates.")
    records = []
    for day, raw in zip(dates, values):
        try:
            date.fromisoformat(day)
        except (ValueError, TypeError):
            raise FeedError("Weather response contains an invalid date.") from None
        value = number(raw)
        quality = "missing" if value is None else "flagged" if not -60 <= value <= 60 else "ok"
        records.append({"metric": "temperature", "instrument": location, "observation_date": day,
                        "source_timestamp": None, "unit": "°C", "raw_value": raw,
                        "clean_value": value, "quality_status": quality, "source_status": "forecast",
                        "data_kind": "forecast", "source_timezone": payload.get("timezone")})
    return records


def fetch_weather(location="Berlin", session=None):
    if location not in LOCATIONS:
        raise ValueError("Unsupported location.")
    latitude, longitude, timezone = LOCATIONS[location]
    params = {
        "latitude": latitude, "longitude": longitude, "daily": "temperature_2m_mean",
        "timezone": timezone, "forecast_days": 15, "temperature_unit": "celsius",
    }
    payload = get_json("https://api.open-meteo.com/v1/forecast", params, session=session)
    records = normalize(payload, location)
    if not records:
        raise FeedError("Weather service returned no forecasts.")
    return batch("Open-Meteo", location, "https://api.open-meteo.com/v1/forecast?" + urlencode(params), payload, records)
