from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
audio_file = open("/Users/petromelnyk/Downloads/exmpl.mp3", "rb")

transcription = client.audio.transcriptions.create(
  model="gpt-4o-mini-transcribe", 
  file=audio_file, 
  response_format="text",
  prompt="The following audio is a Polish conversation about playing Tic-Tac-Toe. Please transcribe it in Polish.")

print(transcription)