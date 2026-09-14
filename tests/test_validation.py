from datetime import datetime, timezone
import unittest
from data.validation import make_observation, parse_timestamp, latest_revisions, validate_url
from utils.units import energy_to_mwh, mcm_to_gwh
from utils.dates import market_today


def observation(**overrides):
    values = dict(series="storage", instrument="EU", raw_value="80", source="Test fixture",
                  source_url="https://example.com/storage", observation_timestamp="2026-01-01T16:00:00+01:00")
    values.update(overrides)
    return make_observation(**values)


class ObservationTests(unittest.TestCase):
    def test_blank_is_null(self):
        row = observation(raw_value=" ")
        self.assertIsNone(row["clean_value"])
        self.assertEqual(row["quality_status"], "missing")

    def test_actual_zero_is_preserved(self):
        self.assertEqual(observation(raw_value="0")["clean_value"], 0)
        self.assertEqual(observation(raw_value="0")["quality_status"], "ok")

    def test_sanity_violation_retained_and_flagged(self):
        row = observation(raw_value="105")
        self.assertEqual(row["clean_value"], 105)
        self.assertEqual(row["quality_status"], "flagged")

    def test_negative_price_not_automatically_deleted(self):
        row = observation(series="ttf", raw_value="-1")
        self.assertEqual(row["quality_status"], "ok")

    def test_nonfinite_rejected(self):
        for value in ["NaN", "inf", "-Infinity"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                observation(raw_value=value)

    def test_ambiguous_numeric_format_rejected(self):
        for value in ["12,5", "1,000", "unavailable"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                observation(raw_value=value)

    def test_required_lineage(self):
        for key in ["source", "instrument", "source_url"]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                observation(**{key: ""})

    def test_raw_and_normalized_value_separate(self):
        row = observation(raw_value=" 80.00 ")
        self.assertEqual(row["raw_value"], " 80.00 ")
        self.assertEqual(row["clean_value"], 80)

    def test_requires_timezone(self):
        with self.assertRaises(ValueError):
            observation(observation_timestamp="2026-01-01T12:00:00")

    def test_utc_normalization_preserves_original_offset(self):
        row = observation()
        self.assertEqual(row["observation_timestamp"], "2026-01-01T15:00:00+00:00")
        self.assertEqual(row["source_timezone"], "UTC+01:00")

    def test_dst_offsets_are_distinct_instants(self):
        early = parse_timestamp("2025-10-26T02:30:00+02:00")
        late = parse_timestamp("2025-10-26T02:30:00+01:00")
        self.assertEqual((late - early).total_seconds(), 3600)

    def test_future_observation_and_publication_rejected(self):
        for key in ["observation_timestamp", "source_timestamp"]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                observation(**{key: "2999-01-01T00:00:00Z"})

    def test_unsafe_source_urls_rejected(self):
        for url in ["javascript:alert(1)", "https://user:secret@example.com", "file:///secret", "https://"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_revision_preserves_as_of_history(self):
        original = observation()
        original["retrieved_at"] = "2026-01-02T00:00:00Z"
        revised = {**original, "clean_value": 81, "retrieved_at": "2026-01-04T00:00:00Z"}
        rows = [original, revised]
        past = latest_revisions(rows, datetime(2026, 1, 3, tzinfo=timezone.utc))
        current = latest_revisions(rows, datetime(2026, 1, 5, tzinfo=timezone.utc))
        self.assertEqual(past[0]["clean_value"], 80)
        self.assertEqual(current[0]["clean_value"], 81)
        self.assertEqual(len(rows), 2)

    def test_later_publication_not_used_in_history(self):
        row = observation()
        row["retrieved_at"] = "2026-01-02T00:00:00Z"
        row["source_timestamp"] = "2026-01-04T00:00:00Z"
        self.assertEqual(latest_revisions([row], datetime(2026, 1, 3, tzinfo=timezone.utc)), [])

    def test_sources_and_contracts_not_combined(self):
        first = observation()
        second = {**first, "source": "Other source"}
        third = {**first, "instrument": "Germany"}
        self.assertEqual(len(latest_revisions([first, second, third])), 3)

    def test_missing_revision_does_not_resurrect_old_value(self):
        old = observation()
        old["retrieved_at"] = "2026-01-02T00:00:00Z"
        new = {**old, "clean_value": None, "quality_status": "missing", "retrieved_at": "2026-01-03T00:00:00Z"}
        self.assertIsNone(latest_revisions([old, new])[0]["clean_value"])


class UnitTests(unittest.TestCase):
    def test_energy_scales(self):
        self.assertEqual(energy_to_mwh(2, "TWh"), 2_000_000)
        self.assertEqual(energy_to_mwh(2, "GWh"), 2_000)

    def test_missing_energy_stays_missing(self):
        self.assertIsNone(energy_to_mwh(None, "TWh"))

    def test_power_not_treated_as_energy(self):
        with self.assertRaises(ValueError):
            energy_to_mwh(1, "MW")

    def test_calorific_value_explicit(self):
        self.assertEqual(mcm_to_gwh(50, 11), 550)
        self.assertEqual(mcm_to_gwh(50, 10), 500)
        self.assertIsNone(mcm_to_gwh(None, 11))

    def test_invalid_calorific_value_rejected(self):
        for value in [0, -1, float("nan"), float("inf")]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                mcm_to_gwh(50, value)

    def test_nonfinite_energy_rejected(self):
        with self.assertRaises(ValueError):
            energy_to_mwh(float("inf"), "GWh")

    def test_market_date_uses_paris_midnight(self):
        instant = datetime(2026, 7, 1, 23, 0, tzinfo=timezone.utc)
        self.assertEqual(market_today(instant).isoformat(), "2026-07-02")

    def test_market_date_requires_timezone(self):
        with self.assertRaises(ValueError):
            market_today(datetime(2026, 7, 1))


if __name__ == "__main__":
    unittest.main()
