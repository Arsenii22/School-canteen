import sqlite3
from bot import data

database = sqlite3.connect("db.db")
c = database.cursor()
c.execute("""CREATE TABLE db (
            School text,
            Like integer,
            Dislike integer,
            Opinion text,
            Rating real,
            Rating_json json
            )""")

for i in range(1, 178):
    c.execute(f"INSERT INTO db VALUES [{data.school}, {data.like}, {data.opinion}, {data.rate}]")