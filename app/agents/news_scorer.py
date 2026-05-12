from __future__ import annotations

from typing import Any

IMPORTANT_KEYWORDS = ["OpenAI", "Claude", "Gemini", "Agent", "AI工具", "AI搜索", "AI视频", "模型", "效率", "内容", "创业"]
ACTIONABLE_KEYWORDS = ["普通人", "内容创作者", "小老板", "职场", "效率", "工具", "赚钱", "副业", "创业", "自动化", "机会"]
TECH_ONLY_KEYWORDS = ["参数", "benchmark", "论文", "训练细节"]


def _text(item: dict[str, Any]) -> str:
    tags = item.get("tags") or []
    if isinstance(tags, list):
        tags = " ".join(map(str, tags))
    return " ".join(str(item.get(k, "")) for k in ("title", "summary", "content", "category")) + " " + str(tags)


def _count_keywords(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lower)


def score_for_briefing(item: dict[str, Any]) -> int:
    text = _text(item)
    importance = min(10, 4 + _count_keywords(text, IMPORTANT_KEYWORDS) * 2)
    relevance = min(10, 3 + _count_keywords(text, ACTIONABLE_KEYWORDS) * 2)
    freshness = 8 if item.get("published_at") else 7
    credibility = 8 if item.get("source") or item.get("url") else 6
    clarity = 8 if item.get("summary") else 5
    penalty = _count_keywords(text, TECH_ONLY_KEYWORDS)
    return max(0, importance + relevance + freshness + credibility + clarity - penalty)


def score_for_interpretation(item: dict[str, Any]) -> int:
    text = _text(item)
    trend = min(10, 4 + _count_keywords(text, IMPORTANT_KEYWORDS) * 2)
    opportunity = min(10, 3 + _count_keywords(text, ACTIONABLE_KEYWORDS) * 2)
    breadth = 8 if any(word in text for word in ["普通人", "职场", "内容创作者", "创业", "工具"]) else 6
    long_term = 8 if any(word in text for word in ["入口", "搜索", "Agent", "自动化", "模型"]) else 6
    actionability = opportunity
    virality = min(10, 5 + _count_keywords(text, ["OpenAI", "视频", "搜索", "赚钱", "工具"]))
    penalty = _count_keywords(text, TECH_ONLY_KEYWORDS) * 2
    return max(0, trend + opportunity + breadth + long_term + actionability + virality - penalty)


def dedupe_news(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_titles: set[str] = set()
    seen_urls: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        if (title and title in seen_titles) or (url and url in seen_urls):
            continue
        if title:
            seen_titles.add(title)
        if url:
            seen_urls.add(url)
        result.append(item)
    return result
