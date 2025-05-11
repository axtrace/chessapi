from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, field_validator
import chess
import chess.engine
from contextlib import asynccontextmanager
from .auth import get_api_key
import asyncio
import platform
import os
from .auth import get_api_key 

# Определяем путь к Stockfish в зависимости от ОС
if platform.system() == "Darwin":  # macOS
    STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"
else:  # Linux/другие системы
    STOCKFISH_PATH = "/usr/games/stockfish"

# Проверяем существование файла
if not os.path.exists(STOCKFISH_PATH):
    raise FileNotFoundError(f"Stockfish not found at {STOCKFISH_PATH}. Please install it first.")

# Инициализируем движок как None, он будет установлен в lifespan
engine = None

class MoveRequest(BaseModel):
    fen: str
    depth: int = 10
    time: float = 0.01  # Время на ход в секундах (по умолчанию 0.01, максимум 2.0)

    @field_validator('fen')
    @classmethod
    def validate_fen(cls, v):
        try:
            chess.Board(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid FEN string: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и очистка ресурсов приложения"""
    global engine
    try:
        # Создаем движок асинхронно
        transport, engine = await chess.engine.popen_uci(STOCKFISH_PATH)
        if engine is None:
            raise RuntimeError("Failed to initialize engine")
            
        # Настраиваем асинхронно
        await engine.configure({
            "Threads": 1,  # Минимум потоков
            "Hash": 1,     # Минимум памяти
            "Skill Level": 0,  # Минимальный уровень сложности
            "Move Overhead": 0  # Минимальная задержка
        })
        print("Stockfish engine started")
        yield
    finally:
        if engine is not None:
            try:
                await engine.quit()
                print("Stockfish engine stopped")
            except Exception as e:
                print(f"Warning: Failed to quit engine: {e}")

app = FastAPI(lifespan=lifespan)

async def ensure_engine():
    """Убеждаемся, что движок инициализирован"""
    global engine
    if engine is None:
        try:
            # Создаем движок асинхронно
            transport, engine = await chess.engine.popen_uci(STOCKFISH_PATH)
            if engine is None:
                raise RuntimeError("Failed to initialize engine")
                
            # Настраиваем асинхронно
            await engine.configure({
                "Threads": 1,  # Минимум потоков
                "Hash": 1,     # Минимум памяти
                "Skill Level": 0,  # Минимальный уровень сложности
                "Move Overhead": 0  # Минимальная задержка
            })
        except Exception as e:
            raise RuntimeError(f"Failed to initialize engine: {str(e)}")
    return engine

@app.post("/bestmove/")
async def best_move(req: MoveRequest, api_key: str = Depends(get_api_key)):
    try:
        engine = await ensure_engine()
    except Exception as e:
        return {"status": "error", "details": f"Engine initialization failed: {str(e)}"}
    
    board = chess.Board(req.fen)
    
    # Check if the game is over
    if board.is_game_over():
        reason = board.outcome().termination.name if board.outcome() else "Unknown"
        return {
            "status": "game_over",
            "error": "Game is over",
            "reason": reason
        }
    
    try:
        # Ограничиваем time максимумом 2.0 (дополнительная проверка)
        time_for_move = min(max(req.time, 0.01), 2.0)
        result = await engine.play(board, chess.engine.Limit(depth=req.depth, time=time_for_move, nodes=100))
        if result.move is None:
            return {
                "status": "no_moves",
                "error": "No legal moves available"
            }
            
        best_move = result.move.uci()
        return {
            "status": "ok",
            "best_move": best_move,
            "used_time": time_for_move,
            "error": None
        }
    except Exception as e:
        return {"status": "error", "details": str(e), "error": str(e)}

@app.get("/healthcheck")
async def healthcheck(api_key: str = Depends(get_api_key)):
    try:
        engine = await ensure_engine()
        await asyncio.wait_for(engine.ping(), timeout=0.01)
        return {"status": "ok", "engine": "Stockfish", "error": None}
    except Exception as e:
        return {"status": "error", "details": str(e), "error": str(e)}
