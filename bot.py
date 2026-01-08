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
    bot.reply_to(message, "Я всё еще борюсь! Кидай ссылку. 🚀")

@bot.message_handler(func=lambda message: True)
def handle_media(message):
    url = message.text
    if "http" not in url: return

    sent_msg = bot.send_message(message.chat.id, "Пытаюсь обмануть систему... ⏳")
    
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
            'noplaylist': True,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'no_warnings': True,
            # ОЧЕНЬ ВАЖНО: Добавляем дополнительные параметры обхода
            'nocheckcertificate': True,
            'addheader': [
                'Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
            ],
            'extractor_args': {'tiktok': {'web_id': ['7318517321115403777']}}, # Фейковый ID для TikTok
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            all_files = [os.path.join('downloads', f) for f in os.listdir('downloads')]
            
            # Сначала ищем видео (приоритет)
            video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.mkv', '.webm', '.mov'))]
            
            if video_files:
                target = max(video_files, key=os.path.getsize)
                with open(target, 'rb') as video:
                    bot.send_video(message.chat.id, video, supports_streaming=True)
            else:
                # Если видео нет, ищем фото (слайд-шоу)
                photos = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                if photos:
                    media_group = [telebot.types.InputMediaPhoto(open(p, 'rb').read()) for p in sorted(photos)[:10]]
                    bot.send_media_group(message.chat.id, media_group)
                else:
                    bot.reply_to(message, "TikTok отдал пустой ответ. 😔 Скорее всего, сервер заблокирован.")

        for file in os.listdir('downloads'): os.remove(os.path.join('downloads', file))

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Ошибка. TikTok защищается сильнее, чем мы думали. ❌")
    finally:
        try: bot.delete_message(message.chat.id, sent_msg.message_id)
        except: pass

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
