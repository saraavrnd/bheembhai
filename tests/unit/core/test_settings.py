from app.core.settings import get_settings


def test_default_settings_use_repo_name() -> None:
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_name == "BeemBhai"
    assert settings.version == "0.1.0"
    assert settings.database_url.startswith("sqlite+pysqlite://")


def test_auth_and_email_settings_are_loaded_from_env(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://demo:demo@postgres:5432/demo")
    monkeypatch.setenv("BREVO_API_KEY", "brevo-key")
    monkeypatch.setenv("BREVO_SENDER_EMAIL", "no-reply@example.com")
    monkeypatch.setenv("BREVO_SENDER_NAME", "BeemBhai Ops")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://demo:demo@postgres:5432/demo"
    assert settings.brevo_api_key == "brevo-key"
    assert settings.brevo_sender_email == "no-reply@example.com"
    assert settings.brevo_sender_name == "BeemBhai Ops"


def test_email_brevo_legacy_names_are_supported(monkeypatch) -> None:
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    monkeypatch.delenv("BREVO_SENDER_EMAIL", raising=False)
    monkeypatch.delenv("BREVO_SENDER_NAME", raising=False)
    monkeypatch.setenv("EMAIL_BREVO_API_KEY", "legacy-brevo-key")
    monkeypatch.setenv("EMAIL_BREVO_FROM_ADDRESS", "legacy-no-reply@example.com")
    monkeypatch.setenv("EMAIL_BREVO_SENDER_NAME", "Legacy BeemBhai")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.brevo_api_key == "legacy-brevo-key"
    assert settings.brevo_sender_email == "legacy-no-reply@example.com"
    assert settings.brevo_sender_name == "Legacy BeemBhai"
