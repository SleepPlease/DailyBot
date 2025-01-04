from datetime import datetime

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import ticker as mticker
from telebot import types

from .bot_utils import BotModule, Callback
from db import DB

matplotlib.use('SVG')  # need for nonparallel plots


class WeightChallenge(BotModule):
    def __init__(self, bot):
        super(WeightChallenge, self).__init__("Weight", bot)
        self.db = DB()
        self.callbacks = [
            Callback(self.title, "add_value", "Add value", self.cb_add_value),
            Callback(self.title, "change_goal", "Change Goal", self.cb_change_goal),
            Callback(self.title, "show_graph", "Show Graph", self.cb_show_graph),
        ]

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
        plt.xlabel("week, pcs")
        plt.ylabel("weight, prcnt")

        new_xticks = []
        locs, _ = plt.xticks()
        for i in range(len(locs) - 3, 0, - len(locs) // 5):
            new_xticks.append(locs[i])
        new_xticks.reverse()

        print(new_xticks)
        plt.xticks(new_xticks)

        plt.title("Weight's change graph")
        plt.legend()
        plt.grid(which="major")

        plt.savefig("w8_graph.png")
        plt.close(plt.gcf())




from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# Эти значения далее будут подставляться в итоговый текст, отсюда
# такая на первый взгляд странная форма прилагательных
available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


@router.message(Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(OrderFood.choosing_food_name)

# Этап выбора блюда #


@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите размер порции:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)


# В целом, никто не мешает указывать стейты полностью строками
# Это может пригодиться, если по какой-то причине
# ваши названия стейтов генерируются в рантайме (но зачем?)
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=make_row_keyboard(available_food_names)
    )

# Этап выбора размера порции и отображение сводной информации #


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
             f"Попробуйте теперь заказать напитки: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого размера порции.\n\n"
             "Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )