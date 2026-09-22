"""Validation for sourced manual asset profiles, option marks and event records."""
from datetime import datetime, timezone
import math
from uuid import uuid4
from data.validation import validate_url, parse_timestamp
from utils.dates import market_today


def numeric(raw, label, minimum=None, maximum=None):
    if raw is None or str(raw).strip() == "":
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(f"{label}: enter a number or leave blank.") from None
    if not math.isfinite(value) or (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        raise ValueError(f"{label}: value is outside the permitted range.")
    return value


def required(value, label):
    if not value.strip():
        raise ValueError(f"{label} is required.")
    return value.strip()


def make_mark(observation_date, underlying, expiry, atm_vol, risk_reversal, butterfly, convention, source_url, notes=""):
    if observation_date > market_today() or expiry < observation_date:
        raise ValueError("Observation date cannot be in the future; expiry must be on or after it.")
    values = {"atm_vol": numeric(atm_vol, "ATM volatility", 0),
              "risk_reversal": numeric(risk_reversal, "Risk reversal"),
              "butterfly": numeric(butterfly, "Butterfly")}
    if all(value is None for value in values.values()):
        raise ValueError("Enter at least one volatility mark.")
    return {"id": str(uuid4()), "observation_date": observation_date.isoformat(),
            "underlying": required(underlying, "Exact underlying"), "expiry": expiry.isoformat(), **values,
            "convention": required(convention, "Quote and delta convention"), "source_url": validate_url(source_url), "notes": notes.strip()}


def make_asset(name, asset_type, country, operator, capacity, capacity_unit, connected_market,
               description, source_url, latitude="", longitude=""):
    cap = numeric(capacity, "Capacity", 0)
    lat, lon = numeric(latitude, "Latitude", -90, 90), numeric(longitude, "Longitude", -180, 180)
    if (lat is None) != (lon is None):
        raise ValueError("Supply both coordinates, or leave both blank.")
    if (cap is None) != (not capacity_unit.strip()):
        raise ValueError("Supply capacity and its unit together, or leave both blank.")
    return {"id": str(uuid4()), "name": required(name, "Asset name"), "asset_type": required(asset_type, "Asset type"),
            "country": required(country, "Country"), "operator": required(operator, "Operator"),
            "capacity": cap, "capacity_unit": capacity_unit.strip() or None,
            "connected_market": connected_market.strip(), "description": description.strip(),
            "source_url": validate_url(source_url), "latitude": lat, "longitude": lon}


def make_event(timestamp, category, entity, headline, description, source_url, physical_impact,
               impact_unit, expected_duration, affected_tenors, confidence, interpretation):
    stamp = parse_timestamp(timestamp)
    if stamp > datetime.now(timezone.utc):
        raise ValueError("Use the time the event was reported, not a future event date.")
    impact = numeric(physical_impact, "Physical impact")
    if (impact is None) != (not impact_unit.strip()):
        raise ValueError("Supply physical impact and its unit together, or leave both blank.")
    if confidence not in (1, 2, 3, 4):
        raise ValueError("Confidence must be 1–4.")
    return {"id": str(uuid4()), "timestamp": stamp.isoformat(), "category": required(category, "Category"),
            "entity": required(entity, "Entity"), "headline": required(headline, "Headline"),
            "description": required(description, "Sourced facts"), "source_url": validate_url(source_url),
            "physical_impact": impact, "impact_unit": impact_unit.strip() or None,
            "expected_duration": expected_duration.strip(), "affected_tenors": affected_tenors.strip(),
            "confidence": confidence, "interpretation": interpretation.strip()}
