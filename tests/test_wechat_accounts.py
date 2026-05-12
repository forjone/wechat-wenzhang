from app.config import Settings
from app.wechat.accounts import WeChatAccount, select_wechat_account


def test_settings_parses_multiple_wechat_accounts_from_env(monkeypatch):
    monkeypatch.setenv("WECHAT_ACCOUNTS", "hao1:appid1:secret1,hao2:appid2:secret2")
    settings = Settings.from_env()

    assert settings.wechat_accounts == (
        WeChatAccount(name="hao1", appid="appid1", appsecret="secret1"),
        WeChatAccount(name="hao2", appid="appid2", appsecret="secret2"),
    )


def test_select_wechat_account_by_name_from_multi_account_config():
    settings = Settings(
        wechat_accounts=(
            WeChatAccount(name="hao1", appid="appid1", appsecret="secret1"),
            WeChatAccount(name="hao2", appid="appid2", appsecret="secret2"),
        )
    )

    account = select_wechat_account(settings, "hao2")

    assert account.name == "hao2"
    assert account.appid == "appid2"
    assert account.appsecret == "secret2"


def test_select_wechat_account_defaults_to_single_legacy_credentials():
    settings = Settings(wechat_appid="legacy_appid", wechat_appsecret="legacy_secret")

    account = select_wechat_account(settings, "default")

    assert account.name == "default"
    assert account.appid == "legacy_appid"
    assert account.appsecret == "legacy_secret"


def test_select_wechat_account_reports_available_accounts():
    settings = Settings(
        wechat_accounts=(
            WeChatAccount(name="hao1", appid="appid1", appsecret="secret1"),
            WeChatAccount(name="hao2", appid="appid2", appsecret="secret2"),
        )
    )

    try:
        select_wechat_account(settings, "missing")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected ValueError")

    assert "WECHAT_ACCOUNT_NOT_FOUND" in message
    assert "missing" in message
    assert "hao1" in message
    assert "hao2" in message
