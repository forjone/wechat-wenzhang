from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from pathlib import Path


class MediaUploader:
    def __init__(self, access_token: str = ""):
        self.access_token = access_token

    def upload_cover_image(self, file_path: str | Path) -> str:
        if not self.access_token:
            digest = hashlib.sha1(str(file_path).encode()).hexdigest()[:16]
            return f"local_media_{digest}"
        raise NotImplementedError("Real permanent media upload needs multipart support; use requests in production.")

    def upload_content_image(self, file_path: str | Path) -> str:
        if not self.access_token:
            return f"local://wechat-image/{Path(file_path).name}"
        raise NotImplementedError("Real content image upload needs multipart support; use requests in production.")

    def replace_html_images(self, html: str) -> str:
        return html
