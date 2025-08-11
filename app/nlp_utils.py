import json
import re
from typing import Optional, Literal, Dict, List, Any
from app.game_logic import TicTacToeBoard

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

Player = Literal["X", "O"]

def _extract_json(content: str) -> dict:
    """
    Wyciąga pierwszy blok JSON z treści odpowiedzi modelu (bez fallbacków/heurystyk semantycznych).
    """
    m = re.search(r"\{.*\}", content, flags=re.DOTALL)
    json_str = m.group(0) if m else content
    return json.loads(json_str)

def llm_parse_move(
    text: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> Dict[str, int | str]:
    """
    Wersja LLM-only: model parsuje komendę tekstową i zwraca ruch.
    Zwraca dokładnie JSON: {"player":"X|O","row":0..2,"col":0..2}.
    Brak heurystyk – jeśli model nie poda poprawnego JSON, funkcja zgłasza błąd.
    """
    client = OpenAI()

    system_msg = (
        "You are a strict JSON command parser for a Tic-Tac-Toe controller. "
        "You MUST return ONLY a valid JSON object with keys: player,row,col. "
        "Indexes are 0-based (0..2). No explanations, no prose, no markdown."
    )

    user_msg = (
        f"User command (PL): {text}\n"
        "Return ONLY JSON like: {\"player\":\"X or O\",\"row\":0..2,\"col\":0..2}"
    )

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )
    content = resp.choices[0].message.content if resp.choices else ""
    if not content:
        raise ValueError("LLM did not return content.")

    data = _extract_json(content)

    # Minimalna walidacja formatowa (nadal bez logiki heurystycznej)
    player = data.get("player")
    row = data.get("row")
    col = data.get("col")
    if player not in ("X", "O"):
        raise ValueError("Invalid 'player' from LLM. Expected 'X' or 'O'.")
    if not isinstance(row, int) or not isinstance(col, int):
        raise ValueError("Invalid 'row'/'col' types from LLM. Expected integers.")
    if not (0 <= row <= 2 and 0 <= col <= 2):
        raise ValueError("Row/col out of range. Expected 0..2.")
    return {"player": player, "row": row, "col": col}

def apply_move_from_text(
    board: TicTacToeBoard,
    text: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> Dict[str, Any]:
    """
    Orkiestracja LLM -> walidacja -> wykonanie ruchu.
    1) LLM parsuje tekst na {player,row,col}
    2) Sprawdzamy, czy pole jest wolne
    3) Jeśli tak, wykonujemy ruch i liczymy wynik gry
    Zwraca dict spójny z logiką API (success/message/board/winner/is_full/move).
    """
    # 1) Parsowanie komendy przez LLM
    move = llm_parse_move(
        text=text,
        model=model,
        temperature=temperature,
    )
    player = move["player"]
    row = int(move["row"])
    col = int(move["col"])

    # 2) Walidacja zajętości pola
    current_cell = board.get_state()[row][col]
    if current_cell in ("X", "O"):
        return {
            "success": False,
            "message": "This cell is already occupied.",
            "board": board.get_state(),
            "board_display": board.get_display(),
            "winner": board.check_winner(),
            "is_full": board.is_full(),
            "move": move,
        }

    # 3) Wykonanie ruchu
    placed = board.make_move(player, row, col)
    if not placed:
        # Teoretycznie nie powinniśmy tutaj trafić, ale zostawmy bezpiecznik
        return {
            "success": False,
            "message": "Move was not executed (unknown error).",
            "board": board.get_state(),
            "board_display": board.get_display(),
            "winner": board.check_winner(),
            "is_full": board.is_full(),
            "move": move,
        }

    # 4) Wyliczenie stanu gry po ruchu
    winner = board.check_winner()
    is_full = board.is_full()

    if winner:
        msg = f"Player {winner} wins!"
    elif is_full:
        msg = "Draw – board is full."
    else:
        msg = "Move executed."

    return {
        "success": True,
        "message": msg,
        "board": board.get_state(),
        "board_display": board.get_display(),
        "winner": winner,
        "is_full": is_full,
        "move": move,
    }
