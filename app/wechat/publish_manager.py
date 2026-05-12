from __future__ import annotations

import hashlib
import json
import urllib.request


class PublishManager:
    def __init__(self, access_token: str = "", auto_publish: bool = False):
        self.access_token = access_token
        self.auto_publish = auto_publish

    def publish_draft(self, draft_id: str) -> str:
        if not self.auto_publish:
            raise PermissionError("AUTO_PUBLISH=false; automatic publishing is disabled in MVP")
        if not draft_id:
            raise ValueError("draft_id is required")
        if not self.access_token:
            digest = hashlib.sha1(draft_id.encode("utf-8")).hexdigest()[:16]
            return f"local_publish_{digest}"
        payload = {"media_id": draft_id}
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={self.access_token}"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
        if "publish_id" not in result:
            raise RuntimeError(f"WECHAT_PUBLISH_FAILED: {result}")
        return result["publish_id"]

    def get_publish_status(self, publish_id: str) -> str:
        return "unknown"
