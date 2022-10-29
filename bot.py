import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    text = State()


@dp.message_handler(commands="start")
async def start(msg: types.Message):
    await Form.text.set()

    await msg.reply_sticker(r"CAACAgIAAxkBAAEZdOdjXSEK1qpOmYrvcQoD3riSA_4zRgACXgYAAlOx9wNkYNhH9eEsgyoE")
    await msg.reply("Приветствуем вас в ультра мега супер пупер боте для отзывов на различные столовые в школах. Введите вашу школу")


@dp.message_handler(state=Form.text)
async def get_school(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.reply(f"Ваша школа: {msg.text}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)