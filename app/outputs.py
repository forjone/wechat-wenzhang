from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def article_slug(article: dict[str, Any]) -> str:
    content_type = str(article.get("content_type", "article"))
    issue_no = int(article.get("issue_no", 0))
    title = str(article.get("title", "untitled")).lower()
    safe_title = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "-", title).strip("-")
    return f"{content_type}-{issue_no:03d}-{safe_title}"[:120]


def save_article_outputs(article: dict[str, Any], output_dir: str | Path = "outputs/articles") -> dict[str, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    slug = article_slug(article)
    markdown_path = directory / f"{slug}.md"
    html_path = directory / f"{slug}.html"
    metadata_path = directory / f"{slug}.json"
    markdown_path.write_text(article.get("content_markdown", ""), encoding="utf-8")
    html_path.write_text(article.get("content_html", ""), encoding="utf-8")
    metadata = {key: value for key, value in article.items() if key not in {"content_markdown", "content_html"}}
    if article.get("image_prompt"):
        metadata["image_prompt"] = article.get("image_prompt")
    if article.get("content_image_path"):
        metadata["content_image_path"] = article.get("content_image_path")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"markdown": markdown_path, "html": html_path, "metadata": metadata_path}
