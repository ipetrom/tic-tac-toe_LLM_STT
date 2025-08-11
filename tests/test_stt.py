from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.stt import transcribe_file, STTError

client = OpenAI()
audio_file = open("/Users/petromelnyk/Downloads/exmpl.mp3", "rb")

transcription = client.audio.transcriptions.create(
  model="gpt-4o-mini-transcribe", 
  file=audio_file, 
  response_format="text",
  prompt="The following audio is a Polish conversation about playing Tic-Tac-Toe. Please transcribe it in Polish.")

#print(transcription)

#-------------

if __name__ == "__main__":
    try:
        result = transcribe_file("/Users/petromelnyk/Downloads/exmpl.mp3")
        print("=== TRANSKRYPCJA ===")
        print(result)
    except STTError as e:
        print(f"Błąd transkrypcji: {e}")
