from __future__ import annotations

from dataclasses import replace
import os

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import Settings, load_dotenv
from app.database import get_article
from app.web import services


WEB_DEFAULT_DATABASE_URL = "sqlite:///data/web/superfa-web.db"


def web_settings_from_env() -> Settings:
    settings = Settings.from_env()
    web_database_url = os.getenv("WEB_DATABASE_URL", WEB_DEFAULT_DATABASE_URL)
    return replace(settings, database_url=web_database_url)


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

    @app.get("/news", response_class=HTMLResponse)
    def news(request: Request, date: str | None = None):
        sources = services.list_sources(settings.database_path, date)
        return render(request, "news.html", {"sources": sources, "date": date or ""})

    @app.post("/news/collect")
    def collect_news(date: str = Form(...)):
        services.collect_sources_for_date(settings, date)
        return RedirectResponse(f"/news?date={date}", status_code=303)

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

    @app.get("/articles/{article_id}", response_class=HTMLResponse)
    def article_detail(request: Request, article_id: int):
        article = get_article(settings.database_path, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        return render(request, "article_detail.html", {"article": article})

    return app


app = create_app()
