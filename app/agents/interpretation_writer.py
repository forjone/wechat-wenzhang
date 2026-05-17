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
        "keywords": ("postgres", "检索", "bm25", "数据库", "搜索", "多智能体", "向量", "psql", "知识库"),
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

def _generic_theme_for_item(item: dict[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or "这次AI变化").strip()
    context = str(item.get("summary") or item.get("content") or item.get("original_excerpt") or "").strip()
    combined = f"{title} {context}".lower()

    if any(keyword in combined for keyword in ("notion", "开发者平台")):
        return {
            "signal": f"{title} 的核心不是又多一个工具入口，而是把工作区、代码、数据同步和自动化流程放到同一个平台里重新组织。",
            "follow_up_question": "当知识库本身能运行代码、同步数据并调用 Agent，团队是不是会少装几个割裂的自动化工具？",
            "importance": f"{title} 值得看，是因为它把原来分散在脚本、数据库同步、内部工具和知识库里的工作，往同一个协作界面里收。\n\n如果这种平台化能力成熟，开发者做的不只是写一个插件，而是把团队日常文档、数据、审批和自动化串成可复用流程。\n\n真正要跟踪的是：它能不能从开发者能力，变成普通团队也能长期使用的工作台。",
            "people": [
                ("Notion重度团队和运营人员", "可以把文档、表格、外部数据和自动化流程放在同一个工作区里管理，减少来回切工具。"),
                ("内部工具开发者", "可以围绕 CLI、Workers、API 和同步能力做轻量应用，而不是从零搭一套后台。"),
                ("知识管理顾问和自动化服务商", "可以把客户的工作流沉淀成 Notion 模板、同步方案和自动化交付包。"),
            ],
            "opportunities": [
                ("模板产品机会", "把销售线索、内容排期、项目管理等流程做成带自动化的 Notion 模板。"),
                ("集成服务机会", "帮团队把 CRM、表单、工单或数据表同步进 Notion，并配好提醒和审批流。"),
                ("教学内容机会", "围绕 Notion CLI、Workers 和 Agent 工具做案例教程，让非纯技术团队也能上手。"),
            ],
            "actions": [
                "选一个自己正在用 Notion 管的流程，标出哪些步骤需要外部数据或重复操作。",
                "用 CLI 或 API 做一个最小自动化，例如把表单线索同步到 Notion 数据库并生成跟进任务。",
                "把完整配置录成教程或模板，测试别人是否能在 30 分钟内复用。",
            ],
        }

    if any(keyword in combined for keyword in ("论文", "研究", "可解释", "隐藏状态", "工具使用", "认知", "行动", "调用失败")):
        return {
            "signal": f"{title} 的重点不是模型又会不会调用工具，而是解释了 Agent 从知道该做什么到真正执行之间为什么会断掉。",
            "follow_up_question": "如果模型内部已经识别出该调用工具，却在最后一步没有行动，单靠改提示词还能解决多少问题？",
            "importance": f"{title} 重要，是因为它把 Agent 失败从表层提示词问题，推进到模型内部机制问题。\n\n这会影响我们评估工具调用、任务规划和自动化系统的方式：失败不一定是没有理解，也可能是理解和行动之间的转换出了问题。\n\n真正要跟踪的是：未来的 Agent 评测能不能提前发现这种“知道但不做”的风险。",
            "people": [
                ("Agent产品和工程团队", "需要在工具调用链路里增加可观测、回放和失败分类，不能只看最终成功率。"),
                ("AI研究者和评测团队", "可以把隐藏状态、调用决策和动作输出拆开评估，定位模型失败发生在哪一层。"),
                ("依赖自动化的业务团队", "在客服、运维、数据分析等场景里，需要为关键工具调用保留确认、兜底和审计机制。"),
            ],
            "opportunities": [
                ("评测工具机会", "做专门检测 Agent 工具调用漏调、错调和迟疑的测试集与监控面板。"),
                ("工程服务机会", "帮企业把 Agent 工作流加上日志、回放、人工确认和失败恢复机制。"),
                ("研究解读机会", "把复杂可解释性论文翻译成产品经理和工程团队能用的上线检查清单。"),
            ],
            "actions": [
                "拿一个现有 Agent 流程，统计模型识别出工具需求但没有调用的案例。",
                "把失败拆成三类：没理解任务、选错工具、知道工具但没有执行。",
                "为高风险工具调用加一层确认或重试策略，先验证成功率能不能提升。",
            ],
        }

    if any(keyword in combined for keyword in ("openrouter", "router", "路由", "模型路由", "智能体工作流", "开源并上线", "ring-")):
        return {
            "signal": f"{title} 的重点不是又多一个模型发布，而是开源模型开始通过 OpenRouter 这类分发入口进入 Agent 工作流。",
            "follow_up_question": "当模型既开源又能被路由平台直接调用，开发者选择模型的标准会不会从“参数大小”转向“任务适配和调用成本”？",
            "importance": f"{title} 值得看，是因为它把模型能力、开源可用性和调用入口连在了一起。\n\n对普通开发者来说，真正的变化不是下载一个大模型，而是能不能在自己的 Agent 流程里低成本测试、切换和组合不同模型。\n\n真正要跟踪的是：这类模型能不能在工具调用、长任务和多步骤推理里表现稳定，而不是只看榜单分数。",
            "people": [
                ("Agent应用开发者", "可以更方便地把新模型接入现有工作流，比较不同任务上的效果和成本。"),
                ("模型平台和工具团队", "需要围绕路由、评测、降级和成本控制设计更清楚的模型选择机制。"),
                ("做AI自动化的小团队", "不必一开始自建推理部署，可以先通过平台验证模型是否适合具体业务流程。"),
            ],
            "opportunities": [
                ("评测内容机会", "用真实 Agent 任务测试模型在工具调用、计划执行和长上下文里的表现。"),
                ("路由方案机会", "把不同模型按任务类型、价格、速度和稳定性做成可复用选择策略。"),
                ("落地服务机会", "帮团队把 OpenRouter 等入口接入现有自动化流程，并建立失败回退方案。"),
            ],
            "actions": [
                "选一个真实 Agent 任务，用同一组提示词比较新模型和现有模型的成功率。",
                "记录每次调用的成本、延迟和失败类型，判断它适合放在主链路还是备用链路。",
                "为关键任务准备至少一个回退模型，避免单一模型不稳定影响整个工作流。",
            ],
        }

    if any(keyword in combined for keyword in ("快捷键", "codex", "设置", "自定义", "效率")):
        return {
            "signal": f"{title} 看起来是小功能，但真正指向的是 AI 工具开始适配个人工作流，而不是让人适应默认交互。",
            "follow_up_question": "当 AI 编程工具能被按个人习惯重新配置，效率差距会不会来自工作流设计，而不只是模型能力？",
            "importance": f"{title} 值得看，是因为高频工具里的小交互会不断累积成生产力差异。\n\n快捷键、入口、默认动作和上下文组织方式一旦能被定制，用户就能把 AI 放进自己的节奏里，而不是每次重新适应工具。\n\n真正要跟踪的是：AI 工具会不会从“会回答”变成“顺手嵌入每天的工作动作”。",
            "people": [
                ("高频使用AI编程工具的开发者", "可以减少重复操作，把常用命令和审查动作变成更顺手的肌肉记忆。"),
                ("团队技术负责人", "需要沉淀团队统一快捷键、命令模板和代码审查流程，降低新人上手成本。"),
                ("效率工具内容创作者", "可以把个性化设置和工作流优化讲成可复制的教程。"),
            ],
            "opportunities": [
                ("工作流模板机会", "整理不同岗位的快捷键配置、命令习惯和自动化脚本包。"),
                ("培训机会", "帮团队把 AI 编程工具从“能用”调到“顺手高频用”。"),
                ("内容机会", "用实际开发任务对比默认设置和定制设置的耗时差异。"),
            ],
            "actions": [
                "记录自己一天里重复最多的 5 个 AI 工具操作，先把其中两个改成快捷键。",
                "为代码生成、解释、测试、提交分别设计固定触发方式，减少来回找入口。",
                "一周后统计节省的点击和切换次数，判断是否值得做成团队模板。",
            ],
        }

    return {
        "signal": f"{title} 的重点不是新闻本身，而是它暴露出一个可以被重新设计的具体流程。",
        "follow_up_question": f"围绕“{_clip(title, 18)}”，到底是哪类人、哪一步工作、哪种交付结果会先发生变化？",
        "importance": f"{title} 值得看，是因为它不是一个抽象的 AI 概念，而是已经落到具体产品、流程或研究问题上。\n\n判断它有没有价值，要回到这条新闻里的对象：谁会使用、解决什么问题、能不能比原来更快或更便宜。\n\n真正要跟踪的是：它会不会从一次发布，变成某个细分场景里的固定工作方式。",
        "people": [
            (f"关注{_clip(title, 10)}的一线使用者", "可以先判断它会不会改变自己的日常任务、信息处理或交付方式。"),
            ("相关产品和服务团队", f"可以围绕“{_clip(title, 16)}”重新设计入口、模板、培训和客户成功流程。"),
            ("想做内容或副业的普通人", "机会在于把新闻翻译成具体案例、操作步骤和可交付服务。"),
        ],
        "opportunities": [
            ("场景拆解机会", f"把“{_clip(title, 18)}”拆成适用人群、使用前后对比和落地边界。"),
            ("模板工具机会", "把新闻里的能力沉淀成提示词、流程表、检查清单或轻量自动化脚本。"),
            ("垂直服务机会", "找一个自己熟悉的小行业，替他们完成从试用到可复用流程的第一步。"),
        ],
        "actions": [
            f"先用一句话写清楚“{_clip(title, 18)}”解决的具体问题，不要停在新闻标题。",
            "选一个真实场景做最小实验，记录使用前后的时间、成本和质量变化。",
            "把实验过程整理成教程、清单或小服务，找 3 个目标用户验证是否愿意复用。",
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
    if any(keyword in haystack for keyword in ("notion", "快捷键", "工具使用代理", "认知与行动", "可解释性论文")):
        return _generic_theme_for_item(item)
    for profile in _KIND_PROFILES:
        if any(keyword.lower() in haystack for keyword in profile["keywords"]):
            return profile
    return _generic_theme_for_item(item)


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
