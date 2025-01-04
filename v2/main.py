import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from handlers import weight_challenge

main_router = Router()
# https://mastergroosha.github.io/aiogram-3-guide/buttons/


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
    await message.answer("Welcome back!", reply_markup=keyboard)


async def main():
    logging.basicConfig(level=logging.INFO)
    with open('../tg_token') as f:
        token = f.readline().split()[0]  # fix this shit -_- ubuntu for fuck's sake have one more symbol at the end
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_routers(
        weight_challenge.router,
        main_router,
    )

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
