import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

# 1. Настройка Flask для Render (чтобы сервис не засыпал)
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
    photo_url = 'https://vot-enot.com/wp-content/uploads/2022/09/image-8.png.webp'
    caption_text = "Привет! Пришли ссылку на Tik Tok или Instagram Reels, и я его скачаю. 🚀"
    try:
        bot.send_photo(message.chat.id, photo_url, caption=caption_text)
    except Exception:
        bot.send_message(message.chat.id, caption_text)

@bot.message_handler(func=lambda message: True)
def handle_video(message):
    url = message.text
    if "http" in url:
        # Проверка на YouTube (чтобы не выдавать системную ошибку)
        if "youtube.com" in url or "youtu.be" in url:
            bot.reply_to(message, "Я пока не рассчитан на YouTube и Instagram stories из-за ограничений. 😔 Пришли ссылку из TikTok или Instagram reels!")
            return

        sent_msg = bot.send_message(message.chat.id, "Пробую скачать, секунду...")
        try:
            ydl_opts = {
                'outtmpl': 'video.mp4',
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            os.remove('video.mp4')
            bot.delete_message(message.chat.id, sent_msg.message_id)
            
        except Exception:
            # Вежливый отказ без кода ошибки
            bot.reply_to(message, "Не могу выдать это видео. ❌ Скорее всего, профиль закрыт или я не поддерживаю этот формат.")
    else:
        bot.reply_to(message, "Пришли мне ссылку на видео.")

# 3. Запуск Flask в потоке и бота
def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive() 
    bot.polling(none_stop=True)
