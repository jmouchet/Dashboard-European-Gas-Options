"""Per-browser-session auth and read cache; authenticated clients are never global."""
import json
import time
import streamlit as st
from database.repository import PreviewRepository, SupabaseRepository, StorageError
from utils.config import connection_settings, validate_settings
from data.validation import utc_now


def setup_sidebar():
    st.session_state.setdefault("preview_rows", {})
    with st.sidebar:
        st.markdown("## GAS INTELLIGENCE")
        st.caption("European gas · Market understanding")
        if st.session_state.get("db_user"):
            st.success("Signed in · Supabase storage")
            if st.button("Sign out", width="stretch"):
                try:
                    st.session_state.db_client.auth.sign_out()
                except Exception:
                    pass  # Always clear local private state, even when offline.
                st.session_state.clear()
                st.rerun()
        else:
            st.info("Session preview · Not saved to disk")
            if any(st.session_state.preview_rows.values()):
                st.download_button("Export preview before signing in", json.dumps(st.session_state.preview_rows, indent=2),
                                   "gas-preview.json", "application/json", width="stretch")
            try:
                secrets = st.secrets.to_dict()
            except FileNotFoundError:
                secrets = {}
            url, key = connection_settings(secrets)
            if url and key:
                try:
                    validate_settings(url, key)
                except ValueError as exc:
                    st.warning(str(exc))
                else:
                    with st.form("sign_in", clear_on_submit=True):
                        email = st.text_input("Email")
                        password = st.text_input("Password", type="password")
                        submitted = st.form_submit_button("Sign in", width="stretch")
                    if submitted:
                        try:
                            from supabase import create_client
                            client = create_client(url, key)
                            result = client.auth.sign_in_with_password({"email": email, "password": password})
                            if not result.user or not result.session:
                                raise ValueError("No authenticated session")
                        except Exception:
                            st.error("Sign-in failed. Check your credentials, project settings and connection.")
                        else:
                            # Do not carry drafts/answers between preview and account contexts.
                            st.session_state.clear()
                            st.session_state.db_client = client
                            st.session_state.db_user = str(result.user.id)
                            st.rerun()
            else:
                st.caption("Open Data / Admin for Supabase setup.")
        st.caption("V0.1 · Manual observations · No live feeds")
        if st.button("Refresh saved data", width="stretch"):
            st.session_state.pop("read_cache", None)
            st.rerun()


def repository():
    if st.session_state.get("db_user"):
        return SupabaseRepository(st.session_state.db_client, st.session_state.db_user)
    return PreviewRepository(st.session_state.setdefault("preview_rows", {}))


def read_rows(table: str) -> list[dict]:
    cache = st.session_state.setdefault("read_cache", {})
    last_success = st.session_state.setdefault("last_success", {})
    cached = cache.get(table)
    if cached and time.monotonic() - cached[0] < 30:
        return cached[1]
    try:
        rows = repository().list(table)
    except StorageError as exc:
        st.error(str(exc))
        st.caption(f"Last successful read: {last_success.get(table, 'none in this session')}")
        st.stop()
    cache[table] = (time.monotonic(), rows)
    last_success[table] = utc_now()
    return rows


def save_row(table: str, row: dict) -> bool:
    try:
        repository().insert(table, row)
    except StorageError as exc:
        st.error(str(exc))
        return False
    st.session_state.pop("read_cache", None)
    st.session_state["flash"] = "Saved to Supabase." if st.session_state.get("db_user") else "Added to this session only. Export from Data / Admin to keep a copy."
    return True


def curriculum():
    from learning.content import get_articles, get_questions
    if not st.session_state.get("db_user"):
        return get_articles(), get_questions()
    articles, questions = read_rows("knowledge_articles"), read_rows("questions")
    if not articles or not questions:
        st.warning("The curriculum is not installed. Run database/seed.sql in Supabase; then refresh saved data.")
        st.stop()
    return (sorted(articles, key=lambda a: a["curriculum_order"]),
            sorted(questions, key=lambda q: q["curriculum_order"]))


def page_header(title: str, description: str):
    st.title(title)
    st.caption(description)
    if not st.session_state.get("db_user"):
        st.warning("Preview: entries last only for this browser session. Export them before closing, reloading or signing in.")
    if message := st.session_state.pop("flash", None):
        st.success(message)
