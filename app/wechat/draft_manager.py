from __future__ import annotations

import hashlib
import json
import urllib.request


class DraftManager:
    def __init__(self, access_token: str = ""):
        self.access_token = access_token

    def create_draft(self, article: dict) -> str:
        required = ["title", "content_html"]
        missing = [key for key in required if not article.get(key)]
        if missing:
            raise ValueError(f"Missing required article fields: {', '.join(missing)}")
        if not self.access_token:
            digest = hashlib.sha1((article.get("title", "") + article.get("content_html", "")).encode("utf-8")).hexdigest()[:16]
            return f"local_draft_{digest}"
        payload = {
            "articles": [{
                "title": article["title"],
                "author": article.get("author", "超级发"),
                "digest": article.get("digest", "")[:120],
                "content": article["content_html"],
                "thumb_media_id": article.get("thumb_media_id", ""),
                "content_source_url": article.get("content_source_url", ""),
                "need_open_comment": article.get("need_open_comment", 1),
                "only_fans_can_comment": article.get("only_fans_can_comment", 0),
            }]
        }
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
        request = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
        if "media_id" not in result:
            raise RuntimeError(f"WECHAT_DRAFT_CREATE_FAILED: {result}")
        return result["media_id"]
