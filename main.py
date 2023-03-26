import os
import sys
import telebot
import openai
import sqlite3
from sqlite3 import Error
from datetime import datetime

# Иппорт ключей
from api_key import openai
from api_key import bot

# создаем соединение с базой данных SQLite
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

def get_last_message(conn):
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM messages ORDER BY id DESC LIMIT 1''')
        row = c.fetchone()
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "user_name": row[2],
                "user_first_name": row[3],
                "user_second_name": row[4],
                "content": row[5],
                "role": row[6],
                "timestamp": row[7]
            }
        else:
            return None
    except Error as e:
        print(f"The error '{e}' occurred")

# Функция для получения истории сообщений из базы данных SQLite
def get_message_history(conn):
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM messages''')
        rows = c.fetchall()
        return rows
    except Error as e:
        print(f"The error '{e}' occurred")

# Создаем таблицу messages, если ее нет
create_table(conn)

messages = []

# Функция, обрабатывающая команду /reload
@bot.message_handler(commands=["reload"])
def reload(m, res=False):
    bot.send_message(m.chat.id, "Вынужденный перезапуск!")
    if(m.chat.id != 421486813): bot.send_message(421486813, f"{m.from_user.first_name} (@{m.from_user.username} диалог-{m.chat.id}) отработана команда /reload!")
    os.execv(sys.executable, [sys.executable] + sys.argv)
    
# Функция, обрабатывающая фото
@bot.message_handler(content_types=["photo"])
def handle_text(tg_message):
    bot.send_message(tg_message.chat.id, 'Я думаю, что на картинке что-то очень важное, но открывать специально не буду:)')

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, f'Здравствуй, {m.from_user.first_name}!\n\
Я - искусственный интеллект, созданный OpenAI и @alexan_25. Я разработан для помощи людям в общении, работе и решении различных задач.\
 Моя цель - помочь людям в их ежедневной жизни и сделать их более продуктивными и удобными.\n\
Как я могу помочь Вам, {m.from_user.first_name}?')

last_message = None

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(tg_message):
    global last_message
    
    # создаем соединение с базой данных SQLite
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
        save_message(conn, user_id, user_name, user_first_name, user_second_name, message, "user", timestamp) # сохраняем сообщение пользователя в базу данных
        messages = [{"role": "user", "content": message}]
        if last_message: messages.append({"role": "assistant", "content": last_message})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages = messages)
        reply = chat.choices[0].message.content
        bot.send_message(tg_message.chat.id, reply)
        last_message = reply
        save_message(conn, user_id, "GPT CHAT", "БОТ", "", reply, "gpt-bot", timestamp) # сохраняем ответ бота в базу данных
    except Exception as e:
        bot.send_message(421486813, f"@{user_name}({user_id} {user_first_name}) перезапуск ошибка->{e}")
        bot.send_message(user_id, "Извините за неудобства, произошла непредвиденная перезагрузка, которая прервала нашу связь. Пожалуйста, повторите ваше последнее сообщение еще раз, чтобы я мог продолжить нашу беседу. Благодарю за понимание!\n\nЕсли я перестал отвечать, напиши об этом моему создателю @alexan_25")
        os.execv(sys.executable, [sys.executable] + sys.argv)

# Запускаем бота
bot.polling(none_stop=True, interval=0)