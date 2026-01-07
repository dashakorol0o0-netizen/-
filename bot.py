import os
import telebot

# Бот должен брать токен из настроек Render, а не просто цифры
token = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Пришли ссылку на видео (TikTok/Reels), и я скачаю его.")

@bot.message_handler(func=lambda message: True)
def handle_video(message):
    url = message.text
    if "http" in url:
        sent_msg = bot.send_message(message.chat.id, "Загружаю видео, подожди...")
        try:
            ydl_opts = {
                'outtmpl': 'video.mp4',
                'format': 'best',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            os.remove('video.mp4')
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {e}")
    else:
        bot.reply_to(message, "Это не ссылка.")

bot.polling(none_stop=True)
