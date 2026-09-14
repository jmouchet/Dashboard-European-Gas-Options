"""Generate reviewable SQL; never connects to a database or edits existing rows."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from learning.content import get_articles, get_questions


def literal(value):
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
    return "'" + value.replace("'", "''") + "'"


def build_seed() -> str:
    lines = ["-- Generated from learning/content.py. Existing IDs are preserved.", "begin;"]
    for table, rows in [("knowledge_articles", get_articles()), ("questions", get_questions())]:
        for row in rows:
            row = {k: v for k, v in row.items() if k not in {"sections", "related"}}
            columns = ", ".join(row)
            values = ", ".join(literal(v) for v in row.values())
            lines.append(f"insert into public.{table} ({columns}) values ({values}) on conflict (id) do nothing;")
    return "\n".join(lines + ["commit;", ""])


if __name__ == "__main__":
    destination = ROOT / "database" / "seed.sql"
    destination.write_text(build_seed(), encoding="utf-8")
    print(f"Wrote {destination.name}: 10 articles and 20 questions.")
