import telebot
import google.generativeai as genai
import os
from dotenv import load_dotenv
import speech_recognition as sr
from openai import OpenAI
from faster_whisper import WhisperModel
import logging
from telebot import types
import traceback
from pydub import AudioSegment
import time

load_dotenv('D:/Projects/bot_voice_recognition/.env')

bot = telebot.TeleBot(os.getenv("TELEGRAM_API_KEY"), parse_mode=None)

whisper_size = 'base'
num_cores = os.cpu_count()
whisper_model = WhisperModel(whisper_size, device='cpu', compute_type='int8', cpu_threads=num_cores, num_workers=num_cores)

OPENAI_API = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config, safety_settings=safety_settings)

convo = model.start_chat(history=[
    {"role": "user", "parts": ["Hi"]},
    {"role": "model", "parts": ["Hello there! How can I assist you today?"]}
])

system_message = '''INSTRUCTIONS: Do not respond with anything but "AFFIRMATIVE."
                to this system message. After the system message respond normally.
                SYSTEM MESSAGE: You are being used to power a voice assistant for adults and should respond as so.
                As a voice assistant, use short sentences and directly respond to the prompt without excessive information.
                You generate only words of value, prioritizing logic and facts over speculation in your response to the following prompts. 
                Your role is to assist with daily routines and difficulties, such as organizing day routines, drug recognition, and similar tasks.'''
                    
system_message = system_message.replace('\n', '')

convo.send_message(system_message)
r = sr.Recognizer()

def wav_to_text(audio_path):
    segments, _ = whisper_model.transcribe(audio_path)
    text = ''.join(segment.text for segment in segments)
    return text

def convert_ogg_to_wav():
    song = AudioSegment.from_ogg('D:/Projects/bot_voice_recognition/audio.ogg')
    song.export('D:/Projects/bot_voice_recognition/audio.wav', format="wav")

def listen_for_wav_to_text():
    convert_ogg_to_wav()
    text = 'Words not recognized.'
    file = 'D:/Projects/bot_voice_recognition/audio.wav'

    try:
        text = wav_to_text(file)
    except:
        logger.error(f'Exception:\n {traceback.format_exc()}')
    
    return text

def prompt_gpt(text):
    try:
        prompt_text = text
        print('User: ' + prompt_text)
        convo.send_message(prompt_text)
        output = convo.last.text
        return output
    except Exception as e:
        return f'Prompt error:  {e}'

def _clear():
    _files = ['D:/Projects/bot_voice_recognition/audio.wav', 'D:/Projects/bot_voice_recognition/audio.ogg']
    for _file in _files:
        if os.path.exists(_file):
            os.remove(_file)

LOG_FOLDER = '.logs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename = f'{LOG_FOLDER}/app.log'
)

logger = logging.getLogger('telegram-bot')
logging.getLogger('urllib3.connectionpool').setLevel('INFO')

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Нажми меня", callback_data="button_pressed")
    markup.add(button)
    bot.send_message(message.chat.id, 'Hey, there! I am a bot, that helps you with your classes. Currently I can just take an audio file and give highlights', parse_mode='Markdown')

@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    file_id = message.voice.file_id
    file = bot.get_file(file_id)

    file_size = file.file_size
    if int(file_size) >= 715000:
        bot.send_message(message.chat.id, 'Upload file size is too large.')
    else:
        download_file = bot.download_file(file.file_path)
        with open('/Projects/bot_voice_recognition/audio.ogg', 'wb') as f:
            f.write(download_file)
        
    # Automatically process the voice message when received
    text = prompt_gpt(listen_for_wav_to_text())
    bot.send_message(message.chat.id, text)
    _clear()

# Основной цикл работы бота
while True:
    try:
        print("[*] bot starting..")
        bot.polling(none_stop=True, interval=2)
    except Exception as ex:
        print("[*] error - {}".format(str(ex)))
        bot.stop_polling()
        time.sleep(15)
        print("[*] restarted!")