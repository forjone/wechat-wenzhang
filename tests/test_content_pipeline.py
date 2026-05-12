from app.sources.aihot_skill import AIHotSkillClient
from app.agents.news_scorer import score_for_briefing, score_for_interpretation, dedupe_news
from app.agents.briefing_writer import generate_briefing
from app.agents.interpretation_writer import generate_interpretation
from app.agents.image_generator import generate_article_images, build_image_prompt
from app.render.markdown_to_html import markdown_to_wechat_html, default_wechat_theme
import json


def test_default_wechat_theme_routes_by_content_type():
    assert default_wechat_theme("briefing") == "bytedance-green"
    assert default_wechat_theme("interpretation") == "fresh-card"
    assert default_wechat_theme("analysis") == "fresh-card"
    assert default_wechat_theme("") == "fresh-card"


def test_markdown_to_wechat_html_applies_content_type_theme():
    briefing_html = markdown_to_wechat_html("# 标题\n\n正文", content_type="briefing")
    interpretation_html = markdown_to_wechat_html("# 标题\n\n正文", content_type="interpretation")

    assert 'data-theme="bytedance-green"' in briefing_html
    assert "#1f3d2b" in briefing_html
    assert 'data-theme="fresh-card"' in interpretation_html
    assert "#f5f8f5" in interpretation_html


def test_aihot_normalizes_common_item_shapes():
    client = AIHotSkillClient()
    raw = {"name": "OpenAI 发布新工具", "link": "https://example.com", "desc": "让普通人更容易制作内容", "tags": ["AI工具"]}
    item = client.normalize_news_item(raw)
    assert item["title"] == "OpenAI 发布新工具"
    assert item["url"] == "https://example.com"
    assert item["summary"] == "让普通人更容易制作内容"
    assert item["raw"] == raw


def test_dedupe_news_removes_same_url_or_title():
    items = [
        {"title": "A", "url": "https://x/1"},
        {"title": "A", "url": "https://x/2"},
        {"title": "B", "url": "https://x/1"},
    ]
    assert dedupe_news(items) == [{"title": "A", "url": "https://x/1"}]


def test_scoring_prioritizes_actionable_ai_tool_news():
    item = {"title": "AI工具 更新", "summary": "内容创作者可以提升效率并产生创业机会", "category": "AI工具", "tags": ["AI工具", "内容"]}
    assert score_for_briefing(item) >= 30
    assert score_for_interpretation(item) >= 35


def test_generate_briefing_outputs_required_structure():
    news = [{
        "title": "OpenAI 新工具显著降低内容创作门槛，这是一个很长的副标题需要被截断",
        "url": "https://x",
        "source": "AIHot",
        "summary": "帮助内容创作者提升效率",
        "what_happened": "OpenAI 发布了新工具。",
        "why_watch": "普通人可以用它提升内容生产效率。",
        "category": "产品发布/更新",
        "tags": ["AI工具"],
    }]
    article = generate_briefing(news, date="2026-05-09", issue_no=1)
    assert article["content_type"] == "briefing"
    assert article["title"] == "AI简报001｜5月10日：OpenAI 新工具显著降低内容创作门槛"
    assert article["date"] == "2026-05-10"
    assert "日期：5月10日" in article["content_markdown"]
    assert "2026年5月10日" not in article["content_markdown"]
    assert "今日AI信号源" not in article["title"]
    assert "## 今日AI信号源" not in article["content_markdown"]
    assert "来源：" not in article["content_markdown"]
    assert "分类：" not in article["content_markdown"]
    assert "原文：" not in article["content_markdown"]
    assert "今日AI信号源" not in article["cover_prompt"]
    assert "`产品发布/更新`" in article["content_markdown"]
    assert "#AI工具" not in article["content_markdown"]
    assert "帮助内容创作者提升效率" in article["content_markdown"]
    assert "超级发AI简报" in article["cover_prompt"]


def test_briefing_markdown_renders_news_headings_and_weak_category_tags():
    news = [{
        "title": "OpenCLI打通微信等私域信息流，聚合个人数据",
        "summary": "个人信息流聚合出现新工具。",
        "category": "ai-products",
        "tags": ["产品发布/更新"],
    }]
    article = generate_briefing(news, date="2026-05-09", issue_no=2)
    html = markdown_to_wechat_html(article["content_markdown"], content_type="briefing")

    assert "### 1." not in html
    assert "#产品发布/更新" not in html
    assert "<h3" in html
    assert "产品发布/更新" in html
    assert "ai-products" not in article["content_markdown"]


def test_generate_interpretation_marks_key_words_for_visual_emphasis():
    news = [{"title": "AI搜索升级", "url": "https://x", "summary": "AI搜索改变信息入口", "tags": ["AI搜索"]}]
    article = generate_interpretation(news, date="2026-05-09", issue_no=1)
    assert "你好，我是**超级发**。" in article["content_markdown"]
    assert "你好，我是**超级发**。\n今天想重点解读一件 AI 变化：" in article["content_markdown"]
    assert "AI搜索改变信息入口\n这件事表面上看是：" in article["content_markdown"]
    assert "**真正值得关注的是**" in article["content_markdown"]
    assert "> [!important] 超级发一句话" in article["content_markdown"]
    assert "**普通人不用关心参数多了多少**" in article["content_markdown"]
    assert "AI搜索改变信息入口\n**普通人不用关心参数多了多少**" in article["content_markdown"]
    assert "**AI 工具正在更直接地进入**" in article["content_markdown"]


def test_generate_interpretation_keeps_original_fetch_details_out_of_visible_body():
    news = [{
        "title": "AI搜索升级",
        "url": "https://x",
        "summary": "AI搜索改变信息入口",
        "original_fetch_status": "failed",
        "original_fetch_error": "URLError",
        "original_content": "原文抓取到了的正文，用于内部分析。",
    }]
    article = generate_interpretation(news, date="2026-05-09", issue_no=1)
    markdown = article["content_markdown"]

    assert "这次拆解参考的是" not in markdown
    assert "原文抓取失败" not in markdown
    assert "原文里真正值得拆开的信息" not in markdown
    assert "原文抓取到了的正文" in markdown
    assert article["source_news"][0]["original_fetch_status"] == "failed"


def test_interpretation_html_keeps_previous_structure_with_emphasis():
    news = [{"title": "AI搜索升级", "url": "https://x", "summary": "AI搜索改变信息入口", "tags": ["AI搜索"]}]
    article = generate_interpretation(news, date="2026-05-09", issue_no=1)
    html = markdown_to_wechat_html(article["content_markdown"], content_type="interpretation")

    assert "一、今天发生了什么" in html
    assert "二、这件事为什么重要" in html
    assert "三、它会影响哪些人" in html
    assert "四、普通人能看到什么机会" in html
    assert "五、现在可以做什么" in html
    assert "font-weight:bold" in html
    assert "[!important]" not in html
    assert "你好，我是<strong" in html
    assert "<br/>今天想重点解读一件 AI 变化" in html


def test_article_image_generation_extracts_prompt_and_writes_assets(tmp_path):
    article = generate_interpretation([
        {"title": "教育科技门槛一夜归零：AI助力单人开发3D教学应用", "summary": "AI工具降低教育应用开发门槛。"}
    ], date="2026-05-09", issue_no=3)

    assets = generate_article_images(article, output_dir=tmp_path)

    assert "教育科技门槛一夜归零" in assets["image_prompt"]
    assert "fresh-card" in assets["image_prompt"]
    assert assets["image_provider"] == "local-svg-placeholder"
    assert assets["cover_path"].endswith("-cover.svg")
    assert assets["content_image_path"].endswith("-inline.svg")
    cover_svg = (tmp_path / assets["cover_path"].split("/")[-1]).read_text(encoding="utf-8")
    inline_svg = (tmp_path / assets["content_image_path"].split("/")[-1]).read_text(encoding="utf-8")
    assert 'width="2048" height="1152"' in cover_svg
    assert 'viewBox="0 0 2048 1152"' in cover_svg
    assert 'width="2048" height="1152"' in inline_svg


def test_briefing_image_prompt_uses_bytedance_green_style():
    article = generate_briefing([
        {"title": "OpenAI 新工具降低内容创作门槛", "summary": "帮助内容创作者提升效率"}
    ], date="2026-05-09", issue_no=2)
    prompt = build_image_prompt(article)

    assert "OpenAI 新工具降低内容创作门槛" in prompt
    assert "bytedance-green" in prompt
    assert "公众号主图" in prompt


def test_generate_interpretation_outputs_required_sections():
    news = [{"title": "AI搜索升级", "url": "https://x", "summary": "AI搜索改变信息入口", "tags": ["AI搜索"]}]
    article = generate_interpretation(news, date="2026-05-09", issue_no=1)
    assert article["content_type"] == "interpretation"
    assert article["title"].startswith("AI解读001｜")
    assert "普通人能看到什么机会" in article["content_markdown"]
    assert "超级发一句话" in article["content_markdown"]


def test_markdown_to_wechat_html_is_mobile_friendly():
    html = markdown_to_wechat_html("# 标题\n\n你好\n\n## 一、新闻\n\n**发生了什么：**\n\n内容")
    assert html.startswith('<section data-theme="fresh-card"')
    assert "font-size:15px" in html
    assert "<h2" in html
    assert '<strong style="font-weight:bold; color:#4a8058;">发生了什么：</strong>' in html
