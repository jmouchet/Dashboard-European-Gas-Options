"""Session preview or authenticated Supabase. Never fall back after an API error."""
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)
WRITABLE = {"manual_observations", "journal_entries", "predictions", "quiz_attempts"}
READABLE = WRITABLE | {"knowledge_articles", "questions", "learning_progress"}


class StorageError(Exception):
    pass


class PreviewRepository:
    def __init__(self, rows: dict):
        self.rows = rows

    def list(self, table: str) -> list[dict]:
        if table not in READABLE:
            raise ValueError("Unknown table.")
        return deepcopy(self.rows.get(table, []))

    def insert(self, table: str, row: dict) -> None:
        if table not in WRITABLE:
            raise ValueError("Table is read-only.")
        records = self.rows.setdefault(table, [])
        if any(r["id"] == row["id"] for r in records):
            return  # Safe retry of the same request.
        records.append(deepcopy(row))


class SupabaseRepository:
    def __init__(self, client, user_id: str):
        self.client = client
        self.user_id = user_id

    def list(self, table: str) -> list[dict]:
        if table not in READABLE:
            raise ValueError("Unknown table.")
        try:
            # PostgREST defaults to a limited result set. Fetch every page explicitly.
            rows = []
            offset = 0
            while True:
                query = self.client.table(table).select("*")
                if table in WRITABLE or table == "learning_progress":
                    query = query.eq("user_id", self.user_id)
                order = "article_id" if table == "learning_progress" else "id"
                page = query.order(order).range(offset, offset + 499).execute().data
                rows.extend(page)
                if len(page) < 500:
                    return rows
                offset += 500
        except Exception as exc:
            # Do not log provider exception bodies: they may contain tokens or user text.
            logger.warning("database_read_failed table=%s error_type=%s", table, type(exc).__name__)
            raise StorageError("Data unavailable. Check your connection, sign-in, and database setup.") from None

    def insert(self, table: str, row: dict) -> None:
        if table not in WRITABLE:
            raise ValueError("Table is read-only.")
        try:
            self.client.table(table).insert({**row, "user_id": self.user_id}).execute()
        except Exception as exc:
            logger.warning("database_write_failed table=%s error_type=%s", table, type(exc).__name__)
            raise StorageError("Save was not confirmed. Check Data / Admin before retrying; your input is still shown.") from None
