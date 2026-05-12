from app.outputs import save_article_outputs, article_slug


def test_article_slug_uses_type_issue_and_safe_title():
    article = {"content_type": "briefing", "issue_no": 12, "title": "AI简报012｜2026年5月9日：今天AI发生了什么？"}
    assert article_slug(article) == "briefing-012-ai简报012-2026年5月9日-今天ai发生了什么"


def test_save_article_outputs_writes_markdown_html_and_metadata(tmp_path):
    article = {
        "content_type": "interpretation",
        "issue_no": 1,
        "title": "AI解读001｜AI搜索",
        "content_markdown": "# MD",
        "content_html": "<section>HTML</section>",
        "cover_prompt": "cover",
    }

    paths = save_article_outputs(article, tmp_path)

    assert paths["markdown"].read_text(encoding="utf-8") == "# MD"
    assert paths["html"].read_text(encoding="utf-8") == "<section>HTML</section>"
    assert '"cover_prompt": "cover"' in paths["metadata"].read_text(encoding="utf-8")
