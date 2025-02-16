import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from mdls import weight_challenge, exercises

# https://mastergroosha.github.io/aiogram-3-guide/buttons/
# https://stackoverflow.com/questions/69846020/how-to-wait-for-user-reply-in-aiogram
# https://matplotlib.org/stable/gallery/statistics/histogram_multihist.html#sphx-glr-gallery-statistics-histogram-multihist-py


main_router = Router()
access_router = Router()
ACL = [70391314, 299193958]


@access_router.message(lambda message: message.from_user.id not in ACL)
async def ignore_forbidden_users(message):
    return


@main_router.message(CommandStart)
@main_router.message(F.text == "..")
async def cmd_start(message):
    kb = [
        [KeyboardButton(text="Weight")],
        [KeyboardButton(text="Exercises")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.reply("Welcome back!", reply_markup=keyboard)

async def main():
    logging.basicConfig(level=logging.INFO)
    with open('tg_token') as f:
        token = f.readline().split()[0]  # fix this shit -_- ubuntu for fuck's sake have one more symbol at the end
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_routers(
        access_router,
        weight_challenge.router,
        exercises.router,
        main_router,
    )

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
