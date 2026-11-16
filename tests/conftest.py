
import secrets
import pytest


@pytest.fixture(autouse=True)
def mock_banner_service_token(monkeypatch):
    token = secrets.token_urlsafe(32)
    monkeypatch.setenv("MOCK_BANNER_SERVICE_TOKEN", token)
    return token
