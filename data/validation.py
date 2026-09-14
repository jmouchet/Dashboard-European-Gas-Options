"""Manual input contract: raw text retained; blanks stay null; dates are UTC."""
from datetime import datetime, timezone
import math
from urllib.parse import urlparse
from uuid import uuid4

SERIES = {
    "ttf": {"label": "TTF futures", "unit": "EUR/MWh", "range": None},
    "storage": {"label": "EU storage fullness", "unit": "%", "range": (0, 100)},
    "norway": {"label": "Norway flows", "unit": "mcm/d", "range": (0, None)},
    "lng": {"label": "LNG send-out", "unit": "GWh/d", "range": (0, None)},
    "atm_vol": {"label": "ATM implied volatility", "unit": "volatility points", "range": (0, None)},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Use an ISO timestamp with an offset, e.g. 2026-09-13T16:00:00+02:00.") from exc
    if result.tzinfo is None:
        raise ValueError("Timestamp requires a timezone offset or Z.")
    return result.astimezone(timezone.utc)


def validate_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Supply a public http(s) source URL without credentials.")
    return value.strip()


def make_observation(series: str, instrument: str, raw_value: str, source: str,
                     source_url: str, observation_timestamp: str,
                     source_timestamp: str = "", notes: str = "") -> dict:
    if series not in SERIES:
        raise ValueError("Unknown series.")
    if not source.strip() or not instrument.strip():
        raise ValueError("Source and exact contract/region are required.")
    source_url = validate_url(source_url)
    observed = parse_timestamp(observation_timestamp)
    now = datetime.now(timezone.utc)
    if observed > now:
        raise ValueError("An observation cannot be dated in the future.")
    published = parse_timestamp(source_timestamp) if source_timestamp.strip() else None
    if published and published > now:
        raise ValueError("Publication time cannot be in the future.")
    try:
        value = float(raw_value.strip()) if raw_value.strip() else None
    except ValueError as exc:
        raise ValueError("Use a numeric value with a decimal point, or leave it blank.") from exc
    if value is not None and not math.isfinite(value):
        raise ValueError("NaN and infinity are not observations; leave missing values blank.")
    status = "missing" if value is None else "ok"
    bounds = SERIES[series]["range"]
    if value is not None and bounds:
        low, high = bounds
        if (low is not None and value < low) or (high is not None and value > high):
            status = "flagged"
    return {
        "id": str(uuid4()), "series": series, "instrument": instrument.strip(),
        "raw_value": raw_value, "clean_value": value, "unit": SERIES[series]["unit"],
        "source": source.strip(), "source_url": source_url,
        "observation_timestamp": observed.isoformat(),
        "source_timestamp": published.isoformat() if published else None,
        "source_timezone": str(datetime.fromisoformat(observation_timestamp.replace("Z", "+00:00")).tzinfo),
        "retrieved_at": now.isoformat(),
        "quality_status": status, "notes": notes.strip(),
    }


def revision_key(row: dict) -> tuple:
    return tuple(row[k] for k in ("series", "instrument", "source", "observation_timestamp"))


def latest_revisions(rows: list[dict], as_of: datetime | None = None) -> list[dict]:
    """Only information observed AND entered/published by as_of is eligible."""
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware.")
    selected = {}
    for row in rows:
        timestamps = [row["observation_timestamp"], row["retrieved_at"]]
        if row.get("source_timestamp"):
            timestamps.append(row["source_timestamp"])
        if any(parse_timestamp(t) > as_of for t in timestamps):
            continue
        key = revision_key(row)
        previous = selected.get(key)
        if previous is None or parse_timestamp(row["retrieved_at"]) > parse_timestamp(previous["retrieved_at"]):
            selected[key] = row
    return sorted(selected.values(), key=lambda row: parse_timestamp(row["observation_timestamp"]))
