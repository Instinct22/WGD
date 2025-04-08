import telebot
from telebot import types
from create_and_rename_wg_users_static import AddWgUser

class TelegramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Создать пользователя")
            btn2 = types.KeyboardButton("Показать ID")
            markup.add(btn1, btn2)
            self.bot.send_message(message.chat.id, "Выбери действия", reply_markup=markup)

        @self.bot.message_handler(content_types=['text'])
        def handle_text(message):
            if message.text == 'Создать пользователя':
                user_id = message.from_user.id

                add_user = AddWgUser(name_user=user_id)
                add_user.create_wg_users()
                add_user.parse_peer_name()
                result = add_user.reconfig_peer()
                self.bot.send_message(message.chat.id, "Пользователь успешно создан!")

            elif message.text == 'Показать ID':
                self.bot.send_message(message.chat.id, f"Ваш ID {message.from_user.id}")



    def run(self):
        self.bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    bot = TelegramBot('7625485527:AAGbFG0A9kuCB3wt6y8s_ONO7zthDJC1jEs')
    bot.run()