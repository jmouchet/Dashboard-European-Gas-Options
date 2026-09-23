"""One explicit live generation for QA; never prints keys, headers or account data."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import os
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from briefing.context import build_context
from briefing.openai_client import DEFAULT_MODEL, generate, BriefError
from data.loaders.base import FeedError
from data.loaders.gie import fetch_storage, fetch_lng
from data.loaders.weather import fetch_weather
from utils.dates import market_today


def main():
    if "--generate" not in sys.argv:
        print("Use --generate for one paid OpenAI Responses + web search request. No automatic retry.")
        return 0
    path = ROOT / ".streamlit/secrets.toml"
    config = tomllib.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    key = os.environ.get("OPENAI_API_KEY") or config.get("OPENAI_API_KEY")
    gie = os.environ.get("GIE_API_KEY") or config.get("GIE_API_KEY")
    model = os.environ.get("OPENAI_BRIEF_MODEL") or config.get("OPENAI_BRIEF_MODEL") or DEFAULT_MODEL
    if not key:
        print("OPENAI_API_KEY is missing.")
        return 1
    feeds = []
    for source, scope, fetch in [
        ("GIE AGSI", "EU", lambda: fetch_storage(gie)),
        ("GIE ALSI", "EU", lambda: fetch_lng(gie)),
        ("Open-Meteo", "Paris", lambda: fetch_weather("Paris")),
    ]:
        try:
            result = {"batch": fetch(), "error": None}
        except FeedError as exc:
            result = {"batch": None, "error": str(exc)}
        feeds.append((source, scope, result))
        print(source, "available" if result["batch"] else "unavailable; gap recorded")
    context = build_context(feeds, datetime.now(timezone.utc))
    try:
        report = generate(key, context, model)
    except BriefError as exc:
        print(str(exc))
        return 1
    target = ROOT / "local_exports" / f"brief-smoke-{market_today()}.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({"model": model, "input_context": context, **report}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OpenAI web brief: completed; citations:", len(report["citations"]))
    print("Usage:", json.dumps(report["usage"]))
    print("QA export:", target.name, "(ignored local_exports directory; not a Supabase archive)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
