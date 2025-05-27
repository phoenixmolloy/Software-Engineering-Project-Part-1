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

def get_question(exclude_ids=None):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    if exclude_ids:
        placeholders = ','.join('?' for _ in exclude_ids)
        query = f"SELECT id, question, a, b, c, d, correct_answer FROM quizzer WHERE id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT 1"
        cur.execute(query, exclude_ids)
    else:
        cur.execute("SELECT id, question, a, b, c, d, correct_answer FROM quizzer ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    con.close()
    if row:
        return {
            "id": row[0],
            "question": row[1],
            "a": row[2],
            "b": row[3],
            "c": row[4],
            "d": row[5],
            "correct_answer": row[6]
        }
    else:
        return None