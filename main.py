import matplotlib
import telebot

from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib import ticker as mticker
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
        btn = types.KeyboardButton("Weight Challenge")
        markup.add(btn)
        return markup

    def start(self, message):
        self.bot.send_message(message.from_user.id, "Welcome back!", reply_markup=self.create_menu_markup())

    def text(self, message):
        if message.text == 'Weight Challenge':
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="Add Weight", callback_data="add_weight")
            btn2 = types.InlineKeyboardButton(text="Add Goal", callback_data="add_goal")
            btn3 = types.InlineKeyboardButton(text="Show Graph", callback_data="show_weight_graph")
            markup.add(btn1, btn2, btn3)
            self.bot.send_message(message.from_user.id, "Choose an option", reply_markup=markup)

    def callback(self, call):
        if call.data == "add_weight":
            msg = self.bot.send_message(
                call.from_user.id, "[Weight] Please input numeric value",
                reply_markup=types.ForceReply()
            )
            self.bot.register_next_step_handler(msg, self._add_weight)
        elif call.data == "add_goal":
            msg = self.bot.send_message(
                call.from_user.id, "[Goal] Please input numeric value",
                reply_markup=types.ForceReply()
            )
            self.bot.register_next_step_handler(msg, self._add_weight_goal)
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

        year, week, _ = datetime.now().isocalendar()

        self.db.upsert_weight(message.from_user.id, weight, week, year)

        self.bot.send_message(
            message.from_user.id, "Weight has been added successfully",
            reply_markup=self.create_menu_markup()
        )

    def _add_weight_goal(self, message):
        goal = message.text
        try:
            goal = float(goal)
        except Exception as e:
            self.bot.send_message(
                message.from_user.id, "Incorrect value, try again",
                reply_markup=self.create_menu_markup()
            )
            return

        year, week, _ = datetime.now().isocalendar()

        self.db.upsert_weight_goal(message.from_user.id, goal, year)

        self.bot.send_message(
            message.from_user.id, "Goal has been added successfully",
            reply_markup=self.create_menu_markup()
        )

    def _prepare_graph(self):
        year, max_week, _ = datetime.now().isocalendar()
        weights = self.db.get_weights_all(year)
        goals = self.db.get_weight_goals_all(year)

        w8_storage = {}
        # fill weights map
        for uid, w8, week, _ in weights:
            if uid not in w8_storage:
                w8_storage[uid] = {}
            if week <= max_week:
                w8_storage[uid][week] = w8

        # эта цикличная конструкция нужна, чтобы дозаполнять пустые значения на основе предыдущих показаний
        for w8_data in w8_storage.values():
            # берем заранее, чтобы покрыть кейс списка без значений в начале
            default_w8 = list(w8_data.values())[0]  # dict_values doesn't support indexing -_-
            # заранее известно точное количество недель от первой до текущей включительно
            for i in range(1, max_week + 1):
                if w8_data.get(i):
                    # значение есть в списке, значит можно обновить дефолтное
                    default_w8 = w8_data[i]
                else:
                    # значения в списке нет, значит берем дефолтное для него
                    w8_data[i] = default_w8
        # ^ код олимпиадника, лол. Выглядит легко, нечитаемо, но работает как надо. Поэтому гора комментов -_-

        result = {uid: {} for uid in w8_storage.keys()}
        for uid, w8_data in w8_storage.items():
            start = list(w8_data.values())[0]

            goal = None
            for goal_uid, weight_goal in goals:
                if goal_uid == uid:
                    goal = weight_goal

            for i in w8_data:
                prcnt = (start - w8_data[i]) / (start - goal) * 100
                result[uid][i] = float("{:.2f}".format(prcnt))

        self._draw_graph(result)

    def _draw_graph(self, weights_data):
        for uid, data in weights_data.items():
            plt.plot(data.keys(), data.values(), label=uid)

        plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
        plt.xlabel('week, pcs')
        plt.ylabel('weight, prcnt')
        plt.title('Weight\'s change graph')
        plt.legend()
        plt.savefig("w8_graph.png")
        plt.close(plt.gcf())


if __name__ == '__main__':
    app = TgBot()
    app.bot.infinity_polling()
