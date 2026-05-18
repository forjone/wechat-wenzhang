from pathlib import Path


def test_daily_runner_uses_beijing_yesterday_source_date_and_cjfai_account():
    script = Path("scripts/run_daily.sh").read_text(encoding="utf-8")

    assert "BUSINESS_TZ=\"${BUSINESS_TZ:-Asia/Shanghai}\"" in script
    assert "RUN_DATE=\"$(TZ=\"$BUSINESS_TZ\" date +%F)\"" in script
    assert "SOURCE_DATE=\"$(TZ=\"$BUSINESS_TZ\" date -d yesterday +%F)\"" in script
    assert "WECHAT_ACCOUNT=\"${WECHAT_ACCOUNT:-cjfai}\"" in script
    assert "python3" in script
    assert "generate-daily" in script
    assert "--create-draft" in script
    assert "--wechat-account \"$WECHAT_ACCOUNT\"" in script
    assert "--no-fallback" in script
    assert "env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY" in script
    assert "NO_PROXY='*' no_proxy='*'" in script


def test_crontab_example_runs_daily_at_1am():
    crontab = Path("scripts/crontab.example").read_text(encoding="utf-8")

    assert "0 1 * * * /home/superfa/superfa-ai-agent/scripts/run_daily.sh" in crontab
