import base64
import json
from pathlib import Path
import unittest
from learning.content import get_articles, get_questions
from learning.review import summarize_attempts
from scripts.build_seed import build_seed
from utils.config import validate_settings


class LearningTests(unittest.TestCase):
    def test_curriculum_is_complete_and_linked(self):
        articles, questions = get_articles(), get_questions()
        self.assertEqual(len(articles), 10)
        self.assertEqual(len(questions), 20)
        ids = {a["id"] for a in articles}
        self.assertEqual(len(ids), 10)
        self.assertEqual(len({q["id"] for q in questions}), 20)
        for article in articles:
            self.assertEqual(sum(q["article_id"] == article["id"] for q in questions), 2)
            self.assertTrue(article["source_urls"])
            self.assertIn("### Historical example", article["content_markdown"])
            self.assertIn("Illustrative", article["content_markdown"])

    def test_seed_matches_bundled_content(self):
        path = Path(__file__).resolve().parents[1] / "database/seed.sql"
        self.assertEqual(path.read_text(encoding="utf-8"), build_seed())

    def test_empty_score_is_missing(self):
        self.assertIsNone(summarize_attempts([])["average_score"])

    def test_confident_errors_and_partial_credit(self):
        summary = summarize_attempts([
            {"score": 0, "confidence": 4}, {"score": 0.5, "confidence": 2}, {"score": 1, "confidence": 3},
        ])
        self.assertEqual(summary, {"attempts": 3, "average_score": 0.5, "confident_errors": 1})


class ConfigTests(unittest.TestCase):
    def test_publishable_key_allowed(self):
        validate_settings("https://example.supabase.co", "sb_publishable_example")

    def test_service_role_and_secret_keys_rejected(self):
        role = base64.urlsafe_b64encode(json.dumps({"role": "service_role"}).encode()).decode().rstrip("=")
        for key in ["sb_secret_example", f"a.{role}.b", "invalid"]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_settings("https://example.supabase.co", key)

    def test_legacy_anon_key_allowed(self):
        role = base64.urlsafe_b64encode(json.dumps({"role": "anon"}).encode()).decode().rstrip("=")
        validate_settings("https://example.supabase.co", f"a.{role}.b")

    def test_project_url_without_credentials(self):
        for url in ["http://example.com", "https://user:secret@example.com", "https://"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_settings(url, "sb_publishable_example")


if __name__ == "__main__":
    unittest.main()
