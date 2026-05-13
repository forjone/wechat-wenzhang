from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.wechat.accounts import WeChatAccount, parse_wechat_accounts


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(frozen=True)
class Settings:
    wechat_appid: str = ""
    wechat_appsecret: str = ""
    wechat_accounts: tuple[WeChatAccount, ...] = ()
    wechat_proxy_url: str = ""
    wechat_proxy_api_key: str = ""
    wechat_proxy_timeout: int = 30
    author_name: str = "超级发"
    auto_publish: bool = False
    database_url: str = "sqlite:///data/superfa.db"
    article_output_dir: str = "outputs/articles"
    image_output_dir: str = "outputs/images"
    aihot_skill_url: str = "https://aihot.virxact.com"
    aihot_skill_timeout: int = 30
    aihot_skill_max_items: int = 20
    aihot_skill_api_key: str = ""
    aihot_user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    allow_fallback: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            wechat_appid=os.getenv("WECHAT_APPID", ""),
            wechat_appsecret=os.getenv("WECHAT_APPSECRET", ""),
            wechat_accounts=parse_wechat_accounts(os.getenv("WECHAT_ACCOUNTS", "")),
            wechat_proxy_url=os.getenv("WECHAT_PROXY_URL", ""),
            wechat_proxy_api_key=os.getenv("WECHAT_PROXY_API_KEY", ""),
            wechat_proxy_timeout=int(os.getenv("WECHAT_PROXY_TIMEOUT", "30")),
            author_name=os.getenv("AUTHOR_NAME", "超级发"),
            auto_publish=os.getenv("AUTO_PUBLISH", "false").lower() == "true",
            database_url=os.getenv("DATABASE_URL", "sqlite:///data/superfa.db"),
            article_output_dir=os.getenv("ARTICLE_OUTPUT_DIR", "outputs/articles"),
            image_output_dir=os.getenv("IMAGE_OUTPUT_DIR", "outputs/images"),
            aihot_skill_url=os.getenv("AIHOT_SKILL_URL", "https://aihot.virxact.com"),
            aihot_skill_timeout=int(os.getenv("AIHOT_SKILL_TIMEOUT", "30")),
            aihot_skill_max_items=int(os.getenv("AIHOT_SKILL_MAX_ITEMS", "20")),
            aihot_skill_api_key=os.getenv("AIHOT_SKILL_API_KEY", ""),
            aihot_user_agent=os.getenv("AIHOT_USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
            allow_fallback=os.getenv("STRICT_SOURCE", "false").lower() != "true",
        )

    @property
    def database_path(self) -> Path:
        if not self.database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// DATABASE_URL is supported in MVP")
        return Path(self.database_url.removeprefix("sqlite:///"))
