import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nlp_utils import _extract_json, llm_parse_move, llm_parse_move_with_board

content = "OK, i'll do it. Here's the JSON:\n{\"player\":\"O\",\"row\":0,\"col\":2}\nGood luck!"
#print(_extract_json(content))

text = "Mam na imię Daniel, jestem z Krakowa. Proszę, zagraj O w prawym górnym rogu planszy."
#print(llm_parse_move(text))

board = [
    ["X", "O", "X"],
    ["O", None, "X"],
    [None, "O", None],
]
text2 = "Zagraj O w lewym dolnym rogu planszy."
print(llm_parse_move_with_board(text2, board))