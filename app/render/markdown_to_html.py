from __future__ import annotations

import html
import re

THEME_STYLES: dict[str, dict[str, str]] = {
    "bytedance-green": {
        "wrapper": "font-size:15px; line-height:1.8; color:#3f5f4a; background:#ffffff; padding:16px;",
        "h1": "font-size:22px; line-height:1.3; margin:24px 0; color:#1f3d2b; text-align:center; letter-spacing:0.08em; padding:10px 24px; border-top:3px solid #74C69D; border-bottom:1px solid rgba(149,213,178,0.5); border-radius:4px; background:linear-gradient(to right, rgba(116,198,157,0.02), rgba(149,213,178,0.05), rgba(116,198,157,0.02));",
        "h2": "font-size:20px; line-height:1.4; margin:36px 0 18px; color:#ffffff; text-align:center; padding:6px 22px; background:linear-gradient(135deg, #74C69D, #95D5B2); border-radius:8px 24px 8px 24px;",
        "h3": "font-size:17px; line-height:1.5; margin:26px 0 12px; color:#1f3d2b; font-weight:bold; padding:0 0 0 12px; border-left:4px solid #74C69D;",
        "p": "margin:0 0 16px; color:#3f5f4a;",
        "blockquote": "margin:18px 0; padding:14px 16px; background:#f0faf4; color:#3f5f4a; border-left:4px solid #95D5B2; border-radius:6px;",
        "hr": "border:none; height:2px; margin:32px 0; background:linear-gradient(to right, rgba(116,198,157,0), #74C69D, #95D5B2, rgba(149,213,178,0));",
    },
    "fresh-card": {
        "wrapper": "font-size:15px; line-height:1.75; color:#3d4a3d; background:#f5f8f5; padding:16px;",
        "h1": "font-size:22px; line-height:1.3; margin:0 0 16px; color:#3d4a3d; text-align:center; padding:16px 24px; border-bottom:1px dashed rgba(74,128,88,0.3); background:#ffffff; border-radius:14px;",
        "h2": "font-size:20px; line-height:1.3; margin:28px 0 14px; color:#6b9b7a; padding:0 0 10px; border-bottom:1px dashed rgba(74,128,88,0.3);",
        "h3": "font-size:17px; line-height:1.5; margin:24px 0 12px; color:#3d4a3d; font-weight:bold; padding:0 0 0 12px; border-left:4px solid #6b9b7a;",
        "p": "margin:0 0 18px; color:#3d4a3d; background:#ffffff; padding:14px 16px; border-radius:12px; box-shadow:0 4px 12px rgba(107,155,122,0.08);",
        "blockquote": "margin:18px 0; padding:15px 20px; background:#e8f0e8; color:#3d4a3d; border-left:5px solid #6b9b7a; border-radius:0 12px 12px 0; box-shadow:inset 0 0 15px rgba(107,155,122,0.1);",
        "hr": "border:none; height:1px; margin:32px 0; background:rgba(74,128,88,0.1);",
    },
}


def default_wechat_theme(content_type: str | None) -> str:
    return "bytedance-green" if content_type == "briefing" else "fresh-card"


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`(.+?)`", r'<code style="background:rgba(107,155,122,0.1); padding:2px 6px; border-radius:4px; color:#4a8058; font-size:90%;">\1</code>', escaped)
    return re.sub(r"\*\*(.+?)\*\*", r'<strong style="font-weight:bold; color:#4a8058;">\1</strong>', escaped)


def _paragraph(lines: list[str], style: str) -> str:
    text = "<br/>".join(_inline(line) for line in lines)
    return f'<p style="{style}">{text}</p>'


def markdown_to_wechat_html(markdown: str, content_type: str | None = None, theme: str | None = None) -> str:
    theme_name = theme or default_wechat_theme(content_type)
    styles = THEME_STYLES.get(theme_name, THEME_STYLES["fresh-card"])
    parts = [f'<section data-theme="{html.escape(theme_name)}" style="{styles["wrapper"]}">']
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            parts.append(_paragraph(paragraph_lines, styles["p"]))
            paragraph_lines = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            continue
        if line == "---":
            flush_paragraph()
            parts.append(f'<hr style="{styles["hr"]}"/>')
        elif line.startswith("# "):
            flush_paragraph()
            parts.append(f'<h1 style="{styles["h1"]}">{_inline(line[2:])}</h1>')
        elif line.startswith("## "):
            flush_paragraph()
            parts.append(f'<h2 style="{styles["h2"]}">{_inline(line[3:])}</h2>')
        elif line.startswith("### "):
            flush_paragraph()
            parts.append(f'<h3 style="{styles["h3"]}">{_inline(line[4:])}</h3>')
        elif line.startswith("> "):
            flush_paragraph()
            quote = line[2:]
            quote = re.sub(r"^\[!\w+\]\s*", "", quote)
            parts.append(f'<blockquote style="{styles["blockquote"]}">{_inline(quote)}</blockquote>')
        else:
            paragraph_lines.append(line)
    flush_paragraph()
    parts.append("</section>")
    return "\n".join(parts)
