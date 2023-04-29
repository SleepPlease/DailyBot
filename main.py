import matplotlib
import telebot
from datetime import datetime
from matplotlib import pyplot as plt
from telebot import types

from db import DB

matplotlib.use('SVG')  # need for nonparallel plots


def check_auth(message):
    if message.from_user.id not in [70391314, 299193958]:  # to config
        return False
    return True


class TgBot:
    def __init__(self):
        with open('tg_token') as f:
            token = f.readline().split()[0]  # fix this shit -_- ubuntu for fuck's sake have one more symbol at the end
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
            btn2 = types.InlineKeyboardButton(text="Show Graph", callback_data="show_weight_graph")
            markup.add(btn1, btn2)
            self.bot.send_message(message.from_user.id, "Choose an option", reply_markup=markup)

    def callback(self, call):
        if call.data == "add_weight":
            msg = self.bot.send_message(
                call.from_user.id, "Please input numeric value",
                reply_markup=types.ForceReply()
            )
            self.bot.register_next_step_handler(msg, self._add_weight)
        elif call.data == "show_weight_graph":
            self._prepare_graph()
            with open("w8_graph.png", "rb") as image:
                self.bot.send_photo(
                    call.from_user.id, image, reply_markup=self.create_menu_markup()
                )
                self.bot.answer_callback_query(call.id)

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

    def _prepare_graph(self):
        result = self.db.get_weights_all()

        weights = {}
        for uid, w, dt in result:
            _dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            if _dt not in weights:
                weights[_dt] = {}
            weights[_dt][uid] = w

        w8_storage = {}
        # эта цикличная конструкция нужна, чтобы дозаполнять пустые значения на основе предыдущих показаний
        for cur_w8s in weights.values():
            # добавляем во временное хранилище данные за каждую дату:
            # - значение есть в хранилище - заменяем новым
            # - значения в хранилище нет - добавляем
            # - значение есть в хранилище, но его нет в текущей дате - оставляем без изменений
            for k, v in cur_w8s.items():
                w8_storage[k] = v
            # актуализируем имеющиеся данные исходя из того, что сложили в хранилище
            for k, v in w8_storage.items():
                if k not in cur_w8s:
                    cur_w8s[k] = v
            # ^ код олимпиадника, лол. Выглядит легко, нечитаемо, но работает как надо. Поэтому гора комментов -_-
        self._draw_graph(weights)

    def _draw_graph(self, weights_data):
        dates = []
        w8s_by_id = {}
        for dt, data in weights_data.items():
            dates.append(dt)
            for uid, weight in data.items():
                if uid not in w8s_by_id:
                    w8s_by_id[uid] = []
                w8s_by_id[uid].append(weight)

        for uid, weights in w8s_by_id.items():
            plt.plot(dates, weights, label=uid)

        plt.xlabel('date')
        plt.ylabel('weight')
        plt.title('Weight graph')
        plt.legend()
        plt.savefig("w8_graph.png")
        plt.close(plt.gcf())


if __name__ == '__main__':
    app = TgBot()
    app.bot.infinity_polling()
