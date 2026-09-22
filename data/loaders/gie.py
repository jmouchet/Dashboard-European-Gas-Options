"""AGSI and ALSI, GIE API manual v007: header auth, explicit scope, paging.

Gas-day labels remain dates: the API does not supply publication timestamps.
Storage is end-of-gas-day inventory in TWh; injection/withdrawal are GWh/d.
"""
from datetime import date, timedelta
import time
from urllib.parse import urlencode
from .base import FeedError, batch, get_json, number
from utils.dates import market_today

SOURCE_URL = "https://agsi.gie.eu/api"
FIELDS = {
    "full": ("storage_full", "%"),
    "gasInStorage": ("storage_energy", "TWh"),
    "workingGasVolume": ("storage_capacity", "TWh"),
    "injection": ("storage_injection", "GWh/d"),
    "withdrawal": ("storage_withdrawal", "GWh/d"),
}
SCOPES = {"EU": "EU aggregate", "DE": "Germany", "FR": "France", "IT": "Italy", "NL": "Netherlands", "AT": "Austria"}
LNG_SCOPES = {k: v for k, v in SCOPES.items() if k != "AT"}
LNG_FIELDS = {"sendOut": ("lng_sendout", "GWh/d"), "dtrs": ("lng_sendout_capacity", "GWh/d")}


def normalize(pages, scope, fields=None):
    fields = FIELDS if fields is None else fields
    records, notes, dates = [], [], set()
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("data"), list):
            raise FeedError("GIE response schema changed: expected a data array.")
        for raw in page["data"]:
            if not isinstance(raw, dict) or "gasDayStart" not in raw or "code" not in raw:
                raise FeedError("GIE response is missing its gas-day or scope identifier.")
            if str(raw["code"]).upper() != scope:
                raise FeedError("GIE returned a different scope; aggregation has been stopped.")
            try:
                day = date.fromisoformat(raw["gasDayStart"])
            except (ValueError, TypeError):
                raise FeedError("GIE returned an invalid gas-day date.") from None
            if day in dates:
                raise FeedError("GIE returned duplicate gas days. The batch was not accepted.")
            dates.add(day)
            status = raw.get("status")
            for field, (metric, unit) in fields.items():
                value = number(raw.get(field))
                quality = "ok"
                if field not in raw:
                    notes.append(f"{day}: missing field {field}")
                if value is None or status == "N":
                    quality = "missing"
                    value = None
                elif not isinstance(status, str) or status not in {"C", "E"} or value < 0 or (field == "full" and value > 100):
                    quality = "flagged"
                records.append({"metric": metric, "instrument": scope, "observation_date": day.isoformat(),
                                "source_timestamp": raw.get("updatedAt"), "source_timezone": None,
                                "unit": unit, "raw_value": raw.get(field),
                                "clean_value": value, "quality_status": quality, "source_status": status,
                                "data_kind": "gas_day"})
    ordered = sorted(dates)
    for left, right in zip(ordered, ordered[1:]):
        if (right - left).days > 1:
            notes.append(f"Missing gas days between {left} and {right}")
    fills = sorted((r for r in records if r["metric"] == "storage_full" and r["quality_status"] == "ok"), key=lambda r: r["observation_date"])
    for left, right in zip(fills, fills[1:]):
        if (date.fromisoformat(right["observation_date"]) - date.fromisoformat(left["observation_date"])).days == 1 and abs(right["clean_value"] - left["clean_value"]) > 5:
            notes.append(f"Large fullness change at {right['observation_date']}; inspect source and reporting coverage")
            right["quality_status"] = "flagged"
    return records, sorted(set(notes))


def fetch_storage(api_key, scope="EU", start=None, end=None, session=None):
    return fetch_series(api_key, scope, start, end, session, "GIE AGSI", SOURCE_URL, FIELDS, SCOPES)


def fetch_lng(api_key, scope="EU", start=None, end=None, session=None):
    end = end or market_today() - timedelta(days=1)
    start = start or end - timedelta(days=365)
    return fetch_series(api_key, scope, start, end, session, "GIE ALSI", "https://alsi.gie.eu/api", LNG_FIELDS, LNG_SCOPES)


def fetch_series(api_key, scope, start, end, session, source, endpoint, fields, scopes):
    if not api_key:
        raise FeedError("GIE API key is not configured. Add GIE_API_KEY in local secrets.")
    if scope not in scopes:
        raise ValueError("Unsupported GIE scope.")
    end = end or market_today() - timedelta(days=1)
    start = start or date(end.year - 5, 1, 1)
    if start > end:
        raise ValueError("Start must not follow end.")
    params = {"type": "eu"} if scope == "EU" else {"country": scope.lower()}
    params.update({"from": start.isoformat(), "to": end.isoformat(), "size": 300})
    pages, last_page = [], 1
    for page_number in range(1, 31):
        if page_number > 1:
            time.sleep(1.1)
        payload = get_json(endpoint, {**params, "page": page_number}, {"x-key": api_key}, session)
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise FeedError("GIE response schema changed or API access was denied.")
        try:
            if isinstance(payload["last_page"], bool) or not str(payload["last_page"]).isdigit():
                raise ValueError("Non-integer page count")
            current_last = int(payload["last_page"])
        except (KeyError, TypeError, ValueError):
            raise FeedError("GIE pagination metadata is missing or invalid.") from None
        if current_last < 1 or current_last > 30:
            raise FeedError("Unexpected GIE page count; reduce the requested date range.")
        if page_number == 1:
            last_page = current_last
        elif last_page != current_last:
            raise FeedError("GIE pagination changed during retrieval; retry the batch.")
        pages.append(payload)
        if page_number == last_page:
            break
    records, notes = normalize(pages, scope, fields)
    if not records:
        raise FeedError("GIE returned no observations for the requested dates.")
    if any(not start.isoformat() <= r["observation_date"] <= end.isoformat() for r in records):
        raise FeedError("GIE returned observations outside the requested date range.")
    return batch(source, scope, endpoint + "?" + urlencode(params), pages, records, notes)
