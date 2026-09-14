from datetime import datetime
from zoneinfo import ZoneInfo


def market_today(now: datetime | None = None):
    """Journal calendar date in Europe/Paris, independent of server timezone."""
    now = now or datetime.now(ZoneInfo("Europe/Paris"))
    if now.tzinfo is None:
        raise ValueError("Supply a timezone-aware instant.")
    return now.astimezone(ZoneInfo("Europe/Paris")).date()
