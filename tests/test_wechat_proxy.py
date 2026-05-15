from app.config import Settings
from app.main import create_draft_if_requested, publish_draft_if_confirmed
from app.wechat.proxy_client import WeChatProxyClient
import json


def test_wechat_proxy_client_posts_draft_with_account_and_auth(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"media_id":"proxy_draft_123"}'

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["body"] = request.data.decode("utf-8")
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = WeChatProxyClient("https://tokyo.example.com/", api_key="secret", timeout=12)
    draft_id = client.create_draft({"title": "测试", "content_html": "<p>内容</p>"}, account="hao1")

    assert draft_id == "proxy_draft_123"
    assert captured["url"] == "https://tokyo.example.com/wechat/draft/add"
    assert '"account": "hao1"' in captured["body"]
    assert '"title": "测试"' in captured["body"]
    assert captured["headers"]["Authorization"] == "Bearer secret"
    assert captured["timeout"] == 12


def test_wechat_proxy_client_posts_generated_thumb_draft(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"draft_id":"generated_thumb_draft_123"}'

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    article = {
        "title": "AI Agent 自动化办公指南",
        "author": "超级发",
        "digest": "一篇关于 AI Agent 工作流的文章",
        "content_html": "<p>正文 HTML 内容</p>",
        "thumb_media_id": "legacy_thumb_should_not_be_sent",
        "content_source_url": "",
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    client = WeChatProxyClient("https://tokyo.example.com/", api_key="secret", timeout=12)
    draft_id = client.create_draft_with_generated_thumb(article, account="hao1", image_size="2048x1152", image_style="text")

    assert draft_id == "generated_thumb_draft_123"
    assert captured["url"] == "https://tokyo.example.com/wechat/draft/create-with-generated-thumb"
    assert captured["payload"] == {
        "account": "hao1",
        "article": {
            "title": "AI Agent 自动化办公指南",
            "author": "超级发",
            "digest": "一篇关于 AI Agent 工作流的文章",
            "content_html": "<p>正文 HTML 内容</p>",
            "content_source_url": "",
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        },
        "image_size": "2048x1152",
        "image_style": "text",
    }
    assert captured["headers"]["Authorization"] == "Bearer secret"
    assert captured["timeout"] == 12


def test_create_draft_uses_generated_thumb_proxy_endpoint_when_image_prompt_exists(monkeypatch):
    settings = Settings(wechat_proxy_url="https://tokyo.example.com", wechat_proxy_api_key="secret")
    calls = []

    class FakeProxy:
        def __init__(self, base_url, api_key="", timeout=30):
            calls.append((base_url, api_key, timeout))

        def create_draft_with_generated_thumb(self, article, account="default", image_size="2048x1152", image_style="text"):
            calls.append(("generated", account, image_size, image_style, article))
            return "generated_thumb_draft_456"

        def create_draft(self, article, account="default"):
            raise AssertionError("generated-thumb articles should not use legacy draft endpoint")

    monkeypatch.setattr("app.main.WeChatProxyClient", FakeProxy)

    draft_id = create_draft_if_requested(
        settings,
        {"title": "标题", "digest": "摘要", "content_html": "<p>正文</p>", "image_prompt": "绿色科技插画"},
        create_draft=True,
        wechat_account="hao1",
    )

    assert draft_id == "generated_thumb_draft_456"
    assert calls[0] == ("https://tokyo.example.com", "secret", 30)
    _, account, image_size, image_style, article = calls[1]
    assert account == "hao1"
    assert image_size == "2048x1152"
    assert image_style == "text"
    assert article["author"] == "超级发"
    assert article["content_source_url"] == ""
    assert "thumb_media_id" not in article


def test_create_draft_keeps_legacy_proxy_endpoint_without_image_prompt(monkeypatch):
    settings = Settings(wechat_proxy_url="https://tokyo.example.com", wechat_proxy_api_key="secret")
    calls = []

    class FakeProxy:
        def __init__(self, base_url, api_key="", timeout=30):
            calls.append((base_url, api_key, timeout))

        def create_draft_with_generated_thumb(self, article, account="default", image_size="2048x1152", image_style="text"):
            raise AssertionError("legacy articles without generated-image prompt should use /wechat/draft/add")

        def create_draft(self, article, account="default"):
            calls.append(("legacy", account, article))
            return "proxy_draft_legacy"

    monkeypatch.setattr("app.main.WeChatProxyClient", FakeProxy)

    draft_id = create_draft_if_requested(
        settings,
        {"title": "标题", "digest": "摘要", "content_html": "<p>正文</p>"},
        create_draft=True,
        wechat_account="hao1",
    )

    assert draft_id == "proxy_draft_legacy"
    assert calls[1][0] == "legacy"


def test_create_draft_uses_proxy_without_local_wechat_credentials(monkeypatch):
    settings = Settings(wechat_proxy_url="https://tokyo.example.com", wechat_proxy_api_key="secret")
    calls = []

    class FakeProxy:
        def __init__(self, base_url, api_key="", timeout=30):
            calls.append((base_url, api_key, timeout))

        def create_draft(self, article, account="default"):
            calls.append((account, article["title"], article["author"]))
            return "proxy_draft_456"

    class ForbiddenTokenManager:
        def __init__(self, *args, **kwargs):
            raise AssertionError("proxy mode should not fetch local WeChat token")

    monkeypatch.setattr("app.main.WeChatProxyClient", FakeProxy)
    monkeypatch.setattr("app.main.TokenManager", ForbiddenTokenManager)

    draft_id = create_draft_if_requested(
        settings,
        {"title": "标题", "digest": "摘要", "content_html": "<p>正文</p>"},
        create_draft=True,
        wechat_account="hao1",
    )

    assert draft_id == "proxy_draft_456"
    assert calls == [("https://tokyo.example.com", "secret", 30), ("hao1", "标题", "超级发")]


def test_create_draft_retries_transient_proxy_failures(monkeypatch):
    settings = Settings(wechat_proxy_url="https://tokyo.example.com", wechat_proxy_api_key="secret")
    calls = []

    class FakeProxy:
        def __init__(self, base_url, api_key="", timeout=30):
            pass

        def create_draft_with_generated_thumb(self, article, account="default", image_size="2048x1152", image_style="text"):
            calls.append(account)
            if len(calls) < 3:
                raise RuntimeError("HTTP Error 504: Gateway Time-out")
            return "draft_after_retry"

        def create_draft(self, article, account="default"):
            raise AssertionError("generated-thumb articles should use generated endpoint")

    monkeypatch.setattr("app.main.WeChatProxyClient", FakeProxy)
    monkeypatch.setattr("app.main.time.sleep", lambda seconds: None)

    draft_id = create_draft_if_requested(
        settings,
        {"title": "标题", "digest": "摘要", "content_html": "<p>正文</p>", "image_prompt": "绿色科技插画"},
        True,
        "mflai",
    )

    assert draft_id == "draft_after_retry"
    assert calls == ["mflai", "mflai", "mflai"]


def test_create_draft_falls_back_to_legacy_proxy_when_generated_thumb_proxy_returns_502(monkeypatch):
    settings = Settings(wechat_proxy_url="https://tokyo.example.com", wechat_proxy_api_key="secret")
    calls = []

    class FakeProxy:
        def __init__(self, base_url, api_key="", timeout=30):
            pass

        def create_draft_with_generated_thumb(self, article, account="default", image_size="2048x1152", image_style="text"):
            calls.append(("generated", account, image_size, image_style))
            raise RuntimeError("HTTP Error 502: Bad Gateway")

        def create_draft(self, article, account="default"):
            calls.append(("legacy", account, article.get("thumb_media_id", ""), "image_prompt" in article))
            return "legacy_draft_after_502"

    monkeypatch.setattr("app.main.WeChatProxyClient", FakeProxy)
    monkeypatch.setattr("app.main.time.sleep", lambda seconds: None)

    draft_id = create_draft_if_requested(
        settings,
        {
            "title": "标题",
            "digest": "摘要",
            "content_html": "<p>正文</p>",
            "image_prompt": "绿色科技插画",
            "thumb_media_id": "legacy_thumb",
        },
        True,
        "cjfai",
    )

    assert draft_id == "legacy_draft_after_502"
    assert calls[:3] == [
        ("generated", "cjfai", "2048x1152", "text"),
        ("generated", "cjfai", "2048x1152", "text"),
        ("generated", "cjfai", "2048x1152", "text"),
    ]
    assert calls[3] == ("legacy", "cjfai", "legacy_thumb", False)


def test_publish_uses_proxy_after_auto_publish_guard(monkeypatch):
    settings = Settings(wechat_proxy_url="https://tokyo.example.com", auto_publish=True)
    calls = []

    class FakeProxy:
        def __init__(self, base_url, api_key="", timeout=30):
            calls.append((base_url, api_key, timeout))

        def publish_draft(self, draft_id, account="default"):
            calls.append((account, draft_id))
            return "proxy_publish_789"

    monkeypatch.setattr("app.main.WeChatProxyClient", FakeProxy)

    publish_id = publish_draft_if_confirmed(settings, "proxy_draft_456", publish_confirm=True, wechat_account="hao2")

    assert publish_id == "proxy_publish_789"
    assert calls == [("https://tokyo.example.com", "", 30), ("hao2", "proxy_draft_456")]


def test_publish_proxy_still_requires_auto_publish_enabled(monkeypatch):
    settings = Settings(wechat_proxy_url="https://tokyo.example.com", auto_publish=False)

    class ForbiddenProxy:
        def __init__(self, *args, **kwargs):
            raise AssertionError("proxy publish should not run while AUTO_PUBLISH is false")

    monkeypatch.setattr("app.main.WeChatProxyClient", ForbiddenProxy)

    try:
        publish_draft_if_confirmed(settings, "draft1", publish_confirm=True, wechat_account="hao1")
    except RuntimeError as exc:
        assert "AUTO_PUBLISH_DISABLED" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
