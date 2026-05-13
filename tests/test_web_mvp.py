from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient

from app.config import Settings
from app.database import init_db, save_article, save_source
from app.web.main import create_app, web_settings_from_env


def make_client(tmp_path, monkeypatch):
    db_path = tmp_path / "web.db"
    settings = Settings(database_url=f"sqlite:///{db_path}")
    monkeypatch.setenv("WEB_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setattr("app.web.main.load_dotenv", lambda: None)
    monkeypatch.setattr("app.web.main.Settings.from_env", lambda: settings)
    return TestClient(create_app()), db_path


def test_web_default_database_is_isolated_from_cli_data(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("WEB_DATABASE_URL", raising=False)

    settings = web_settings_from_env()

    assert settings.database_url == "sqlite:///data/web/superfa-web.db"


def test_web_database_url_can_be_overridden_separately(monkeypatch, tmp_path):
    cli_db = tmp_path / "cli.db"
    web_db = tmp_path / "web-isolated.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{cli_db}")
    monkeypatch.setenv("WEB_DATABASE_URL", f"sqlite:///{web_db}")

    settings = web_settings_from_env()

    assert settings.database_url == f"sqlite:///{web_db}"


def test_web_dashboard_renders_without_touching_cli(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path, monkeypatch)
    init_db(db_path)
    save_source(db_path, {"date": "2026-05-09", "title": "新闻 A", "url": "https://example.com/a", "source": "AIHot", "summary": "摘要"})
    save_article(db_path, {"content_type": "briefing", "issue_no": 1, "date": "2026-05-10", "title": "简报 A", "digest": "摘要", "content_markdown": "# 简报", "content_html": "<h1>简报</h1>", "status": "generated"})

    response = client.get("/")

    assert response.status_code == 200
    assert "超级发 AI 内容工作台" in response.text
    assert "新闻源" in response.text
    assert "文章" in response.text


def test_news_page_collects_and_lists_sources(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path, monkeypatch)

    def fake_prepare_news(settings, target_date, allow_fallback=None):
        return [
            {"date": target_date, "title": "AI 新闻一", "url": "https://example.com/1", "source": "AIHot", "summary": "摘要一", "category": "产品", "tags": ["AI"], "score": 88, "source_provider": "aihot_skill"},
            {"date": target_date, "title": "AI 新闻二", "url": "https://example.com/2", "source": "AIHot", "summary": "摘要二", "category": "行业", "tags": ["Agent"], "score": 77, "source_provider": "aihot_skill"},
        ]

    monkeypatch.setattr("app.web.services.prepare_news", fake_prepare_news)

    response = client.post("/news/collect", data={"date": "2026-05-09"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/news?date=2026-05-09"
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("select count(*) from sources").fetchone()[0] == 2

    page = client.get("/news?date=2026-05-09")
    assert page.status_code == 200
    assert "AI 新闻一" in page.text
    assert "生成文章" in page.text


def test_generate_source_article_stores_article_with_selected_style_and_account(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path, monkeypatch)
    init_db(db_path)
    source_id = save_source(db_path, {"date": "2026-05-09", "title": "可生成新闻", "url": "https://example.com/src", "source": "AIHot", "summary": "摘要", "content": "正文"})

    def fake_create_draft(settings, article, create_draft, wechat_account="default", **kwargs):
        assert create_draft is True
        assert wechat_account == "mflai"
        return "local_draft_web"

    monkeypatch.setattr("app.web.services.create_draft_if_requested", fake_create_draft)

    response = client.post(
        f"/news/{source_id}/generate",
        data={"content_type": "interpretation", "theme": "fresh-card", "wechat_account": "mflai", "create_draft": "on"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    article_id = response.headers["location"].removeprefix("/articles/")
    assert article_id.isdigit()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("select * from articles where id = ?", (int(article_id),)).fetchone()
        assert row["title"]
        assert row["status"] == "draft_created"
        assert row["draft_id"] == "local_draft_web"


def test_web_generated_article_outputs_are_isolated_from_cli_outputs(tmp_path, monkeypatch):
    web_output_dir = tmp_path / "web-outputs" / "articles"
    cli_output_dir = tmp_path / "cli-outputs" / "articles"
    monkeypatch.setenv("WEB_OUTPUT_DIR", str(web_output_dir))
    client, db_path = make_client(tmp_path, monkeypatch)
    init_db(db_path)
    source_id = save_source(db_path, {"date": "2026-05-09", "title": "隔离输出新闻", "url": "https://example.com/src", "source": "AIHot", "summary": "摘要", "content": "正文"})
    cli_output_dir.mkdir(parents=True)
    monkeypatch.setattr("app.web.services.create_draft_if_requested", lambda *args, **kwargs: "")

    response = client.post(
        f"/news/{source_id}/generate",
        data={"content_type": "briefing", "theme": "bytedance-green", "wechat_account": "cjfai"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert list(web_output_dir.glob("briefing-*.md"))
    assert not list(cli_output_dir.glob("*.md"))
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("select cover_path from articles order by id desc limit 1").fetchone()
    assert row["cover_path"]
    assert "data/web/outputs/images" in row["cover_path"]


def test_article_detail_shows_markdown_and_html_preview(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path, monkeypatch)
    init_db(db_path)
    article_id = save_article(db_path, {"content_type": "briefing", "issue_no": 1, "date": "2026-05-10", "title": "详情文章", "digest": "摘要", "content_markdown": "# Markdown", "content_html": "<h1>HTML</h1>", "status": "generated"})

    response = client.get(f"/articles/{article_id}")

    assert response.status_code == 200
    assert "详情文章" in response.text
    assert "# Markdown" in response.text
    assert "HTML 预览" in response.text
    assert "&lt;h1&gt;HTML&lt;/h1&gt;" not in response.text


def test_news_collect_button_has_loading_state(tmp_path, monkeypatch):
    client, _ = make_client(tmp_path, monkeypatch)

    response = client.get("/news?date=2026-05-09")

    assert response.status_code == 200
    assert "data-loading-text=\"采集中...\"" in response.text
    assert "spinner" in response.text
    assert "正在采集，请稍候" in response.text


def test_bulk_delete_sources_deletes_only_selected_rows(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path, monkeypatch)
    init_db(db_path)
    first_id = save_source(db_path, {"date": "2026-05-09", "title": "删除新闻", "url": "https://example.com/delete", "source": "AIHot", "summary": "删"})
    keep_id = save_source(db_path, {"date": "2026-05-09", "title": "保留新闻", "url": "https://example.com/keep", "source": "AIHot", "summary": "留"})

    response = client.post("/news/bulk-delete", data={"ids": [str(first_id)], "date": "2026-05-09"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/news?date=2026-05-09"
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("select count(*) from sources where id = ?", (first_id,)).fetchone()[0] == 0
        assert conn.execute("select count(*) from sources where id = ?", (keep_id,)).fetchone()[0] == 1


def test_bulk_delete_articles_deletes_only_selected_rows(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path, monkeypatch)
    init_db(db_path)
    delete_id = save_article(db_path, {"content_type": "briefing", "issue_no": 1, "date": "2026-05-10", "title": "删除文章", "digest": "摘要", "content_markdown": "# 删", "content_html": "<h1>删</h1>", "status": "generated"})
    keep_id = save_article(db_path, {"content_type": "briefing", "issue_no": 2, "date": "2026-05-10", "title": "保留文章", "digest": "摘要", "content_markdown": "# 留", "content_html": "<h1>留</h1>", "status": "generated"})

    response = client.post("/articles/bulk-delete", data={"ids": [str(delete_id)]}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/articles"
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("select count(*) from articles where id = ?", (delete_id,)).fetchone()[0] == 0
        assert conn.execute("select count(*) from articles where id = ?", (keep_id,)).fetchone()[0] == 1


def test_list_pages_render_bulk_delete_controls(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path, monkeypatch)
    init_db(db_path)
    save_source(db_path, {"date": "2026-05-09", "title": "可勾选新闻", "url": "https://example.com/src", "source": "AIHot", "summary": "摘要"})
    save_article(db_path, {"content_type": "briefing", "issue_no": 1, "date": "2026-05-10", "title": "可勾选文章", "digest": "摘要", "content_markdown": "# 文", "content_html": "<h1>文</h1>", "status": "generated"})

    news_page = client.get("/news?date=2026-05-09")
    articles_page = client.get("/articles")

    assert 'action="/news/bulk-delete"' in news_page.text
    assert 'name="ids"' in news_page.text
    assert "批量删除" in news_page.text
    assert 'action="/articles/bulk-delete"' in articles_page.text
    assert 'name="ids"' in articles_page.text
