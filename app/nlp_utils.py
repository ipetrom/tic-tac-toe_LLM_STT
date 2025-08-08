import json
import re
from typing import Optional, Literal, Dict, List

from openai import OpenAI

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
    default_player: Optional[Player] = None,
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
        f"Default player: {default_player if default_player else 'NONE'}\n\n"
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

def llm_parse_move_with_board(
    text: str,
    board: List[List[Optional[str]]],
    default_player: Optional[Player] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> Dict[str, int | str]:
    """
    Wersja LLM-only z kontekstem bieżącej planszy.
    Model dostaje stan gry i ma zwrócić legalny ruch w formacie JSON.
    Nie dodajemy żadnych heurystyk – jeśli JSON jest zły lub ruch nielegalny,
    funkcja rzuca ValueError (walidacja minimalna: format i zakres).
    """
    client = OpenAI()

    # Serializacja planszy do prostego formatu – None -> ".", X/O bez zmian
    serial_board = [[(cell if cell in ("X", "O") else ".") for cell in row] for row in board]

    system_msg = (
        "You are a strict JSON command parser and controller for Tic-Tac-Toe. "
        "Given the current 3x3 board ('.' means empty, 'X'/'O' are occupied), "
        "and a user instruction, return ONLY a valid JSON object with keys: player,row,col. "
        "Rules: indexes are 0..2; the target cell must be empty; player must be 'X' or 'O'. "
        "No explanations, no markdown, only the JSON object."
    )

    user_msg = (
        f"Board (3 rows, 0-based indices):\n{serial_board}\n\n"
        f"User command (PL): {text}\n"
        f"Default player: {default_player if default_player else 'NONE'}\n\n"
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

    # Minimalna walidacja formatowa (bez heurystyk wyboru)
    player = data.get("player")
    row = data.get("row")
    col = data.get("col")
    if player not in ("X", "O"):
        raise ValueError("Invalid 'player' from LLM. Expected 'X' or 'O'.")
    if not isinstance(row, int) or not isinstance(col, int):
        raise ValueError("Invalid 'row'/'col' types from LLM. Expected integers.")
    if not (0 <= row <= 2 and 0 <= col <= 2):
        raise ValueError("Row/col out of range. Expected 0..2.")
    # Sprawdź zajętość pola – to nadal walidacja formalna (legalność ruchu)
    if board[row][col] in ("X", "O"):
        raise ValueError("Cell is already occupied according to provided board.")
    return {"player": player, "row": row, "col": col}
