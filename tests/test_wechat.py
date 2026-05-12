from app.wechat.token_manager import TokenManager
from app.wechat.draft_manager import DraftManager
from app.wechat.publish_manager import PublishManager


def test_token_manager_requires_credentials_for_real_token(tmp_path):
    manager = TokenManager(appid="", appsecret="", token_store=tmp_path / "token.json")
    try:
        manager.get_access_token()
    except ValueError as exc:
        assert "WECHAT_APPID" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_draft_manager_returns_local_draft_without_credentials():
    manager = DraftManager(access_token="")
    draft_id = manager.create_draft({"title": "测试", "content_html": "<p>内容</p>"})
    assert draft_id.startswith("local_draft_")


def test_publish_manager_blocks_when_auto_publish_false():
    manager = PublishManager(auto_publish=False)
    try:
        manager.publish_draft("draft1")
    except PermissionError as exc:
        assert "AUTO_PUBLISH=false" in str(exc)
    else:
        raise AssertionError("expected PermissionError")


def test_publish_manager_returns_local_publish_id_without_access_token():
    manager = PublishManager(access_token="", auto_publish=True)
    publish_id = manager.publish_draft("local_draft_abc")
    assert publish_id.startswith("local_publish_")


def test_publish_manager_calls_wechat_freepublish_submit(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"publish_id":"pub123"}'

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["body"] = request.data.decode("utf-8")
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    manager = PublishManager(access_token="token123", auto_publish=True)
    publish_id = manager.publish_draft("media123")

    assert publish_id == "pub123"
    assert "freepublish/submit" in captured["url"]
    assert "access_token=token123" in captured["url"]
    assert '"media_id": "media123"' in captured["body"]
