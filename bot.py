import logging
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from fuzzywuzzy import process
import datetime
import sqlite3
import config

database = sqlite3.connect("db.db")
cur = database.cursor()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    school = State() # Школа
    like = State() # Нравится еда или нет
    opinion_good = State() # Что больше понравилось / не понравилось
    opinion_bad = State()
    rate = State() # Оценка по 10 балльной шкале

    
@dp.message_handler(commands="start")
async def start(msg: types.Message):
    if msg.from_user.id in config.MODERATORS_IDS:
        await msg.answer("Приветствуем вас в ультра-мега-супер-пупер-боте для отзывов на различные столовые в школах")
        await msg.answer("Что вы хотите просмотреть?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Топ по школам", callback_data="moderator_top")).add(InlineKeyboardButton("Самые популярные проблемы", callback_data="moderator_top_problems")).add(InlineKeyboardButton("Таблицу с данными по школам", callback_data="moderator_schools_reviews")).add(InlineKeyboardButton("Таблицу со всеми отзывами", callback_data="moderator_all_reviews")))
    else:
        await Form.school.set()

        await msg.answer_sticker(r"CAACAgIAAxkBAAEZdOdjXSEK1qpOmYrvcQoD3riSA_4zRgACXgYAAlOx9wNkYNhH9eEsgyoE")
        await msg.answer("Приветствуем вас в ультра-мега-супер-пупер-боте для отзывов на различные столовые в школах")
        await msg.answer("Не волнуйся, это анонимно :)")
        await msg.answer("Введите свою школу:")

@dp.callback_query_handler(lambda c: c.startswith("moderator_"))
async def moderator(query: types.CallbackQuery):
    pass

@dp.message_handler(state=Form.school)
async def get_school(msg: types.Message, state: FSMContext):
    cur.execute(f"SELECT name FROM schools")
    best_school = process.extractOne(msg.text, sum(cur.fetchall(), ()))

    if best_school[1] != 0:
        await msg.reply(f"Ваша школа: {best_school[0]}?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Да", callback_data="yes")).add(InlineKeyboardButton("Нет", callback_data="no")))
    else:
        await msg.reply(f"Мы не смогли найти вашу школу, попробуйте ещё раз :(")

@dp.callback_query_handler(state=Form.all_states)
async def answers(query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(query.id)

    if query.data == "yes" and query.message.text.startswith("Ваша школа:"): # КОСТЫЛЬ ПИЗДЕЦ
        async with state.proxy() as data:
            data["school"] = query.message.text.replace("Ваша школа: ", "").replace("?", "")
        await Form.next()

        await query.message.edit_reply_markup()
        await query.message.reply("Нравится ли вам еда в школьной столовой?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Да", callback_data="yes")).add(InlineKeyboardButton("Нет", callback_data="no")))

    elif query.data == "no" and query.message.text.startswith("Ваша школа:"): # КОСТЫЛЬ ПИЗДЕЦ
        await query.message.edit_reply_markup()
        await query.message.edit_text("Введите свою школу:")

    elif query.data == "yes" and query.message.text == "Нравится ли вам еда в школьной столовой?": # КОСТЫЛЬ ПИЗДЕЦ
        async with state.proxy() as data:
            data["like"] = True
        await Form.next()

        await query.message.edit_reply_markup()
        await query.message.reply("Что вам больше всего понравилось?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Свежая еда", callback_data="opinion_fresh")).add(InlineKeyboardButton("вкусная еда", callback_data="opinion_vkusno")).add(InlineKeyboardButton("аппетитно", callback_data="opinion_appetitno")).add(InlineKeyboardButton("сытно вкусно", callback_data="opinion_very_very_vkusno")))

    elif (query.data == "no" and query.message.text == "Нравится ли вам еда в школьной столовой?") or (query.data.startswith("opinion_") and query.message.text == "Что вам больше всего понравилось?"): # КОСТЫЛЬ ПИЗДЕЦ
        async with state.proxy() as data:
            data["opinion_good"] = ""
            if query.data.startswith("opinion_"):
                data["opinion_good"] = query.data
            else:
                data["like"] = False
                await Form.next()
        await Form.next()
        
        await query.message.edit_reply_markup()
        await query.message.reply("Что вам больше всего не понравилось?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("НЕ Свежая еда", callback_data="opinion_not_fresh")).add(InlineKeyboardButton("НЕ Очень вкусно", callback_data="opinion_not_vkusno")).add(InlineKeyboardButton("НЕ Очень очень вкусно", callback_data="opinion_not_very_vkusno")).add(InlineKeyboardButton("НЕ Очень очень очень вкусно", callback_data="opinion_not_very_very_vkusno")))
    elif query.data.startswith("opinion_"): # КОСТЫЛЬ ПИЗДЕЦ
        async with state.proxy() as data:
            data["opinion_bad"] = query.data
        await Form.next()

        await query.message.edit_reply_markup()
        await query.message.reply("Оцените качество еды по 10 балльной шкале", reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton("1️⃣", callback_data="1"), InlineKeyboardButton("2️⃣", callback_data="2")).row(InlineKeyboardButton("3️⃣", callback_data="3"), InlineKeyboardButton("4️⃣", callback_data="4")).row(InlineKeyboardButton("5️⃣", callback_data="5"), InlineKeyboardButton("6️⃣", callback_data="6")).row(InlineKeyboardButton("7️⃣", callback_data="7"), InlineKeyboardButton("8️⃣", callback_data="8")).row(InlineKeyboardButton("9️⃣", callback_data="9"), InlineKeyboardButton("🔟", callback_data="10")))
    elif query.data in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]: # ... у меня нет слов
        async with state.proxy() as data:
            data["rate"] = int(query.data)

            cur.execute(f"SELECT ID FROM schools WHERE name='{data['school']}'")
            cur.execute(f"INSERT INTO comments(school_id, like, opinion_good, opinion_bad, rate, timestamp) VALUES('{cur.fetchall()[0][0]}', {data['like']}, '{data['opinion_good']}', '{data['opinion_bad']}', {data['rate']}, '{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}')")
            database.commit()
        
        await query.message.edit_reply_markup()
        await query.message.reply("Спасибо за прохождение опроса, он обязательно поможет улучшить питание в твоей школьной столовой")

        await state.finish()
    else:
        await state.finish()

        await query.message.reply("Извините, что-то пошло не так, попробуйте перезапустить бота")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)