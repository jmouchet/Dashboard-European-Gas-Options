"""Scheduled worker: same Supabase Auth account as the dashboard, public data only."""
from datetime import datetime, timezone
from pathlib import Path
import os
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from briefing.openai_client import DEFAULT_MODEL, BriefError
from briefing.service import create_daily, daily_status, edition_day, PARIS
from components.market_data import refresh_feed
from database.brief_store import BriefStore
from database.market_store import MarketStore
from database.repository import StorageError
from utils.config import validate_settings


def settings():
    path = ROOT / ".streamlit/secrets.toml"
    local = tomllib.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    names = ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_BRIEF_EMAIL", "SUPABASE_BRIEF_PASSWORD", "GIE_API_KEY", "OPENAI_API_KEY", "OPENAI_BRIEF_MODEL")
    return {name: os.environ.get(name) or local.get(name, "") for name in names}


def main():
    retry = "--retry" in sys.argv or os.environ.get("BRIEF_RETRY", "").lower() == "true"
    config = settings()
    required = ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_BRIEF_EMAIL", "SUPABASE_BRIEF_PASSWORD", "GIE_API_KEY", "OPENAI_API_KEY")
    missing = [name for name in required if not config[name]]
    if missing:
        print("Configuration incomplete. Missing secret names: " + ", ".join(missing))
        return 1
    try:
        validate_settings(config["SUPABASE_URL"], config["SUPABASE_ANON_KEY"])
    except ValueError:
        print("Supabase public connection settings are invalid.")
        return 1
    now = datetime.now(timezone.utc)
    if edition_day(now) != now.astimezone(PARIS).date():
        print("Before 06:00 Europe/Paris: no new edition is due.")
        return 0
    from supabase import create_client
    try:
        client = create_client(config["SUPABASE_URL"], config["SUPABASE_ANON_KEY"])
        auth = client.auth.sign_in_with_password({"email": config["SUPABASE_BRIEF_EMAIL"], "password": config["SUPABASE_BRIEF_PASSWORD"]})
        if not auth.user or not auth.session:
            raise ValueError("Missing authenticated session")
    except Exception:
        print("Supabase authentication failed. Check the worker account secrets.")
        return 1
    try:
        store = BriefStore(client, str(auth.user.id))
        status = daily_status(store, now)
        if status["state"] != "missing" and not (retry and status["state"] in {"failed", "interrupted"}):
            print("Daily brief state:", status["state"], "- no automatic paid retry.")
            return 0 if status["state"] in {"success", "running"} else 1
        market = MarketStore(client, str(auth.user.id))
        feeds = []
        for source, scope in [("GIE AGSI", "EU"), ("GIE ALSI", "EU"), ("Open-Meteo", "Paris")]:
            value = refresh_feed(market, source, scope, config["GIE_API_KEY"], force=True)
            feeds.append((source, scope, value))
            print(source, "-", "refresh failed; gap flagged in context" if value["error"] else "saved/check complete")
        result = create_daily(store, feeds, config["OPENAI_API_KEY"], config["OPENAI_BRIEF_MODEL"] or DEFAULT_MODEL, retry=retry)
        print("Daily brief state:", result["state"])
        if result.get("error"):
            print(result["error"])
        return 0 if result["state"] == "success" else 1
    except (StorageError, BriefError) as exc:
        print(str(exc))
        return 1
    except Exception as exc:
        print("Worker failed; error type:", type(exc).__name__)
        return 1
    finally:
        try:
            # Local scope avoids revoking the user's open dashboard sessions.
            client.auth.sign_out({"scope": "local"})
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
