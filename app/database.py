from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_type TEXT,
  issue_no INTEGER,
  date TEXT,
  title TEXT,
  digest TEXT,
  source_title TEXT,
  source_url TEXT,
  topic TEXT,
  content_markdown TEXT,
  content_html TEXT,
  cover_prompt TEXT,
  cover_path TEXT,
  draft_id TEXT,
  publish_id TEXT,
  status TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  title TEXT,
  url TEXT,
  source TEXT,
  summary TEXT,
  content TEXT,
  category TEXT,
  tags TEXT,
  score INTEGER,
  selected INTEGER,
  source_provider TEXT,
  raw_json TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT
);
"""


def _resolve(db_path: str | Path) -> Path:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(_resolve(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)


def next_issue_no(db_path: str | Path, content_type: str) -> int:
    key = f"last_{content_type}_issue_no"
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        current = int(row["value"]) if row else 0
        new_value = current + 1
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(new_value)),
        )
        return new_value


def save_source(db_path: str | Path, item: dict[str, Any]) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO sources(date, title, url, source, summary, content, category, tags, score, selected, source_provider, raw_json, created_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("date"), item.get("title"), item.get("url"), item.get("source"),
                item.get("summary"), item.get("content"), item.get("category"),
                json.dumps(item.get("tags", []), ensure_ascii=False), item.get("score", 0),
                item.get("selected", 0), item.get("source_provider", "aihot_skill"),
                json.dumps(item.get("raw", item.get("raw_json", {})) or {"published_at": item.get("published_at")}, ensure_ascii=False), now,
            ),
        )
        return int(cursor.lastrowid)


def save_article(db_path: str | Path, article: dict[str, Any]) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO articles(content_type, issue_no, date, title, digest, source_title, source_url, topic, content_markdown, content_html, cover_prompt, cover_path, draft_id, publish_id, status, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                article.get("content_type"), article.get("issue_no"), article.get("date"), article.get("title"),
                article.get("digest"), article.get("source_title"), article.get("source_url"), article.get("topic"),
                article.get("content_markdown"), article.get("content_html"), article.get("cover_prompt"), article.get("cover_path"),
                article.get("draft_id"), article.get("publish_id"), article.get("status", "generated"), now, now,
            ),
        )
        return int(cursor.lastrowid)


def update_article_draft(db_path: str | Path, article_id: int, draft_id: str, status: str = "draft_created") -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        conn.execute("UPDATE articles SET draft_id = ?, status = ?, updated_at = ? WHERE id = ?", (draft_id, status, now, article_id))


def update_article_publish(db_path: str | Path, article_id: int, publish_id: str, status: str = "published") -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        conn.execute("UPDATE articles SET publish_id = ?, status = ?, updated_at = ? WHERE id = ?", (publish_id, status, now, article_id))


def get_article(db_path: str | Path, article_id: int) -> dict[str, Any] | None:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    return dict(row) if row else None
