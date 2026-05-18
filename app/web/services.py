from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

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
from app.render.markdown_to_html import THEME_STYLES, default_wechat_theme, markdown_to_wechat_html


CHINA_TZ = timezone(timedelta(hours=8))
ARTICLE_STATUSES = {"generated", "draft_created", "published", "voided", "needs_review"}


def ensure_web_db(db_path: str | Path) -> None:
    init_db(db_path)


def _format_published_time(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return text[:16] if len(text) > 16 else text
    return parsed.strftime("%m-%d %H:%M")


def source_published_time(source: dict[str, Any]) -> str:
    raw = source.get("raw_json") or ""
    if isinstance(raw, str) and raw.strip():
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
    elif isinstance(raw, dict):
        payload = raw
    else:
        payload = {}
    for key in ("publishedAt", "published_at", "date", "time"):
        value = payload.get(key)
        if value:
            return _format_published_time(value)
    return _format_published_time(source.get("published_at") or source.get("date") or "")


def _used_articles_by_url(db_path: str | Path) -> dict[str, list[dict[str, Any]]]:
    ensure_web_db(db_path)
    with get_connection(db_path) as conn:
        rows = [dict(row) for row in conn.execute("SELECT id, content_type, title, source_url, status, draft_id FROM articles WHERE source_url IS NOT NULL AND source_url != ''").fetchall()]
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("source_url") or ""), []).append(row)
    return result


def annotate_source_usage(db_path: str | Path, sources: list[dict[str, Any]]) -> None:
    used_by_url = _used_articles_by_url(db_path)
    seen_titles: set[str] = set()
    for source in sources:
        url = str(source.get("url") or "")
        articles = used_by_url.get(url, [])
        source["used_articles"] = articles
        source["used_status"] = "、".join(f"已生成{'简报' if a.get('content_type') == 'briefing' else '解读'}({a.get('status') or '-'})" for a in articles)
        title_key = str(source.get("title") or "").strip().lower()[:40]
        source["duplicate_hint"] = "疑似重复" if title_key and title_key in seen_titles else ""
        if title_key:
            seen_titles.add(title_key)


def list_sources(db_path: str | Path, date: str | None = None) -> list[dict[str, Any]]:
    ensure_web_db(db_path)
    sql = "SELECT * FROM sources"
    params: tuple[Any, ...] = ()
    if date:
        sql += " WHERE date = ?"
        params = (date,)
    sql += " ORDER BY id DESC LIMIT 100"
    with get_connection(db_path) as conn:
        rows = [dict(row) for row in conn.execute(sql, params).fetchall()]
    for row in rows:
        row["published_time"] = source_published_time(row)
    annotate_source_usage(db_path, rows)
    return rows


def list_articles(db_path: str | Path) -> list[dict[str, Any]]:
    ensure_web_db(db_path)
    with get_connection(db_path) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM articles ORDER BY id DESC LIMIT 100").fetchall()]


def list_drafts(db_path: str | Path) -> list[dict[str, Any]]:
    ensure_web_db(db_path)
    with get_connection(db_path) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM articles WHERE (draft_id IS NOT NULL AND draft_id != '') OR status IN ('draft_created','published','voided','needs_review') ORDER BY id DESC LIMIT 100").fetchall()]


def current_issue_counters(db_path: str | Path) -> dict[str, int]:
    ensure_web_db(db_path)
    keys = ["last_briefing_issue_no", "last_interpretation_issue_no", "last_mflai_interpretation_issue_no"]
    with get_connection(db_path) as conn:
        rows = {row["key"]: int(row["value"] or 0) for row in conn.execute("SELECT key, value FROM settings WHERE key IN (?,?,?)", keys)}
    return {key: rows.get(key, 0) for key in keys}


def next_issue_preview(db_path: str | Path) -> dict[str, int]:
    counters = current_issue_counters(db_path)
    return {key.replace("last_", "next_"): value + 1 for key, value in counters.items()}


def today_default_source_date() -> str:
    return (datetime.now(CHINA_TZ).date() - timedelta(days=1)).isoformat()


def workbench_context(db_path: str | Path, date: str | None = None) -> dict[str, Any]:
    target_date = date or today_default_source_date()
    return {"date": target_date, "sources": list_sources(db_path, target_date), "next_issues": next_issue_preview(db_path)}


def bulk_delete_sources(db_path: str | Path, ids: Sequence[int]) -> int:
    ensure_web_db(db_path)
    clean_ids = [int(item_id) for item_id in ids if int(item_id) > 0]
    if not clean_ids:
        return 0
    placeholders = ",".join("?" for _ in clean_ids)
    with get_connection(db_path) as conn:
        cursor = conn.execute(f"DELETE FROM sources WHERE id IN ({placeholders})", tuple(clean_ids))
        return int(cursor.rowcount or 0)


def bulk_delete_articles(db_path: str | Path, ids: Sequence[int]) -> int:
    ensure_web_db(db_path)
    clean_ids = [int(item_id) for item_id in ids if int(item_id) > 0]
    if not clean_ids:
        return 0
    placeholders = ",".join("?" for _ in clean_ids)
    with get_connection(db_path) as conn:
        cursor = conn.execute(f"DELETE FROM articles WHERE id IN ({placeholders})", tuple(clean_ids))
        return int(cursor.rowcount or 0)


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


def generate_selected_workbench_articles(
    settings: Settings,
    *,
    briefing_source_id: int | None = None,
    interpretation_source_id: int | None = None,
    mflai_source_id: int | None = None,
    create_draft: bool = False,
) -> list[int]:
    created: list[int] = []
    if briefing_source_id:
        created.append(generate_article_from_source(settings, briefing_source_id, content_type="briefing", theme="bytedance-green", wechat_account="cjfai", create_draft=create_draft))
    if interpretation_source_id:
        created.append(generate_article_from_source(settings, interpretation_source_id, content_type="interpretation", theme="fresh-card", wechat_account="cjfai", create_draft=create_draft))
    if mflai_source_id:
        created.append(generate_article_from_source(settings, mflai_source_id, content_type="interpretation", theme="fresh-card", wechat_account="mflai", create_draft=create_draft))
    return created


def update_article_content(db_path: str | Path, article_id: int, *, title: str, digest: str, content_markdown: str, theme: str | None = None) -> None:
    article = get_article(db_path, article_id)
    if article is None:
        raise ValueError("ARTICLE_NOT_FOUND")
    selected_theme = theme or default_wechat_theme(article.get("content_type"))
    content_html = markdown_to_wechat_html(content_markdown, content_type=article.get("content_type"), theme=selected_theme)
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        conn.execute("UPDATE articles SET title=?, digest=?, content_markdown=?, content_html=?, updated_at=? WHERE id=?", (title, digest, content_markdown, content_html, now, article_id))


def update_article_status(db_path: str | Path, article_id: int, status: str) -> None:
    if status not in ARTICLE_STATUSES:
        raise ValueError("UNSUPPORTED_STATUS")
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        conn.execute("UPDATE articles SET status=?, updated_at=? WHERE id=?", (status, now, article_id))


def create_draft_for_existing_article(settings: Settings, article_id: int, wechat_account: str) -> str:
    article = get_article(settings.database_path, article_id)
    if article is None:
        raise ValueError("ARTICLE_NOT_FOUND")
    draft_id = create_draft_if_requested(settings, article, True, wechat_account, retry_delay_seconds=0)
    if draft_id:
        update_article_draft(settings.database_path, article_id, draft_id, "draft_created")
    return draft_id or ""


def update_cover_prompt(db_path: str | Path, article_id: int, cover_prompt: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        conn.execute("UPDATE articles SET cover_prompt=?, updated_at=? WHERE id=?", (cover_prompt, now, article_id))


def rerender_article_theme(db_path: str | Path, article_id: int, theme: str) -> None:
    article = get_article(db_path, article_id)
    if article is None:
        raise ValueError("ARTICLE_NOT_FOUND")
    content_html = markdown_to_wechat_html(article.get("content_markdown") or "", content_type=article.get("content_type"), theme=theme)
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        conn.execute("UPDATE articles SET content_html=?, updated_at=? WHERE id=?", (content_html, now, article_id))


def article_angles(article: dict[str, Any]) -> list[str]:
    title = article.get("source_title") or article.get("title") or "这条新闻"
    return [
        f"普通人效率角度：{title} 对个人工作流意味着什么",
        f"创作者机会角度：如何把 {title} 转成内容/产品机会",
        f"开发者自动化角度：从 {title} 看可落地的自动化场景",
    ]


def health_snapshot(db_path: str | Path) -> dict[str, Any]:
    ensure_web_db(db_path)
    now_utc = datetime.now(timezone.utc)
    cron = "未知"
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=3)
        cron = "已配置" if "scripts/run_daily.sh" in result.stdout else "未检测到 daily crontab"
    except Exception:
        cron = "无法读取"
    latest = list_articles(db_path)[:5]
    return {
        "server_time": datetime.now().astimezone().strftime("%F %T %Z"),
        "beijing_time": now_utc.astimezone(CHINA_TZ).strftime("%F %T CST"),
        "timezone": os.environ.get("TZ") or datetime.now().astimezone().tzname(),
        "cron_status": cron,
        "next_issues": next_issue_preview(db_path),
        "recent_articles": latest,
    }


def available_themes() -> list[str]:
    return list(THEME_STYLES.keys())
