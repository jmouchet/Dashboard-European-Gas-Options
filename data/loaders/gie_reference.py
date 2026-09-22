"""GIE v007 dataset directory and service announcements, separate from outages."""
from html.parser import HTMLParser
from datetime import datetime
from urllib.parse import urlencode
from .base import FeedError, batch, get_json


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(value):
    parser = PlainText()
    parser.feed(str(value or ""))
    return " ".join(" ".join(parser.parts).split())


def normalize_catalog(payload):
    if not isinstance(payload, list):
        raise FeedError("GIE directory schema changed; expected an operator list.")
    rows, seen = [], set()
    for operator in payload:
        if not isinstance(operator, dict) or not isinstance(operator.get("facilities"), list):
            raise FeedError("GIE directory is missing its facility list.")
        for facility in operator["facilities"]:
            if not isinstance(facility, dict) or not all(facility.get(k) for k in ("name", "eic", "country")) or not operator.get("eic"):
                raise FeedError("GIE directory is missing dataset identifiers.")
            # GIE retains pre/post-Brexit datasets under GB and GB* with the
            # same EIC pair. Country and operational dates distinguish vintages.
            identity = (operator["eic"], facility["eic"], facility["country"],
                        facility.get("operational_start_date"), facility.get("operational_end_date"))
            if identity in seen:
                raise FeedError("GIE directory contains duplicate dataset identifiers.")
            seen.add(identity)
            rows.append({"name": facility["name"], "country": facility["country"],
                         "asset_type": facility.get("type"), "operator": operator.get("name"),
                         "operator_eic": operator["eic"], "facility_eic": facility["eic"],
                         "operational_start_date": facility.get("operational_start_date"),
                         "operational_end_date": facility.get("operational_end_date"),
                         "data_kind": "dataset_directory"})
    if not rows:
        raise FeedError("GIE directory returned no datasets.")
    return rows


def fetch_catalog(api_key, platform="AGSI", session=None):
    if platform not in {"AGSI", "ALSI"}:
        raise ValueError("Unsupported directory.")
    if not api_key:
        raise FeedError("GIE API key is not configured.")
    url = f"https://{platform.lower()}.gie.eu/api/about"
    payload = get_json(url, {"show": "listing"}, {"x-key": api_key}, session)
    return batch("GIE Directory", platform, url + "?show=listing", payload, normalize_catalog(payload))


def normalize_news(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise FeedError("GIE announcements schema changed.")
    rows, seen = [], set()
    for item in payload["data"]:
        if not isinstance(item, dict) or not all(item.get(k) is not None for k in ("url", "title", "start_at")):
            raise FeedError("GIE announcement is missing its identifier, title or date.")
        identifier = str(item["url"])
        try:
            datetime.fromisoformat(item["start_at"])
        except (ValueError, TypeError):
            raise FeedError("GIE announcement has an invalid source date.") from None
        if identifier in seen:
            raise FeedError("GIE returned duplicate announcements.")
        seen.add(identifier)
        rows.append({"id": identifier, "headline": plain_text(item["title"]),
                     "timestamp": item["start_at"], "source_timezone": None,
                     "end_at": item.get("end_at"), "description": plain_text(item.get("summary")),
                     "details": plain_text(item.get("details")), "data_kind": "service_announcement",
                     "source_url": "https://agsi.gie.eu/api/news?" + urlencode({"turl": identifier})})
    return rows


def fetch_news(api_key, scope="AGSI", session=None):
    if scope != "AGSI":
        raise ValueError("Unsupported announcement feed.")
    if not api_key:
        raise FeedError("GIE API key is not configured.")
    url = "https://agsi.gie.eu/api/news"
    params = {"page": 1, "size": 20}
    payload = get_json(url, params, {"x-key": api_key}, session)
    return batch("GIE Announcements", scope, url + "?" + urlencode(params), payload, normalize_news(payload))
