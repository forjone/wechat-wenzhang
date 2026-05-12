from __future__ import annotations

from typing import Any


def _context_from_original_or_summary(item: dict[str, Any]) -> str:
    original = str(item.get("original_content") or item.get("original_excerpt") or "").strip()
    if original:
        return original
    return str(item.get("summary") or item.get("content") or item.get("title") or "").strip()


def _summary_from_original_or_summary(item: dict[str, Any]) -> str:
    original = str(item.get("original_excerpt") or item.get("original_content") or "").strip()
    if original:
        return original[:900]
    return str(item.get("summary") or item.get("content") or item.get("title") or "").strip()


def _clip(text: str, limit: int) -> str:
    text = str(text or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _source_news_metadata(item: dict[str, Any], summary: str) -> dict[str, Any]:
    return {
        "title": item.get("title"),
        "url": item.get("url", ""),
        "summary": summary,
        "source_mode": item.get("source_mode", ""),
        "source_error": item.get("source_error", ""),
        "source_provider": item.get("source_provider", ""),
        "original_url": item.get("original_url", item.get("url", "")),
        "original_title": item.get("original_title", ""),
        "original_author": item.get("original_author", ""),
        "original_content": item.get("original_content", ""),
        "original_excerpt": item.get("original_excerpt", ""),
        "original_fetch_status": item.get("original_fetch_status", "not_requested"),
        "original_fetch_error": item.get("original_fetch_error", ""),
    }


def generate_interpretation(
    news_items: list[dict[str, Any]],
    date: str,
    issue_no: int,
    *,
    include_issue_number: bool = True,
) -> dict[str, Any]:
    item = news_items[0]
    event_title = str(item.get("title", "这次AI变化"))
    summary = _summary_from_original_or_summary(item)
    analysis_context = _context_from_original_or_summary(item)
    title_event = event_title[:28]
    if include_issue_number:
        title = f"AI解读{issue_no:03d}｜{title_event}，普通人该看到什么机会？"
    else:
        title = f"{title_event}，普通人该看到什么机会？"
    real_signal = "AI 正在从少数人的技术能力，变成普通人可以直接使用的生产力工具。"
    markdown = f"""你好，我是**超级发**。
今天想重点解读一件 AI 变化：
{summary}
这件事表面上看是：
{event_title}
**真正值得关注的是**：
{real_signal}

## 一、今天发生了什么？

{summary}
**普通人不用关心参数多了多少**，真正要关心的是：这个变化会不会改变你的工作方式。

## 二、这件事为什么重要？

{analysis_context}

它重要的地方不在于又多了一个 AI 新闻，而在于 **AI 工具正在更直接地进入** 内容生产、信息获取、办公协作和小生意流程。
如果原文里已经出现产品能力、使用门槛、目标用户或商业化路径，这些信息比单纯的发布标题更值得跟踪。

## 三、它会影响哪些人？

1. 内容创作者
可以更快完成选题、资料整理、脚本和图文生产。

2. 职场人
可以把一部分重复的信息处理工作交给 AI，提高日常工作效率。

3. 个体创业者和小老板
可以用更低成本搭建获客、客服、内容和自动化流程。

## 四、普通人能看到什么机会？

1. 内容机会
围绕这个变化做解释型内容、教程、案例拆解，帮助别人看懂和用起来。

2. 工具机会
把复杂能力包装成模板、工作流、小工具或自动化服务。

3. 副业机会
为垂直行业提供“AI 代搭建”“AI 流程改造”“AI 内容生产”服务。

4. 行业机会
越靠近信息处理、内容生产、客户沟通的岗位，越会先被 AI 改变。

## 五、现在可以做什么？

1. 先找到一个自己每天重复做的工作环节，用 AI 试着替代 30%。
2. 记录使用过程，把经验整理成教程或案例。
3. 观察身边哪个行业最缺这种能力，尝试做一个小服务。

> [!important] 超级发一句话
> 机会不在 AI 新闻本身，而在你能不能把这条新闻翻译成一个别人愿意使用的工具、服务或行动方案。
"""
    return {
        "content_type": "interpretation",
        "title": title,
        "digest": f"{event_title} 表面上是一次AI变化，背后是普通人使用AI的方式正在改变。"[:120],
        "date": date,
        "issue_no": issue_no,
        "source_mode": item.get("source_mode", "unknown"),
        "source_error": item.get("source_error", ""),
        "source_news": [_source_news_metadata(item, summary)],
        "real_signal": real_signal,
        "affected_people": [
            {"group": "内容创作者", "impact": "更快完成选题、资料整理和内容生产"},
            {"group": "职场人", "impact": "提高信息处理和办公协作效率"},
            {"group": "个体创业者", "impact": "降低获客、客服和自动化成本"},
        ],
        "opportunities": {"content": "解释型内容和教程", "tool": "模板、工作流、小工具", "side_business": "AI流程改造服务", "industry": "信息处理和客户沟通岗位"},
        "actions": ["替代一个重复工作环节", "整理教程或案例", "尝试垂直小服务"],
        "content_markdown": markdown,
        "cover_prompt": f"一张微信公众号文章题图，主题是“{title_event}”。画面中央是一个普通人站在巨大的AI信息网络前，前方有搜索框、数据流、网页卡片和智能助手图标。整体风格简洁、现代、科技感，蓝白色调，文字为“超级发AI解读”。不要过度赛博朋克，不要复杂背景。",
        "status": "generated",
    }
