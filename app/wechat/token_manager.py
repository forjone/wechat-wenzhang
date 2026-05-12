from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


class TokenManager:
    def __init__(self, appid: str, appsecret: str, token_store: str | Path = "data/token_store.json"):
        self.appid = appid
        self.appsecret = appsecret
        self.token_store = Path(token_store)

    def get_access_token(self, force_refresh: bool = False) -> str:
        if not force_refresh:
            cached = self._read_cached()
            if cached:
                return cached
        if not self.appid or not self.appsecret:
            raise ValueError("WECHAT_APPID and WECHAT_APPSECRET are required to get access_token")
        params = urllib.parse.urlencode({"grant_type": "client_credential", "appid": self.appid, "secret": self.appsecret})
        url = f"https://api.weixin.qq.com/cgi-bin/token?{params}"
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if "access_token" not in payload:
            raise RuntimeError(f"WECHAT_TOKEN_FAILED: {payload}")
        expires_at = int(time.time()) + int(payload.get("expires_in", 7200)) - 300
        self.token_store.parent.mkdir(parents=True, exist_ok=True)
        self.token_store.write_text(json.dumps({"access_token": payload["access_token"], "expires_at": expires_at}), encoding="utf-8")
        return payload["access_token"]

    def _read_cached(self) -> str | None:
        if not self.token_store.exists():
            return None
        try:
            data = json.loads(self.token_store.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, ValueError):
            return None
        if data.get("access_token") and int(data.get("expires_at", 0)) > int(time.time()):
            return data["access_token"]
        return None
