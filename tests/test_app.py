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
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
        self.app.secrets["SUPABASE_URL"] = ""
        self.app.secrets["SUPABASE_ANON_KEY"] = ""
        self.app.run()

    def page(self, name):
        self.app.switch_page(f"views/{name}.py").run()
        self.assertFalse(self.app.exception)

    def test_morning_starts_empty(self):
        self.assertFalse(self.app.exception)
        self.assertEqual([m.value for m in self.app.metric], ["—"] * 4)

    def test_knowledge_page(self):
        self.page("knowledge")

    def test_daily_learning_page(self):
        self.page("daily_learning")

    def test_quiz_page(self):
        self.page("quiz")

    def test_journal_page(self):
        self.page("journal")

    def test_admin_page(self):
        self.page("admin")

    def test_manual_observation_workflow(self):
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
        self.assertIn("80.00", [m.value for m in app.metric])

    def test_quiz_captures_answer_before_grading(self):
        self.page("quiz")
        app = self.app
        app.text_area[0].input("2,000 GWh")
        app.radio[0].set_value(4)
        next(b for b in app.button if b.label == "Reveal reference answer").click().run()
        self.assertFalse(app.exception)
        app.radio[0].set_value(1.0).run()
        next(b for b in app.button if b.label == "Save attempt").click().run()
        self.assertFalse(app.exception)
        row = app.session_state["preview_rows"]["quiz_attempts"][0]
        self.assertEqual(row["confidence"], 4)
        self.assertEqual(row["user_answer"], "2,000 GWh")
        self.assertEqual(row["score"], 1)

    def test_journal_save(self):
        self.page("journal")
        app = self.app
        next(t for t in app.text_area if t.label == "Market regime").input("Test thesis")
        next(b for b in app.button if b.label == "Save journal entry").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state["preview_rows"]["journal_entries"]), 1)


if __name__ == "__main__":
    unittest.main()
