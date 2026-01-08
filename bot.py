import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Бот в строю!"
def run(): app.run(host='0.0.0.0', port=8080)

token = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Я проснулся! Кидай ссылку (TikTok, YT, Instagram). 🚀")

@bot.message_handler(func=lambda message: True)
def handle_media(message):
    url = message.text
    if "http" not in url: return

    sent_msg = bot.send_message(message.chat.id, "Разбираюсь с контентом... ⏳")
    
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
            'noplaylist': True,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем инфу
            info = ydl.extract_info(url, download=True)
            
            # Собираем файлы
            all_files = [os.path.join('downloads', f) for f in os.listdir('downloads')]
            
            # Ищем КАРТИНКИ (TikTok фото)
            photos = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            
            if photos:
                # Отправляем фото альбомом
                media_group = [telebot.types.InputMediaPhoto(open(p, 'rb').read()) for p in sorted(photos)[:10]]
                bot.send_media_group(message.chat.id, media_group)
            else:
                # Ищем ВИДЕО
                video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.mkv', '.webm', '.mov'))]
                if video_files:
                    target = max(video_files, key=os.path.getsize)
                    with open(target, 'rb') as video:
                        bot.send_video(message.chat.id, video, supports_streaming=True)
                else:
                    bot.reply_to(message, "Не нашел файл для отправки. 😔")

        # Чистим за собой
        for file in os.listdir('downloads'):
            os.remove(os.path.join('downloads', file))

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Не вышло. ❌ Попробуй еще раз или проверь ссылку.")
    finally:
        try: bot.delete_message(message.chat.id, sent_msg.message_id)
        except: pass

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
