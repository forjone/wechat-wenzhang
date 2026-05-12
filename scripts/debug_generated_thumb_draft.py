#!/usr/bin/env python3
"""Smoke test Tokyo WeChat proxy generated-thumb draft endpoint.

Usage:
  python3 scripts/debug_generated_thumb_draft.py \
    --proxy-url https://your-tokyo-proxy.example.com \
    --account hao1 \
    --api-key "$WECHAT_PROXY_API_KEY"

The script only creates a WeChat draft. It does not publish.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import Settings, load_dotenv
from app.wechat.proxy_client import WeChatProxyClient


def _redact(value: str) -> str:
    return "[REDACTED]" if value else ""


def build_demo_article() -> dict[str, object]:
    return {
        "title": "AI Agent 自动化办公指南",
        "author": "超级发",
        "digest": "一篇关于 AI Agent 工作流的文章",
        "content_html": "<p>正文 HTML 内容</p><p>这是一篇用于调试生成主图接口的草稿。</p>",
        "content_source_url": "",
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }


def main(argv: list[str] | None = None) -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    settings = Settings.from_env()

    parser = argparse.ArgumentParser(description="Debug /wechat/draft/create-with-generated-thumb")
    parser.add_argument("--proxy-url", default=settings.wechat_proxy_url, help="Tokyo WeChat proxy base URL; defaults to WECHAT_PROXY_URL")
    parser.add_argument("--api-key", default=settings.wechat_proxy_api_key, help="Proxy API key; defaults to WECHAT_PROXY_API_KEY")
    parser.add_argument("--account", default="hao1", help="Proxy account alias, e.g. hao1/cjfai")
    parser.add_argument("--image-size", default="2048x1152", help="Generated thumbnail size")
    parser.add_argument("--image-style", choices=["text", "metaphor"], default="text", help="Generated thumbnail style")
    parser.add_argument("--title", default="AI Agent 自动化办公指南")
    parser.add_argument("--digest", default="一篇关于 AI Agent 工作流的文章")
    parser.add_argument("--content-html", default="<p>正文 HTML 内容</p><p>这是一篇用于调试生成主图接口的草稿。</p>")
    args = parser.parse_args(argv)

    if not args.proxy_url:
        print(json.dumps({"status": "failed", "error": "WECHAT_PROXY_URL_REQUIRED"}, ensure_ascii=False, indent=2))
        return 1

    article = build_demo_article()
    article["title"] = args.title
    article["digest"] = args.digest
    article["content_html"] = args.content_html

    client = WeChatProxyClient(args.proxy_url, api_key=args.api_key, timeout=settings.wechat_proxy_timeout)
    try:
        draft_id = client.create_draft_with_generated_thumb(article, account=args.account, image_size=args.image_size, image_style=args.image_style)
    except Exception as exc:
        print(json.dumps({
            "status": "failed",
            "endpoint": "/wechat/draft/create-with-generated-thumb",
            "proxy_url": args.proxy_url,
            "account": args.account,
            "api_key": _redact(args.api_key),
            "image_size": args.image_size,
            "image_style": args.image_style,
            "error": str(exc),
        }, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({
        "status": "success",
        "endpoint": "/wechat/draft/create-with-generated-thumb",
        "account": args.account,
        "image_size": args.image_size,
        "image_style": args.image_style,
        "draft_id": draft_id,
        "message": "Draft created only; not published.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
