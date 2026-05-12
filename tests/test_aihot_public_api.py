from app.sources.aihot_skill import AIHotSkillClient


def test_aihot_public_items_url_defaults_to_selected_with_user_agent():
    client = AIHotSkillClient(base_url="https://aihot.virxact.com", user_agent="Test UA")
    request = client.build_items_request(date="2026-05-09", max_items=30)
    assert request.full_url.startswith("https://aihot.virxact.com/api/public/items?")
    assert "mode=selected" in request.full_url
    assert "take=30" in request.full_url
    assert "since=" in request.full_url
    assert request.headers["User-agent"] == "Test UA"


def test_aihot_normalizes_public_items_schema():
    client = AIHotSkillClient()
    raw = {
        "id": "cm9abc456def789ghi012jkl3",
        "title": "中文标题",
        "title_en": "English title",
        "url": "https://example.com/item",
        "source": "OpenAI Blog",
        "publishedAt": "2026-05-07T15:30:00.000Z",
        "summary": "中文摘要",
        "category": "ai-models",
    }
    item = client.normalize_news_item(raw)
    assert item["external_id"] == "cm9abc456def789ghi012jkl3"
    assert item["title"] == "中文标题"
    assert item["url"] == "https://example.com/item"
    assert item["source"] == "OpenAI Blog"
    assert item["published_at"] == "2026-05-07T15:30:00.000Z"
    assert item["summary"] == "中文摘要"
    assert item["category"] == "ai-models"
    assert item["tags"] == ["模型发布/更新"]


def test_aihot_daily_schema_sections_are_extractable():
    client = AIHotSkillClient()
    payload = {
        "date": "2026-05-07",
        "sections": [
            {
                "label": "模型发布/更新",
                "items": [
                    {
                        "title": "模型新闻",
                        "summary": "摘要",
                        "sourceUrl": "https://example.com/model",
                        "sourceName": "AIHot",
                    }
                ],
            }
        ],
    }
    items = client._extract_items(payload)
    assert items == [
        {
            "title": "模型新闻",
            "summary": "摘要",
            "sourceUrl": "https://example.com/model",
            "sourceName": "AIHot",
            "category": "模型发布/更新",
        }
    ]
