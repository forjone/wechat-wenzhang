from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from app.agents.briefing_writer import generate_briefing
from app.agents.interpretation_writer import generate_interpretation
from app.agents.image_generator import generate_article_images
from app.config import Settings
from app.database import (
    get_article,
    get_connection,
    init_db,
    next_issue_no,
    save_article,
    save_source,
    update_article_draft,
)
from app.main import create_draft_if_requested, prepare_news
from app.outputs import save_article_outputs
from app.render.markdown_to_html import markdown_to_wechat_html


def ensure_web_db(db_path: str | Path) -> None:
    init_db(db_path)


def list_sources(db_path: str | Path, date: str | None = None) -> list[dict[str, Any]]:
    ensure_web_db(db_path)
    sql = "SELECT * FROM sources"
    params: tuple[Any, ...] = ()
    if date:
        sql += " WHERE date = ?"
        params = (date,)
    sql += " ORDER BY id DESC LIMIT 100"
    with get_connection(db_path) as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def list_articles(db_path: str | Path) -> list[dict[str, Any]]:
    ensure_web_db(db_path)
    with get_connection(db_path) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM articles ORDER BY id DESC LIMIT 100").fetchall()]


def dashboard_counts(db_path: str | Path) -> dict[str, int]:
    ensure_web_db(db_path)
    with get_connection(db_path) as conn:
        source_count = conn.execute("SELECT count(*) FROM sources").fetchone()[0]
        article_count = conn.execute("SELECT count(*) FROM articles").fetchone()[0]
        draft_count = conn.execute("SELECT count(*) FROM articles WHERE draft_id IS NOT NULL AND draft_id != ''").fetchone()[0]
    return {"source_count": source_count, "article_count": article_count, "draft_count": draft_count}


def collect_sources_for_date(settings: Settings, target_date: str) -> int:
    ensure_web_db(settings.database_path)
    news = prepare_news(settings, target_date)
    count = 0
    for item in news:
        save_source(settings.database_path, {**item, "selected": 0, "date": item.get("date") or target_date})
        count += 1
    return count


def get_source(db_path: str | Path, source_id: int) -> dict[str, Any] | None:
    ensure_web_db(db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    return dict(row) if row else None


def generate_article_from_source(
    settings: Settings,
    source_id: int,
    *,
    content_type: str,
    theme: str,
    wechat_account: str,
    create_draft: bool,
) -> int:
    source = get_source(settings.database_path, source_id)
    if source is None:
        raise ValueError("SOURCE_NOT_FOUND")
    news_item = {
        "title": source.get("title"),
        "url": source.get("url"),
        "source": source.get("source"),
        "summary": source.get("summary"),
        "content": source.get("content") or source.get("summary"),
        "category": source.get("category"),
        "score": source.get("score") or 0,
        "date": source.get("date"),
        "source_provider": source.get("source_provider"),
    }
    target_date = source.get("date") or ""
    if content_type == "briefing":
        issue_no = next_issue_no(settings.database_path, "briefing")
        article = generate_briefing([news_item], target_date, issue_no, max_items=1)
    elif content_type == "interpretation":
        issue_no = next_issue_no(settings.database_path, "interpretation")
        article = generate_interpretation([news_item], target_date, issue_no)
    else:
        raise ValueError("UNSUPPORTED_CONTENT_TYPE")

    article.update(generate_article_images(article, output_dir=settings.image_output_dir))
    article["content_html"] = markdown_to_wechat_html(article["content_markdown"], content_type=article["content_type"], theme=theme)
    article["topic"] = source.get("title")
    article["source_title"] = source.get("title")
    article["source_url"] = source.get("url")
    output_paths = save_article_outputs(article, output_dir=settings.article_output_dir)
    article["files"] = {key: str(path) for key, path in output_paths.items()}
    article_id = save_article(settings.database_path, article)
    draft_id = create_draft_if_requested(settings, article, create_draft, wechat_account, retry_delay_seconds=0)
    if draft_id:
        update_article_draft(settings.database_path, article_id, draft_id, "draft_created")
    return article_id
