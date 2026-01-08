import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Бот работает!"
def run(): app.run(host='0.0.0.0', port=8080)

token = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Я готов! Присылай ссылки на YouTube, TikTok (видео/фото) или Instagram.")

@bot.message_handler(func=lambda message: True)
def handle_media(message):
    url = message.text
    if "http" not in url: return

    sent_msg = bot.send_message(message.chat.id, "Начинаю загрузку... ⏳")
    
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            # Ограничиваем до 720p и MP4, чтобы файл не превысил 50МБ и открывался везде
            'format': 'best[height<=720][ext=mp4]/bestvideo[height<=720]+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
            'cookiefile': 'cookies.txt', 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Пытаемся извлечь информацию и скачать
            info = ydl.extract_info(url, download=True)
            
            # Проверяем папку на наличие файлов (картинки или видео)
            all_files = [os.path.join('downloads', f) for f in os.listdir('downloads')]
            
            # 1. Проверка на TikTok ФОТО (слайд-шоу)
            photos = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if photos:
                media_group = []
                for p in sorted(photos)[:10]: # Максимум 10 фото за раз
                    with open(p, 'rb') as f:
                        media_group.append(telebot.types.InputMediaPhoto(f.read()))
                bot.send_media_group(message.chat.id, media_group)
            
            # 2. Проверка на ВИДЕО (YouTube, Shorts, Reels, TikTok видео)
            else:
                video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.mkv', '.webm', '.mov'))]
                if video_files:
                    # Берем самый большой файл из скачанных (обычно это и есть видео после склейки)
                    target_video = max(video_files, key=os.path.getsize)
                    with open(target_video, 'rb') as video:
                        bot.send_video(message.chat.id, video, supports_streaming=True)
                else:
                    bot.reply_to(message, "Не удалось найти файл видео. Возможно, он слишком тяжелый.")

        # Очистка папки downloads
        for file in os.listdir('downloads'):
            os.remove(os.path.join('downloads', file))

    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Ошибка при скачивании. Проверь, не закрыт ли аккаунт (для Instagram) и не удалено ли видео.")
    finally:
        try: bot.delete_message(message.chat.id, sent_msg.message_id)
        except: pass

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
