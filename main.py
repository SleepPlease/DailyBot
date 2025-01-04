import telebot
from telebot import types

from mdls import Exercises, WeightChallenge


def check_auth(message):
    if message.from_user.id not in [70391314, 299193958]:  # to config
        return False
    return True


class TgBot:
    def __init__(self):
        with open('tg_token') as f:
            token = f.readline().split()[0]  # fix this shit -_- ubuntu for fuck's sake have one more symbol at the end
        self.bot = telebot.TeleBot(token)

        self.callbacks = {}
        self.modules = []
        self.modules.append(WeightChallenge(self.bot))
        self.modules.append(Exercises(self.bot))

        mm = self.create_menu_markup()
        for module in self.modules:
            module.add_menu_markup(mm)
            for callback in module.callbacks:
                self.callbacks[callback.name] = callback

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
        for module in self.modules:
            btn = types.KeyboardButton(module.title)
            markup.add(btn)
        return markup

    def start(self, message):
        self.bot.send_message(message.from_user.id, "Welcome back!", reply_markup=self.create_menu_markup())

    def text(self, message):
        for module in self.modules:
            if module.title == message.text:
                markup = types.InlineKeyboardMarkup()
                for callback in module.callbacks.values():
                    btn = types.InlineKeyboardButton(text=callback.text, callback_data=callback.name)
                    markup.add(btn)
                self.bot.send_message(message.from_user.id, "[{}] Choose an option".format(module.title), reply_markup=markup)

    def callback(self, call):
        if handler := self.callbacks.get(call.data):
            handler.func(call)


if __name__ == '__main__':
    app = TgBot()
    app.bot.infinity_polling()
