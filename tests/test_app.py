"""Real Streamlit smoke/workflow tests, skipped visibly if UI dependencies are absent."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

READY = all(importlib.util.find_spec(name) for name in ["streamlit", "plotly", "pandas"])
ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(READY, "Install requirements.txt to run Streamlit smoke tests")
class AppTests(unittest.TestCase):
    def setUp(self):
        from streamlit.testing.v1 import AppTest
        self.env = patch.dict("os.environ", {"SUPABASE_URL": "", "SUPABASE_ANON_KEY": ""})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=45)
        self.app.secrets["SUPABASE_URL"] = ""
        self.app.secrets["SUPABASE_ANON_KEY"] = ""
        self.app.secrets["OPENAI_API_KEY"] = ""
        self.app.run()

    def page(self, name):
        self.app.switch_page(f"views/{name}.py").run()
        self.assertFalse(self.app.exception)

    def test_morning_starts_empty(self):
        self.assertFalse(self.app.exception)
        self.assertTrue(all(m.value == "—" for m in self.app.metric))
        self.assertGreaterEqual(len(self.app.metric), 2)
        self.assertNotIn("Today's investigation", [s.value for s in self.app.subheader])
        self.assertNotIn("Observation history", [s.value for s in self.app.subheader])
        self.assertFalse(any(b.label == "Save observation" for b in self.app.button))

    def test_new_market_pages(self):
        for name in ("markets", "fundamentals", "physical", "events"):
            with self.subTest(page=name):
                self.page(name)

    def test_fundamental_sections(self):
        self.page("fundamentals")
        self.app.radio[0].set_value("LNG").run()
        self.assertFalse(self.app.exception)
        self.app.radio[0].set_value("Weather").run()
        self.assertFalse(self.app.exception)

    def test_only_market_and_workspace_navigation(self):
        import streamlit as st
        with patch("streamlit.navigation", wraps=st.navigation) as navigation:
            self.app.run()
        sections = navigation.call_args.args[0]
        self.assertEqual(set(sections), {"Market Dashboard", "Workspace"})
        self.assertEqual([p.title for p in sections["Market Dashboard"]],
                         ["Morning", "Markets", "Fundamentals", "Physical System", "Events"])

    def test_journal_page(self):
        self.page("journal")

    def test_admin_page(self):
        self.page("admin")

    def test_manual_observation_workflow(self):
        self.page("admin")
        app = self.app
        app.selectbox(key="input_series").select("storage").run()
        values = {"Exact contract or geographic scope": "EU test fixture", "Value": "80",
                  "Observation timestamp with timezone": "2026-01-01T00:00:00Z",
                  "Source name": "Test fixture", "Public source URL": "https://example.com"}
        for widget in app.text_input:
            if widget.label in values:
                widget.input(values[widget.label])
        next(b for b in app.button if b.label == "Save observation").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["preview_rows"]["manual_observations"][0]["clean_value"], 80)
        self.assertTrue(any("Added to this session" in s.value for s in app.success))

    def test_journal_save(self):
        self.page("journal")
        app = self.app
        next(t for t in app.text_area if t.label == "Market regime").input("Test thesis")
        next(b for b in app.button if b.label == "Save journal entry").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state["preview_rows"]["journal_entries"]), 1)

    def test_asset_profile_save_and_display(self):
        self.page("physical")
        values = {"Asset name": "Fixture storage", "Asset country": "DE", "Operator": "Fixture operator", "Public source URL": "https://example.com"}
        for widget in self.app.text_input:
            if widget.label in values:
                widget.input(values[widget.label])
        next(b for b in self.app.button if b.label == "Save asset profile").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.session_state["preview_rows"]["assets"]), 1)

    def test_event_save_and_display(self):
        self.page("events")
        values = {"Affected entity": "Fixture entity", "Headline": "Fixture event", "Public source URL": "https://example.com"}
        for widget in self.app.text_input:
            if widget.label in values:
                widget.input(values[widget.label])
        next(t for t in self.app.text_area if t.label == "Sourced facts").input("Synthetic test facts")
        next(b for b in self.app.button if b.label == "Save market event").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.session_state["preview_rows"]["market_events"]), 1)

    def test_populated_gie_cards_and_fundamentals(self):
        from data.loaders.gie import normalize
        from tests.test_market_feeds import gas_row
        normalized, _ = normalize([{"data": [gas_row("2026-01-01", full="70"), gas_row("2026-01-02", full="71")]}], "EU")
        result = {"batch": {"clean_records": normalized, "quality_notes": [], "source_url": "https://example.com", "retrieved_at": "2026-01-03T12:00:00Z"},
                  "last_success": "2026-01-03T12:00:00Z", "error": None}
        empty = {"batch": None, "last_success": None, "error": "Fixture feed unavailable"}
        with patch("components.market_data.load_feed", side_effect=lambda source, scope, force=False: result if source == "GIE AGSI" else empty):
            self.app.run()
            self.assertFalse(self.app.exception)
            self.assertGreaterEqual(len(self.app.get("plotly_chart")), 4)
            self.assertTrue(any(s.value == "Stockage · Où en est-on ?" for s in self.app.subheader))
            self.page("fundamentals")


if __name__ == "__main__":
    unittest.main()
