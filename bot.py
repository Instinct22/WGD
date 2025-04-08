import telebot
from telebot import types


from create_and_rename_wg_users_static import AddWgUser





bot = telebot.TeleBot('7625485527:AAGbFG0A9kuCB3wt6y8s_ONO7zthDJC1jEs')

@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Создать пользователя")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Выбери действия", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'Создать пользователя':
        # Получаем ID пользователя и преобразуем его в строку
        user_id = str(message.from_user.id)
        
        # Создаем экземпляр класса с ID пользователя в качестве имени
        add_user = AddWgUser(name_user=user_id)
        add_user.create_wg_users()
        add_user.parse_peer_name()
        result = add_user.reconfig_peer()
        bot.send_message(message.from_user.id, f"Пользователь {user_id} успешно создан!")


bot.polling(none_stop=True, interval=0) 