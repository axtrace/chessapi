import os
import pytest
from chessapi.config import Settings

@pytest.fixture(autouse=True)
def test_settings():
    """Фикстура для установки тестовых настроек"""
    os.environ["API_KEY"] = "test_key_123"
    settings = Settings()
    return settings