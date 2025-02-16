from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import ticker as mticker

from db.exercises import ExercisesDB


matplotlib.use('SVG')  # need for nonparallel plots


router = Router()


@router.message(F.text.lower() == "exercises")
async def cmd_exercises(message):
    btn_graph = InlineKeyboardButton(text="Graph", callback_data="exercises.get_graph")
    btn_abs = InlineKeyboardButton(text="Abs: Crunches", callback_data="exercises.abs")
    btn_arms = InlineKeyboardButton(text="Arms: Push-up", callback_data="exercises.arms")
    btn_legs = InlineKeyboardButton(text="Legs: Squat", callback_data="exercises.legs")

    builder = InlineKeyboardBuilder()
    builder.row(btn_graph)
    builder.row(btn_abs, btn_arms, btn_legs)

    await message.reply(
        "[exercises] Choose an option",
        reply_markup=builder.as_markup(),
    )


class ExercisesFSM(StatesGroup):
    st_abs = State()
    st_arms = State()
    st_legs = State()


@router.callback_query(F.data == "exercises.abs")
async def do_abs(callback, state):
    await callback.message.answer("[exercises] How many crunches did you do today?")
    await state.set_state(ExercisesFSM.st_abs)
    await callback.answer()


@router.message(ExercisesFSM.st_abs)
async def do_abs_processor(message, state):
    value = message.text
    try:
        value = int(value)
    except ValueError:
        await message.reply("[exercises] Invalid value. Try again using numbers.")
        return
    if value <= 0:
        await message.reply("[exercises] Invalid value. Try again using positive number.")
        return

    today = datetime.now()
    day = today.strftime("%j")
    year = today.strftime("%Y")

    db = ExercisesDB()
    db.upsert_abs(message.from_user.id, value, day, year)

    await message.reply("[exercises] Nice abs bro!")
    await state.clear()


@router.callback_query(F.data == "exercises.arms")
async def do_arms(callback, state):
    await callback.message.answer("[exercises] How many push-ups did you do today?")
    await state.set_state(ExercisesFSM.st_arms)
    await callback.answer()


@router.message(ExercisesFSM.st_arms)
async def do_arms_processor(message, state):
    value = message.text
    try:
        value = int(value)
    except ValueError:
        await message.reply("[exercises] Invalid value. Try again using positive numbers.")
        return
    if value <= 0:
        await message.reply("[exercises] Invalid value. Try again using positive number.")
        return

    today = datetime.now()
    day = today.strftime("%j")
    year = today.strftime("%Y")

    db = ExercisesDB()
    db.upsert_arms(message.from_user.id, value, day, year)

    await message.reply("[exercises] Nice arms bro!")
    await state.clear()


@router.callback_query(F.data == "exercises.legs")
async def do_legs(callback, state):
    await callback.message.answer("[exercises] How many squat did you do today?")
    await state.set_state(ExercisesFSM.st_legs)
    await callback.answer()


@router.message(ExercisesFSM.st_legs)
async def do_legs_processor(message, state):
    value = message.text
    try:
        value = int(value)
    except ValueError:
        await message.reply("[exercises] Invalid value. Try again using positive numbers.")
        return
    if value <= 0:
        await message.reply("[exercises] Invalid value. Try again using positive number.")
        return

    today = datetime.now()
    day = today.strftime("%j")
    year = today.strftime("%Y")

    db = ExercisesDB()
    db.upsert_legs(message.from_user.id, value, day, year)

    await message.reply("[exercises] Nice legs bro!")
    await state.clear()


@router.callback_query(F.data == "exercises.get_graph")
async def show_graph(callback):
    prepare_graph(callback.from_user.id)

    await callback.message.answer_photo(FSInputFile("graph_exercises.png"))
    await callback.answer()

def prepare_graph(uid):
    db = ExercisesDB()
    year = datetime.now().strftime("%Y")

    result = {"abs": {}, "arms": {}, "legs": {}}

    # last 7 days by limit
    # TODO: error with empty values
    for day, reps in db.get_abs(uid, year):
        result["abs"][day] = reps
    for day, reps in db.get_arms(uid, year):
        result["arms"][day] = reps
    for day, reps in db.get_legs(uid, year):
        result["legs"][day] = reps

    draw_graph(result)

# TODO: move to hist? o_O
def draw_graph(exercises_data):
    for type, data in exercises_data.items():
        plt.plot(data.keys(), data.values(), label=type)

    plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
    plt.xlabel("day")
    plt.ylabel("reps")

    plt.title("Exercises progress graph")
    plt.legend()
    plt.grid(which="major")

    plt.savefig("graph_exercises.png")
    plt.close(plt.gcf())
