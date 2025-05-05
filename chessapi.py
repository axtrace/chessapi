from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import chess
import chess.engine
from contextlib import asynccontextmanager
from auth import get_api_key

STOCKFISH_PATH = "/usr/games/stockfish"

class MoveRequest(BaseModel):
    fen: str
    depth: int = 10

engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    print("Stockfish engine started")
    try:
        yield
    finally:
        if engine is not None:
            engine.quit()
            print("Stockfish engine stopped")

app = FastAPI(lifespan=lifespan)

@app.post("/bestmove/")
async def best_move(req: MoveRequest, api_key: str = Depends(get_api_key)):
    board = chess.Board(req.fen)
    
    # Check if the game is over
    if board.is_game_over():
        reason = board.outcome().termination.name if board.outcome() else "Unknown"
        return {
            "error": "Game is over",
            "reason": reason,
            "status": "game_over"
        }
    
    result = engine.play(board, chess.engine.Limit(depth=req.depth))
    if result.move is None:
        return {
            "error": "No legal moves available",
            "status": "no_moves"
        }
        
    best_move = result.move.uci()
    return {"best move": best_move}

@app.get("/healthcheck")
async def healthcheck(api_key: str = Depends(get_api_key)):
    global engine
    try:
        info = engine.id
        return {"status": "ok", "engine": info.get("name", "unknown")}
    except Exception as e:
        return {"status": "error", "details": str(e)}
