import os
import telebot
import yt_dlp

# Railway сам подставит сюда токен из настроек
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Кидай ссылку на TikTok/Reels/Shorts, и я скачаю видео.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        msg = bot.send_message(message.chat.id, "Обрабатываю ссылку... ⏳")
        
        # Настройки для скачивания без водяного знака
        ydl_opts = {
            'outtmpl': 'video.mp4',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            os.remove('video.mp4') # Чистим место за собой
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"Ошибка: {e}", message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, "Это не похоже на ссылку.")

bot.polling(none_stop=True)
