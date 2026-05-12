import os
import sqlite3
from pathlib import Path

from app.config import Settings
from app.database import init_db, get_connection, next_issue_no, save_source, save_article


def test_settings_loads_defaults_and_env(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTHOR_NAME", "超级发")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'superfa.db'}")
    settings = Settings.from_env()
    assert settings.author_name == "超级发"
    assert settings.database_path == tmp_path / "superfa.db"
    assert settings.auto_publish is False
    assert settings.aihot_skill_url == "https://aihot.virxact.com"
    assert "Mozilla/5.0" in settings.aihot_user_agent


def test_init_db_creates_required_tables(tmp_path):
    db_path = tmp_path / "superfa.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"articles", "sources", "settings"}.issubset(tables)


def test_next_issue_no_is_separate_per_content_type(tmp_path):
    db_path = tmp_path / "superfa.db"
    init_db(db_path)
    assert next_issue_no(db_path, "briefing") == 1
    assert next_issue_no(db_path, "interpretation") == 1
    assert next_issue_no(db_path, "briefing") == 2


def test_save_source_and_article_return_ids(tmp_path):
    db_path = tmp_path / "superfa.db"
    init_db(db_path)
    source_id = save_source(db_path, {"date": "2026-05-09", "title": "新闻", "url": "https://x", "source": "AIHot", "summary": "摘要", "content": "正文", "category": "AI工具", "tags": ["AI"], "score": 8, "selected": 1, "source_provider": "aihot_skill", "raw": {"a": 1}})
    article_id = save_article(db_path, {"content_type": "briefing", "issue_no": 1, "date": "2026-05-09", "title": "标题", "digest": "摘要", "content_markdown": "md", "content_html": "html", "cover_prompt": "prompt", "status": "generated"})
    assert source_id == 1
    assert article_id == 1
