from app.config import Settings
from app.main import publish_draft_if_confirmed, main
from app.wechat.accounts import WeChatAccount


def test_publish_draft_requires_explicit_confirmation(monkeypatch):
    settings = Settings(auto_publish=True)

    class FakePublishManager:
        def __init__(self, access_token="", auto_publish=False):
            raise AssertionError("publish manager should not be constructed without confirmation")

    monkeypatch.setattr("app.main.PublishManager", FakePublishManager)

    result = publish_draft_if_confirmed(settings, "draft1", publish_confirm=False)

    assert result is None


def test_publish_draft_uses_selected_account_and_returns_publish_id(monkeypatch):
    settings = Settings(
        auto_publish=True,
        wechat_accounts=(WeChatAccount(name="hao2", appid="appid2", appsecret="secret2"),),
    )
    token_calls = []
    publish_calls = []

    class FakeTokenManager:
        def __init__(self, appid, appsecret, token_store="data/token_store.json"):
            token_calls.append((appid, appsecret, str(token_store)))

        def get_access_token(self):
            return "token2"

    class FakePublishManager:
        def __init__(self, access_token="", auto_publish=False):
            self.access_token = access_token
            self.auto_publish = auto_publish

        def publish_draft(self, draft_id):
            publish_calls.append((self.access_token, self.auto_publish, draft_id))
            return "publish2"

    monkeypatch.setattr("app.main.TokenManager", FakeTokenManager)
    monkeypatch.setattr("app.main.PublishManager", FakePublishManager)

    publish_id = publish_draft_if_confirmed(settings, "draft2", publish_confirm=True, wechat_account="hao2")

    assert publish_id == "publish2"
    assert token_calls == [("appid2", "secret2", "data/token_store_hao2.json")]
    assert publish_calls == [("token2", True, "draft2")]


def test_generate_briefing_accepts_publish_confirm_argument(tmp_path, monkeypatch):
    db_path = tmp_path / "superfa.db"
    captured = {}

    def fake_generate_briefing_command(settings, target_date, create_draft, item_limit=10, wechat_account="default", publish_confirm=False):
        captured["publish_confirm"] = publish_confirm
        captured["create_draft"] = create_draft
        captured["wechat_account"] = wechat_account
        return {"status": "success", "date": target_date, "briefing": {"publish_id": "publish1"}}

    monkeypatch.setattr("app.main.generate_briefing_command", fake_generate_briefing_command)

    exit_code = main([
        "generate-briefing",
        "--date", "2026-05-09",
        "--database", str(db_path),
        "--wechat-account", "hao1",
        "--publish-confirm",
    ])

    assert exit_code == 0
    assert captured == {
        "publish_confirm": True,
        "create_draft": True,
        "wechat_account": "hao1",
    }
