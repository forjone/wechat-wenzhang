import json
import subprocess
import sys

from app.config import Settings
from app.main import generate_briefing_command, prepare_news


def test_prepare_news_marks_fallback_source_when_aihot_fails():
    settings = Settings(aihot_skill_url="http://127.0.0.1:1/unavailable", aihot_skill_timeout=1)

    news = prepare_news(settings, "2026-05-09", allow_fallback=True)

    assert news
    assert all(item["source_mode"] == "fallback" for item in news)
    assert all(item["source_error"] == "AIHOT_SKILL_REQUEST_FAILED" for item in news)
    assert all(item["source_provider"] == "fallback" for item in news)


def test_prepare_news_strict_mode_raises_when_aihot_fails():
    settings = Settings(aihot_skill_url="http://127.0.0.1:1/unavailable", aihot_skill_timeout=1)

    try:
        prepare_news(settings, "2026-05-09", allow_fallback=False)
    except RuntimeError as exc:
        assert str(exc) == "AIHOT_SKILL_REQUEST_FAILED"
    else:
        raise AssertionError("strict mode should raise AIHOT_SKILL_REQUEST_FAILED")


def test_generated_article_metadata_records_fallback_source(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'superfa.db'}",
        aihot_skill_url="http://127.0.0.1:1/unavailable",
        aihot_skill_timeout=1,
    )

    result = generate_briefing_command(settings, "2026-05-09", create_draft=False)

    assert result["status"] == "success"
    metadata_path = result["briefing"]["files"]["metadata"]
    metadata = json.loads(open(metadata_path, encoding="utf-8").read())
    assert metadata["source_mode"] == "fallback"
    assert metadata["source_error"] == "AIHOT_SKILL_REQUEST_FAILED"
    assert metadata["news_items"]
    assert all(item["source_mode"] == "fallback" for item in metadata["news_items"])


def test_cli_no_fallback_exits_failed_when_source_unavailable(tmp_path):
    db_path = tmp_path / "superfa.db"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.main",
            "generate-briefing",
            "--date",
            "2026-05-09",
            "--database",
            str(db_path),
            "--aihot-url",
            "http://127.0.0.1:1/unavailable",
            "--no-fallback",
        ],
        cwd="/home/superfa/superfa-ai-agent",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["error"] == "AIHOT_SKILL_REQUEST_FAILED"
