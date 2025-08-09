from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any

from app.game_logic import TicTacToeBoard
from app.nlp_utils import llm_parse_move, apply_move_from_text

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
    move: Optional[Dict[str, Any]] = None  # dla LLM-owych endpointów

class TextCommand(BaseModel):
    text: str = Field(..., description="Write a command to play a move, e.g., 'X plays at row 1, column 2'")
    default_player: Optional[Literal["X", "O"]] = Field(None, description="Default player if not specified in command")
    model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model to use for parsing")
    temperature: float = Field(0.0, ge=0.0, le=1.0, description="Temperature for LLM")

class ParsedMove(BaseModel):
    player: Literal["X", "O"]
    row: int
    col: int

@app.get("/state", response_model=MoveResponse)
def get_board_state():
    winner = board.check_winner()
    return MoveResponse(
        success=True,
        message="Current board state.",
        board=board.get_state(),
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
        winner = board.check_winner()
        return MoveResponse(
            success=False,
            message=f"Game over! Winner: {board.check_winner()}",
            board=board.get_state(),
            winner=winner,
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
            winner=winner,
            is_full=board.is_full()
        )
    else:
        return MoveResponse(
            success=False,
            message="Invalid move: cell already occupied.",
            board=board.get_state(),
            winner=board.check_winner(),
            is_full=board.is_full()
        )

@app.post("/reset")
def reset_board():
    board.reset()
    return {"message": "Board reset."}

# ===== Endpoints LLM =====

@app.post("/parse_command", response_model=ParsedMove)
def parse_command(cmd: TextCommand):
    """
    1) LLM parsuje polecenie na {player,row,col}
    2) NIE wykonuje ruchu
    """
    try:
        move = llm_parse_move(
            text=cmd.text,
            default_player=cmd.default_player,
            model=cmd.model or "gpt-4o-mini",
            temperature=cmd.temperature,
        )
        return ParsedMove(**move)  # walidacja schematu
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/move_from_text", response_model=MoveResponse)
def move_from_text(cmd: TextCommand):
    """
    1) LLM parsuje
    2) Walidujemy względem planszy
    3) Jeśli legalny — wykonujemy i zwracamy stan gry
    """
    try:
        result = apply_move_from_text(
            board=board,
            text=cmd.text,
            default_player=cmd.default_player,
            model=cmd.model or "gpt-4o-mini",
            temperature=cmd.temperature,
        )
        # result to słownik zgodny z MoveResponse (+ move)
        return MoveResponse(**result)
    except ValueError as e:
        # gdy llm_parse_move zwróci niepoprawne dane itp.
        raise HTTPException(status_code=400, detail=str(e))  