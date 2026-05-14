from __future__ import annotations

from typing import Any


_KIND_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "keywords": ("音乐", "suno", "音频", "歌曲", "流媒体", "carplay", "android auto", "车载"),
        "signal": "AI 音乐正在从创作工具进入真实播放场景，车载系统会把“随手生成、随处收听”的音乐消费变成日常习惯。",
        "follow_up_question": "当音乐可以在车里即时生成和播放时，通勤、自驾、亲子出行这些场景会不会出现新的内容入口？",
        "importance": "Suno 这次不是简单多了一个播放渠道，而是把 AI 音乐接进了 Apple CarPlay 和 Android Auto 这样的高频车载入口。\n\n这意味着用户创作的音乐不只停留在网页或 App 里，而是可以进入通勤、旅行、夜路和亲子出行。\n\n真正要跟踪的是：车内娱乐会不会从“搜索现成歌曲”，变成“按场景生成声音内容”。",
        "people": [
            ("音乐创作者和播客作者", "可以把 AI 生成内容直接放进通勤、旅行、车内娱乐等高频收听场景，测试更真实的用户反馈。"),
            ("车载与智能座舱团队", "需要重新思考车内内容服务：播放列表不再只来自版权曲库，也可能来自用户即时生成的个性化声音。"),
            ("普通通勤用户", "可以用更低门槛把情绪、路线、场景变成专属歌单，音乐体验从“搜索播放”转向“描述生成”。"),
        ],
        "opportunities": [
            ("场景内容机会", "围绕通勤、亲子出行、露营、自驾等场景制作 AI 歌单、声音包和使用教程。"),
            ("服务机会", "为品牌、门店、车友会定制车内播放内容，把 AI 音乐包装成可交付的场景化素材。"),
            ("产品机会", "做连接 AI 音乐、车机、播客和个人歌单的小工具，降低用户从创作到播放的链路成本。"),
        ],
        "actions": [
            "用 Suno 做 3 组具体车内场景歌单：通勤、夜路、自驾，并记录每组提示词。",
            "观察 Apple CarPlay / Android Auto 上 AI 内容入口的位置，判断用户是否真的能顺手使用。",
            "把一次完整体验写成教程或短视频，重点讲“怎么在车里用起来”，而不是只讲模型能力。",
        ],
    },
    {
        "keywords": ("电影", "视频", "runway", "kling", "可灵", "影像", "动画", "storyboard", "剪辑", "3d"),
        "signal": "AI 视频正在从单点生成能力走向完整制作流程，真正的变化是创意人可以用更小团队完成过去需要多角色协作的影像工作。",
        "follow_up_question": "当视频生产从单个镜头生成走向脚本、分镜、样片和剪辑协同，个人和小团队能不能更快交付完整作品？",
        "importance": "这类变化重要的地方不只是模型效果更好，而是视频制作链条被重新拆开。\n\n过去需要编剧、分镜、拍摄、后期多角色反复沟通的环节，现在可能被压缩成一套更轻的 AI 工作流。\n\n真正要跟踪的是：谁能把创意判断、镜头语言和工具流程组合起来，稳定交付可用的视频草案。",
        "people": [
            ("短视频和影视创作者", "分镜、概念片、样片和后期试错成本会下降，个人创作者更容易拿出接近工业流程的作品雏形。"),
            ("品牌市场团队", "可以更快把活动创意变成可评审的视频草案，减少外包沟通和等待周期。"),
            ("设计与动画从业者", "竞争重点会从单一软件操作，转向镜头语言、叙事节奏和 AI 工作流组织能力。"),
        ],
        "opportunities": [
            ("案例拆解机会", "拆解这个工具适合哪类镜头、哪类风格、哪类商业短片，帮助创作者避开无效试错。"),
            ("工作流机会", "把脚本、分镜、生成、剪辑、封面包装成一套可复用模板，卖给内容团队或中小商家。"),
            ("垂直服务机会", "针对房产、教育、招聘、门店活动等场景提供低成本 AI 视频样片服务。"),
        ],
        "actions": [
            "选一个 30 秒商业短片题目，跑通从脚本到分镜再到成片草案的完整流程。",
            "记录每一步耗时和失败点，形成可复用的提示词和镜头模板。",
            "找一个具体行业客户验证：他们愿不愿意为“更快看到视频草案”付费。",
        ],
    },
    {
        "keywords": ("postgres", "检索", "bm25", "数据库", "搜索", "agent", "多智能体", "向量", "psql"),
        "signal": "AI 应用的瓶颈正在从“能不能生成”转向“能不能又快又准地找到上下文”，检索基础设施会直接决定 Agent 的可用性。",
        "follow_up_question": "如果 AI 搜索和 Agent 找不到准确上下文，再强的模型是不是也只能给出看似流畅但不可靠的答案？",
        "importance": "AI 搜索升级值得看，不是因为搜索框换了一个名字，而是它会影响人和 Agent 获取上下文的方式。\n\n当信息入口从关键词列表变成可对话、可调用、可组合的上下文层，产品差距就会落到召回质量、延迟、权限和可验证性上。\n\n真正要跟踪的是：AI 能不能在正确的数据里找到正确材料，而不是只生成一段漂亮回答。",
        "people": [
            ("AI 应用开发者", "可以在熟悉的数据库里提升关键词检索和上下文召回，减少额外维护搜索系统的成本。"),
            ("企业技术团队", "在数据合规、权限和稳定性要求高的场景里，更愿意把检索能力放进现有 PostgreSQL 体系。"),
            ("做知识库和 Agent 的创业者", "产品差距会越来越体现在召回质量、延迟和部署复杂度，而不是只看接入了哪个大模型。"),
        ],
        "opportunities": [
            ("技术内容机会", "用真实数据对比 BM25、向量检索和混合检索，做成开发者能直接复用的教程。"),
            ("工具机会", "封装面向客服、销售、文档问答的 PostgreSQL 检索模板，降低中小团队部署 Agent 的门槛。"),
            ("咨询机会", "帮助已有数据库的企业把内部知识库改造成可评估、可迭代的 Agent 检索层。"),
        ],
        "actions": [
            "拿一个现有文档库做检索评测，比较关键词、向量和混合检索在准确率与延迟上的差异。",
            "整理一份“Agent 检索上线清单”：数据清洗、权限、评测集、日志和回滚方案。",
            "优先找已经使用 PostgreSQL 的团队验证，因为迁移阻力最低。",
        ],
    },
    {
        "keywords": ("小型企业", "small business", "企业", "销售", "客服", "财务", "quickbooks", "paypal", "hubspot", "claude"),
        "signal": "AI 正在从个人效率工具进入小企业的经营流程，价值不再只是写文案，而是把财务、销售、客服和运营串起来。",
        "follow_up_question": "当 AI 能接入财务、销售、客服这些日常系统，小企业老板会不会先为“少漏单、少重复录入”买单？",
        "importance": "小企业场景重要的地方不是又多了一个聊天助手，而是 AI 开始碰到经营里的具体流程。\n\n财务、销售、客服和运营如果能被串起来，AI 的价值就从写一段文案，变成减少漏单、缩短跟进、降低人工重复劳动。\n\n真正要跟踪的是：这些能力能不能接入老板已经在用的工具，并且带来可计算的时间和成本节省。",
        "people": [
            ("小企业老板", "可以用更低成本补齐财务整理、客户跟进、销售材料和内部流程自动化能力。"),
            ("SaaS 服务商和顾问", "客户会更关心 AI 能否接入现有工具并带来可量化节省，而不是单纯聊天体验。"),
            ("运营和销售人员", "重复录入、汇总、跟进提醒会被自动化，人的重点转向客户判断和关系维护。"),
        ],
        "opportunities": [
            ("行业方案机会", "针对餐饮、门店、咨询、跨境电商等小企业做 AI 自动化套餐。"),
            ("集成服务机会", "围绕 QuickBooks、PayPal、HubSpot 等工具提供连接、模板和培训。"),
            ("内容机会", "用具体账单、客户跟进、报价单场景讲清楚 AI 如何省时间、少漏单。"),
        ],
        "actions": [
            "选一个小企业高频流程，比如收款后自动生成跟进任务，画出 AI 可介入的步骤。",
            "做一份 1 页 ROI 表：每周节省几小时、减少哪些错误、需要多少订阅成本。",
            "找 3 个真实小老板访谈，确认他们最愿意先自动化的是财务、销售还是客服。",
        ],
    },
)

_DEFAULT_PROFILE = {
    "signal": "这条新闻的重点不是又多了一个 AI 产品，而是它把 AI 能力推进到一个更具体、更高频的使用场景里。",
    "follow_up_question": "这个变化到底会改变哪一个具体人群、哪一个具体流程、哪一个具体交付结果？",
    "importance": "这条新闻值得看的地方，不是标题里出现了 AI，而是它指向了一个更具体的落地场景。\n\n判断它有没有价值，要看它能不能降低某个流程的门槛，缩短一次交付的时间，或者让过去很难规模化的服务变得可复制。\n\n真正要跟踪的是：这次变化会不会从一次发布，变成一个具体行业愿意持续使用的工作方式。",
    "people": [
        ("这个领域的一线使用者", "需要判断它是否能缩短流程、降低成本，或者带来新的交付方式。"),
        ("相关产品和服务团队", "可以围绕这次变化重新设计入口、模板、培训和客户成功流程。"),
        ("想做副业的普通人", "机会在于把新能力翻译成行业能听懂、能购买、能复用的小方案。"),
    ],
    "opportunities": [
        ("解释机会", "把这条新闻讲成具体场景、具体人群、具体用法，而不是停留在发布信息。"),
        ("模板机会", "把新能力沉淀成提示词、流程表、检查清单或自动化脚本。"),
        ("服务机会", "找到一个垂直行业，替他们完成从试用到落地的第一公里。"),
    ],
    "actions": [
        "把新闻里的产品、目标用户、使用场景各写成一句话，先确认它到底解决什么问题。",
        "找一个自己熟悉的行业，设计一个最小可验证用法，并用真实素材试一次。",
        "记录使用前后的时间、成本和质量变化，判断它是否值得做成内容或服务。",
    ],
}


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


def _profile_for_item(item: dict[str, Any]) -> dict[str, Any]:
    haystack = " ".join(
        str(part or "")
        for part in (
            item.get("title"),
            item.get("summary"),
            item.get("content"),
            item.get("category"),
            " ".join(str(tag) for tag in item.get("tags") or []),
        )
    ).lower()
    for profile in _KIND_PROFILES:
        if any(keyword.lower() in haystack for keyword in profile["keywords"]):
            return profile
    return _DEFAULT_PROFILE


def _numbered_lines(items: list[tuple[str, str]]) -> str:
    return "\n\n".join(f"{idx}. {title}\n{body}" for idx, (title, body) in enumerate(items, start=1))


def _action_lines(actions: list[str]) -> str:
    return "\n".join(f"{idx}. {action}" for idx, action in enumerate(actions, start=1))


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
    profile = _profile_for_item(item)
    real_signal = profile["signal"]
    follow_up_question = profile["follow_up_question"]
    importance = profile["importance"]
    affected_people = [{"group": group, "impact": impact} for group, impact in profile["people"]]
    opportunities = {f"opportunity_{idx}": f"{title}：{body}" for idx, (title, body) in enumerate(profile["opportunities"], start=1)}
    actions = list(profile["actions"])
    markdown = f"""你好，我是**超级发**。
今天想重点解读一件 AI 变化：
{summary}
这件事表面上看是：
{event_title}
**真正值得关注的是**：
{real_signal}

## 一、今天发生了什么？

{summary}
**真正要问的是**：{follow_up_question}

## 二、这件事为什么重要？

{analysis_context}

{importance}

## 三、它会影响哪些人？

{_numbered_lines(profile["people"])}

## 四、普通人能看到什么机会？

{_numbered_lines(profile["opportunities"])}

## 五、现在可以做什么？

{_action_lines(actions)}

> [!important] 超级发一句话
> 机会不在 AI 新闻本身，而在你能不能把“{_clip(event_title, 18)}”翻译成一个具体人群愿意使用的工具、服务或行动方案。
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
        "affected_people": affected_people,
        "opportunities": opportunities,
        "actions": actions,
        "content_markdown": markdown,
        "cover_prompt": f"一张微信公众号文章题图，主题是“{title_event}”。画面中央是一个普通人站在巨大的AI信息网络前，前方有搜索框、数据流、网页卡片和智能助手图标。整体风格简洁、现代、科技感，蓝白色调，文字为“超级发AI解读”。不要过度赛博朋克，不要复杂背景。",
        "status": "generated",
    }
