from datetime import datetime, date, timezone, timedelta
import json
import unittest
from unittest.mock import Mock, call, patch
import requests
from briefing.openai_client import generate, parse_response, BriefError, public_url
from briefing.context import build_context
from briefing.service import create_daily, daily_status, edition_day
from database.brief_store import BriefStore
from database.repository import StorageError
from components.morning_charts import card_html, spark_figure, weather_figure


def response_fixture():
    text = "Fait de test daté. Interprétation conditionnelle."
    return {"status": "completed", "id": "fixture_response", "usage": {"input_tokens": 100, "output_tokens": 20}, "output": [
        {"type": "web_search_call", "status": "completed", "action": {"type": "search"}},
        {"type": "message", "content": [{"type": "output_text", "text": text, "annotations": [
            {"type": "url_citation", "start_index": 0, "end_index": 18, "title": "Fixture source", "url": "https://example.com/article"}]}]}]}


class OpenAIClientTests(unittest.TestCase):
    def test_citation_does_not_remove_annotated_claim(self):
        parsed = parse_response(response_fixture())
        self.assertIn("Fait de test daté.", parsed["body"])
        self.assertIn("[1](https://example.com/article)", parsed["body"])
        self.assertEqual(len(parsed["citations"]), 1)

    def test_rejects_no_search_no_sources_and_truncated_output(self):
        no_search = response_fixture()
        no_search["output"] = no_search["output"][1:]
        no_cites = response_fixture()
        no_cites["output"][1]["content"][0]["annotations"] = []
        truncated = {**response_fixture(), "status": "incomplete"}
        malformed = response_fixture()
        malformed["output"][1]["content"] = None
        for payload in (no_search, no_cites, truncated, malformed):
            with self.subTest(payload=payload), self.assertRaises(BriefError):
                parse_response(payload)

    def test_citation_bounds_and_unsafe_url(self):
        for fields in ({"end_index": 9999}, {"url": "javascript:alert(1)"}, {"url": "https://secret@example.com"}):
            payload = response_fixture()
            payload["output"][1]["content"][0]["annotations"][0].update(fields)
            with self.assertRaises(BriefError):
                parse_response(payload)
        self.assertEqual(public_url("https://example.com/a(b)"), "https://example.com/a%28b%29")

    def test_request_limits_mandatory_live_search_and_no_storage(self):
        session = Mock()
        session.post.return_value = Mock(status_code=200)
        session.post.return_value.json.return_value = response_fixture()
        result = generate("fixture-key", {"public_feeds": []}, session=session)
        request = session.post.call_args.kwargs
        self.assertEqual(request["json"]["tool_choice"], "required")
        self.assertTrue(request["json"]["tools"][0]["external_web_access"])
        self.assertFalse(request["json"]["store"])
        self.assertLessEqual(request["json"]["max_tool_calls"], 5)
        self.assertEqual(request["headers"], {"Authorization": "Bearer fixture-key"})
        self.assertNotIn("fixture-key", str(result))
        self.assertNotIn("fixture-key", json.dumps(request["json"]))

    def test_paid_post_never_retried_and_errors_do_not_leak(self):
        session = Mock()
        session.post.side_effect = requests.Timeout("private-fixture-key")
        with self.assertRaises(BriefError) as caught:
            generate("fixture-key", {}, session=session)
        self.assertNotIn("private-fixture-key", str(caught.exception))
        self.assertEqual(session.post.call_count, 1)
        session.post.side_effect = None
        session.post.return_value = Mock(status_code=429, text="private-fixture-key")
        with self.assertRaises(BriefError) as caught:
            generate("fixture-key", {}, session=session)
        self.assertNotIn("private-fixture-key", str(caught.exception))

    def test_public_context_excludes_private_rows_raw_and_error_text(self):
        from data.loaders.gie import normalize
        from tests.test_market_feeds import gas_row
        rows, _ = normalize([{"data": [gas_row()]}], "EU")
        feeds = [("GIE AGSI", "EU", {"error": "PRIVATE-FIXTURE", "batch": {
            "retrieved_at": "2026-01-03T12:00:00Z", "raw_payload": "PRIVATE-FIXTURE",
            "source_url": "PRIVATE-FIXTURE", "clean_records": rows, "notes": "PRIVATE-FIXTURE"}}),
            ("Journal", "personal", {"batch": {"notes": "PRIVATE-FIXTURE"}})]
        context = build_context(feeds, datetime(2026, 1, 4, 12, tzinfo=timezone.utc))
        self.assertNotIn("PRIVATE-FIXTURE", json.dumps(context))
        self.assertEqual(len(context["public_feeds"]), 1)
        self.assertTrue(context["public_feeds"][0]["refresh_failed"])
        self.assertEqual(context["public_feeds"][0]["metrics"]["storage_full"]["value"], 70)

    def test_billing_error_is_actionable_and_malformed_error_stays_safe(self):
        session = Mock()
        session.post.return_value = Mock(status_code=429)
        session.post.return_value.json.return_value = {"error": {"code": "insufficient_quota", "message": "private-fixture"}}
        with self.assertRaisesRegex(BriefError, "facturation"):
            generate("fixture-key", {}, session=session)
        session.post.return_value.json.return_value = {"error": {"code": ["private-fixture"]}}
        with self.assertRaisesRegex(BriefError, "Quota"):
            generate("fixture-key", {}, session=session)


class BriefWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 22, 10, tzinfo=timezone.utc)
        self.store = Mock()
        self.store.results.return_value = []
        self.store.runs.return_value = []
        self.store.claim.return_value = {"id": "fixture-run"}
        self.generate = Mock(return_value=parse_response(response_fixture()))

    def run_brief(self, **kwargs):
        return create_daily(self.store, [], "fixture-key", now=self.now, generator=self.generate, **kwargs)

    def test_six_am_paris_in_winter_summer_and_dst(self):
        for value, expected in [("2026-01-15T04:59:00+00:00", "2026-01-14"),
                                ("2026-01-15T05:00:00+00:00", "2026-01-15"),
                                ("2026-07-15T03:59:00+00:00", "2026-07-14"),
                                ("2026-07-15T04:00:00+00:00", "2026-07-15"),
                                ("2026-03-29T04:00:00+00:00", "2026-03-29"),
                                ("2026-10-25T05:00:00+00:00", "2026-10-25")]:
            with self.subTest(value=value):
                self.assertEqual(edition_day(datetime.fromisoformat(value)).isoformat(), expected)
        with self.assertRaises(ValueError):
            edition_day(datetime(2026, 1, 1))

    def test_before_six_does_not_call_api_or_claim(self):
        result = create_daily(self.store, [], "fixture-key", now=datetime(2026, 7, 1, 3, tzinfo=timezone.utc), generator=self.generate)
        self.assertEqual(result["state"], "before_six")
        self.generate.assert_not_called()
        self.store.claim.assert_not_called()

    def test_success_saved_once_with_context_and_sources(self):
        result = self.run_brief()
        self.assertEqual(result["state"], "success")
        saved = self.store.save.call_args.args[0]
        self.assertEqual(saved["brief_date"], "2026-09-22")
        self.assertEqual(saved["as_of"], self.now.isoformat())
        self.assertTrue(saved["citations"])
        self.assertNotIn("fixture-key", str(saved))

    def test_successful_existing_edition_prevents_any_new_call(self):
        self.store.results.return_value = [{"status": "success", "run_id": "old"}]
        self.assertEqual(self.run_brief(retry=True)["state"], "success")
        self.generate.assert_not_called()
        self.store.claim.assert_not_called()

    def test_concurrent_claim_loser_does_not_spend(self):
        self.store.claim.return_value = None
        self.assertEqual(self.run_brief()["state"], "running")
        self.generate.assert_not_called()

    def test_failure_is_archived_and_requires_explicit_retry(self):
        self.generate.side_effect = BriefError("Fixture unavailable")
        self.assertEqual(self.run_brief()["state"], "failed")
        self.assertEqual(self.store.save.call_args.args[0]["error_message"], "Fixture unavailable")
        self.store.runs.return_value = [{"id": "fixture-run", "attempt": 1, "started_at": self.now.isoformat()}]
        self.store.results.return_value = [{"run_id": "fixture-run", "status": "failed"}]
        self.generate.reset_mock()
        self.assertEqual(self.run_brief()["state"], "failed")
        self.generate.assert_not_called()
        self.run_brief(retry=True)
        self.store.claim.assert_called_with(date(2026, 9, 22), 2)

    def test_interrupted_claim_waits_fifteen_minutes_and_caps_attempts(self):
        self.store.runs.return_value = [{"id": "fixture-run", "attempt": 1, "started_at": self.now.isoformat()}]
        self.assertEqual(self.run_brief(retry=True)["state"], "running")
        self.generate.assert_not_called()
        self.store.runs.return_value[0].update(attempt=2, started_at=(self.now - timedelta(minutes=20)).isoformat())
        self.assertEqual(self.run_brief(retry=True)["state"], "attempt_limit")
        self.generate.assert_not_called()

    def test_failed_database_save_returns_recoverable_result_without_new_call(self):
        self.store.save.side_effect = StorageError("Fixture save failure")
        result = self.run_brief()
        self.assertEqual(result["state"], "unsaved")
        self.assertEqual(result["report"]["status"], "success")
        self.assertEqual(self.generate.call_count, 1)

    def test_missing_key_never_claims_or_spends(self):
        with self.assertRaises(BriefError):
            create_daily(self.store, [], "", now=self.now, generator=self.generate)
        self.store.claim.assert_not_called()

    def test_invalid_local_context_does_not_consume_an_attempt(self):
        with patch("briefing.service.build_context", side_effect=ValueError("private-fixture")):
            with self.assertRaises(BriefError) as caught:
                self.run_brief()
        self.assertNotIn("private-fixture", str(caught.exception))
        self.store.claim.assert_not_called()
        self.generate.assert_not_called()


class BriefStoreTests(unittest.TestCase):
    def test_owner_filters_claim_collision_and_save_owner_override(self):
        client = Mock()
        query = client.table.return_value
        for method in ("select", "eq", "order", "limit", "upsert"):
            getattr(query, method).return_value = query
        query.execute.return_value.data = []
        store = BriefStore(client, "owner-fixture")
        store.latest()
        self.assertIn(call("user_id", "owner-fixture"), query.eq.call_args_list)
        self.assertIsNone(store.claim(date(2026, 1, 1), 1))
        self.assertTrue(query.upsert.call_args.kwargs["ignore_duplicates"])
        store.save({"run_id": "fixture-run", "user_id": "other-fixture"})
        self.assertEqual(query.upsert.call_args.args[0]["user_id"], "owner-fixture")


class BriefDisplayTests(unittest.TestCase):
    def setUp(self):
        from streamlit.testing.v1 import AppTest
        self.now = datetime(2026, 9, 22, 10, tzinfo=timezone.utc)
        self.report = {**parse_response(response_fixture()), "status": "success", "run_id": "fixture-run",
                       "brief_date": "2026-09-22", "generated_at": self.now.isoformat(),
                       "as_of": self.now.isoformat(), "model": "fixture-model", "prompt_version": "fixture-v1"}
        self.store = Mock()
        self.store.runs.return_value = []
        self.store.results.return_value = [self.report]
        self.store.latest.return_value = None
        self.app = AppTest.from_string("from components.brief import render_brief\nrender_brief([])")
        self.app.session_state["db_user"] = "fixture-user"
        self.app.session_state["db_client"] = Mock()
        for target, kwargs in [("components.brief.BriefStore", {"return_value": self.store}),
                               ("components.brief.setting", {"return_value": "fixture-key"}),
                               ("components.brief.datetime", {"wraps": datetime})]:
            patcher = patch(target, **kwargs)
            mocked = patcher.start()
            self.addCleanup(patcher.stop)
            if target.endswith("datetime"):
                mocked.now.return_value = self.now

    def test_read_and_rerun_never_generate_and_citations_are_visible(self):
        with patch("components.brief.create_daily") as generate_daily:
            self.app.run().run()
            self.assertFalse(self.app.exception)
            self.assertTrue(any("[1](https://example.com/article)" in m.value for m in self.app.markdown))
            self.assertFalse(any(b.label == "Générer le brief du jour" for b in self.app.button))
            self.store.results.return_value = []
            self.app.run()
            self.assertTrue(any(b.label == "Générer le brief du jour" for b in self.app.button))
            generate_daily.assert_not_called()

    def test_unsaved_brief_retries_only_database_save(self):
        self.app.session_state["brief_unsaved"] = self.report
        with patch("components.brief.create_daily") as generate_daily:
            self.app.run()
            next(b for b in self.app.button if b.label == "Réessayer la sauvegarde du brief").click().run()
            self.assertFalse(self.app.exception)
            self.store.save.assert_called_once_with(self.report)
            self.assertNotIn("brief_unsaved", self.app.session_state)
            generate_daily.assert_not_called()


class MorningChartsTests(unittest.TestCase):
    def test_card_escapes_labels_and_shows_physical_direction(self):
        html = card_html("<script>fixture</script>", 70, "%", -1, "pp", "Gas day fixture")
        self.assertNotIn("<script>", html)
        self.assertIn("↓ -1.00 pp", html)
        self.assertIn("70.00", html)
        self.assertIn("—", card_html("Fixture", None, "%", None, "pp", "Missing"))

    def test_sparkline_retains_missing_day_gap(self):
        from tests.test_market_analytics import row
        fig = spark_figure([row("2026-01-01", 70), row("2026-01-03", 71)], "storage_full")
        self.assertEqual(len(fig.data[0].x), 3)
        self.assertFalse(fig.data[0].connectgaps)

    def test_weather_chart_distinguishes_18_degree_base(self):
        from tests.test_market_analytics import row
        rows = [row("2026-01-01", 10), row("2026-01-02", 20)]
        chart = weather_figure(rows)
        self.assertNotEqual(chart.data[0].marker.color[0], chart.data[0].marker.color[1])
        self.assertEqual(chart.layout.shapes[0].y0, 18)
