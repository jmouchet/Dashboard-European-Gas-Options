"""Refresh on access, persistent same-source fallback, session-scoped clients/cache."""
from datetime import datetime, timezone
import os
import time
import streamlit as st
from data.loaders.base import FeedError
from data.loaders.gie import fetch_storage, fetch_lng
from data.loaders.gie_reference import fetch_catalog, fetch_news
from data.loaders.weather import fetch_weather
from database.market_store import MarketStore
from database.repository import StorageError

FEEDS = {
    "GIE AGSI": (fetch_storage, 21600),
    "GIE ALSI": (fetch_lng, 21600),
    "GIE Directory": (fetch_catalog, 86400),
    "GIE Announcements": (fetch_news, 21600),
    "Open-Meteo": (fetch_weather, 3600),
}


def setting(name):
    if os.environ.get(name):
        return os.environ[name]
    try:
        return st.secrets.get(name, "")
    except FileNotFoundError:
        return ""


def refresh_feed(store, source, scope, api_key="", force=False, now=None):
    """Orchestration boundary with injectable storage and clock for failure tests."""
    fetch, ttl = FEEDS[source]
    now = now or datetime.now(timezone.utc)
    result = {"batch": None, "error": None, "last_success": None, "retry_in": ttl}
    try:
        saved = store.latest("market_feed_batches", source, scope)
        result["batch"] = saved
        result["last_success"] = saved["retrieved_at"] if saved else None
        last_run = store.latest("ingestion_runs", source, scope)
        if last_run and not force:
            age = max(0, (now - datetime.fromisoformat(last_run["finished_at"].replace("Z", "+00:00"))).total_seconds())
            interval = ttl if last_run["status"] == "success" else 900
            if age < interval and (saved or last_run["status"] == "failed"):
                result["retry_in"] = interval - age
                if last_run["status"] == "failed":
                    result["error"] = last_run["message"] or "The previous refresh failed."
                else:
                    result["last_success"] = last_run["finished_at"]
                return result
        try:
            if source.startswith("GIE") and not api_key:
                raise FeedError("GIE API key is not configured.")
            fresh = fetch(api_key, scope) if source.startswith("GIE") else fetch(scope)
            # Keep every changed vintage, including A -> B -> A, but avoid
            # repeatedly storing identical large GIE directories/notices.
            if saved is None or saved.get("raw_payload") != fresh.get("raw_payload"):
                store.save_batch(fresh)
                result["batch"] = fresh
            result["last_success"] = fresh["retrieved_at"]
            store.log_run(source, scope, now.isoformat(), "success", len(fresh["clean_records"]))
        except FeedError as exc:
            result["error"] = str(exc)
            store.log_run(source, scope, now.isoformat(), "failed", message=str(exc))
    except StorageError as exc:
        result["error"] = str(exc)
    if result["error"]:
        result["retry_in"] = 900
    return result


def load_feed(source, scope, force=False):
    if source not in FEEDS:
        raise ValueError("Unknown feed.")
    if not st.session_state.get("db_user"):
        return {"batch": None, "error": "Sign in to load and archive market feeds.", "last_success": None}
    cache_key = (source, scope)
    cache = st.session_state.setdefault("market_cache", {})
    previous = cache.get(cache_key)
    if previous and not force and time.monotonic() < previous["expires"]:
        return previous
    store = MarketStore(st.session_state.db_client, st.session_state.db_user)
    with st.spinner(f"Updating {source} · {scope}…"):
        result = refresh_feed(store, source, scope, setting("GIE_API_KEY"), force)
    result["expires"] = time.monotonic() + result["retry_in"]
    cache[cache_key] = result
    return result


def feed_status(result, label):
    if result.get("error"):
        st.warning(f"{label}: {result['error']}")
    if result.get("last_success"):
        st.caption(f"{label} · Last successful check {result['last_success']}")
    if result.get("batch"):
        notes = result["batch"].get("quality_notes", [])
        clean = result["batch"]["clean_records"]
        excluded = sum(r.get("quality_status") in {"missing", "flagged"} for r in clean)
        with st.expander(f"{label} · Source and quality ({len(notes)} notes, {excluded} missing/flagged values)"):
            source = result["batch"].get("source", "")
            if source.startswith("GIE"):
                platform = "alsi" if source == "GIE ALSI" or (source == "GIE Directory" and result["batch"].get("scope") == "ALSI") else "agsi"
                st.link_button("Open GIE platform", f"https://{platform}.gie.eu/")
                st.text(f"API request: {result['batch']['source_url']}")
            else:
                st.link_button("Open source request", result["batch"]["source_url"])
            st.caption(f"Snapshot retrieved {result['batch']['retrieved_at']}. An unchanged provider response reuses its saved snapshot.")
            st.caption("GIE E = estimated, C = confirmed, N = no data. Gas-day dates and forecast dates are distinct from retrieval times.")
            for note in notes[:50]:
                st.text(note)
            if len(notes) > 50:
                st.caption("Full quality notes are included in the snapshot export in Data / Admin.")


def records(result):
    return result["batch"]["clean_records"] if result.get("batch") else []
