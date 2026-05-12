from app.agents.news_scorer import score_for_briefing
from app.config import Settings
from app.main import generate_daily_command, prepare_news, select_briefing_items


def _news_items(count: int):
    return [
        {
            "title": f"新闻{idx}",
            "url": f"https://example.com/{idx}",
            "source": "AIHot",
            "published_at": "2026-05-09T00:00:00Z",
            "summary": f"这是第{idx}条原始摘要。",
            "category": "产品发布/更新",
            "tags": ["AI工具"],
            "source_mode": "aihot_skill",
            "source_error": "",
            "source_provider": "aihot_skill",
        }
        for idx in range(1, count + 1)
    ]


def test_select_briefing_items_defaults_to_top_ten_by_importance_score():
    items = _news_items(12)
    items[10]["title"] = "OpenAI Agent AI视频 模型 创业 重要突破"
    items[10]["summary"] = "影响内容创作者、普通人和职场效率，具备自动化机会。"

    selected = select_briefing_items(items)

    assert len(selected) == 10
    assert selected[0]["title"] == "OpenAI Agent AI视频 模型 创业 重要突破"
    scores = [score_for_briefing(item) for item in selected]
    assert scores == sorted(scores, reverse=True)


def test_select_briefing_items_can_show_all_items_sorted_by_importance():
    items = _news_items(12)
    items[-1]["title"] = "Claude Agent AI工具 影响普通人创业"
    items[-1]["summary"] = "覆盖范围大，能提升内容创作者效率。"

    selected = select_briefing_items(items, limit=0)

    assert len(selected) == 12
    assert selected[0]["title"] == "Claude Agent AI工具 影响普通人创业"


def test_generate_daily_uses_ten_briefing_items_and_interprets_top_item(tmp_path, monkeypatch):
    news = _news_items(12)
    news[9]["title"] = "OpenAI Agent AI工具 改变全球办公和创业"
    news[9]["summary"] = "影响范围覆盖普通人、职场和内容创作者，价值在于效率、自动化和创业机会。"
    news[9]["tags"] = ["OpenAI", "Agent", "AI工具", "创业", "自动化"]

    def fake_prepare_news(settings, target_date):
        return [dict(item) for item in news]

    monkeypatch.setattr("app.main.prepare_news", fake_prepare_news)
    monkeypatch.setattr("app.main.save_article_outputs", lambda article: {"markdown": tmp_path / f"{article['content_type']}.md", "html": tmp_path / f"{article['content_type']}.html", "metadata": tmp_path / f"{article['content_type']}.json"})

    db_path = tmp_path / "superfa.db"
    settings = Settings(database_url=f"sqlite:///{db_path}")

    result = generate_daily_command(settings, "2026-05-09", create_draft=False, item_limit=10)

    assert result["status"] == "success"
    assert result["date"] == "2026-05-10"
    from app.database import get_article

    briefing = get_article(db_path, result["briefing"]["article_id"])
    interpretation = get_article(db_path, result["interpretation"]["article_id"])
    briefing_metadata = result["briefing"]["metadata"]
    interpretation_metadata = result["interpretation"]["metadata"]
    assert len(briefing_metadata["news_items"]) == 10
    assert briefing_metadata["news_items"][0]["title"] == "OpenAI Agent AI工具 改变全球办公和创业"
    assert interpretation_metadata["source_news"][0]["title"] == briefing_metadata["news_items"][0]["title"]
    assert briefing_metadata["cover_path"].endswith("-cover.svg")
    assert interpretation_metadata["cover_path"].endswith("-cover.svg")
    assert "image_prompt" in briefing_metadata
    assert "image_prompt" in interpretation_metadata
    assert "bytedance-green" in briefing_metadata["image_prompt"]
    assert "fresh-card" in interpretation_metadata["image_prompt"]
    assert "条目：10 条" in briefing["content_markdown"]
    assert interpretation_metadata["source_news"][0]["title"] in interpretation["content_markdown"]


def test_prepare_news_respects_max_items_from_settings():
    settings = Settings(aihot_skill_max_items=7, allow_fallback=True, aihot_skill_url="http://127.0.0.1:1/unavailable", aihot_skill_timeout=1)

    news = prepare_news(settings, "2026-05-09")

    assert len(news) <= 7
