import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nlp_utils import _extract_json, llm_parse_move, apply_move_from_text
from app.game_logic import TicTacToeBoard

content = "OK, i'll do it. Here's the JSON:\n{\"player\":\"O\",\"row\":0,\"col\":2}\nGood luck!"
#print(_extract_json(content))

text = "Mam na imię Daniel, jestem z Krakowa. Proszę, zagraj O w prawym górnym rogu planszy."
#print(llm_parse_move(text))

board = [
    [None, None, None],
    [None, None, None],
    [None, None, None],
]

board_instance = TicTacToeBoard()
board_instance.board = board

# First move
result1 = apply_move_from_text(board_instance, "Zagraj X w lewym górnym rogu planszy.")
print(result1)
print(board_instance.get_display())

# Second move
result2 = apply_move_from_text(board_instance, "Zagraj O w prawym dolnym rogu planszy.")
print(result2)
print(board_instance.get_display())

# Third move
result3 = apply_move_from_text(board_instance, "Zagraj X w drugim wierszu i pierwszej kolumnie planszy.")
print(result3)
print(board_instance.get_display())

# Fourth move
result4 = apply_move_from_text(board_instance, "Zagraj O w środkowej kolumnie i trzecim wierszu planszy.")
print(result4)
print(board_instance.get_display())

# Fifth move (should be invalid, as the cell is occupied)
result5 = apply_move_from_text(board_instance, "Zagraj X w lewym górnym rogu planszy.")
print(result5)
print(board_instance.get_display())

# Sixth move (winner check)
result6 = apply_move_from_text(board_instance, "Zagraj X w lewym dolnym rogu planszy.")
print(result6)
print(board_instance.get_display())