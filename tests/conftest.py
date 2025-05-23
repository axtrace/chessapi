import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
import os
import sys
import chess.engine
import asyncio
import platform

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Устанавливаем тестовый API ключ до импорта приложения
os.environ["API_KEY"] = "test_key_123"

# Определяем путь к Stockfish в зависимости от ОС
if platform.system() == "Darwin":  # macOS
    STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"
else:  # Linux/другие системы
    STOCKFISH_PATH = "/usr/games/stockfish"

# Проверяем существование файла
if not os.path.exists(STOCKFISH_PATH):
    raise FileNotFoundError(f"Stockfish not found at {STOCKFISH_PATH}. Please install it first.")

# Импортируем приложение после установки переменных окружения
from chessapi.chessapi import app

# Настройка pytest-asyncio
def pytest_configure(config):
    config.option.asyncio_mode = "strict"
    config.option.asyncio_default_fixture_loop_scope = "function"

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def mock_stockfish_path(monkeypatch):
    """Мокаем путь к Stockfish для тестов"""
    monkeypatch.setenv("STOCKFISH_PATH", STOCKFISH_PATH)

@pytest_asyncio.fixture(scope="function")
async def mock_engine(monkeypatch):
    """Инициализируем mock-движок для каждого теста и подменяем глобальный engine"""
    engine = AsyncMock()
    engine.ping = AsyncMock()
    engine.play = AsyncMock(return_value=AsyncMock(move=chess.Move.from_uci("e2e4")))
    # Подменяем глобальный engine в chessapi.chessapi
    import chessapi.chessapi
    monkeypatch.setattr(chessapi.chessapi, "engine", engine)
    yield engine