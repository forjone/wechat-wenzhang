from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def _cn_date(date: str, *, include_year: bool = False) -> str:
    dt = datetime.strptime(date, "%Y-%m-%d")
    if include_year:
        return f"{dt.year}年{dt.month}月{dt.day}日"
    return f"{dt.month}月{dt.day}日"


def display_date_for_news_date(date: str) -> str:
    """Return the publication/display date for a fetched news date.

    Daily briefings usually cover the previous day's news but are published the
    next day, so user-facing titles and metadata should show the publication day.
    """
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return date
    return (dt + timedelta(days=1)).strftime("%Y-%m-%d")


def _short_title(raw_title: Any, max_chars: int = 24) -> str:
    title = str(raw_title or "AI重要信号").strip()
    for separator in ["：", ":", "，", ",", "｜", "|", "—", "-"]:
        if separator in title:
            title = title.split(separator, 1)[0].strip()
            break
    return title[:max_chars].strip() or "AI重要信号"


def _format_category(category: Any) -> str:
    if not category:
        return ""
    labels = {
        "tip": "技巧与观点",
        "ai-products": "产品发布/更新",
        "industry": "行业动态",
        "research": "研究进展",
    }
    raw = str(category).strip()
    return f"`{labels.get(raw, raw)}`"


def generate_briefing(news_items: list[dict[str, Any]], date: str, issue_no: int, max_items: int = 10) -> dict[str, Any]:
    display_date = display_date_for_news_date(date)
    selected = news_items if max_items == 0 else news_items[:max_items]
    title_signal = _short_title(selected[0].get("title") if selected else "AI重要信号")
    title = f"AI简报{issue_no:03d}｜{_cn_date(display_date)}：{title_signal}"
    lines = [
        f"# {title}",
        "",
        f"日期：{_cn_date(display_date)}",
        f"条目：{len(selected)} 条",
        "排序：按新闻影响范围和价值重要度降序取前10条" if len(selected) >= 10 else "排序：按新闻影响范围和价值重要度降序",
        "",
    ]
    normalized_items = []
    for idx, item in enumerate(selected, 1):
        summary = item.get("summary") or item.get("content") or ""
        category = _format_category(item.get("category"))
        url = item.get("url", "")
        lines.extend([f"### {idx}. {item.get('title')}", ""])
        if category:
            lines.extend([category, ""])
        if summary:
            lines.extend([str(summary), ""])
        lines.extend(["---", ""])
        normalized_items.append({
            "title": item.get("title"),
            "url": url,
            "source": item.get("source", ""),
            "published_at": item.get("published_at", ""),
            "category": item.get("category", ""),
            "summary": summary,
            "raw_summary": summary,
            "tags": item.get("tags", []),
            "source_mode": item.get("source_mode", ""),
            "source_error": item.get("source_error", ""),
            "source_provider": item.get("source_provider", ""),
        })
    if not selected:
        lines.append("今天暂未获取到 AIHot 信号源条目。")
    markdown = "\n".join(lines).strip() + "\n"
    digest_titles = "、".join(str(x.get("title", "")) for x in selected[:3])
    digest = f"今日AI简报{len(selected)}条" + (f"：{digest_titles}" if digest_titles else "")
    cover_subject = title_signal
    return {
        "content_type": "briefing",
        "title": title,
        "digest": digest[:120],
        "date": display_date,
        "issue_no": issue_no,
        "source_mode": selected[0].get("source_mode", "unknown") if selected else "empty",
        "source_error": selected[0].get("source_error", "") if selected else "NO_NEWS_SELECTED",
        "news_items": normalized_items,
        "content_markdown": markdown,
        "cover_prompt": f"一张微信公众号文章题图，主题是“{cover_subject}”。画面是简洁的信息流列表，包含AI新闻卡片、趋势箭头和智能助手图标。绿色科技感，清爽、可信、信息密度适中，文字为“超级发AI简报”。",
        "status": "generated",
    }
