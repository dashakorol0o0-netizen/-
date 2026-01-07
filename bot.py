import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

# 1. Настройка Flask (чтобы Render не ругался на порты)
app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

# 2. Настройка Бота
token = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Пришли ссылку на видео, и я его скачаю.")

@bot.message_handler(func=lambda message: True)
def handle_video(message):
    url = message.text
    if "http" in url:
        bot.send_message(message.chat.id, "Загружаю видео, подожди...")
        try:
            ydl_opts = {'outtmpl': 'video.mp4', 'format': 'best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove('video.mp4')
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {e}")
    else:
        bot.reply_to(message, "Это не ссылка.")

# 3. Запуск Flask в отдельном потоке и бота
def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()  # Запускаем "веб-сайт"
    bot.polling(none_stop=True) # Запускаем бота
