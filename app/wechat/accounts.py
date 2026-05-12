from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeChatAccount:
    name: str
    appid: str
    appsecret: str


def parse_wechat_accounts(value: str) -> tuple[WeChatAccount, ...]:
    accounts: list[WeChatAccount] = []
    for raw_entry in value.split(","):
        entry = raw_entry.strip()
        if not entry:
            continue
        parts = entry.split(":", 2)
        if len(parts) != 3 or not all(part.strip() for part in parts):
            raise ValueError("WECHAT_ACCOUNTS entries must use name:appid:appsecret")
        name, appid, appsecret = (part.strip() for part in parts)
        accounts.append(WeChatAccount(name=name, appid=appid, appsecret=appsecret))
    return tuple(accounts)


def select_wechat_account(settings, account_name: str = "default") -> WeChatAccount:
    requested = account_name or "default"
    accounts = getattr(settings, "wechat_accounts", ())
    if accounts:
        for account in accounts:
            if account.name == requested:
                return account
        available = ", ".join(account.name for account in accounts)
        raise ValueError(f"WECHAT_ACCOUNT_NOT_FOUND: {requested}. Available accounts: {available}")
    if requested != "default":
        raise ValueError(f"WECHAT_ACCOUNT_NOT_FOUND: {requested}. Available accounts: default")
    return WeChatAccount(
        name="default",
        appid=getattr(settings, "wechat_appid", ""),
        appsecret=getattr(settings, "wechat_appsecret", ""),
    )
