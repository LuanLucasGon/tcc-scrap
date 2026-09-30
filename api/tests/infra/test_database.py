def test_get_database_url_builds_expected_url(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "u")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p")
    monkeypatch.setenv("POSTGRES_HOST", "h")
    monkeypatch.setenv("POSTGRES_PORT", "1234")
    monkeypatch.setenv("POSTGRES_DB", "d")

    from infra.database import get_database_url

    assert get_database_url() == "postgresql+psycopg://u:p@h:1234/d"


def test_env_is_loaded_from_repository_root(monkeypatch):
    import os

    monkeypatch.delenv("POSTGRES_USER", raising=False)

    from dotenv import load_dotenv

    load_dotenv()

    assert os.getenv("POSTGRES_USER") is not None
