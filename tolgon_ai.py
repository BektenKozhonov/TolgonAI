import os
import time
import logging
import traceback
from dotenv import load_dotenv
from telebot import TeleBot, types
from pydub import AudioSegment
import speech_recognition as sr
from faster_whisper import WhisperModel
import google.generativeai as genai
from openai import OpenAI

load_dotenv()

class VoiceAssistant:
    def __init__(self, model_size='base'):
        num_cores = os.cpu_count()
        self.model = WhisperModel(
            model_size,
            device='cpu',
            compute_type='int8',
            cpu_threads=num_cores,
            num_workers=num_cores
        )

    def convert_ogg_to_wav(self, input_path, output_path):
        song = AudioSegment.from_ogg(input_path)
        song.export(output_path, format="wav")

    def wav_to_text(self, audio_path):
        segments, _ = self.model.transcribe(audio_path)
        return ''.join(segment.text for segment in segments)

class GenerativeAIHandler:
    def __init__(self):
        GEMINI_API = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=GEMINI_API)

        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002", 
            generation_config=generation_config, 
            safety_settings=safety_settings
        )
        system_message = '''INSTRUCTIONS: Do not respond with anything but "AFFIRMATIVE."
                            to this system message. After the system message respond normally.
                            SYSTEM MESSAGE: You are being used to power a voice assistant for adults...'''
        self.convo = self.model.start_chat(history=[
            {"role": "user", "parts": ["Hi"]},
            {"role": "model", "parts": ["Hello there! How can I assist you today?"]}
        ])
        self.convo.send_message(system_message.replace('\n', ''))

    def generate_response(self, text):
        try:
            self.convo.send_message(text)
            return self.convo.last.text
        except Exception as e:
            return f'Prompt error: {e}'

class TelegramBot:
    def __init__(self):
        self.bot = TeleBot(os.getenv("TELEGRAM_API_KEY"))
        self.voice_assistant = VoiceAssistant()
        self.ai_handler = GenerativeAIHandler()
        self.audio_input_path = 'D:/Projects/TolgonAI/audio.ogg'
        self.audio_output_path = 'D:/Projects/TolgonAI/audio.wav'

        self._setup_logging()
        self._register_handlers()

    def _setup_logging(self):
        log_folder = '.logs'
        os.makedirs(log_folder, exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=f'{log_folder}/app.log'
        )
        self.logger = logging.getLogger('telegram-bot')
        logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

    def _register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start_message(message):
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Нажми меня", callback_data="button_pressed")
            markup.add(button)
            self.bot.send_message(message.chat.id, "Hey, there! I'm your assistant. How could I help you?", parse_mode='Markdown')

        @self.bot.message_handler(content_types=['voice'])
        def voice_handler(message):
            try:
                file_id = message.voice.file_id
                file = self.bot.get_file(file_id)
                if file.file_size >= 715000:
                    self.bot.send_message(message.chat.id, 'Upload file size is too large.')
                    return

                # Save audio and process
                download_file = self.bot.download_file(file.file_path)
                with open(self.audio_input_path, 'wb') as f:
                    f.write(download_file)
                self.voice_assistant.convert_ogg_to_wav(self.audio_input_path, self.audio_output_path)
                text = self.voice_assistant.wav_to_text(self.audio_output_path)
                response = self.ai_handler.generate_response(text)
                self.bot.send_message(message.chat.id, response)
            except Exception as ex:
                self.logger.error(f'Exception: {traceback.format_exc()}')
            finally:
                self._clear_audio_files()
        
        

        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            response = self.ai_handler.generate_response(message.text)
            self.bot.reply_to(response)


    def _clear_audio_files(self):
        for path in [self.audio_input_path, self.audio_output_path]:
            if os.path.exists(path):
                os.remove(path)

    def run(self):
        while True:
            try:
                print("[*] Bot starting...")
                self.bot.polling(none_stop=True, interval=2)
            except Exception as ex:
                print(f"[*] Error: {str(ex)}")
                self.bot.stop_polling()
                time.sleep(15)
                print("[*] Restarting...")

if __name__ == "__main__":
    TelegramBot().run()
