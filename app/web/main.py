from __future__ import annotations

from dataclasses import replace
import os

from fastapi import FastAPI, Form, HTTPException, Request
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import Settings, load_dotenv
from app.database import get_article
from app.web import services


WEB_DEFAULT_DATABASE_URL = "sqlite:///data/web/superfa-web.db"


def web_settings_from_env() -> Settings:
    settings = Settings.from_env()
    web_database_url = os.getenv("WEB_DATABASE_URL", WEB_DEFAULT_DATABASE_URL)
    web_article_output_dir = os.getenv("WEB_OUTPUT_DIR", "data/web/outputs/articles")
    web_image_output_dir = os.getenv("WEB_IMAGE_OUTPUT_DIR", "data/web/outputs/images")
    return replace(
        settings,
        database_url=web_database_url,
        article_output_dir=web_article_output_dir,
        image_output_dir=web_image_output_dir,
    )


def _optional_int(value: str | None) -> int | None:
    if value is None or value == "" or value == "0":
        return None
    return int(value)


def create_app() -> FastAPI:
    load_dotenv()
    settings = web_settings_from_env()
    templates = Jinja2Templates(directory="app/web/templates")
    app = FastAPI(title="超级发 AI 内容工作台")
    app.state.settings = settings

    def render(request: Request, template_name: str, context: dict):
        return templates.TemplateResponse(request, template_name, context)

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        counts = services.dashboard_counts(settings.database_path)
        recent_articles = services.list_articles(settings.database_path)[:5]
        recent_sources = services.list_sources(settings.database_path)[:5]
        return render(request, "dashboard.html", {"counts": counts, "articles": recent_articles, "sources": recent_sources})

    @app.get("/today", response_class=HTMLResponse)
    def today(request: Request, date: str | None = None):
        return render(request, "today.html", services.workbench_context(settings.database_path, date))

    @app.post("/today/generate")
    def today_generate(
        date: str = Form(""),
        briefing_source_id: str | None = Form(None),
        interpretation_source_id: str | None = Form(None),
        mflai_source_id: str | None = Form(None),
        create_draft: str | None = Form(None),
    ):
        created = services.generate_selected_workbench_articles(
            settings,
            briefing_source_id=_optional_int(briefing_source_id),
            interpretation_source_id=_optional_int(interpretation_source_id),
            mflai_source_id=_optional_int(mflai_source_id),
            create_draft=create_draft is not None,
        )
        if created:
            return RedirectResponse(f"/articles/{created[-1]}", status_code=303)
        location = f"/today?date={date}" if date else "/today"
        return RedirectResponse(location, status_code=303)

    @app.get("/news", response_class=HTMLResponse)
    def news(request: Request, date: str | None = None):
        sources = services.list_sources(settings.database_path, date)
        return render(request, "news.html", {"sources": sources, "date": date or ""})

    @app.post("/news/collect")
    def collect_news(date: str = Form(...)):
        services.collect_sources_for_date(settings, date)
        return RedirectResponse(f"/news?date={date}", status_code=303)

    @app.post("/news/bulk-delete")
    def bulk_delete_news(ids: Annotated[list[int] | None, Form()] = None, date: str = Form("")):
        services.bulk_delete_sources(settings.database_path, ids or [])
        location = f"/news?date={date}" if date else "/news"
        return RedirectResponse(location, status_code=303)

    @app.get("/news/{source_id}/generate", response_class=HTMLResponse)
    def generate_form(request: Request, source_id: int):
        source = services.get_source(settings.database_path, source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found")
        return render(request, "generate.html", {"source": source})

    @app.post("/news/{source_id}/generate")
    def generate_source_article(
        source_id: int,
        content_type: str = Form("interpretation"),
        theme: str = Form("fresh-card"),
        wechat_account: str = Form("default"),
        create_draft: str | None = Form(None),
    ):
        article_id = services.generate_article_from_source(
            settings,
            source_id,
            content_type=content_type,
            theme=theme,
            wechat_account=wechat_account,
            create_draft=create_draft is not None,
        )
        return RedirectResponse(f"/articles/{article_id}", status_code=303)

    @app.get("/articles", response_class=HTMLResponse)
    def articles(request: Request):
        rows = services.list_articles(settings.database_path)
        return render(request, "articles.html", {"articles": rows})

    @app.post("/articles/bulk-delete")
    def bulk_delete_articles(ids: Annotated[list[int] | None, Form()] = None):
        services.bulk_delete_articles(settings.database_path, ids or [])
        return RedirectResponse("/articles", status_code=303)

    @app.get("/articles/{article_id}", response_class=HTMLResponse)
    def article_detail(request: Request, article_id: int):
        article = get_article(settings.database_path, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        return render(
            request,
            "article_detail.html",
            {"article": article, "angles": services.article_angles(article), "themes": services.available_themes()},
        )

    @app.post("/articles/{article_id}/edit")
    def edit_article(article_id: int, title: str = Form(...), digest: str = Form(""), content_markdown: str = Form(...), theme: str | None = Form(None)):
        services.update_article_content(settings.database_path, article_id, title=title, digest=digest, content_markdown=content_markdown, theme=theme)
        return RedirectResponse(f"/articles/{article_id}", status_code=303)

    @app.post("/articles/{article_id}/status")
    def article_status(article_id: int, status: str = Form(...)):
        services.update_article_status(settings.database_path, article_id, status)
        return RedirectResponse("/drafts", status_code=303)

    @app.post("/articles/{article_id}/create-draft")
    def article_create_draft(article_id: int, wechat_account: str = Form("cjfai")):
        services.create_draft_for_existing_article(settings, article_id, wechat_account)
        return RedirectResponse(f"/articles/{article_id}", status_code=303)

    @app.post("/articles/{article_id}/cover")
    def article_cover(article_id: int, cover_prompt: str = Form("")):
        services.update_cover_prompt(settings.database_path, article_id, cover_prompt)
        return RedirectResponse(f"/articles/{article_id}", status_code=303)

    @app.post("/articles/{article_id}/theme-preview")
    def article_theme_preview(article_id: int, theme: str = Form("fresh-card")):
        services.rerender_article_theme(settings.database_path, article_id, theme)
        return RedirectResponse(f"/articles/{article_id}", status_code=303)

    @app.get("/drafts", response_class=HTMLResponse)
    def drafts(request: Request):
        return render(request, "drafts.html", {"articles": services.list_drafts(settings.database_path)})

    @app.get("/health", response_class=HTMLResponse)
    def health(request: Request):
        return render(request, "health.html", {"health": services.health_snapshot(settings.database_path)})

    return app


app = create_app()
