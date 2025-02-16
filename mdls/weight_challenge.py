from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import ticker as mticker

from db import DB

matplotlib.use('SVG')  # need for nonparallel plots

router = Router()


@router.message(F.text.lower() == "weight")
async def cmd(message):
    btn_weight = InlineKeyboardButton(text="Weight", callback_data="weight.upsert_value")
    btn_goal = InlineKeyboardButton(text="Goal", callback_data="weight.upsert_goal")
    btn_graph = InlineKeyboardButton(text="Graph", callback_data="weight.get_graph")
    builder = InlineKeyboardBuilder()
    builder.row(btn_graph)
    builder.row(btn_weight, btn_goal)

    await message.reply(
        "[weight] Choose an option",
        reply_markup=builder.as_markup(),
    )


class WeightFSM(StatesGroup):
    adding_value = State()
    changing_goal = State()


@router.callback_query(F.data == "weight.upsert_value")
async def add_value(callback, state):
    await callback.message.answer("[weight] How much do you weigh this week?")
    await state.set_state(WeightFSM.adding_value)
    await callback.answer()


@router.message(WeightFSM.adding_value)
async def add_value_processor(message, state):
    value = message.text
    try:
        value = float(value)
    except ValueError:
        await message.reply("[weight] Invalid value. Try again using numbers.")
        return
    if value <= 0:
        await message.reply("[weight] Invalid value. Try again using positive number.")
        return

    year, week, _ = datetime.now().isocalendar()

    db = DB()
    db.upsert_weight(message.from_user.id, value, week, year)

    await message.reply("[weight] Your weekly weight has been added successfully.")
    await state.clear()


@router.callback_query(F.data == "weight.upsert_goal")
async def change_goal(callback, state):
    await callback.message.answer("[weight] How much do you want to weigh?")
    await state.set_state(WeightFSM.changing_goal)
    await callback.answer()


@router.message(WeightFSM.changing_goal)
async def change_goal_processor(message, state):
    goal = message.text
    try:
        goal = float(goal)
    except ValueError:
        await message.reply("[weight] Invalid value. Try again using numbers.")
        return
    if goal <= 0:
        await message.reply("[weight] Invalid value. Try again using positive number.")
        return

    year, week, _ = datetime.now().isocalendar()

    db = DB()
    db.upsert_weight_goal(message.from_user.id, goal, year)

    await message.reply("[weight] Your goal has been changed successfully.")
    await state.clear()


@router.callback_query(F.data == "weight.get_graph")
async def show_graph(callback):
    prepare_graph()
    await callback.message.answer_photo(FSInputFile("w8_graph.png"))
    await callback.answer()


def prepare_graph():
    db = DB()

    year, max_week, _ = datetime.now().isocalendar()
    weights = db.get_weights_all(year)
    goals = db.get_weight_goals_all(year)

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

    draw_graph(result)


def draw_graph(weights_data):
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
