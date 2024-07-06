import os
import telebot
from voice_assistant import VoiceAssistant


class TelegramBot:

    def __init__(self, telegram_token, openai_api_key, gemini_api_key):
        self.bot = telebot.TeleBot(telegram_token)
        self.voice_assistant = VoiceAssistant(openai_api_key, gemini_api_key)
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(content_types=['voice'])
        def handle_voice_message(message):
            file_info = self.bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file = self.bot.download_file(file_path)

            # Save the voice message as an OGG file
            ogg_file_path = 'voice_message.ogg'
            with open(ogg_file_path, 'wb') as f:
                f.write(downloaded_file)

            # Convert OGG to WAV using ffmpeg
            wav_file_path = 'voice_message.wav'
            os.system(f'ffmpeg -i "{ogg_file_path}" "{wav_file_path}"')

            # Process the WAV file
            text = self.voice_assistant.wav_to_text(wav_file_path)
            response = self.voice_assistant.generate_response(text)
            self.voice_assistant.speak(response)
            self.bot.reply_to(message, response)

    def run(self):
        print("Bot is polling...")
        self.bot.polling()


# Example usage
if __name__ == "__main__":
    TELEGRAM_API = 'your_telegram_bot_api_key'
    OPENAI_API = 'your_openai_api_key'
    GEMINI_API = 'your_gemini_api_key'

    bot = TelegramBot(TELEGRAM_API, OPENAI_API, GEMINI_API)
    bot.run()
