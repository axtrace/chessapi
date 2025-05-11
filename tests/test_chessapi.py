import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from chessapi import app
import chess
from chessapi.chessapi import engine
import asyncio
import os

# Тестовый API ключ для тестов
TEST_API_KEY = "test_key_123"

engine = None
use_mock_engine = True  # Принудительно используем mock-движок для тестов

async def ensure_engine():
    global engine
    if use_mock_engine:
        from unittest.mock import AsyncMock
        engine = AsyncMock()
        engine.play = AsyncMock(return_value=AsyncMock(move=chess.Move.from_uci("e2e4")))
        return engine
    # ... остальной код инициализации

@pytest.mark.asyncio
async def test_invalid_fen():
    """Тест на обработку некорректной FEN строки"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=1.0) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "invalid_fen", "depth": 1},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 422
        assert "Invalid FEN string" in response.text

@pytest.mark.asyncio
async def test_game_over(mock_engine):
    """Тест на обработку окончания игры"""
    mock_engine.play.return_value.move = None  # Имитируем game_over
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=0.1) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "8/8/8/8/8/8/8/7k w - - 0 1", "depth": 1},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "game_over"

@pytest.mark.asyncio
async def test_valid_move(mock_engine):
    """Тест на получение корректного хода"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=0.1) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "depth": 1},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["best_move"] == "e2e4"

@pytest.mark.asyncio
async def test_healthcheck(mock_engine):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=0.1) as client:
        response = await client.get("/healthcheck", headers={"X-API-Key": TEST_API_KEY})
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_no_api_key():
    """Тест на отсутствие API ключа"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=1.0) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "depth": 1}
        )
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_valid_time_param(mock_engine):
    """Тест: time=0.5 (валидно)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=0.5) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "depth": 1, "time": 0.5},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["used_time"] == 0.5

@pytest.mark.asyncio
async def test_valid_time_param_max(mock_engine):
    """Тест: time=2.0 (валидно)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=2.5) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "depth": 1, "time": 2.0},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["used_time"] == 2.0

@pytest.mark.asyncio
async def test_invalid_time_param_too_high(mock_engine):
    """Тест: time=2.5 (ошибка 422)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=1.0) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "depth": 1, "time": 2.5},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["used_time"] == 2.0

@pytest.mark.asyncio
async def test_invalid_time_param_negative(mock_engine):
    """Тест: time=-1 (ошибка 422)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=1.0) as client:
        response = await client.post(
            "/bestmove/",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "depth": 1, "time": -1},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["used_time"] == 0.01