from datetime import date, timedelta
import unittest
import numpy as np
from analytics.market import snapshot, seasonal_reference, history_frame, realized_volatility, net_injection, weather_window, hdd
from data.market_entries import make_mark, make_asset, make_event


def row(day, value, metric="storage_full", unit="%", **extra):
    return {"observation_date": day, "clean_value": value, "metric": metric, "unit": unit,
            "instrument": "EU", "quality_status": "ok", "source_status": "C", **extra}


class AnalyticsTests(unittest.TestCase):
    def test_delta_exact_previous_day_and_missing_latest(self):
        rows = [row("2026-01-01", 70), row("2026-01-03", 71)]
        self.assertIsNone(snapshot(rows, "storage_full")["delta"])
        self.assertEqual(snapshot(rows, "storage_full", previous_published=True)["delta"], 1)
        rows.append(row("2026-01-04", None, quality_status="missing"))
        self.assertIsNone(snapshot(rows, "storage_full")["value"])
        self.assertEqual(snapshot(rows, "storage_full")["date"], "2026-01-04")

    def test_no_future_dates_mixed_units_or_unresolved_revisions(self):
        rows = [row("2026-01-01", 70), row("2026-01-02", 71)]
        self.assertEqual(snapshot(rows, "storage_full", as_of=date(2026, 1, 1))["value"], 70)
        with self.assertRaises(ValueError):
            snapshot(rows + [row("2026-01-03", 5, unit="TWh")], "storage_full")
        with self.assertRaises(ValueError):
            snapshot(rows + [rows[0]], "storage_full")

    def test_seasonal_requires_all_prior_years_excludes_current(self):
        rows = [row(f"{year}-09-22", value) for year, value in zip(range(2021, 2027), [60, 70, 80, 90, 100, 1])]
        result = seasonal_reference(rows, "storage_full", date(2026, 9, 22))
        self.assertEqual(result["mean"], 80)
        self.assertEqual(result["min"], 60)
        self.assertIsNone(seasonal_reference(rows[1:], "storage_full", date(2026, 9, 22))["mean"])
        self.assertIsNone(seasonal_reference([row("2020-02-29", 50)], "storage_full", date(2024, 2, 29))["mean"])

    def test_chart_breaks_at_date_gaps_and_flagged_values(self):
        frame = history_frame([row("2026-01-01", 70), row("2026-01-03", 80, quality_status="flagged")], "storage_full")
        self.assertEqual(len(frame), 3)
        self.assertTrue(frame.value.iloc[1:].isna().all())

    def test_net_injection_is_same_day_and_unit(self):
        rows = [row("2026-01-01", 30, "storage_injection", "GWh/d"), row("2026-01-01", 40, "storage_withdrawal", "GWh/d"),
                row("2026-01-02", 35, "storage_injection", "GWh/d")]
        result = net_injection(rows)
        self.assertEqual(result[0]["clean_value"], -10)
        self.assertIsNone(result[1]["clean_value"])
        with self.assertRaises(ValueError):
            net_injection([row("2026-01-01", 1, "storage_injection", "TWh")])

    def test_realized_vol_regression_and_invalid_windows(self):
        values = [100, 110, 99, 108.9]
        expected = np.std(np.log(np.array(values[1:]) / np.array(values[:-1])), ddof=1) * np.sqrt(252) * 100
        self.assertAlmostEqual(realized_volatility(values, window=3).iloc[-1], expected)
        self.assertTrue(realized_volatility([100, None, 110, 120], window=2).isna().all())
        self.assertTrue(realized_volatility([100, 0, 110], window=2).isna().all())
        with self.assertRaises(ValueError):
            realized_volatility(values, window=1)

    def test_weather_exact_horizon_and_degree_day_base(self):
        start = date(2026, 1, 1)
        rows = [row((start + timedelta(days=i)).isoformat(), 10, "temperature", "°C", instrument="Paris") for i in range(7)]
        result = weather_window(rows, start)
        self.assertEqual(result["mean"], 10)
        self.assertEqual(result["hdd"], 56)
        self.assertIsNone(weather_window(rows[1:], start)["mean"])
        self.assertEqual(hdd(20), 0)
        self.assertIsNone(hdd(None))


class EntryTests(unittest.TestCase):
    def test_option_units_nulls_and_expiry_validation(self):
        args = [date(2026, 1, 1), "Fixture TTF", date(2026, 2, 1), "50", "-2", "", "Fixture convention", "https://example.com"]
        result = make_mark(*args)
        self.assertEqual(result["atm_vol"], 50)
        self.assertEqual(result["risk_reversal"], -2)
        self.assertIsNone(result["butterfly"])
        args[2] = date(2025, 1, 1)
        with self.assertRaises(ValueError):
            make_mark(*args)

    def test_asset_capacity_coordinates_and_missing_values(self):
        args = ["Fixture", "Storage", "DE", "Fixture operator", "", "", "TTF", "Fixture description", "https://example.com"]
        self.assertIsNone(make_asset(*args)["capacity"])
        with self.assertRaises(ValueError):
            make_asset(*args, latitude="50")
        with self.assertRaises(ValueError):
            make_asset(*args, latitude="NaN", longitude="1")
        args[4] = "10"
        with self.assertRaises(ValueError):
            make_asset(*args)

    def test_event_timezone_and_impact_pair(self):
        args = ["2026-01-01T12:00:00+01:00", "Storage", "Fixture", "Fixture event", "Fixture facts", "https://example.com", "-10", "GWh/d", "1 day", "M1", 2, "Fixture interpretation"]
        result = make_event(*args)
        self.assertEqual(result["timestamp"], "2026-01-01T11:00:00+00:00")
        self.assertEqual(result["physical_impact"], -10)
        args[7] = ""
        with self.assertRaises(ValueError):
            make_event(*args)
