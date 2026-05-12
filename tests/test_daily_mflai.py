from app.config import Settings
from app.main import generate_daily_command


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


def test_daily_keeps_cjfai_briefing_and_numbered_interpretation_plus_mflai_extra_breakdown(tmp_path, monkeypatch):
    news = _news_items(12)
    news[0]["title"] = "第一主题 AI办公大模型升级"
    news[0]["summary"] = "第一主题影响职场效率。"
    news[0]["tags"] = ["AI工具", "办公"]
    news[1]["title"] = "第二主题 AI教育产品爆发"
    news[1]["summary"] = "第二主题影响普通人学习和教育创业。"
    news[1]["tags"] = ["AI教育", "创业", "普通人"]

    def fake_prepare_news(settings, target_date):
        return [dict(item) for item in news]

    draft_calls = []
    enriched_titles = []

    def fake_enrich(item, settings):
        enriched_titles.append(item["title"])
        enriched = dict(item)
        enriched["original_fetch_status"] = "success"
        enriched["original_title"] = f"原文：{item['title']}"
        enriched["original_content"] = f"{item['title']} 的原文全文。这里包含比摘要更多的业务背景、产品细节和影响分析。"
        enriched["original_excerpt"] = enriched["original_content"]
        return enriched

    created_articles = []

    def fake_create_draft(settings, article, create_draft, wechat_account="default", **kwargs):
        if create_draft:
            source_title = article["source_news"][0]["title"] if article["content_type"] == "interpretation" else None
            draft_calls.append((wechat_account, article["title"], source_title))
            created_articles.append(article)
            return f"draft_{wechat_account}_{len(draft_calls)}"
        return None

    monkeypatch.setattr("app.main.prepare_news", fake_prepare_news)
    monkeypatch.setattr("app.main.enrich_interpretation_item", fake_enrich)
    monkeypatch.setattr("app.main.save_article_outputs", lambda article: {"markdown": tmp_path / f"{article['title']}.md", "html": tmp_path / f"{article['title']}.html", "metadata": tmp_path / f"{article['title']}.json"})
    monkeypatch.setattr("app.main.create_draft_if_requested", fake_create_draft)

    settings = Settings(database_url=f"sqlite:///{tmp_path / 'superfa.db'}")
    result = generate_daily_command(settings, "2026-05-09", create_draft=True, item_limit=10, wechat_account="cjfai")

    assert result["status"] == "success"
    assert result["briefing"]["draft_account"] == "cjfai"
    assert result["interpretation"]["draft_account"] == "cjfai"
    assert result["interpretation"]["title"].startswith("AI解读001｜第一主题 AI办公大模型升级")
    assert result["interpretation"]["metadata"]["source_news"][0]["title"] == "第一主题 AI办公大模型升级"
    assert result["interpretation"]["metadata"]["source_news"][0]["original_fetch_status"] == "success"
    assert "原文全文" in result["interpretation"]["metadata"]["source_news"][0]["original_content"]

    assert result["mflai_interpretation"]["draft_account"] == "mflai"
    assert result["mflai_interpretation"]["title"].startswith("第二主题 AI教育产品爆发")
    assert not result["mflai_interpretation"]["title"].startswith("AI解读")
    assert result["mflai_interpretation"]["metadata"]["source_news"][0]["title"] == "第二主题 AI教育产品爆发"
    assert result["mflai_interpretation"]["metadata"]["source_news"][0]["original_fetch_status"] == "success"
    assert "业务背景、产品细节和影响分析" in created_articles[2]["content_markdown"]

    assert enriched_titles == ["第一主题 AI办公大模型升级", "第二主题 AI教育产品爆发"]
    assert draft_calls[0][0] == "cjfai"
    assert draft_calls[1] == ("cjfai", result["interpretation"]["title"], "第一主题 AI办公大模型升级")
    assert draft_calls[2] == ("mflai", result["mflai_interpretation"]["title"], "第二主题 AI教育产品爆发")
