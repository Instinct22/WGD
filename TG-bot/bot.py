import os
import telebot
from telebot import types
from create_and_rename_wg_users_static import AddWgUser
from dotenv import load_dotenv

load_dotenv()

class TelegramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.register_handlers()

    """Главное меню"""
    def show_main_menu(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Создать конфигурацию VPN")
        btn2 = types.KeyboardButton("Восстановить конфигурацию (В разработке)")
        markup.add(btn1)
        markup.add(btn2)
        self.bot.send_message(chat_id, "Выбери действие:", reply_markup=markup)

    """Создать конфигурацию"""
    def create_user(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Создать конфигурацию для ПК")
        btn2 = types.KeyboardButton("Создать конфигурацию для Мобильника")
        # btn3 = types.KeyboardButton("Создать конфигурацию для ПК и Мобильника")
        btn4 = types.KeyboardButton("Главное меню")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn4)
        self.bot.send_message(chat_id, "Какую конфигурацию вы желаете создать:", reply_markup=markup)

    """Потерял конфигурацию"""
    def lost_configuration(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Да")
        btn2 = types.KeyboardButton("Нет")
        markup.add(btn1, btn2)
        self.bot.send_message(chat_id, "Восстановить конфигурацию?", reply_markup=markup)

    def configuration_selection(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Конфигурация на ПК")
        btn2 = types.KeyboardButton("Конфигурация на Мобильный")
        markup.add(btn1, btn2)
        self.bot.send_message(chat_id, "Какую конфигурацию желаете восстановить?", reply_markup=markup)

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.show_main_menu(message.chat.id)

        @self.bot.message_handler(content_types=['text'])
        def handle_text(message):

            """Необходимо переработать функцию 'Создать конфигурацию для ПК' и 'Создать конфигурацию для Мобильника'. Так, чтоб проверка была в условии,а не на стороне выполнения функции check_client_configuration"""

            if message.text == 'Создать конфигурацию для ПК':
                user_id = message.from_user.id
                add_user = AddWgUser(name_user=user_id)

                if not add_user.check_client_configuration():
                    self.bot.send_message(message.chat.id, "⚠️ У вас уже есть конфигурация!")
                    return

                add_user.create_wg_users()
                add_user.parse_peer_name()
                add_user.reconfig_peer()

                config_file = add_user.download_peer_config()

                if config_file:
                    with open(config_file, 'rb') as file:
                        self.bot.send_document(
                            chat_id=message.chat.id,
                            document=file,
                            caption="Ваша конфигурация WireGuard 🚀"
                        )
                else:
                    self.bot.send_message(message.chat.id, "❌ Ошибка при создании конфигурации!")



            elif message.text == 'Создать конфигурацию для Мобильника':
                user_id = message.from_user.id
                add_user = AddWgUser(name_user=f'{user_id}_mobile')

                if not add_user.check_client_configuration():
                    self.bot.send_message(message.chat.id, "⚠️ У вас уже есть конфигурация!")
                    return

                add_user.create_wg_users()
                add_user.parse_peer_name()
                add_user.reconfig_peer()

                config_file = add_user.download_peer_config()

                if config_file:
                    with open(config_file, 'rb') as file:
                        self.bot.send_document(
                            chat_id=message.chat.id,
                            document=file,
                            caption="Ваша конфигурация WireGuard 🚀"
                        )
                else:
                    self.bot.send_message(message.chat.id, "❌ Ошибка при создании конфигурации!")



            elif message.text == 'Конфигурация на ПК' or message.text == 'Конфигурация на Мобильный':
                user_id = message.from_user.id
                self.show_main_menu(message.chat.id)





            elif message.text == 'Да':
                self.configuration_selection(message.chat.id)

            elif message.text == 'Создать конфигурацию VPN':
                self.create_user(message.chat.id)

            elif message.text == 'Главное меню' or message.text == 'Нет':
                self.show_main_menu(message.chat.id)

            elif message.text == 'Восстановить конфигурацию':
                self.lost_configuration(message.chat.id)







    def run(self):
        self.bot.polling(none_stop=True, interval=1, skip_pending=True)

if __name__ == "__main__":
    bot = TelegramBot(os.getenv("TELEGRAM_BOT_TOKEN"))
    bot.run()