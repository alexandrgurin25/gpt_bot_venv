import os
import sys
import openai
import sqlite3
import requests  # импортируем модуль requests для проверки доступа к Интернету
import time  # импортируем модуль time для добавления задержки
from datetime import datetime
from sqlite3 import Error

# Импортируем ключи доступа
from api_key import openai
from api_key import bot

messages = []


# Функция для проверки доступа к Интернету
def check_internet():
    url = 'http://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False


# Функция для ожидания доступа к Интернету и повторного подключения
def pause_and_retry():
    while True:
        time.sleep(10)  # ждем 10 секунд, прежде чем повторно попытаться подключиться
        if check_internet():
            try:
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except Exception:
                pass


# Запускаем функцию повторного подключения, если нет доступа к Интернету
if not check_internet():
    pause_and_retry()


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, f'Здравствуй, {m.from_user.first_name}!\nЯ - искусственный интеллект, созданный OpenAI. Я разработан для помощи людям в общении, работе и решении различных задач.\n Моя цель - помочь людям в их ежедневной жизни и сделать их более продуктивными и удобными.\nКак я могу помочь Вам, {m.from_user.first_name}?')

# Функция, обрабатывающая команду /help
@bot.message_handler(commands=["help"])
def help(m, res=False):
    bot.send_message(m.chat.id, 'Список команд:\n/start - Начать работу с ботом\n/help - Помощь\n/reload - Перезапустить бота')


# Функция, обрабатывающая команду /reload
@bot.message_handler(commands=["reload"])
def reload(m, res=False):
    bot.send_message(m.chat.id, "Перезапуск!")
    if(m.chat.id != 421486813): bot.send_message(421486813, f"{m.from_user.first_name}@{m.from_user.username}Вынужденный перезапуск!")
    os.execv(sys.executable, [sys.executable] + sys.argv)


# Функция, обрабатывающая стикеры
@bot.message_handler(content_types=["sticker"])
def handle_sticker(tg_message):
    bot.send_message(tg_message.chat.id, 'Красивый стикер! :)')


# Функция, обрабатывающая аудио, видео, голосовые сообщения
@bot.message_handler(content_types=["audio", "voice", "video"])
def handle_media(tg_message):
    bot.send_message(tg_message.chat.id, 'Я не могу обработать этот тип контента, но в скором времени меня научат!')


# Функция, обрабатывающая фото
@bot.message_handler(content_types=["photo"])
def handle_text(tg_message):
    bot.send_message(tg_message.chat.id, 'Я думаю, что на картинке что-то очень важное, но открывать специально не буду:)')

# Создаем соединение с базой данных SQLite
try:
    conn = sqlite3.connect('messages.db')
except Error as e:
    print(f"The error '{e}' occurred")


# Функция для создания таблицы в базе данных SQLite
def create_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      user_name TEXT,
                      user_first_name TEXT,
                      user_second_name TEXT,
                      content TEXT,
                      role TEXT,
                      timestamp TEXT)''')
    except Error as e:
        print(f"The error '{e}' occurred")


# Функция для сохранения сообщения в базе данных SQLite
def save_message(conn, user_id, user_name, user_first_name, user_second_name, content, role, timestamp):
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO messages (user_id, user_name, user_first_name, user_second_name, content, role, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (user_id, user_name, user_first_name, user_second_name, content, role, timestamp))
        conn.commit()
    except Error as e:
        print(f"The error '{e}' occurred")


# Создаем таблицу messages, если ее нет
create_table(conn)


# Получаем сообщения от пользователя
@bot.message_handler(content_types=["text"])
def handle_text(tg_message):
    try:
        conn = sqlite3.connect('messages.db')
    except Error as e:
        print(f"The error '{e}' occurred")
    try:
        user_id = tg_message.chat.id
        user_name = tg_message.from_user.username
        message = tg_message.text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_first_name = tg_message.from_user.first_name
        user_second_name = tg_message.from_user.last_name
        messages.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages = messages)
        reply = chat.choices[0].message.content
        bot.send_message(tg_message.chat.id, reply)
        messages.append({"role":"assistant", "content": reply})
        # сохраняем сообщение пользователя в базу данных
        save_message(conn, user_id, user_name, user_first_name, user_second_name, message, "user", timestamp)
        # сохраняем ответ бота в базу данных
        save_message(conn, user_id, "GPT CHAT", "БОТ", "", reply, "gpt-bot", timestamp) 
    except Exception as e:
        bot.send_message(421486813, f"@{user_name}-({user_id} - {user_first_name}) перезапуск ошибка->\n{e}")
        os.execv(sys.executable, [sys.executable] + sys.argv)


# Запускаем бота
while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception:
        bot.stop_polling()
        pause_and_retry()
