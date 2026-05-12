from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

DEFAULT_AIHOT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

CATEGORY_LABELS = {
    "ai-models": "模型发布/更新",
    "ai-products": "产品发布/更新",
    "industry": "行业动态",
    "paper": "论文研究",
    "tip": "技巧与观点",
}


class AIHotSkillClient:
    def __init__(
        self,
        base_url: str = "https://aihot.virxact.com",
        timeout: int = 30,
        api_key: str = "",
        user_agent: str = DEFAULT_AIHOT_USER_AGENT,
        mode: str = "selected",
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self.user_agent = user_agent
        self.mode = mode

    def build_items_request(self, date: str | None = None, max_items: int = 20) -> urllib.request.Request:
        params: dict[str, str | int] = {
            "mode": self.mode,
            "take": max(1, min(int(max_items), 100)),
        }
        if date:
            params["since"] = self._since_for_date(date)
        url = f"{self.base_url}/api/public/items?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            },
        )
        if self.api_key:
            request.add_header("Authorization", f"Bearer {self.api_key}")
        return request

    def fetch_daily_news(self, date: str | None = None, max_items: int = 20) -> list[dict[str, Any]]:
        request = self.build_items_request(date=date, max_items=max_items)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError("AIHOT_SKILL_REQUEST_FAILED") from exc

        raw_items = self._extract_items(payload)
        items = [self.normalize_news_item(item) for item in raw_items]
        items = [item for item in items if item.get("title") and item.get("summary")]
        if not items:
            raise RuntimeError("AIHOT_SKILL_EMPTY_RESULT")
        return items[:max_items]

    def _since_for_date(self, date: str) -> str:
        try:
            target = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return date
        # items API is limited to the recent 7-day window. For a target date, ask from
        # that UTC day start; the server will clamp very old dates if needed.
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        since = max(target, seven_days_ago)
        return since.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _extract_items(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]
        if isinstance(payload, dict):
            sections = payload.get("sections")
            if isinstance(sections, list):
                flattened: list[dict[str, Any]] = []
                for section in sections:
                    if not isinstance(section, dict):
                        continue
                    label = section.get("label") or section.get("category")
                    for item in section.get("items") or []:
                        if isinstance(item, dict):
                            enriched = dict(item)
                            if label and not enriched.get("category"):
                                enriched["category"] = label
                            flattened.append(enriched)
                if flattened:
                    return flattened
            for key in ("items", "news", "data", "results", "hot_news"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [x for x in value if isinstance(x, dict)]
                if isinstance(value, dict):
                    nested = self._extract_items(value)
                    if nested:
                        return nested
        return []

    def normalize_news_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        title = raw_item.get("title") or raw_item.get("name") or raw_item.get("headline") or ""
        url = raw_item.get("url") or raw_item.get("link") or raw_item.get("sourceUrl") or raw_item.get("source_url") or ""
        summary = raw_item.get("summary") or raw_item.get("desc") or raw_item.get("description") or raw_item.get("content") or ""
        content = raw_item.get("content") or raw_item.get("body") or summary
        category = raw_item.get("category") or raw_item.get("type") or "AI资讯"
        tags = raw_item.get("tags") or raw_item.get("keywords") or []
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.replace("，", ",").split(",") if tag.strip()]
        if not tags and isinstance(category, str):
            tags = [CATEGORY_LABELS.get(category, category)]
        return {
            "external_id": raw_item.get("id") or "",
            "title": str(title).strip(),
            "title_en": raw_item.get("title_en") or raw_item.get("titleEn") or "",
            "url": str(url).strip(),
            "source": raw_item.get("source") or raw_item.get("sourceName") or raw_item.get("site") or "AIHot",
            "published_at": raw_item.get("publishedAt") or raw_item.get("published_at") or raw_item.get("date") or raw_item.get("time") or "",
            "summary": str(summary).strip(),
            "content": str(content).strip(),
            "category": category,
            "tags": tags,
            "raw": raw_item,
        }
