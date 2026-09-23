"""Owner-scoped, append-only daily claims and AI results; no privileged DB key."""
import logging
from uuid import uuid4
from database.repository import StorageError

logger = logging.getLogger(__name__)


class BriefStore:
    def __init__(self, client, user_id):
        self.client, self.user_id = client, user_id

    def _read(self, table, day=None, successful=False):
        try:
            query = self.client.table(table).select("*").eq("user_id", self.user_id)
            if day:
                query = query.eq("brief_date", day.isoformat())
            if successful:
                query = query.eq("status", "success")
            order = "started_at" if table == "market_brief_runs" else "generated_at"
            return query.order(order, desc=True).limit(2 if day else 1).execute().data
        except Exception as exc:
            logger.warning("brief_read_failed error_type=%s", type(exc).__name__)
            raise StorageError("Brief indisponible : vérifie la connexion et la migration 003_market_briefs.sql.") from None

    def runs(self, day):
        return self._read("market_brief_runs", day)

    def results(self, day):
        return self._read("market_briefs", day)

    def latest(self):
        rows = self._read("market_briefs", successful=True)
        return rows[0] if rows else None

    def claim(self, day, attempt):
        row = {"id": str(uuid4()), "user_id": self.user_id, "brief_date": day.isoformat(), "attempt": attempt}
        try:
            # ON CONFLICT DO NOTHING: only the caller that inserted may spend.
            data = self.client.table("market_brief_runs").upsert(
                row, on_conflict="user_id,brief_date,attempt", ignore_duplicates=True).execute().data
            return data[0] if data else None
        except Exception as exc:
            logger.warning("brief_claim_failed error_type=%s", type(exc).__name__)
            raise StorageError("Réservation du brief non confirmée. Aucun appel OpenAI n'a été lancé.") from None

    def save(self, row):
        try:
            self.client.table("market_briefs").upsert(
                {**row, "user_id": self.user_id}, on_conflict="run_id", ignore_duplicates=True).execute()
        except Exception as exc:
            logger.warning("brief_save_failed error_type=%s", type(exc).__name__)
            raise StorageError("Le résultat du brief n'a pas pu être archivé dans Supabase.") from None
