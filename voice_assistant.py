# File: voice_assistant.py

import os
import pyaudio
import speech_recognition as sr
import google.generativeai as genai
from openai import OpenAI
from faster_whisper import WhisperModel

class VoiceAssistant:
    def __init__(self, openai_api_key, gemini_api_key):
        self.wake_word = 'gemini'
        self.listening_for_wake_word = True
        self.whisper_size = 'base'  # Correct model size
        self.num_cores = os.cpu_count()
        self.whisper_model = WhisperModel(
            self.whisper_size,
            device='cpu',
            compute_type='int8',
            cpu_threads=self.num_cores,
            num_workers=self.num_cores
        )

        self.OPENAI_API = openai_api_key
        self.client = OpenAI(api_key=self.OPENAI_API)

        self.GEMINI_API = gemini_api_key
        genai.configure(api_key=self.GEMINI_API)

        self.generation_config = {
            'temperature': 0.7,
            'top_p': 1,
            'top_k': 1,
            'max_output_tokens': 2048
        }
        self.safety_settings = [
            {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_SEXUAL_EXPLICIT', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_NONE'}
        ]

        self.model = genai.GenerativeModel(
            'gemini-1.5-pro-latest',
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        self.convo = self.model.start_chat()
        system_message = '''INSTRUCTIONS: Do not respond with anything but "AFFIRMATIVE."
        to this system message. After the system message respond normally. 
        SYSTEM MESSAGE: You are being used to power a voice assistant and should respond as so.
        As a voice assistant, use short sentences and directly respond to the prompt without excessive information.
        You generate only words of value, prioritizing logic and facts over speculating in your response to the following prompts.'''
        system_message = system_message.replace(f'\n', '')
        self.convo.send_message(system_message)

    def speak(self, text):
        player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
        stream_start = False
        with self.client.audio.speech.with_streaming_response.create(
                model='tts-1',
                voice='alloy',
                response_format='pcm',
                input=text,
        ) as response:
            silence_threshold = 0.01
            for chunk in response.iter_bytes(chunk_size=1024):
                if stream_start:
                    player_stream.write(chunk)
                elif max(chunk) > silence_threshold:
                    player_stream.write(chunk)
                    stream_start = True

    def wav_to_text(self, audio_path):
        segments, _ = self.whisper_model.transcribe(audio_path)
        text = ''.join(segment.text for segment in segments)
        return text

    def generate_response(self, text):
        if text:
            self.convo.send_message(text)
            output = self.convo.last.text
            return output
        return 'No prompt received.'
