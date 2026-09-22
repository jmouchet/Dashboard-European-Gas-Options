"""Provider boundary: retain payloads and expose only sanitized failures."""
from datetime import datetime, timezone
import hashlib
import json
import math
import time
import requests


class FeedError(Exception):
    pass


def get_json(url, params=None, headers=None, session=None):
    client = session or requests.Session()
    for attempt in range(3):
        try:
            response = client.get(url, params=params, headers=headers, timeout=(8, 25), allow_redirects=False)
        except requests.RequestException:
            raise FeedError("Provider connection failed or timed out.") from None
        if response.status_code in (429, 502, 503, 504) and attempt < 2:
            time.sleep(2 ** attempt)
            continue
        if response.status_code != 200:
            raise FeedError(f"Provider returned HTTP {response.status_code}. Check access and try later.")
        try:
            return response.json()
        except ValueError:
            raise FeedError("Provider returned invalid JSON.") from None


def number(raw):
    if isinstance(raw, bool):
        return None
    if raw is None or (isinstance(raw, str) and raw.strip() in {"", "-", "--", "N/A"}):
        return None
    try:
        value = float(raw)
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) else None


def batch(source, scope, source_url, payload, records, warnings=None):
    retrieved_at = datetime.now(timezone.utc).isoformat()
    return {
        "source": source, "scope": scope, "source_url": source_url,
        "retrieved_at": retrieved_at, "raw_payload": payload, "clean_records": records,
        # Hash the retrieval envelope: identical content fetched later is a new
        # vintage. Retrying this same batch is idempotent, including A -> B -> A.
        "payload_hash": hashlib.sha256(json.dumps({"retrieved_at": retrieved_at, "raw_payload": payload},
                                                  sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "quality_notes": warnings or [],
    }
