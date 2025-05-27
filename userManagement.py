import sqlite3 as sql
import bcrypt
import random


### example
def getUsers():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM id7-tusers")
    con.close()
    return cur

def get_question():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT question, a, b, c, d, correct_answer FROM quizzer ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    con.close()
    if row:
        return {
            "question": row[0],
            "a": row[1],
            "b": row[2],
            "c": row[3],
            "d": row[4],
            "correct_answer": row[5]  # e.g., "a", "b", "c", or "d"
        }
    else:
        return None