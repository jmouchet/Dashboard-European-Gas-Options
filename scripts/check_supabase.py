"""Read-only connectivity checks using the configured public key.

Never prints keys, response bodies, session tokens or user records. These checks
cannot verify authenticated persistence or distinguish all schema/policy issues.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import tomllib

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils.config import connection_settings, validate_settings


def main() -> int:
    path = ROOT / ".streamlit" / "secrets.toml"
    secrets = tomllib.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    url, key = connection_settings(secrets)
    try:
        validate_settings(url, key)
    except ValueError:
        print("Connection settings are missing or invalid. Check the local secrets file.")
        return 1
    headers = {"apikey": key}
    if not key.startswith("sb_publishable_"):
        headers["Authorization"] = f"Bearer {key}"

    def check(item):
        label, endpoint = item
        try:
            response = requests.get(url.rstrip("/") + endpoint, headers=headers, timeout=15)
        except requests.RequestException as exc:
            print(f"{label}: network unavailable ({type(exc).__name__})")
            return False
        if label == "Auth service":
            ok = response.status_code == 200
            print(f"{label}: HTTP {response.status_code} ({'reachable with configured key' if ok else 'check project and key'})")
            return ok
        try:
            body = response.json()
        except ValueError:
            body = {}
        denied = response.status_code in (401, 403) and isinstance(body, dict) and body.get("code") == "42501"
        print(f"{label}: HTTP {response.status_code} ({'anonymous access denied as expected' if denied else 'unexpected result; review schema and permissions'})")
        return denied

    endpoints = [("Auth service", "/auth/v1/settings")]
    for table in ["knowledge_articles", "questions", "manual_observations", "journal_entries", "predictions", "quiz_attempts", "learning_progress"]:
        column = "article_id" if table == "learning_progress" else "id"
        endpoints.append((table, f"/rest/v1/{table}?select={column}&limit=0"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, endpoints))
    print("Authenticated sign-in, curriculum contents and save/reload checks still require your app login.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
