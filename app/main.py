from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional

from app.game_logic import TicTacToeBoard

app = FastAPI()
board = TicTacToeBoard()

class MoveRequest(BaseModel):
    player: Literal["X", "O"]
    row: int  # 0, 1, 2
    col: int  # 0, 1, 2

class MoveResponse(BaseModel):
    success: bool
    message: str
    board: list[list[Optional[str]]]
    board_display: str
    winner: Optional[str] = None
    is_full: bool = False

@app.get("/state", response_model=MoveResponse)
def get_board_state():
    winner = board.check_winner()
    return MoveResponse(
        success=True,
        message="Current board state.",
        board=board.get_state(),
        board_display=board.get_display(),
        winner=winner,
        is_full=board.is_full()
    )

@app.post("/move", response_model=MoveResponse)
def make_move(move: MoveRequest):
    if move.player not in ["X", "O"]:
        raise HTTPException(status_code=400, detail="Player must be 'X' or 'O'.")
    if not (0 <= move.row <= 2 and 0 <= move.col <= 2):
        raise HTTPException(status_code=400, detail="Row and column must be 0, 1, or 2.")

    if board.check_winner():
        return MoveResponse(
            success=False,
            message=f"Game over! Winner: {board.check_winner()}",
            board=board.get_state(),
            board_display=board.get_display(),
            winner=board.check_winner(),
            is_full=board.is_full()
        )

    if board.make_move(move.player, move.row, move.col):
        winner = board.check_winner()
        msg = "Move accepted."
        if winner:
            msg = f"Player {winner} wins!"
        elif board.is_full():
            msg = "It's a draw!"
        return MoveResponse(
            success=True,
            message=msg,
            board=board.get_state(),
            board_display=board.get_display(),
            winner=winner,
            is_full=board.is_full()
        )
    else:
        return MoveResponse(
            success=False,
            message="Invalid move: cell already occupied.",
            board=board.get_state(),
            board_display=board.get_display(),
            winner=board.check_winner(),
            is_full=board.is_full()
        )

@app.post("/reset")
def reset_board():
    board.reset()
    return {"message": "Board reset."}
