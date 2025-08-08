import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nlp_utils import _extract_json

content = "OK, i'll do it. Here's the JSON:\n{\"player\":\"O\",\"row\":0,\"col\":2}\nGood luck!"
#print(_extract_json(content))

