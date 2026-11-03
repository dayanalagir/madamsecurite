import pytest


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path):
    """Тесты не читают настоящий .env и не трогают рабочую базу."""
    for key in ("SMTP_APP_PASSWORD", "SMTP_USER", "DIGEST_TO", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setattr("madam_digest.settings.load_dotenv", lambda *a, **k: False)
    return tmp_path
