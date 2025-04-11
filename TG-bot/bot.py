import os
import telebot
from telebot import types
from create_and_rename_wg_users_static import AddWgUser
from dotenv import load_dotenv


load_dotenv()

class TelegramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        # ID канала, на который должен быть подписан пользователь
        self.channel_id = os.getenv("CHANNEL_ID")
        self.register_handlers()

        self.channel_info = self.bot.get_chat(self.channel_id)
        self.channel_name = self.channel_info.title
        self.channel_link = []

        self.photo_files = []
        self.image_path = []
        self.media = []
        self.file_handles = []
        self.caption = []

    """ Приветствие"""
    def greeting(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("👋 Поздороваться")
        markup.add(btn1)
        self.bot.send_message(chat_id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)

    """Главное меню"""
    def show_main_menu(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Создать конфигурацию VPN")
        btn2 = types.KeyboardButton("Восстановить конфигурацию (В разработке)")
        btn3 = types.KeyboardButton("Инструкции")
        btn4 = types.KeyboardButton("Техподдержка")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        markup.add(btn4)
    
        self.bot.send_message(chat_id, "Выбери действие:", reply_markup=markup)

    """Создать конфигурацию"""
    def create_user(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Создать конфигурацию для ПК")
        btn2 = types.KeyboardButton("Создать конфигурацию для телефона")
        # btn3 = types.KeyboardButton("Создать конфигурацию для ПК и телефона")
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

    """Потерял конфигурацию"""
    def configuration_selection(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Конфигурация на ПК")
        btn2 = types.KeyboardButton("Конфигурация на телефон")
        markup.add(btn1, btn2)
        self.bot.send_message(chat_id, "Какую конфигурацию желаете восстановить?", reply_markup=markup)

    """ Выбор инструкции"""
    def select_configuration(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Инструкция для PC")
        btn2 = types.KeyboardButton("Инструкция для телефона")
        btn3 = types.KeyboardButton("Главное меню")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        self.bot.send_message(chat_id, "Каким телефоном вы пользуетесь?", reply_markup=markup)


    """ Выбор инструкции для телефона"""
    def select_mobile_configuration(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Инструкция для IPhone")
        btn2 = types.KeyboardButton("Инструкция для Android")
        btn3 = types.KeyboardButton("Главное меню")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        self.bot.send_message(chat_id, "Каким телефоном вы пользуетесь?", reply_markup=markup)


    """Проверка подписки на канал"""
    def check_subscription(self, user_id):
        try:
            # Получаем информацию о подписке пользователя
            member_info = self.bot.get_chat_member(self.channel_id, user_id)
            # Проверяем статус подписки
            if member_info.status in ['member', 'administrator', 'creator']:
                return True
            return False
        except Exception as e:
            print(f"Ошибка при проверке подписки: {e}")
            return False

    """Отправка сообщения о необходимости подписки"""
    def show_subscription_message(self, chat_id):
        markup = types.InlineKeyboardMarkup()
        self.channel_link = self.channel_info.invite_link

        btn = types.InlineKeyboardButton(text=f"Подписаться на {self.channel_name}", url=self.channel_link)
        markup.add(btn)
        
        btn_check = types.InlineKeyboardButton(text="Я подписался ✅", callback_data="check_subscription")
        markup.add(btn_check)
        
        self.bot.send_message(
            chat_id,
            f"⚠️ Для доступа к функционалу бота необходимо подписаться на канал {self.channel_name}.",
            reply_markup=markup
        )

    def show_support_chat(self, chat_id):
        self.channel_link = self.channel_info.invite_link
        link = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Чат тех-поддержки", url=self.channel_link)
        link.add(btn)
        self.bot.send_message(chat_id, "Нажмите кнопку ниже, чтобы перейти в чат техподдержки:", reply_markup=link)

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.greeting(message.chat.id)
            
        @self.bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
        def callback_check(call):
            # Проверяем, подписался ли пользователь
            if self.check_subscription(call.from_user.id):
                self.bot.answer_callback_query(call.id, "Спасибо за подписку! Теперь вы можете пользоваться ботом.")
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
                self.show_main_menu(call.message.chat.id)
            else:
                self.bot.answer_callback_query(call.id, "Вы все еще не подписаны на канал.", show_alert=True)

        @self.bot.message_handler(content_types=['text'])
        def handle_text(message):
            if message.text == '👋 Поздороваться':
                # После приветствия проверяем подписку на канал
                if self.check_subscription(message.from_user.id):
                    self.show_main_menu(message.chat.id)
                else:
                    self.show_subscription_message(message.chat.id)
                return

            # Для остальных команд проверяем подписку
            if not self.check_subscription(message.from_user.id):
                self.show_subscription_message(message.chat.id)
                return

            if message.text in ["Инструкция для IPhone", "Инструкция для Android", "Инструкция для PC"]:
                if message.text == "Инструкция для IPhone":
                    self.photo_files = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png']
                    self.image_path = 'image/IPhone'
                    self.caption = """ Инструкция для IPhone📱:

- Устанавливаем WireGuard с AppStore ☑️
- Возвращаемся в Бота и скачиваем конфигурацию в удобное место 🎇
- Нажимаем "Добавить туннель" 🔧
- Нажимаем на "Создать из файла или архива" 🪽
- Откроется окно выбора, смело выберем нужную конфигурацию.🛸
- Отлично. Настройка завершена! теперь можешь нажать кнопку "Подключить" напротив своей конфигурации🛜
- Вы прекрасны!🍾"""

                    self.import_image(message)

                elif message.text == "Инструкция для Android":
                    self.photo_files = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png']
                    self.image_path = 'image/Android'
                    self.caption = """ Инструкция для Android📱:

- Устанавливаем WireGuard с GooglePlay ☑️
- Возвращаемся в Бота и скачиваем конфигурацию в удобное место 🎇
- Нажимаем на кнопку внизу экрана🔧
- Выбираем последнюю скачанную конфигурацию из списка файлов🪽
- Откроется окно подтверждения создания соединения, смело жмем "ОК".🛸
- Отлично. Настройка завершена! теперь можешь нажать кнопку "Подключить" напротив своей конфигурации🛜
- Вы прекрасны!🍾"""


                    self.import_image(message)
                    self.bot.send_message(message.chat.id,
""" ВАЖНО❗❗❗ Если видите ошибку "Невозможно импортировать туннель":
- Переименуйте файл, удалив "_Mob" в названии
- Если не получается - обратитесь в поддержку""")

                elif message.text == "Инструкция для PC":
                    self.photo_files = ['1.png', '2.png', '3.png', '4.png', '5.png']
                    self.image_path = 'image/PC'
                    self.caption = """ Инструкция для ПК🖥:

- Качаем WireGuard с официального сайта или можете скачать на прямую по ⇒ [ССЫЛКЕ](https://download.wireguard.com/windows-client/wireguard-installer.exe) ⇐
- Устанавливаем 🫡
- Запускаем💡
- Изначально в нём нет ни каких конфигураций.🧶
- Проверяем что скачали только что созданную конфигурацию со своим ID 🫵
- Нажимаем на "Импорт туннелей" или "Добавить туннель", кнопки выполняют одну функцию, так что выберем любую 🪽
- Откроется окно выбора, смело выберем нужную конфигурацию.🎇
- Отлично. Настройка завершена! теперь можешь нажать кнопку "Подключить"🛜
- Вы прекрасны!🍾"""

                    self.import_image(message)

                    return




            if message.text == 'Создать конфигурацию для ПК' or message.text == 'Создать конфигурацию для телефона':

                if message.text == 'Создать конфигурацию для ПК':
                    user_id = message.from_user.id
                else:
                    user_id = f"{message.from_user.id}_Mob"
                add_user = AddWgUser(name_user=user_id)

                if str(user_id) in add_user.check_client_configuration():
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
                        
                    try:
                        os.remove(config_file)
                    except Exception as e:
                        print(f"Ошибка при удалении файла {config_file}: {e}")

                    try:
                        if message.text == 'Создать конфигурацию для ПК':
                            self.photo_files = ['1.png', '2.png', '3.png', '4.png', '5.png']
                            self.image_path = 'image/PC'
                            self.caption = """ Инструкция для ПК🖥:

- Качаем WireGuard с официального сайта или можете скачать на прямую по ⇒ [ССЫЛКЕ](https://download.wireguard.com/windows-client/wireguard-installer.exe) ⇐
- Устанавливаем 🫡
- Запускаем💡
- Изначально в нём нет ни каких конфигураций.🧶
- Проверяем что скачали только что созданную конфигурацию со своим ID 🫵
- Нажимаем на "Импорт туннелей" или "Добавить туннель", кнопки выполняют одну функцию, так что выберем любую 🪽
- Откроется окно выбора, смело выберем нужную конфигурацию.🎇
- Отлично. Настройка завершена! теперь можешь нажать кнопку "Подключить"🛜
- Вы прекрасны!🍾"""

                            self.import_image(message)

                        elif message.text == 'Создать конфигурацию для телефона':
                            self.select_mobile_configuration(message.chat.id)

                    except Exception as photo_error:
                        print(f"Ошибка при отправке фото: {photo_error}")
                        self.bot.send_message(
                            chat_id=message.chat.id,
                            text=f"⚠️ Не удалось отправить инструкцию, но конфигурация создана успешно. Напишите об этой проблеме в чат группы: {self.channel_link}"

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

            elif message.text == 'Инструкции':
                self.select_configuration(message.chat.id)

            elif message.text == 'Инструкция для телефона':
                self.select_mobile_configuration(message.chat.id)

            elif message.text == 'Техподдержка':
                self.show_support_chat(message.chat.id)


    # Функция доставки Инструкции (Альбом изоображений + текст инструкции)
    def import_image(self, message):
        self.media = []
        self.file_handles = []

        try:
            for i, file_name in enumerate(self.photo_files):
                photo_path = os.path.join(self.image_path, file_name)
                try:
                    file = open(photo_path, 'rb')
                    self.file_handles.append(file)
                    if i == 0:
                        self.media.append(types.InputMediaPhoto(
                            media=file,
                            caption=self.caption,
                            parse_mode="Markdown"
                        ))
                    else:
                        self.media.append(types.InputMediaPhoto(file))

                except FileNotFoundError:
                    print(f"Файл {photo_path} не найден")
                    continue

            if self.media:
                self.bot.send_media_group(
                    chat_id=message.chat.id,
                    media=self.media
                )

            else:
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text="Не удалось загрузить изображения инструкции"
                )

        except Exception as e:
            print(f"Ошибка при отправке медиагруппы: {e}")
            self.bot.send_message(
                chat_id=message.chat.id,
                text="⚠️ Произошла ошибка при отправке инструкции"
            )

        finally:
            for file in self.file_handles:
                try:
                    file.close()
                except:
                    pass

    def run(self):
        self.bot.polling(none_stop=True, interval=1, skip_pending=True)

if __name__ == "__main__":
    bot = TelegramBot(os.getenv("TELEGRAM_BOT_TOKEN"))
    bot.run()