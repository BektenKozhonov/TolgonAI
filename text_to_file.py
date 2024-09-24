from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

client = OpenAI(os.getenv('OPENAI_API_KEY'))

speech_file_path = 'D:/Projects/bot_voice_recognition/speech.mp3'
response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Today is a wonderful day to build something people love!"
)

response.stream_to_file(speech_file_path)