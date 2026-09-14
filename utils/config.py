"""Load only public Supabase connection settings; credentials stay outside Git."""
import os
from urllib.parse import urlparse


def connection_settings(secrets) -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", "") or secrets.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "") or secrets.get("SUPABASE_ANON_KEY", "")
    return str(url).strip(), str(key).strip()


def validate_settings(url: str, key: str) -> None:
    import base64
    import json

    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("SUPABASE_URL must be an HTTPS project URL without credentials.")
    if not key or "YOUR_" in key:
        raise ValueError("Add your Supabase publishable or legacy anon key to the local secrets file.")
    if key.startswith("sb_secret_"):
        raise ValueError("Use a publishable key, not a server secret key.")
    if key.startswith("sb_publishable_"):
        return
    try:
        payload = key.split(".")[1]
        decoded = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except (ValueError, IndexError, UnicodeError):
        raise ValueError("Expected a Supabase publishable key or legacy anon JWT.") from None
    if not isinstance(decoded, dict) or decoded.get("role") != "anon":
        raise ValueError("Use the legacy anon key, not a service-role key.")
