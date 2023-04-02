import telebot
from telebot import types

from db import DB


def check_auth(message):
    if message.from_user.id not in [70391314, 299193958]:  # to config
        return False
    return True


class TgBot:
    def __init__(self):
        with open('tg_token') as f:
            token = f.readline()
        self.bot = telebot.TeleBot(token)
        self.db = DB()

        @self.bot.message_handler(commands=['start'], func=check_auth)
        def _start(message):
            self.start(message)

        @self.bot.message_handler(content_types=['text'], func=check_auth)
        def _text(message):
            self.text(message)

        @self.bot.callback_query_handler(func=check_auth)
        def _callback(call):
            self.callback(call)

    def create_menu_markup(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Weight Challenge")
        markup.add(btn1)
        return markup

    def start(self, message):
        self.bot.send_message(message.from_user.id, "Welcome back!", reply_markup=self.create_menu_markup())

    def text(self, message):
        if message.text == 'Weight Challenge':
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="Add Weight", callback_data="add_weight")
            # btn2 = types.InlineKeyboardButton(text="Show Graph")
            markup.add(btn1)
            self.bot.send_message(message.from_user.id, "Choose an option", reply_markup=markup)
        elif message.text == "Add Weight":
            msg = self.bot.send_message(
                message.from_user.id, "Please input numeric value",
                reply_markup=types.ForceReply()
            )
            self.bot.register_next_step_handler(msg, self._add_weight)

    def callback(self, call):
        if call.data == "add_weight":
            msg = self.bot.send_message(
                call.from_user.id, "Please input numeric value",
                reply_markup=types.ForceReply()
            )
            self.bot.register_next_step_handler(msg, self._add_weight)

    def _add_weight(self, message):
        weight = message.text
        try:
            weight = float(weight)
        except Exception as e:
            self.bot.send_message(
                message.from_user.id, "Incorrect value, try again",
                reply_markup=self.create_menu_markup()
            )
            return

        self.db.add_weight(message.from_user.id, weight)

        self.bot.send_message(
            message.from_user.id, "Weight has been added successfully",
            reply_markup=self.create_menu_markup()
        )


if __name__ == '__main__':
    app = TgBot()
    app.bot.polling(none_stop=True, interval=0)
