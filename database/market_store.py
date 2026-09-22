"""Append-only feed snapshots and ingestion audit using the current user's JWT."""
from datetime import datetime, timezone
import logging
from database.repository import StorageError

logger = logging.getLogger(__name__)


class MarketStore:
    def __init__(self, client, user_id):
        self.client, self.user_id = client, user_id

    def latest(self, table, source, scope):
        if table not in {"market_feed_batches", "ingestion_runs"}:
            raise ValueError("Unsupported market table.")
        order = "retrieved_at" if table == "market_feed_batches" else "finished_at"
        try:
            result = (self.client.table(table).select("*").eq("user_id", self.user_id)
                      .eq("source", source).eq("scope", scope).order(order, desc=True).limit(1).execute())
            return result.data[0] if result.data else None
        except Exception as exc:
            logger.warning("market_read_failed table=%s error_type=%s", table, type(exc).__name__)
            raise StorageError("Market storage is unavailable. Apply migration 002, or check the connection and sign-in.") from None

    def save_batch(self, value):
        try:
            self.client.table("market_feed_batches").upsert(
                {**value, "user_id": self.user_id}, on_conflict="user_id,source,scope,payload_hash",
                ignore_duplicates=True).execute()
        except Exception as exc:
            logger.warning("market_batch_save_failed error_type=%s", type(exc).__name__)
            raise StorageError("Fetched market data could not be saved. Check migration 002 and the connection.") from None

    def log_run(self, source, scope, started_at, status, count=0, message=""):
        try:
            self.client.table("ingestion_runs").insert({
                "user_id": self.user_id, "source": source, "scope": scope, "started_at": started_at,
                "finished_at": datetime.now(timezone.utc).isoformat(), "status": status,
                "record_count": count, "message": message,
            }).execute()
        except Exception as exc:
            logger.warning("ingestion_log_failed error_type=%s", type(exc).__name__)
            raise StorageError("The ingestion audit could not be saved. Check database access.") from None
