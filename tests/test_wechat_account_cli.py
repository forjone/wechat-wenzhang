import json

from app.main import main


def test_generate_briefing_accepts_wechat_account_argument(tmp_path, monkeypatch):
    db_path = tmp_path / "superfa.db"
    monkeypatch.setenv("WECHAT_ACCOUNTS", "hao1:appid1:secret1,hao2:appid2:secret2")

    captured = {}

    def fake_generate_briefing_command(settings, target_date, create_draft, item_limit=10, wechat_account="default", publish_confirm=False):
        captured["target_date"] = target_date
        captured["create_draft"] = create_draft
        captured["item_limit"] = item_limit
        captured["wechat_account"] = wechat_account
        captured["publish_confirm"] = publish_confirm
        captured["database_url"] = settings.database_url
        return {"status": "success", "date": target_date, "briefing": {"draft_id": "draft1"}}

    monkeypatch.setattr("app.main.generate_briefing_command", fake_generate_briefing_command)

    exit_code = main([
        "generate-briefing",
        "--date", "2026-05-09",
        "--create-draft",
        "--items", "10",
        "--database", str(db_path),
        "--wechat-account", "hao2",
    ])

    assert exit_code == 0
    assert captured["wechat_account"] == "hao2"
    assert captured["create_draft"] is True
    assert captured["item_limit"] == 10


def test_create_draft_uses_selected_wechat_account_for_token(tmp_path, monkeypatch):
    from app.config import Settings
    from app.main import create_draft_if_requested
    from app.wechat.accounts import WeChatAccount

    settings = Settings(
        wechat_accounts=(
            WeChatAccount(name="hao1", appid="appid1", appsecret="secret1"),
            WeChatAccount(name="hao2", appid="appid2", appsecret="secret2"),
        )
    )
    article = {"title": "标题", "digest": "摘要", "content_html": "<p>正文</p>"}
    token_calls = []
    draft_payloads = []

    class FakeTokenManager:
        def __init__(self, appid, appsecret, token_store="data/token_store.json"):
            token_calls.append((appid, appsecret, str(token_store)))

        def get_access_token(self):
            return "token2"

    class FakeDraftManager:
        def __init__(self, access_token=""):
            self.access_token = access_token

        def create_draft(self, payload):
            draft_payloads.append((self.access_token, payload))
            return "draft2"

    monkeypatch.setattr("app.main.TokenManager", FakeTokenManager)
    monkeypatch.setattr("app.main.DraftManager", FakeDraftManager)

    draft_id = create_draft_if_requested(settings, article, True, "hao2")

    assert draft_id == "draft2"
    assert token_calls == [("appid2", "secret2", "data/token_store_hao2.json")]
    assert draft_payloads[0][0] == "token2"
    assert draft_payloads[0][1]["title"] == "标题"
