from __future__ import annotations

import re
import urllib.request
from html.parser import HTMLParser
from typing import Any

DEFAULT_ORIGINAL_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_MAX_CONTENT_CHARS = 12000
_MAX_EXCERPT_CHARS = 1800


class _ArticleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.author = ""
        self._in_title = False
        self._skip_depth = 0
        self._article_depth = 0
        self._capture_article = False
        self._fallback_parts: list[str] = []
        self._article_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        tag = tag.lower()
        attrs_dict = {key.lower(): (value or "") for key, value in attrs}
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header", "aside", "form"}:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        if tag == "meta" and not self.author:
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            if name in {"author", "article:author", "og:article:author"}:
                self.author = attrs_dict.get("content", "").strip()
        if tag == "article":
            self._capture_article = True
            self._article_depth = 1
            return
        if self._capture_article:
            self._article_depth += 1
        if tag in {"p", "h1", "h2", "h3", "li", "blockquote"}:
            self._append("\n")

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if self._capture_article:
            self._article_depth -= 1
            if self._article_depth <= 0:
                self._capture_article = False
        if tag in {"p", "h1", "h2", "h3", "li", "blockquote", "div", "section"}:
            self._append("\n")

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
            return
        self._append(text)

    def _append(self, text: str):
        if self._capture_article:
            self._article_parts.append(text)
        else:
            self._fallback_parts.append(text)

    @property
    def title(self) -> str:
        title = " ".join(self.title_parts).strip()
        title = re.split(r"\s+[-_|]\s+", title)[0].strip()
        return title

    @property
    def content(self) -> str:
        article_text = _normalize_text(" ".join(self._article_parts))
        if article_text:
            return article_text
        return _normalize_text(" ".join(self._fallback_parts))


def _normalize_text(text: str) -> str:
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()


def _decode_response(response: Any) -> str:
    raw = response.read()
    charset = "utf-8"
    try:
        content_type = response.headers.get_content_type() if hasattr(response, "headers") else ""
        if content_type and "html" not in content_type and "text" not in content_type:
            return ""
        if hasattr(response, "headers"):
            charset = response.headers.get_content_charset() or charset
    except Exception:
        pass
    if hasattr(response, "getheaders"):
        for key, value in response.getheaders():
            if key.lower() == "content-type":
                match = re.search(r"charset=([^;]+)", value, flags=re.I)
                if match:
                    charset = match.group(1).strip()
    try:
        return raw.decode(charset, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def fetch_original_article(url: str, *, timeout: int = 10, user_agent: str = DEFAULT_ORIGINAL_USER_AGENT) -> dict[str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        html = _decode_response(response)
    parser = _ArticleHTMLParser()
    parser.feed(html)
    content = parser.content[:_MAX_CONTENT_CHARS]
    return {
        "original_url": url,
        "original_title": parser.title,
        "original_author": parser.author,
        "original_content": content,
        "original_excerpt": content[:_MAX_EXCERPT_CHARS],
        "original_fetch_status": "success" if content else "empty",
        "original_fetch_error": "",
    }


def enrich_news_item_with_original(item: dict[str, Any], *, timeout: int = 10) -> dict[str, Any]:
    enriched = dict(item)
    url = str(item.get("url") or "").strip()
    if not url:
        enriched.update(
            {
                "original_url": "",
                "original_title": "",
                "original_author": "",
                "original_content": "",
                "original_excerpt": "",
                "original_fetch_status": "skipped",
                "original_fetch_error": "",
            }
        )
        return enriched
    try:
        enriched.update(fetch_original_article(url, timeout=timeout))
    except Exception as exc:
        enriched.update(
            {
                "original_url": url,
                "original_title": "",
                "original_author": "",
                "original_content": "",
                "original_excerpt": "",
                "original_fetch_status": "failed",
                "original_fetch_error": exc.__class__.__name__,
            }
        )
    return enriched
