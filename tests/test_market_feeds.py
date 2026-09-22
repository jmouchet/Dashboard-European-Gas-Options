"""Provider fixtures are synthetic test data, never dashboard fallback data."""
from datetime import date, datetime, timedelta, timezone
import unittest
from unittest.mock import Mock, patch
import requests
from data.loaders.base import FeedError, batch, get_json, number
from data.loaders.gie import normalize, fetch_storage, fetch_lng, LNG_FIELDS
from data.loaders.weather import normalize as normalize_weather
from data.loaders.gie_reference import normalize_catalog, normalize_news
from components.market_data import refresh_feed, FEEDS
from database.repository import StorageError
from database.market_store import MarketStore


def gas_row(day="2026-01-02", **values):
    return {"gasDayStart": day, "code": "eu", "status": "C", "full": "70.0", "gasInStorage": "700.0",
            "workingGasVolume": "1000.0", "injection": "20.0", "withdrawal": "30.0", **values}


def response(payload, status=200):
    result = Mock(status_code=status)
    result.json.return_value = payload
    return result


class FeedTests(unittest.TestCase):
    def test_gie_units_missing_estimates_and_zero(self):
        rows, _ = normalize([{"data": [gas_row(status="E", full="0", injection="-", withdrawal="0")]}], "EU")
        by_metric = {r["metric"]: r for r in rows}
        self.assertEqual(by_metric["storage_energy"]["unit"], "TWh")
        self.assertEqual(by_metric["storage_withdrawal"]["unit"], "GWh/d")
        self.assertEqual(by_metric["storage_withdrawal"]["clean_value"], 0)
        self.assertIsNone(by_metric["storage_injection"]["clean_value"])
        self.assertEqual(by_metric["storage_full"]["source_status"], "E")
        self.assertEqual(by_metric["storage_full"]["quality_status"], "ok")

    def test_gie_n_status_overrides_numeric_raw(self):
        rows, _ = normalize([{"data": [gas_row(status="N")]}], "EU")
        self.assertTrue(all(r["clean_value"] is None for r in rows))
        self.assertEqual(rows[0]["raw_value"], "70.0")

    def test_gie_flags_suspicious_values_without_destroying_them(self):
        rows, _ = normalize([{"data": [gas_row(full="101", injection="-2")]}], "EU")
        self.assertEqual(rows[0]["quality_status"], "flagged")
        self.assertEqual(rows[0]["clean_value"], 101)
        self.assertEqual(next(r for r in rows if r["metric"] == "storage_injection")["quality_status"], "flagged")

    def test_gie_rejects_schema_scope_and_duplicate_dates(self):
        for payload in ({}, {"data": [gas_row(code="de")]}, {"data": [gas_row(), gas_row()]}, {"data": [{}]}):
            with self.subTest(payload=payload), self.assertRaises(FeedError):
                normalize([payload], "EU")

    def test_gie_gap_and_daily_jump(self):
        rows, notes = normalize([{"data": [gas_row("2026-01-01"), gas_row("2026-01-02", full="80"), gas_row("2026-01-04", full="81")]}], "EU")
        self.assertTrue(any("Missing gas days" in n for n in notes))
        self.assertTrue(any("Large fullness" in n for n in notes))
        self.assertEqual(next(r for r in rows if r["metric"] == "storage_full" and r["observation_date"] == "2026-01-02")["quality_status"], "flagged")

    @patch("data.loaders.gie.time.sleep")
    def test_pagination_and_header_only_credentials(self, _sleep):
        session = Mock()
        session.get.side_effect = [response({"last_page": 2, "data": [gas_row("2026-01-02")]}),
                                   response({"last_page": 2, "data": [gas_row("2026-01-01")]})]
        result = fetch_storage("fixture-key", start=date(2026, 1, 1), end=date(2026, 1, 2), session=session)
        self.assertEqual(len(result["clean_records"]), 10)
        self.assertEqual(session.get.call_args.kwargs["headers"], {"x-key": "fixture-key"})
        self.assertEqual(session.get.call_args.kwargs["params"]["page"], 2)
        self.assertNotIn("fixture-key", str(result))
        self.assertIn("from=2026-01-01", result["source_url"])

    def test_out_of_range_response_and_missing_paging_metadata_fail(self):
        for payload in ({"data": [gas_row()]}, {"last_page": 1, "data": [gas_row("2025-12-31")]},
                        {"last_page": 1.5, "data": [gas_row()]}, {"last_page": True, "data": [gas_row()]}):
            session = Mock()
            session.get.return_value = response(payload)
            with self.assertRaises(FeedError):
                fetch_storage("fixture", start=date(2026, 1, 1), end=date(2026, 1, 2), session=session)

    def test_lng_uses_documented_energy_flow_fields(self):
        session = Mock()
        session.get.return_value = response({"last_page": 1, "data": [gas_row(sendOut="100.5", dtrs="200", inventory={"lng": "9", "gwh": "60"})]})
        result = fetch_lng("fixture", start=date(2026, 1, 1), end=date(2026, 1, 2), session=session)
        self.assertEqual({r["metric"] for r in result["clean_records"]}, {"lng_sendout", "lng_sendout_capacity"})
        self.assertEqual({r["unit"] for r in result["clean_records"]}, {"GWh/d"})
        self.assertTrue(session.get.call_args.args[0].startswith("https://alsi.gie.eu/"))

    def test_weather_units_missing_and_duplicate_dates(self):
        payload = {"daily_units": {"temperature_2m_mean": "°C"}, "timezone": "Europe/Paris",
                   "daily": {"time": ["2026-01-01", "2026-01-02"], "temperature_2m_mean": [None, 0]}}
        rows = normalize_weather(payload, "Paris")
        self.assertIsNone(rows[0]["clean_value"])
        self.assertEqual(rows[1]["clean_value"], 0)
        self.assertIsNone(rows[1]["source_timestamp"])
        payload["daily_units"]["temperature_2m_mean"] = "°F"
        with self.assertRaises(FeedError):
            normalize_weather(payload, "Paris")
        payload["daily_units"]["temperature_2m_mean"] = "°C"
        payload["daily"]["time"] = ["2026-01-01", "2026-01-01"]
        with self.assertRaises(FeedError):
            normalize_weather(payload, "Paris")

    @patch("data.loaders.base.time.sleep")
    def test_retry_and_sanitized_connection_failure(self, sleep):
        session = Mock()
        session.get.side_effect = [response({}, 429), response({"ok": True})]
        self.assertEqual(get_json("https://example.com", session=session), {"ok": True})
        self.assertEqual(session.get.call_count, 2)
        session.get.side_effect = requests.ConnectionError("sensitive-header-fixture")
        with self.assertRaises(FeedError) as caught:
            get_json("https://example.com", session=session)
        self.assertNotIn("sensitive", str(caught.exception))

    def test_batch_preserves_returned_vintages_and_retry_hash(self):
        first = batch("fixture", "EU", "https://example.com", {"a": 1}, [])
        with patch("data.loaders.base.datetime") as clock:
            clock.now.return_value = datetime(2030, 1, 1, tzinfo=timezone.utc)
            repeated = batch("fixture", "EU", "https://example.com", {"a": 1}, [])
        self.assertNotEqual(first["payload_hash"], repeated["payload_hash"])
        self.assertEqual(first["payload_hash"], dict(first)["payload_hash"])
        self.assertEqual(first["raw_payload"], repeated["raw_payload"])

    def test_reference_data_identity_and_safe_text(self):
        fixture = [{"name": "Fixture operator", "eic": "operator-1", "facilities": [
            {"name": "Fixture storage group", "eic": "facility-1", "country": "DE", "type": "UGS"}]}]
        self.assertEqual(normalize_catalog(fixture)[0]["operator_eic"], "operator-1")
        fixture[0]["facilities"].append({"name": "Historical fixture", "eic": "facility-1", "country": "GB", "type": "UGS"})
        self.assertEqual(len(normalize_catalog(fixture)), 2)
        fixture[0]["facilities"].append(dict(fixture[0]["facilities"][0]))
        with self.assertRaises(FeedError):
            normalize_catalog(fixture)
        news = normalize_news({"data": [{"url": "123", "title": "Fixture", "start_at": "2026-01-01 10:00:00", "summary": "<b>Data</b> &amp; coverage"}]})
        self.assertEqual(news[0]["description"], "Data & coverage")
        self.assertIsNone(news[0]["source_timezone"])
        self.assertEqual(news[0]["data_kind"], "service_announcement")


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 22, 12, tzinfo=timezone.utc)
        self.saved = {"retrieved_at": "2026-09-22T06:00:00Z", "clean_records": [{"fixture": 1}], "raw_payload": {"fixture": "old"}}
        self.store = Mock()
        self.fetch = Mock(return_value={**self.saved, "retrieved_at": self.now.isoformat(), "raw_payload": {"fixture": "new"}})
        self.feed_patch = patch.dict(FEEDS, {"GIE AGSI": (self.fetch, 21600)})
        self.feed_patch.start()
        self.addCleanup(self.feed_patch.stop)

    def test_recent_saved_batch_only_uses_remaining_ttl(self):
        self.store.latest.side_effect = [self.saved, {"status": "success", "finished_at": "2026-09-22T06:01:00Z"}]
        result = refresh_feed(self.store, "GIE AGSI", "EU", "fixture", now=self.now)
        self.assertEqual(result["retry_in"], 60)
        self.fetch.assert_not_called()

    def test_provider_failure_preserves_same_source_last_good(self):
        self.store.latest.side_effect = [self.saved, None]
        self.fetch.side_effect = FeedError("Provider unavailable")
        result = refresh_feed(self.store, "GIE AGSI", "EU", "fixture", now=self.now)
        self.assertEqual(result["batch"], self.saved)
        self.assertEqual(result["error"], "Provider unavailable")
        self.assertEqual(self.store.log_run.call_args.args[3], "failed")
        self.store.save_batch.assert_not_called()

    def test_missing_key_keeps_saved_snapshot(self):
        self.store.latest.side_effect = [self.saved, None]
        result = refresh_feed(self.store, "GIE AGSI", "EU", now=self.now)
        self.assertEqual(result["batch"], self.saved)
        self.assertIn("key", result["error"])
        self.fetch.assert_not_called()

    def test_unchanged_payload_is_checked_without_duplicate_archive(self):
        self.store.latest.side_effect = [self.saved, None]
        self.fetch.return_value = {**self.saved, "retrieved_at": self.now.isoformat()}
        result = refresh_feed(self.store, "GIE AGSI", "EU", "fixture", now=self.now)
        self.assertEqual(result["batch"], self.saved)
        self.assertEqual(result["last_success"], self.now.isoformat())
        self.store.save_batch.assert_not_called()
        self.store.log_run.assert_called_once()

    def test_save_failure_does_not_display_unsaved_data(self):
        self.store.latest.side_effect = [self.saved, None]
        self.store.save_batch.side_effect = StorageError("Save failed")
        result = refresh_feed(self.store, "GIE AGSI", "EU", "fixture", now=self.now)
        self.assertEqual(result["batch"], self.saved)
        self.assertEqual(result["error"], "Save failed")

    def test_forced_refresh_bypasses_recent_failure(self):
        self.store.latest.side_effect = [self.saved, {"status": "failed", "finished_at": self.now.isoformat(), "message": "fixture failure"}]
        result = refresh_feed(self.store, "GIE AGSI", "EU", "fixture", force=True, now=self.now)
        self.assertIsNone(result["error"])
        self.fetch.assert_called_once_with("fixture", "EU")
        self.store.save_batch.assert_called_once()

    def test_store_owner_filters_and_immutable_retry(self):
        client = Mock()
        query = client.table.return_value
        query.select.return_value = query
        query.eq.return_value = query
        query.order.return_value = query
        query.limit.return_value = query
        query.execute.return_value.data = [self.saved]
        store = MarketStore(client, "owner-fixture")
        self.assertEqual(store.latest("market_feed_batches", "GIE AGSI", "EU"), self.saved)
        self.assertIn(unittest.mock.call("user_id", "owner-fixture"), query.eq.call_args_list)
        store.save_batch({"user_id": "other-fixture", "payload_hash": "fixture"})
        self.assertEqual(query.upsert.call_args.args[0]["user_id"], "owner-fixture")
        self.assertTrue(query.upsert.call_args.kwargs["ignore_duplicates"])
