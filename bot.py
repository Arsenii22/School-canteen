import logging
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
import json

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    school = State() # Школа
    like = State() # Нравится еда или нет
    opinion = State() # Что больше понравилось / не понравилось
    rate = State() # Оценка по 10 балльной шкале

    
@dp.message_handler(commands="start")
async def start(msg: types.Message):
    await Form.school.set()

    await msg.answer_sticker(r"CAACAgIAAxkBAAEZdOdjXSEK1qpOmYrvcQoD3riSA_4zRgACXgYAAlOx9wNkYNhH9eEsgyoE")
    await msg.answer("Приветствуем вас в ультра-мега-супер-пупер-боте для отзывов на различные столовые в школах")
    await msg.answer("Не волнуйся, это анонимно :)")
    await msg.answer("Введите свою школу:")

@dp.message_handler(state=Form.school)
async def get_school(msg: types.Message, state: FSMContext):
    await msg.reply(f"Ваша школа: {msg.text}", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Да", callback_data="yes")).add(InlineKeyboardButton("Нет", callback_data="no")))

@dp.callback_query_handler(text="yes", state=Form.all_states)
@dp.callback_query_handler(text="no", state=Form.all_states)
async def answers(query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(query.id)

    if query.data == "yes" and query.message.text.startswith("Ваша школа:"):
        async with state.proxy() as data:
            data["school"] = query.message.text.replace("Ваша школа: ", "")
        await Form.next()

        await query.message.edit_reply_markup()
        await query.message.reply("Нравится ли вам еда в школьной столовой?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Да", callback_data="yes")).add(InlineKeyboardButton("Нет", callback_data="no")))

    elif query.data == "no" and query.message.text.startswith("Ваша школа:"):
        await query.message.edit_reply_markup()
        await query.message.edit_text("Введите свою школу:")

    elif query.data == "yes" and query.message.text == "Нравится ли вам еда в школьной столовой?":
        async with state.proxy() as data:
            data["like"] = True
        await Form.next()

        await query.message.edit_reply_markup()
        await query.message.reply("Что вам больше всего понравилось?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Свежая еда", callback_data="opinion_fresh")).add(InlineKeyboardButton("Очень вкусно", callback_data="opinion_vkusno")).add(InlineKeyboardButton("Очень очень вкусно", callback_data="opinion_very_vkusno")).add(InlineKeyboardButton("Очень очень очень вкусно", callback_data="opinion_very_very_vkusno")))

    elif query.data == "no" and query.message.text == "Нравится ли вам еда в школьной столовой?":
        async with state.proxy() as data:
            data["like"] = False
        await Form.next()

        await query.message.reply("Что вам больше всего не понравилось?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("НЕ Свежая еда", callback_data="opinion_not_fresh")).add(InlineKeyboardButton("НЕ Очень вкусно", callback_data="opinion_not_vkusno")).add(InlineKeyboardButton("НЕ Очень очень вкусно", callback_data="opinion_not_very_vkusno")).add(InlineKeyboardButton("НЕ Очень очень очень вкусно", callback_data="opinion_not_very_very_vkusno")))


@dp.callback_query_handler(lambda c: c.data.startswith("opinion_"), state=Form.all_states)
async def answers_continue(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["opinion"] = query.data
    await Form.next()

    await query.message.reply("Оцените качество еды по 10 балльной шкале", reply_markup=ReplyKeyboardMarkup().add(KeyboardButton("1️⃣")).add(KeyboardButton("2️⃣")).add(KeyboardButton("3️⃣")).add(KeyboardButton("4️⃣")).add(KeyboardButton("5️⃣")).add(KeyboardButton("6️⃣")).add(KeyboardButton("7️⃣")).add(KeyboardButton("8️⃣")).add(KeyboardButton("9️⃣")).add(KeyboardButton("🔟")))

@dp.message_handler(lambda t: t.text in "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟", state=Form.all_states)
async def get_rate(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["rate"] = {"1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5, "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "🔟": 10}[msg.text]

        await msg.reply(str(data))
        await msg.answer(reply_markup=ReplyKeyboardRemove())
    
    
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp)