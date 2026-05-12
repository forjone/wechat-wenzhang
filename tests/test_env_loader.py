from app.config import Settings, load_dotenv


def test_load_dotenv_sets_missing_environment_variables(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("AUTHOR_NAME=本地超级发\nAUTO_PUBLISH=true\nAIHOT_SKILL_TIMEOUT=7\n# comment\nEMPTY_VALUE=\n", encoding="utf-8")
    monkeypatch.delenv("AUTHOR_NAME", raising=False)
    monkeypatch.delenv("AUTO_PUBLISH", raising=False)
    monkeypatch.delenv("AIHOT_SKILL_TIMEOUT", raising=False)

    load_dotenv(env_file)
    settings = Settings.from_env()

    assert settings.author_name == "本地超级发"
    assert settings.auto_publish is True
    assert settings.aihot_skill_timeout == 7


def test_load_dotenv_does_not_override_existing_environment(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("AUTHOR_NAME=文件里的名字\n", encoding="utf-8")
    monkeypatch.setenv("AUTHOR_NAME", "环境里的名字")

    load_dotenv(env_file)

    assert Settings.from_env().author_name == "环境里的名字"
