from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date as date_cls, datetime, timezone
from pathlib import Path
from typing import Any

from app.agents.briefing_writer import generate_briefing, display_date_for_news_date
from app.agents.interpretation_writer import generate_interpretation
from app.agents.news_scorer import dedupe_news, score_for_briefing, score_for_interpretation
from app.agents.image_generator import generate_article_images
from app.config import Settings, load_dotenv
from app.database import get_article, init_db, next_issue_no, save_article, save_source, update_article_draft, update_article_publish
from app.outputs import save_article_outputs
from app.render.markdown_to_html import markdown_to_wechat_html
from app.sources.aihot_skill import AIHotSkillClient
from app.sources.original_article import enrich_news_item_with_original
from app.wechat.draft_manager import DraftManager
from app.wechat.publish_manager import PublishManager
from app.wechat.proxy_client import WeChatProxyClient
from app.wechat.token_manager import TokenManager
from app.wechat.accounts import select_wechat_account


def _today() -> str:
    return date_cls.today().isoformat()


def collect_news(settings: Settings, target_date: str) -> list[dict[str, Any]]:
    client = AIHotSkillClient(
        base_url=settings.aihot_skill_url,
        timeout=settings.aihot_skill_timeout,
        api_key=settings.aihot_skill_api_key,
        user_agent=settings.aihot_user_agent,
    )
    return client.fetch_daily_news(target_date, settings.aihot_skill_max_items)


def _published_date(item: dict[str, Any]) -> str:
    value = str(item.get("published_at") or item.get("date") or "").strip()
    if not value:
        return ""
    if len(value) >= 10 and value[4:5] == "-" and value[7:8] == "-":
        return value[:10]
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return ""
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc)
    return parsed.date().isoformat()


def filter_news_for_target_date(news: list[dict[str, Any]], target_date: str) -> list[dict[str, Any]]:
    return [item for item in news if _published_date(item) == target_date]


def fallback_news(target_date: str) -> list[dict[str, Any]]:
    return [
        {"title": "AI搜索和智能助手继续改变信息入口", "url": "", "source": "fallback", "published_at": target_date, "summary": "AI搜索、智能助手和内容生成工具正在进入更多普通人的工作流程。", "content": "AI搜索、智能助手和内容生成工具正在进入更多普通人的工作流程。", "category": "AI搜索", "tags": ["AI搜索", "Agent", "效率"], "raw": {}},
        {"title": "AI视频和图像工具降低内容生产门槛", "url": "", "source": "fallback", "published_at": target_date, "summary": "AI视频和图像工具让内容创作者可以用更低成本完成创意表达。", "content": "AI视频和图像工具让内容创作者可以用更低成本完成创意表达。", "category": "AI工具", "tags": ["AI视频", "内容创作者", "工具"], "raw": {}},
        {"title": "企业开始把 Agent 用到客服和办公自动化", "url": "", "source": "fallback", "published_at": target_date, "summary": "越来越多企业把 Agent 用在客服、销售线索处理和内部办公自动化。", "content": "越来越多企业把 Agent 用在客服、销售线索处理和内部办公自动化。", "category": "Agent", "tags": ["Agent", "创业", "自动化"], "raw": {}},
    ]


def prepare_news(settings: Settings, target_date: str, allow_fallback: bool | None = None) -> list[dict[str, Any]]:
    fallback_allowed = settings.allow_fallback if allow_fallback is None else allow_fallback
    source_mode = "aihot_skill"
    source_error = ""
    try:
        news = collect_news(settings, target_date)
    except Exception as exc:
        source_error = str(exc) or exc.__class__.__name__
        if not fallback_allowed:
            raise RuntimeError(source_error) from exc
        source_mode = "fallback"
        news = fallback_news(target_date)
    news = filter_news_for_target_date(dedupe_news(news), target_date)[: settings.aihot_skill_max_items]
    for item in news:
        item["date"] = target_date
        item["score"] = score_for_briefing(item)
        item["source_mode"] = source_mode
        item["source_error"] = source_error
        item["source_provider"] = "aihot_skill" if source_mode == "aihot_skill" else "fallback"
    return news


def select_briefing_items(news: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(news, key=score_for_briefing, reverse=True)
    if limit == 0:
        return ranked
    return ranked[:limit]


def _get_wechat_access_token(settings: Settings, wechat_account: str = "default") -> str:
    account = select_wechat_account(settings, wechat_account)
    if not (account.appid and account.appsecret):
        return ""
    token_store = "data/token_store.json" if account.name == "default" else f"data/token_store_{account.name}.json"
    return TokenManager(account.appid, account.appsecret, token_store=token_store).get_access_token()


def _get_wechat_proxy(settings: Settings) -> WeChatProxyClient | None:
    if not settings.wechat_proxy_url:
        return None
    return WeChatProxyClient(
        settings.wechat_proxy_url,
        api_key=settings.wechat_proxy_api_key,
        timeout=settings.wechat_proxy_timeout,
    )


def create_draft_if_requested(
    settings: Settings,
    article: dict[str, Any],
    create_draft: bool,
    wechat_account: str = "default",
    *,
    max_attempts: int = 3,
    retry_delay_seconds: float = 2.0,
) -> str | None:
    if not create_draft:
        return None
    proxy = _get_wechat_proxy(settings)
    draft_article = {
        "title": article["title"],
        "author": settings.author_name,
        "digest": article.get("digest", ""),
        "content_html": article["content_html"],
        "content_source_url": article.get("content_source_url", ""),
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }

    def create_once() -> str:
        if proxy:
            if article.get("image_prompt"):
                return proxy.create_draft_with_generated_thumb(draft_article, account=wechat_account, image_size="2048x1152", image_style="text")
            draft_article["thumb_media_id"] = article.get("thumb_media_id", "")
            return proxy.create_draft(draft_article, account=wechat_account)
        draft_article["thumb_media_id"] = article.get("thumb_media_id", "")
        access_token = _get_wechat_access_token(settings, wechat_account)
        return DraftManager(access_token).create_draft(draft_article)

    attempts = max(1, max_attempts)
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return create_once()
        except Exception as exc:
            last_exc = exc
            if attempt >= attempts:
                break
            time.sleep(retry_delay_seconds * attempt)
    assert last_exc is not None
    raise last_exc


def publish_draft_if_confirmed(settings: Settings, draft_id: str | None, publish_confirm: bool, wechat_account: str = "default") -> str | None:
    if not publish_confirm:
        return None
    if not draft_id:
        raise RuntimeError("PUBLISH_REQUIRES_DRAFT_ID")
    if not settings.auto_publish:
        raise RuntimeError("AUTO_PUBLISH_DISABLED: set AUTO_PUBLISH=true and pass --publish-confirm to publish")
    proxy = _get_wechat_proxy(settings)
    if proxy:
        return proxy.publish_draft(draft_id, account=wechat_account)
    access_token = _get_wechat_access_token(settings, wechat_account)
    return PublishManager(access_token, auto_publish=True).publish_draft(draft_id)


def attach_article_images(article: dict[str, Any], output_dir: str | None = None) -> dict[str, Any]:
    image_assets = generate_article_images(article, output_dir=output_dir or "outputs/images")
    article.update(image_assets)
    return article


def persist_article(
    settings: Settings,
    article: dict[str, Any],
    create_draft: bool,
    wechat_account: str = "default",
    publish_confirm: bool = False,
) -> dict[str, Any]:
    output_paths = save_article_outputs(article, output_dir=settings.article_output_dir)
    article_id = save_article(settings.database_path, article)
    draft_id = create_draft_if_requested(settings, article, create_draft, wechat_account, retry_delay_seconds=0 if settings.wechat_proxy_url else 2.0)
    publish_id = publish_draft_if_confirmed(settings, draft_id, publish_confirm, wechat_account)
    status = "published" if publish_id else ("draft_created" if draft_id else "generated")
    if draft_id:
        update_article_draft(settings.database_path, article_id, draft_id, status)
    if publish_id:
        update_article_publish(settings.database_path, article_id, publish_id, status)
    return {
        "article_id": article_id,
        "content_type": article["content_type"],
        "issue_no": article["issue_no"],
        "title": article["title"],
        "draft_id": draft_id,
        "draft_account": wechat_account if draft_id else None,
        "publish_id": publish_id,
        "status": status,
        "metadata": {key: value for key, value in article.items() if key not in {"content_markdown", "content_html"}},
        "files": {key: str(path) for key, path in output_paths.items()},
    }


def generate_briefing_command(settings: Settings, target_date: str, create_draft: bool, item_limit: int = 10, wechat_account: str = "default", publish_confirm: bool = False) -> dict[str, Any]:
    init_db(settings.database_path)
    news = prepare_news(settings, target_date)
    for item in news:
        save_source(settings.database_path, {**item, "selected": 0})
    selected = select_briefing_items(news, item_limit)
    issue_no = next_issue_no(settings.database_path, "briefing")
    article = generate_briefing(selected, target_date, issue_no, max_items=0)
    attach_article_images(article)
    article["content_html"] = markdown_to_wechat_html(article["content_markdown"], content_type=article["content_type"])
    result = persist_article(settings, article, create_draft or publish_confirm, wechat_account, publish_confirm)
    return {"status": "success", "date": article["date"], "source_date": target_date, "briefing": result}


def generate_interpretation_command(settings: Settings, target_date: str, create_draft: bool, news: list[dict[str, Any]] | None = None, wechat_account: str = "default", publish_confirm: bool = False) -> dict[str, Any]:
    init_db(settings.database_path)
    if news is None:
        news = prepare_news(settings, target_date)
    selected = sorted(news, key=score_for_interpretation, reverse=True)[:1]
    selected = enrich_interpretation_selection(selected, settings)
    issue_no = next_issue_no(settings.database_path, "interpretation")
    article = generate_interpretation(selected, target_date, issue_no)
    attach_article_images(article)
    article["content_html"] = markdown_to_wechat_html(article["content_markdown"], content_type=article["content_type"])
    result = persist_article(settings, article, create_draft or publish_confirm, wechat_account, publish_confirm)
    return {"status": "success", "date": target_date, "interpretation": result}


def select_interpretation_item(selected_briefing: list[dict[str, Any]], *, avoid_first: bool = False) -> list[dict[str, Any]]:
    if not selected_briefing:
        return []
    if avoid_first and len(selected_briefing) > 1:
        return [selected_briefing[1]]
    return selected_briefing[:1]


def enrich_interpretation_item(item: dict[str, Any], settings: Settings) -> dict[str, Any]:
    return enrich_news_item_with_original(item, timeout=min(settings.aihot_skill_timeout, 20))


def enrich_interpretation_selection(selected: list[dict[str, Any]], settings: Settings) -> list[dict[str, Any]]:
    return [enrich_interpretation_item(item, settings) for item in selected]


def generate_daily_command(settings: Settings, target_date: str, create_draft: bool, item_limit: int = 10, wechat_account: str = "default", publish_confirm: bool = False) -> dict[str, Any]:
    init_db(settings.database_path)
    news = prepare_news(settings, target_date)
    for item in news:
        save_source(settings.database_path, {**item, "selected": 0})
    selected_briefing = select_briefing_items(news, item_limit)
    briefing_issue = next_issue_no(settings.database_path, "briefing")
    briefing = generate_briefing(selected_briefing, target_date, briefing_issue, max_items=0)
    attach_article_images(briefing)
    briefing["content_html"] = markdown_to_wechat_html(briefing["content_markdown"], content_type=briefing["content_type"])
    briefing_result = persist_article(settings, briefing, create_draft or publish_confirm, wechat_account, publish_confirm)

    selected_interpretation = enrich_interpretation_selection(select_interpretation_item(selected_briefing), settings)
    interpretation_issue = next_issue_no(settings.database_path, "interpretation")
    display_date = display_date_for_news_date(target_date)
    interpretation = generate_interpretation(
        selected_interpretation,
        display_date,
        interpretation_issue,
        include_issue_number=True,
    )
    attach_article_images(interpretation)
    interpretation["content_html"] = markdown_to_wechat_html(interpretation["content_markdown"], content_type=interpretation["content_type"])
    interpretation_result = persist_article(settings, interpretation, create_draft or publish_confirm, wechat_account, publish_confirm)

    result = {"status": "success", "date": display_date, "source_date": target_date, "briefing": briefing_result, "interpretation": interpretation_result}
    if wechat_account == "cjfai":
        selected_mflai = enrich_interpretation_selection(select_interpretation_item(selected_briefing, avoid_first=True), settings)
        mflai_issue = next_issue_no(settings.database_path, "interpretation")
        mflai_interpretation = generate_interpretation(
            selected_mflai,
            display_date,
            mflai_issue,
            include_issue_number=False,
        )
        attach_article_images(mflai_interpretation)
        mflai_interpretation["content_html"] = markdown_to_wechat_html(mflai_interpretation["content_markdown"], content_type=mflai_interpretation["content_type"])
        result["mflai_interpretation"] = persist_article(settings, mflai_interpretation, create_draft or publish_confirm, "mflai", publish_confirm)
    return result


def preview_article_command(settings: Settings, article_id: int, output_format: str = "markdown", database: str | None = None) -> dict[str, Any]:
    db_path = database or str(settings.database_path)
    init_db(db_path)
    article = get_article(db_path, article_id)
    if article is None:
        return {"status": "failed", "error": "ARTICLE_NOT_FOUND", "message": f"Article {article_id} not found."}
    if output_format == "markdown":
        article.pop("content_html", None)
    elif output_format == "html":
        article.pop("content_markdown", None)
    elif output_format == "metadata":
        article.pop("content_markdown", None)
        article.pop("content_html", None)
    return {"status": "success", "article": article}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="超级发AI情报公众号更新 Agent")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["generate-briefing", "generate-interpretation", "generate-daily"]:
        p = sub.add_parser(name)
        p.add_argument("--date", default=_today())
        p.add_argument("--create-draft", action="store_true")
        p.add_argument("--no-fallback", action="store_true", help="AIHot 数据源失败时直接报错，不使用本地样例")
        p.add_argument("--database", default=None, help="覆盖默认 SQLite 数据库路径")
        p.add_argument("--aihot-url", default=None, help="覆盖 AIHot Skill URL")
        p.add_argument("--items", type=int, default=10, help="简报展示条数；0 表示展示本次获取到的全部条目")
        p.add_argument("--wechat-account", default="default", help="选择微信公众号账号别名；默认使用 WECHAT_APPID/WECHAT_APPSECRET")
        p.add_argument("--publish-confirm", action="store_true", help="高风险：创建草稿后立即发布/群发。必须同时设置 AUTO_PUBLISH=true")
    p = sub.add_parser("preview")
    p.add_argument("--article-id", type=int, required=True)
    p.add_argument("--database", default=None, help="覆盖默认 SQLite 数据库路径")
    p.add_argument("--format", choices=["markdown", "html", "metadata"], default="markdown")
    p = sub.add_parser("create-draft")
    p.add_argument("--article-id", type=int, required=True)
    p = sub.add_parser("publish")
    p.add_argument("--article-id", type=int, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv()
    settings = Settings.from_env()
    if getattr(args, "database", None):
        settings = Settings(**{**settings.__dict__, "database_url": f"sqlite:///{args.database}"})
    if getattr(args, "aihot_url", None):
        settings = Settings(**{**settings.__dict__, "aihot_skill_url": args.aihot_url})
    if getattr(args, "no_fallback", False):
        settings = Settings(**{**settings.__dict__, "allow_fallback": False})
    try:
        if args.command == "generate-briefing":
            result = generate_briefing_command(settings, args.date, args.create_draft or args.publish_confirm, args.items, args.wechat_account, args.publish_confirm)
        elif args.command == "generate-interpretation":
            result = generate_interpretation_command(settings, args.date, args.create_draft or args.publish_confirm, wechat_account=args.wechat_account, publish_confirm=args.publish_confirm)
        elif args.command == "generate-daily":
            result = generate_daily_command(settings, args.date, args.create_draft or args.publish_confirm, args.items, args.wechat_account, args.publish_confirm)
        elif args.command == "preview":
            result = preview_article_command(settings, args.article_id, args.format, args.database)
        elif args.command == "create-draft":
            result = {"status": "failed", "error": "NOT_IMPLEMENTED", "message": "Use generate commands with --create-draft in MVP."}
        elif args.command == "publish":
            result = {"status": "failed", "error": "AUTO_PUBLISH_DISABLED", "message": "MVP 默认不自动发布，只创建草稿。"}
        else:
            raise AssertionError(args.command)
    except (RuntimeError, ValueError) as exc:
        result = {"status": "failed", "error": str(exc) or exc.__class__.__name__}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

