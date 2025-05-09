import telebot
from telebot import types
import requests
import openai
import json

# ВСТАВЬ СВОИ ТОКЕНЫ СЮДА
TELEGRAM_BOT_TOKEN = '7753608741:AAGuR4R7wwwPKLgViJ-_nwnBLVk-FJ4r7KQ'
OPENAI_API_KEY = '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'
WEATHER_API_KEY = 'd7e728fd470cf320b445cd02e20d135f'
YOUTUBE_API_KEY = 'AIzaSyB3b6v9KDVlzjZNK63hcWfXcREULQ9e1n0'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# Внутреннее хранилище расписаний для каждого пользователя
user_schedules = {}

# Команды бота (для /help и подсказок)
COMMANDS = {
    'start': 'Начать работу с ботом',
    'help': 'Показать список команд',
    'weather': 'Узнать погоду в городе',
    'ask': 'Задать вопрос ChatGPT',
    'schedule_add': 'Добавить событие в расписание',
    'schedule_view': 'Посмотреть расписание',
    'youtube': 'Поиск видео на YouTube'
}

# При старте
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/weather", "/ask", "/schedule_add", "/schedule_view", "/youtube", "/help"]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "👋 Привет! Я умный бот. Вот что я умею:", reply_markup=markup)
    send_help(message)

# Помощь
@bot.message_handler(commands=['help'])
def send_help(message):
    text = "📋 Доступные команды:\n\n"
    for cmd, desc in COMMANDS.items():
        text += f"/{cmd} — {desc}\n"
    bot.send_message(message.chat.id, text)

# Погода
@bot.message_handler(commands=['weather'])
def weather(message):
    msg = bot.send_message(message.chat.id, "🌍 Введи название города для прогноза погоды:")
    bot.register_next_step_handler(msg, get_weather)

def get_weather(message):
    city = message.text
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_text = f"🌦 Погода в {city}:\nТемпература: {data['main']['temp']}°C\n" \
                       f"Ощущается как: {data['main']['feels_like']}°C\n" \
                       f"Описание: {data['weather'][0]['description']}"
        bot.send_message(message.chat.id, weather_text)
    else:
        bot.send_message(message.chat.id, "❌ Не удалось найти город. Попробуй ещё раз.")

# ChatGPT
@bot.message_handler(commands=['ask'])
def ask(message):
    msg = bot.send_message(message.chat.id, "💬 Введи вопрос для ChatGPT:")
    bot.register_next_step_handler(msg, gpt_answer)

def gpt_answer(message):
    question = message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Или gpt-4o если есть доступ
            messages=[{"role": "user", "content": question}],
            max_tokens=500
        )
        answer = response.choices[0].message['content'].strip()
        bot.send_message(message.chat.id, f"🤖 Ответ:\n{answer}")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Произошла ошибка при обращении к ChatGPT.")

# Добавление события в расписание
@bot.message_handler(commands=['schedule_add'])
def schedule_add(message):
    msg = bot.send_message(message.chat.id, "🗓 Введи событие (например: Понедельник 14:00 — Математика):")
    bot.register_next_step_handler(msg, save_schedule)

def save_schedule(message):
    user_id = message.chat.id
    event = message.text
    if user_id not in user_schedules:
        user_schedules[user_id] = []
    user_schedules[user_id].append(event)
    bot.send_message(message.chat.id, "✅ Событие добавлено в расписание!")

# Просмотр расписания
@bot.message_handler(commands=['schedule_view'])
def schedule_view(message):
    user_id = message.chat.id
    if user_id in user_schedules and user_schedules[user_id]:
        text = "🗓 Твоё расписание:\n\n"
        text += "\n".join(user_schedules[user_id])
    else:
        text = "📭 У тебя пока нет событий в расписании."
    bot.send_message(message.chat.id, text)

# Поиск видео на YouTube
@bot.message_handler(commands=['youtube'])
def youtube(message):
    msg = bot.send_message(message.chat.id, "🔎 Введи запрос для поиска на YouTube:")
    bot.register_next_step_handler(msg, search_youtube)

def search_youtube(message):
    query = message.text
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=3&q={query}&key={YOUTUBE_API_KEY}&type=video"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        videos = data.get('items', [])
        if not videos:
            bot.send_message(message.chat.id, "❌ Видео не найдено.")
            return
        text = "📹 Вот что нашлось на YouTube:\n\n"
        for video in videos:
            title = video['snippet']['title']
            video_id = video['id']['videoId']
            link = f"https://youtu.be/{video_id}"
            text += f"{title}\n{link}\n\n"
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "❌ Не удалось выполнить поиск.")

# Запуск бота
print('Бот запущен')
bot.infinity_polling()



