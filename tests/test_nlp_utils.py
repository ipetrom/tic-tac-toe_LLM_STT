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
    ["X", "O", "X"],
    ["O", None, "X"],
    [None, "O", None],
]
text2 = "Zagraj jako O w lewym dolnym rogu planszy."
#print(llm_parse_move_with_board(text2, board))

board_instance = TicTacToeBoard()
board_instance.board = board

text3 = "Zagraj O w prawym dolnym rogu planszy."
result = apply_move_from_text(board_instance, text3, default_player="O")
print(result)  # Expected: {'success': True, 'message': 'Move executed.', ...}