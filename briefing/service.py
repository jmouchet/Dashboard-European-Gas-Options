"""Daily brief workflow shared by Streamlit and the scheduled GitHub worker."""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from uuid import uuid4
from briefing.context import build_context
from briefing.openai_client import BriefError, DEFAULT_MODEL, PROMPT_VERSION, generate
from database.repository import StorageError

PARIS = ZoneInfo("Europe/Paris")


def edition_day(now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Timezone-aware clock required.")
    local = now.astimezone(PARIS)
    return local.date() if local.hour >= 6 else local.date() - timedelta(days=1)


def daily_status(store, now=None):
    now = now or datetime.now(timezone.utc)
    day = edition_day(now)
    results, runs = store.results(day), store.runs(day)
    successful = next((r for r in results if r["status"] == "success"), None)
    if successful:
        return {"state": "success", "report": successful, "day": day}
    if not runs:
        return {"state": "missing", "report": None, "day": day}
    latest = max(runs, key=lambda r: r["attempt"])
    outcome = next((r for r in results if r["run_id"] == latest["id"]), None)
    age = (now - datetime.fromisoformat(latest["started_at"].replace("Z", "+00:00"))).total_seconds()
    state = "failed" if outcome else "interrupted" if age >= 900 else "running"
    return {"state": state, "report": outcome, "day": day, "attempt": latest["attempt"]}


def create_daily(store, feeds, api_key, model=DEFAULT_MODEL, now=None, retry=False, generator=generate):
    now = now or datetime.now(timezone.utc)
    day = edition_day(now)
    if day != now.astimezone(PARIS).date():
        return {"state": "before_six", "report": None, "day": day}
    status = daily_status(store, now)
    if status["state"] in {"success", "running"}:
        return status
    if status["state"] != "missing" and not retry:
        return status
    attempt = status.get("attempt", 0) + 1
    if attempt > 2:
        return {**status, "state": "attempt_limit"}
    if not api_key:
        raise BriefError("OPENAI_API_KEY n'est pas configurée.")
    # Validate local inputs before reserving a paid attempt in the database.
    try:
        context = build_context(feeds, now)
    except (ValueError, TypeError, KeyError):
        raise BriefError("Les données du dashboard ne permettent pas de préparer le contexte du brief. Actualise les données.") from None
    run = store.claim(day, attempt)
    if not run:
        return {"state": "running", "report": None, "day": day}
    row = {"id": str(uuid4()), "run_id": run["id"], "brief_date": day.isoformat(),
           "as_of": now.isoformat(), "model": model, "prompt_version": PROMPT_VERSION,
           "input_context": context, "body": "", "citations": [], "usage": {}, "raw_response": None,
           "error_message": ""}
    try:
        row.update(generator(api_key, context, model=model))
        row["status"] = "success"
    except BriefError as exc:
        row.update(status="failed", error_message=str(exc))
    row["generated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        store.save(row)
    except StorageError as exc:
        return {"state": "unsaved", "report": row, "error": str(exc), "day": day}
    return {"state": row["status"], "report": row, "day": day, "attempt": attempt}
