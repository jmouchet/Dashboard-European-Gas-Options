from types import SimpleNamespace
from unittest.mock import MagicMock
import unittest
from database.repository import PreviewRepository, SupabaseRepository, StorageError


class RepositoryTests(unittest.TestCase):
    def test_preview_sessions_are_isolated(self):
        one, two = PreviewRepository({}), PreviewRepository({})
        one.insert("journal_entries", {"id": "1", "sections": {"fact": "Test"}})
        self.assertEqual(two.list("journal_entries"), [])

    def test_preview_copies_and_safe_retries(self):
        repo = PreviewRepository({})
        row = {"id": "1", "sections": {"fact": "Test"}}
        repo.insert("journal_entries", row)
        repo.insert("journal_entries", row)
        row["sections"]["fact"] = "Changed"
        result = repo.list("journal_entries")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sections"]["fact"], "Test")
        result.clear()
        self.assertEqual(len(repo.list("journal_entries")), 1)

    def test_curated_content_cannot_be_written_by_app(self):
        for repo in [PreviewRepository({}), SupabaseRepository(MagicMock(), "me")]:
            with self.subTest(repo=type(repo).__name__), self.assertRaises(ValueError):
                repo.insert("knowledge_articles", {"id": "1"})

    def test_reads_paginate_and_scope_to_user(self):
        client = MagicMock()
        query = client.table.return_value
        for method in ["select", "eq", "order", "range"]:
            getattr(query, method).return_value = query
        query.execute.side_effect = [SimpleNamespace(data=[{"id": str(i)} for i in range(500)]), SimpleNamespace(data=[{"id": "500"}])]
        rows = SupabaseRepository(client, "me").list("manual_observations")
        self.assertEqual(len(rows), 501)
        query.eq.assert_called_with("user_id", "me")
        self.assertEqual(query.range.call_args_list[1].args, (500, 999))

    def test_write_owner_cannot_be_overridden(self):
        client = MagicMock()
        SupabaseRepository(client, "me").insert("journal_entries", {"id": "1", "user_id": "someone-else"})
        self.assertEqual(client.table.return_value.insert.call_args.args[0]["user_id"], "me")

    def test_errors_do_not_expose_provider_body(self):
        client = MagicMock()
        client.table.side_effect = RuntimeError("secret-token private-journal-text")
        repo = SupabaseRepository(client, "me")
        with self.assertLogs("database.repository", level="WARNING") as logs:
            with self.assertRaises(StorageError) as read_error:
                repo.list("journal_entries")
            with self.assertRaises(StorageError) as write_error:
                repo.insert("journal_entries", {"id": "1"})
        for text in [str(read_error.exception), str(write_error.exception), " ".join(logs.output)]:
            self.assertNotIn("secret-token", text)
            self.assertNotIn("private-journal-text", text)


if __name__ == "__main__":
    unittest.main()
