from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import DB

router = Router()


@router.message(F.text.lower() == "exercises")
async def cmd_exercises(message):
    btn_graph = InlineKeyboardButton(text="Graph", callback_data="weight.add_value")
    btn_abs = InlineKeyboardButton(text="Abs: Crunches", callback_data="weight.show_graph")
    btn_arms = InlineKeyboardButton(text="Arms: Push-up", callback_data="weight.add_value")
    btn_legs = InlineKeyboardButton(text="Legs: Squat", callback_data="weight.change_goal")

    builder = InlineKeyboardBuilder()
    builder.row(btn_graph)
    builder.row(btn_abs, btn_arms, btn_legs)

    await message.reply(
        "[exercises] Choose an option:",
        reply_markup=builder.as_markup(),
    )
# https://matplotlib.org/stable/gallery/statistics/histogram_multihist.html#sphx-glr-gallery-statistics-histogram-multihist-py
