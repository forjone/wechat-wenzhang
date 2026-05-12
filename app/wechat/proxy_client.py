from __future__ import annotations

import json
import urllib.request
from typing import Any


class WeChatProxyClient:
    """Client for a fixed-IP WeChat outbound proxy.

    The NAS/local agent keeps content generation and persistence local, then asks
    this proxy to perform WeChat API calls from a whitelisted server IP.
    """

    def __init__(self, base_url: str, api_key: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def create_draft(self, article: dict[str, Any], account: str = "default") -> str:
        payload = {"account": account, "article": article}
        result = self._post_json("/wechat/draft/add", payload)
        draft_id = result.get("media_id") or result.get("draft_id")
        if not draft_id:
            raise RuntimeError(f"WECHAT_PROXY_DRAFT_CREATE_FAILED: {result}")
        return str(draft_id)

    def create_draft_with_generated_thumb(
        self,
        article: dict[str, Any],
        account: str = "default",
        image_size: str = "2048x1152",
        image_style: str = "text",
    ) -> str:
        generated_article = {
            "title": article.get("title", ""),
            "author": article.get("author", ""),
            "digest": article.get("digest", ""),
            "content_html": article.get("content_html", ""),
            "content_source_url": article.get("content_source_url", ""),
            "need_open_comment": article.get("need_open_comment", 1),
            "only_fans_can_comment": article.get("only_fans_can_comment", 0),
        }
        payload = {"account": account, "article": generated_article, "image_size": image_size, "image_style": image_style}
        result = self._post_json("/wechat/draft/create-with-generated-thumb", payload)
        draft_id = result.get("media_id") or result.get("draft_id")
        if not draft_id:
            raise RuntimeError(f"WECHAT_PROXY_GENERATED_THUMB_DRAFT_CREATE_FAILED: {result}")
        return str(draft_id)

    def publish_draft(self, draft_id: str, account: str = "default") -> str:
        payload = {"account": account, "media_id": draft_id, "draft_id": draft_id}
        result = self._post_json("/wechat/freepublish/submit", payload)
        publish_id = result.get("publish_id")
        if not publish_id:
            raise RuntimeError(f"WECHAT_PROXY_PUBLISH_FAILED: {result}")
        return str(publish_id)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            raise ValueError("WECHAT_PROXY_URL is required for WeChat proxy calls")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            raw = response.read().decode("utf-8")
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"WECHAT_PROXY_INVALID_JSON: {raw[:200]}") from exc
        if not isinstance(result, dict):
            raise RuntimeError(f"WECHAT_PROXY_INVALID_RESPONSE: {result}")
        return result
