from datetime import datetime

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import ticker as mticker
from telebot import types

from .bot_module import BotModule
from db import DB

matplotlib.use('SVG')  # need for nonparallel plots


class WeightChallenge(BotModule):
    def __init__(self, bot):
        super(WeightChallenge, self).__init__("Weight", bot)
        self.db = DB()
        self.callbacks = {
            "weight.add_value": {"text": "Add value", "callback": self.cb_add_value},
            "weight.change_goal": {"text": "Change Goal", "callback": self.cb_change_goal},
            "weight.show_graph": {"text": "Show Graph", "callback": self.cb_show_graph},
        }

    def cb_add_value(self, call):
        msg = self.bot.send_message(
            call.from_user.id, "[{}] Please enter your current weight".format(self.title),
            reply_markup=types.ForceReply()
        )
        self.bot.register_next_step_handler(msg, self._add_weight)

    def _add_weight(self, message):
        weight = message.text
        try:
            weight = float(weight)
        except Exception as e:
            self.bot.send_message(
                message.from_user.id, "[{}] Incorrect value, try again".format(self.title),
                reply_markup=self.menu_markup
            )
            return

        year, week, _ = datetime.now().isocalendar()

        self.db.upsert_weight(message.from_user.id, weight, week, year)

        self.bot.send_message(
            message.from_user.id, "[{}] Weekly value has been added successfully".format(self.title),
            reply_markup=self.menu_markup
        )

    def cb_change_goal(self, call):
        msg = self.bot.send_message(
            call.from_user.id, "[{}] Please enter new goal".format(self.title),
            reply_markup=types.ForceReply()
        )
        self.bot.register_next_step_handler(msg, self._add_weight_goal)

    def _add_weight_goal(self, message):
        goal = message.text
        try:
            goal = float(goal)
        except Exception as e:
            self.bot.send_message(
                message.from_user.id, "[{}] Incorrect value, try again".format(self.title),
                reply_markup=self.menu_markup
            )
            return

        year, week, _ = datetime.now().isocalendar()

        self.db.upsert_weight_goal(message.from_user.id, goal, year)

        self.bot.send_message(
            message.from_user.id, "[{}] Goal has been changed successfully".format(self.title),
            reply_markup=self.menu_markup
        )

    def cb_show_graph(self, call):
        self._prepare_graph()
        with open("w8_graph.png", "rb") as image:
            self.bot.send_photo(
                call.from_user.id, image, reply_markup=self.menu_markup
            )
            self.bot.answer_callback_query(call.id)

    def _prepare_graph(self):
        year, max_week, _ = datetime.now().isocalendar()
        weights = self.db.get_weights_all(year)
        goals = self.db.get_weight_goals_all(year)

        w8_storage = {}
        # fill weights map
        for uid, w8, week, _ in weights:
            if uid not in w8_storage:
                w8_storage[uid] = {i: None for i in range(1, max_week + 1)}
            if week <= max_week:
                w8_storage[uid][week] = w8

        # эта цикличная конструкция нужна, чтобы дозаполнять пустые значения на основе предыдущих показаний
        for w8_data in w8_storage.values():
            # первый вес считаем дефолтным, чтобы покрыть кейс списка без значений в начале
            default_w8 = 0
            for dw in w8_data.values():
                if dw and dw > default_w8:
                    default_w8 = dw
                    break
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
        plt.xlabel("week, pcs")
        plt.ylabel("weight, prcnt")

        new_xticks = []
        locs, _ = plt.xticks()
        for i in range(len(locs) - 3, 0, - len(locs) // 5):
            new_xticks.append(locs[i])
        new_xticks.reverse()
        plt.xticks(new_xticks)

        plt.title("Weight's change graph")
        plt.legend()
        plt.grid(which="major")

        plt.savefig("w8_graph.png")
        plt.close(plt.gcf())
