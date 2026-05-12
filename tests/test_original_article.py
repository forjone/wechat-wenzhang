from app.sources.original_article import enrich_news_item_with_original


def test_enrich_news_item_with_original_extracts_article_text(monkeypatch):
    html = """
    <html>
      <head>
        <title>原文标题 - Site</title>
        <meta name="author" content="原文作者" />
      </head>
      <body>
        <nav>导航应该被移除</nav>
        <article>
          <h1>原文标题</h1>
          <p>第一段原文内容，包含关键背景。</p>
          <p>第二段原文内容，说明产品能力和影响。</p>
          <script>bad()</script>
        </article>
      </body>
    </html>
    """

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return html.encode("utf-8")

        def getheaders(self):
            return [("Content-Type", "text/html; charset=utf-8")]

    def fake_urlopen(request, timeout=10):
        assert request.full_url == "https://example.com/news"
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    item = {"title": "摘要标题", "url": "https://example.com/news", "summary": "短摘要"}
    enriched = enrich_news_item_with_original(item, timeout=5)

    assert enriched["original_fetch_status"] == "success"
    assert enriched["original_title"] == "原文标题"
    assert enriched["original_author"] == "原文作者"
    assert "第一段原文内容" in enriched["original_content"]
    assert "第二段原文内容" in enriched["original_content"]
    assert "导航应该被移除" not in enriched["original_content"]
    assert "bad()" not in enriched["original_content"]
    assert enriched["original_url"] == "https://example.com/news"


def test_enrich_news_item_with_original_falls_back_without_url():
    item = {"title": "无链接新闻", "summary": "短摘要"}
    enriched = enrich_news_item_with_original(item)

    assert enriched["original_fetch_status"] == "skipped"
    assert enriched["original_content"] == ""
    assert enriched["summary"] == "短摘要"
