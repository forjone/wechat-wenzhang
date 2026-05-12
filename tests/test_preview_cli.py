import json
import subprocess
import sys

from app.database import init_db, save_article


def test_preview_article_outputs_markdown_by_id(tmp_path):
    db_path = tmp_path / "superfa.db"
    init_db(db_path)
    article_id = save_article(
        db_path,
        {
            "content_type": "briefing",
            "issue_no": 1,
            "date": "2026-05-09",
            "title": "AI简报001",
            "digest": "摘要",
            "content_markdown": "# AI简报001\n\n正文",
            "content_html": "<h1>AI简报001</h1>",
        },
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.main",
            "preview",
            "--database",
            str(db_path),
            "--article-id",
            str(article_id),
        ],
        cwd="/home/superfa/superfa-ai-agent",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["article"]["id"] == article_id
    assert payload["article"]["content_markdown"] == "# AI简报001\n\n正文"
    assert "content_html" not in payload["article"]


def test_preview_article_can_output_html_by_id(tmp_path):
    db_path = tmp_path / "superfa.db"
    init_db(db_path)
    article_id = save_article(db_path, {"content_type": "briefing", "issue_no": 1, "title": "T", "content_markdown": "MD", "content_html": "<p>HTML</p>"})

    result = subprocess.run(
        [sys.executable, "-m", "app.main", "preview", "--database", str(db_path), "--article-id", str(article_id), "--format", "html"],
        cwd="/home/superfa/superfa-ai-agent",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["article"]["content_html"] == "<p>HTML</p>"
    assert "content_markdown" not in payload["article"]


def test_preview_missing_article_returns_failure(tmp_path):
    db_path = tmp_path / "superfa.db"
    init_db(db_path)

    result = subprocess.run(
        [sys.executable, "-m", "app.main", "preview", "--database", str(db_path), "--article-id", "999"],
        cwd="/home/superfa/superfa-ai-agent",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["error"] == "ARTICLE_NOT_FOUND"
