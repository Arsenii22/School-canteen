import logging
from re import I
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from openpyxl import Workbook 
import matplotlib.pyplot as plt
import sqlite3
import config

database = sqlite3.connect("db.db")
cur = database.cursor()

bot = Bot(token=config.TOKEN_ADMIN)
dp = Dispatcher(bot)

async def get_school_name_by_id(school_id: int):
    cur.execute(f"SELECT name FROM schools WHERE ID={school_id}")
    return cur.fetchall()[0][0]
    
@dp.message_handler(commands="start")
async def start(msg: types.Message):
    await msg.answer("Приветствуем вас.", reply_markup=ReplyKeyboardRemove())
    await msg.answer("Что вы хотите просмотреть?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Топ по школам", callback_data="moderator_top")).add(InlineKeyboardButton("Самые популярные проблемы", callback_data="moderator_top_problems")).add(InlineKeyboardButton("Таблицу с данными по школам", callback_data="moderator_schools_reviews")).add(InlineKeyboardButton("Таблицу со всеми отзывами", callback_data="moderator_all_reviews")))

@dp.callback_query_handler(lambda c: c.data.startswith("moderator_"))
async def moderator(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id)

    if query.data == "moderator_top":
        fig, ax = plt.subplots()
        vals, labels = [], []

        cur.execute(f"SELECT school_id, ROUND(AVG(rate), 2) FROM comments GROUP BY school_id ORDER BY AVG(rate) DESC")
        top_schools = cur.fetchall()
        text = "Топ по школам Калининград:\n"

        for i in range(5):
            text += f"{i + 1}. {await get_school_name_by_id(top_schools[i][0])} ({top_schools[i][1]})\n"
        
        for i in top_schools:
            labels.append(await get_school_name_by_id(i[0]))
            vals.append(i[1])
        
        ax.pie(vals, labels=labels)
        ax.axis("equal")

        plt.savefig("plt.png")
        
        m = await query.message.reply(text)
        await m.reply_photo(types.InputFile("plt.png"))

    elif query.data == "moderator_top_problems":
        fig, ax = plt.subplots()
        vals, labels = [], []

        cur.execute(f"SELECT opinion_bad, COUNT(opinion_bad) FROM comments GROUP BY opinion_bad ORDER BY COUNT(opinion_bad) DESC LIMIT 5;")
        top_problems = cur.fetchall()
        text = "Самые популярные проблемы:\n"

        for i in range(3):
            text += f"{i + 1}. {config.OPINIONS[top_problems[i][0]]} ({top_problems[i][1]})\n"
        
        for i in top_problems:
            labels.append(config.OPINIONS[i[0]])
            vals.append(i[1])

        ax.pie(vals, labels=labels)
        ax.axis("equal")

        plt.savefig("plt.png")
        
        m = await query.message.reply(text)
        await m.reply_photo(types.InputFile("plt.png"))
    
    elif query.data == "moderator_schools_reviews":
        wb = Workbook()
        table = wb.active

        table.append(["Школа", "Сотношение нравиться/не нравиться", "Самые популярные плюсы", "Самые популярные минусы", "Средняя оценка"])

        cur.execute(f"SELECT * FROM schools")

        for i in cur.fetchall():
            cur.execute(f"SELECT ROUND(AVG(like), 2), ROUND(AVG(rate), 2) FROM comments WHERE school_id={i[0]};")
            data = cur.fetchall()[0]

            if None in data:
                table.append([i[1], f"Нет данных", f"Нет данных", f"Нет данных", f"Нет данных"])
            else:
                cur.execute(f"SELECT opinion_bad FROM comments WHERE school_id={i[0]} GROUP BY opinion_bad HAVING COUNT(opinion_bad)=(SELECT COUNT(opinion_bad) FROM comments WHERE school_id={i[0]} GROUP BY opinion_bad ORDER BY COUNT(opinion_bad) DESC LIMIT 1)")
                data_opinion_bad = [config.OPINIONS[i[0]] for i in cur.fetchall()]
                cur.execute(f"SELECT opinion_good FROM comments WHERE school_id={i[0]} GROUP BY opinion_good HAVING COUNT(opinion_good)=(SELECT COUNT(opinion_good) FROM comments WHERE school_id={i[0]} GROUP BY opinion_good ORDER BY COUNT(opinion_good) DESC LIMIT 1)")
                data_opinion_good = [config.OPINIONS[i[0]] for i in cur.fetchall()]
                
                table.append([i[1], f"{data[0] * 100}%", ", ".join(data_opinion_bad), ", ".join(data_opinion_good), f"{data[1]}"])

        wb.save(f"Таблица.xlsx")

        await query.message.reply_document(document=types.InputFile("Таблица.xlsx"))
    
    elif query.data == "moderator_all_reviews":
        wb = Workbook()
        table = wb.active

        table.append(["Школа", "Нравиться/не нравиться", "Плюсы", "Минусы", "Оценка", "Метка времени"])

        cur.execute(f"SELECT school_id, like, opinion_good, opinion_bad, rate, timestamp FROM comments")

        for i in cur.fetchall():
            table.append([await get_school_name_by_id(i[0]), bool(i[1]), config.OPINIONS[i[2]], config.OPINIONS[i[3]], i[4], i[5]])

        wb.save(f"Таблица.xlsx")

        await query.message.reply_document(document=types.InputFile("Таблица.xlsx"))
    
    await query.message.answer("Что вы хотите просмотреть?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Топ по школам", callback_data="moderator_top")).add(InlineKeyboardButton("Самые популярные проблемы", callback_data="moderator_top_problems")).add(InlineKeyboardButton("Таблицу с данными по школам", callback_data="moderator_schools_reviews")).add(InlineKeyboardButton("Таблицу со всеми отзывами", callback_data="moderator_all_reviews")))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)