import os
import sys
import telebot
import openai


# указываем ключ из личного кабинета openai
openai.api_key = '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'
messages = []

# Создаем экземпляр бота
bot = telebot.TeleBot('6007451380:AAEjLTNJCUOeeAHLYP93CcfP-6l6EVOC-OI')

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Я на связи. Напиши мне что-нибудь )')

@bot.message_handler(content_types=["photo"])
def handle_text(tg_message):
    bot.send_message(tg_message.chat.id, 'Я думаю, что на картинке что-то очень важное, но открывать специально не буду:)')

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(tg_message):
    try:
        user_id = tg_message.chat.id
        user_name = tg_message.from_user.username
        message = tg_message.text
        messages.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages = messages)
        reply = chat.choices[0].message.content
        bot.send_message(tg_message.chat.id, reply)
        messages.append({"role":"assistant", "content": reply})
        #print(f'@{user_name}({user_id})->'+message)
        #print('Bot->'+reply)
    except Exception as e:
        bot.send_message(421486813, f"@{user_name}({user_id}) перезапуск ошибка->{e}")
        bot.send_message(tg_message.chat.id, "Извините, мой пул сообщений был переполнен, повторите свое последнее сообщение.\nЕсли я перестал отвечать, напиши об этом моему создателю @alexan_25")
        #print(e)
        # при возникновении исключения запускаем программу заново
        os.execv(sys.executable, [sys.executable] + sys.argv)

# Запускаем бота
bot.polling(none_stop=True, interval=0)