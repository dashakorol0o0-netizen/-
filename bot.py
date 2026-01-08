import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

# 1. Настройка Flask
app = Flask('')
@app.route('/')
def home(): return "Бот-комбайн работает!"
def run(): app.run(host='0.0.0.0', port=8080)

# 2. Настройка Бота
token = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    photo_url = 'https://vot-enot.com/wp-content/uploads/2022/09/image-8.png.webp'
    caption_text = "Привет! Теперь я качаю всё: TikTok (видео и фото), Instagram (Reels и Stories) и YouTube! 🚀"
    try:
        bot.send_photo(message.chat.id, photo_url, caption=caption_text)
    except Exception:
        bot.send_message(message.chat.id, caption_text)

@bot.message_handler(func=lambda message: True)
def handle_media(message):
    url = message.text
    if "http" not in url:
        bot.reply_to(message, "Пришли ссылку на видео или фото.")
        return

    sent_msg = bot.send_message(message.chat.id, "Обрабатываю медиа, подожди... ⏳")
    
    try:
        # Папка для временных файлов
        if not os.path.exists('downloads'): os.makedirs('downloads')

        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Принудительно MP4
            'quiet': True,
            'noplaylist': True,
            # 'cookiefile': 'cookies.txt',  # Раскомментируй эту строку, когда добавишь файл cookies.txt на GitHub!
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Если это TikTok фото (слайд-шоу)
            if 'entries' in info or info.get('_type') == 'playlist':
                media_group = []
                for entry in info.get('entries', []):
                    file_path = ydl.prepare_filename(entry)
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            media_group.append(telebot.types.InputMediaPhoto(f.read()))
                if media_group:
                    bot.send_media_group(message.chat.id, media_group[:10]) # Лимит 10 фото
            
            # Если это обычное видео (YouTube, Reels, TikTok видео)
            else:
                file_path = ydl.prepare_filename(info)
                # Иногда расширение может измениться после склейки
                if not os.path.exists(file_path):
                    file_path = file_path.rsplit('.', 1)[0] + ".mp4"
                
                with open(file_path, 'rb') as video:
                    bot.send_video(message.chat.id, video)

        # Очистка папки
        for file in os.listdir('downloads'):
            os.remove(os.path.join('downloads', file))

    except Exception as e:
        bot.reply_to(message, "Не удалось скачать. ❌ Возможно, это приватная сторис или YouTube требует авторизации.")
    finally:
        bot.delete_message(message.chat.id, sent_msg.message_id)

# 3. Запуск
def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
