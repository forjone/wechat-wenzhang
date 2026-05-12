from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path
from typing import Any


_PALETTE = {
    "briefing": {"bg": "#F0FAF4", "fg": "#1F3D2B", "accent": "#74C69D", "muted": "#3F5F4A", "label": "AI简报"},
    "interpretation": {"bg": "#F5F8F5", "fg": "#3D4A3D", "accent": "#6B9B7A", "muted": "#4A8058", "label": "AI解读"},
}


def _clean_text(value: Any, max_chars: int = 36) -> str:
    text = re.sub(r"\s+", " ", str(value or "AI重要信号")).strip()
    return text[:max_chars].strip() or "AI重要信号"


def _wrap_svg_text(text: str, max_chars: int = 14) -> list[str]:
    text = _clean_text(text, 60)
    lines: list[str] = []
    current = ""
    for char in text:
        width = 2 if "\u4e00" <= char <= "\u9fff" else 1
        current_width = sum(2 if "\u4e00" <= c <= "\u9fff" else 1 for c in current)
        if current and current_width + width > max_chars * 2:
            lines.append(current)
            current = char
        else:
            current += char
    if current:
        lines.append(current)
    return lines[:3]


def build_image_prompt(article: dict[str, Any]) -> str:
    content_type = str(article.get("content_type") or "article")
    title = _clean_text(article.get("title"), 60)
    digest = _clean_text(article.get("digest"), 80)
    base = article.get("cover_prompt") or f"微信公众号文章配图，主题是“{title}”。"
    if content_type == "briefing":
        style = "bytedance-green 绿色科技简报风，信息流卡片、趋势箭头、清爽可信，适合作为公众号主图。"
    else:
        style = "fresh-card 清新卡片风，浅绿色背景、白色圆角卡片、柔和阴影，适合作为公众号解读文章主图和正文配图。"
    return f"{base}\n提炼主题：{title}\n摘要重点：{digest}\n视觉要求：{style}\n避免真实品牌 Logo、避免复杂小字、避免过度赛博朋克。"


def generate_article_images(article: dict[str, Any], output_dir: str | Path = "outputs/images") -> dict[str, Any]:
    """Generate deterministic local SVG placeholders for article cover/content images.

    The function records the extracted image prompt and creates local image assets.
    A real image model can later consume image_prompt and overwrite these paths.
    """
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    content_type = str(article.get("content_type") or "article")
    issue_no = int(article.get("issue_no") or 0)
    title = _clean_text(article.get("title"), 60)
    prompt = build_image_prompt(article)
    digest = _clean_text(article.get("digest"), 90)
    slug = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "-", title.lower()).strip("-")[:80] or "article"
    prefix = f"{content_type}-{issue_no:03d}-{slug}"
    palette = _PALETTE.get(content_type, _PALETTE["interpretation"])

    def render_svg(kind: str, width: int, height: int) -> str:
        title_lines = _wrap_svg_text(title, 14 if width < 1000 else 18)
        digest_lines = _wrap_svg_text(digest, 18 if width < 1000 else 26)
        y = 190 if kind == "cover" else 145
        title_spans = []
        for line in title_lines:
            title_spans.append(f'<text x="72" y="{y}" font-size="54" font-weight="700" fill="{palette["fg"]}">{html.escape(line)}</text>')
            y += 70
        dy = y + 28
        digest_spans = []
        for line in digest_lines[:2]:
            digest_spans.append(f'<text x="72" y="{dy}" font-size="28" fill="{palette["muted"]}">{html.escape(line)}</text>')
            dy += 42
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{palette['bg']}"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="{palette['accent']}" flood-opacity="0.16"/></filter>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{palette['accent']}" opacity="0.16"/></pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <rect x="40" y="40" width="{width-80}" height="{height-80}" rx="36" fill="#FFFFFF" filter="url(#shadow)"/>
  <rect x="40" y="40" width="{width-80}" height="{height-80}" rx="36" fill="url(#dots)" opacity="0.7"/>
  <rect x="72" y="82" width="132" height="44" rx="22" fill="{palette['accent']}" opacity="0.92"/>
  <text x="96" y="112" font-size="24" fill="#FFFFFF" font-weight="700">{html.escape(palette['label'])}</text>
  <circle cx="{width-128}" cy="112" r="28" fill="{palette['accent']}" opacity="0.25"/>
  <path d="M{width-176} {height-132} C{width-130} {height-208}, {width-72} {height-182}, {width-42} {height-260}" stroke="{palette['accent']}" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.55"/>
  {''.join(title_spans)}
  {''.join(digest_spans)}
  <text x="72" y="{height-82}" font-size="24" fill="{palette['muted']}" opacity="0.78">超级发 · AI 情报</text>
</svg>
'''

    cover_path = directory / f"{prefix}-cover.svg"
    inline_path = directory / f"{prefix}-inline.svg"
    cover_path.write_text(render_svg("cover", 2048, 1152), encoding="utf-8")
    inline_path.write_text(render_svg("inline", 2048, 1152), encoding="utf-8")
    prompt_path = directory / f"{prefix}-prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    return {
        "image_prompt": prompt,
        "cover_path": str(cover_path),
        "content_image_path": str(inline_path),
        "image_prompt_path": str(prompt_path),
        "image_provider": "local-svg-placeholder",
        "image_fingerprint": hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:16],
    }
