"""Pure analytics. Missing comparisons are never replaced by zero or a nearer date."""
from datetime import date, timedelta
import numpy as np
import pandas as pd
from utils.dates import market_today


def valid_value(row):
    return row.get("clean_value") if row and row.get("quality_status") == "ok" else None


def snapshot(records, metric, as_of=None, previous_published=False):
    as_of = as_of or market_today()
    rows = sorted([r for r in records if r["metric"] == metric and r["observation_date"] <= as_of.isoformat()],
                  key=lambda r: r["observation_date"])
    if not rows:
        return {"value": None, "delta": None, "date": None, "previous_date": None, "status": "missing"}
    # Callers must choose one instrument/source/unit before computing changes.
    if len({(r["instrument"], r["unit"]) for r in rows}) > 1:
        raise ValueError("Do not compare mixed instruments or units.")
    if len({r["observation_date"] for r in rows}) != len(rows):
        raise ValueError("Resolve revisions before computing changes.")
    latest = rows[-1]
    target = (date.fromisoformat(latest["observation_date"]) - timedelta(days=1)).isoformat()
    previous = rows[-2] if previous_published and len(rows) > 1 else next((r for r in rows if r["observation_date"] == target), None)
    value, old = valid_value(latest), valid_value(previous)
    return {"value": value, "delta": value - old if value is not None and old is not None else None,
            "date": latest["observation_date"], "previous_date": previous["observation_date"] if previous else None,
            "status": latest["quality_status"], "source_status": latest.get("source_status")}


def seasonal_reference(records, metric, day, years=5):
    rows = [r for r in records if r["metric"] == metric]
    if years < 1:
        raise ValueError("At least one reference year is required.")
    if len({(r["instrument"], r["unit"]) for r in rows}) > 1 or len({r["observation_date"] for r in rows}) != len(rows):
        raise ValueError("Select one series and resolve revisions first.")
    lookup = {r["observation_date"]: valid_value(r) for r in rows}
    values = []
    for year in range(day.year - years, day.year):
        try:
            target = day.replace(year=year).isoformat()
        except ValueError:
            continue
        if lookup.get(target) is not None:
            values.append(lookup[target])
    return {"mean": float(np.mean(values)) if len(values) == years else None,
            "min": min(values) if len(values) == years else None,
            "max": max(values) if len(values) == years else None, "years_available": len(values)}


def history_frame(records, metric):
    rows = [r for r in records if r["metric"] == metric]
    if not rows:
        return pd.DataFrame(columns=["date", "value"])
    frame = pd.DataFrame({"date": pd.to_datetime([r["observation_date"] for r in rows]),
                          "value": [valid_value(r) for r in rows]}).set_index("date").sort_index()
    # Insert empty daily slots so line charts visibly break at provider date gaps.
    return frame.reindex(pd.date_range(frame.index.min(), frame.index.max(), freq="D", name="date")).reset_index()


def realized_volatility(values, window=30, annualization=252):
    """Sample std of log settlement returns × sqrt(252) × 100; fixed contract only.

    A window is N returns and requires N+1 strictly positive prices. NaN invalidates
    affected windows; missing prices are never forward-filled. Assumes observations
    are consecutive trading-session settlements; calendar verification is upstream.
    """
    if window < 2 or annualization <= 0:
        raise ValueError("Window must be at least two returns; annualization must be positive.")
    prices = pd.Series(values, dtype=float)
    returns = np.log(prices.where(prices > 0)).diff()
    return returns.rolling(window, min_periods=window).std(ddof=1) * np.sqrt(annualization) * 100


def hdd(temperature, base=18.0):
    return None if temperature is None else max(base - temperature, 0.0)


def net_injection(records):
    """Injection minus withdrawal, same instrument/gas day; GWh/d, positive = fill."""
    inputs = [r for r in records if r["metric"] in {"storage_injection", "storage_withdrawal"}]
    lookup = {}
    for row in inputs:
        key = (row["instrument"], row["observation_date"], row["metric"])
        if row["unit"] != "GWh/d" or key in lookup:
            raise ValueError("Net injection requires unique GWh/d observations.")
        lookup[key] = row
    result = []
    for instrument, day in sorted({(r["instrument"], r["observation_date"]) for r in inputs}):
        injection = lookup.get((instrument, day, "storage_injection"))
        withdrawal = lookup.get((instrument, day, "storage_withdrawal"))
        a, b = valid_value(injection), valid_value(withdrawal)
        value = a - b if a is not None and b is not None else None
        result.append({"metric": "net_injection", "instrument": instrument, "observation_date": day,
                       "unit": "GWh/d", "clean_value": value, "quality_status": "ok" if value is not None else "missing",
                       "source_status": "E" if any(r and r.get("source_status") == "E" for r in (injection, withdrawal)) else "C"})
    return result


def weather_window(records, start, days=7):
    """Exact forward calendar window. Require every daily mean for aggregates."""
    rows = [r for r in records if r["metric"] == "temperature"]
    if len({r["instrument"] for r in rows}) > 1 or len({r["observation_date"] for r in rows}) != len(rows):
        raise ValueError("Select one forecast vintage and location.")
    lookup = {r["observation_date"]: valid_value(r) for r in rows}
    values = [lookup.get((start + timedelta(days=i)).isoformat()) for i in range(days)]
    complete = days > 0 and all(v is not None for v in values)
    return {"mean": float(np.mean(values)) if complete else None,
            "hdd": sum(hdd(v) for v in values) if complete else None,
            "available": sum(v is not None for v in values), "days": days}
