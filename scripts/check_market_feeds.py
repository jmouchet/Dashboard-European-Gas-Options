"""Read-only provider smoke check; never prints keys or request headers."""
from datetime import date, timedelta
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data.loaders.gie import fetch_storage, fetch_lng
from data.loaders.gie_reference import fetch_catalog, fetch_news
from data.loaders.weather import fetch_weather
from data.loaders.base import FeedError


def main():
    settings = tomllib.loads((ROOT / ".streamlit/secrets.toml").read_text(encoding="utf-8-sig"))
    failed = False
    full = "--full" in sys.argv
    start = None if full else date.today() - timedelta(days=10)
    calls = [("GIE AGSI", lambda: fetch_storage(settings.get("GIE_API_KEY"), start=start)),
             ("GIE ALSI", lambda: fetch_lng(settings.get("GIE_API_KEY"), start=start)),
             ("Open-Meteo", lambda: fetch_weather("Paris")),
             ("GIE storage directory", lambda: fetch_catalog(settings.get("GIE_API_KEY"), "AGSI")),
             ("GIE LNG directory", lambda: fetch_catalog(settings.get("GIE_API_KEY"), "ALSI")),
             ("GIE announcements", lambda: fetch_news(settings.get("GIE_API_KEY")))]
    for name, call in calls:
        try:
            result = call()
            records = result["clean_records"]
            print(f"{name}: {len(records)} normalized records; {len(result['quality_notes'])} quality notes")
            if records and "observation_date" in records[0]:
                print(f"Dates: {min(r['observation_date'] for r in records)} to {max(r['observation_date'] for r in records)}")
                print("Units:", sorted({r["unit"] for r in records}))
                for metric in sorted({r['metric'] for r in records}):
                    latest = max((r for r in records if r['metric'] == metric), key=lambda r: r['observation_date'])
                    print(f"  {metric}: {latest['clean_value']} {latest['unit']} ({latest['observation_date']}, {latest['quality_status']}, {latest['source_status']})")
        except FeedError as exc:
            failed = True
            print(f"{name}: {exc}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
