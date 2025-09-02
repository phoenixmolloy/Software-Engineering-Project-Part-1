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
        query = f"""SELECT question_id, question, a, b, c, d, correct_answer, core, topic
                    FROM questions
                    WHERE question_id NOT IN ({placeholders})
                    ORDER BY RANDOM() LIMIT 1"""
        cur.execute(query, exclude_ids)
    else:
        cur.execute("""SELECT question_id, question, a, b, c, d, correct_answer, core, topic
                       FROM questions
                       ORDER BY RANDOM() LIMIT 1""")
    row = cur.fetchone()
    con.close()
    if row:
        return {
            "question_id": row[0],
            "question": row[1],
            "a": row[2],
            "b": row[3],
            "c": row[4],
            "d": row[5],
            "correct_answer": row[6],
            "core": row[7],
            "topic": row[8]
        }
    else:
        return None


def record_quiz_answer(quiz_id, question_id, mark, core, topic, selected_answer, correct_answer):
    conn = sql.connect("databaseFiles/database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Quizzes (quiz_id, question_id, mark, core, topic, selected_answer, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (quiz_id, question_id, mark, core, topic, selected_answer, correct_answer)
    )
    conn.commit()
    conn.close()

def get_next_quiz_id():
    conn = sql.connect("databaseFiles/database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(quiz_id) FROM Quizzes")
    result = cursor.fetchone()
    conn.close()
    return (result[0] or 0) + 1

def get_quiz_summaries():
    conn = sql.connect("databaseFiles/database.db")
    cursor = conn.cursor()
    # Get all quiz_ids
    cursor.execute("SELECT DISTINCT quiz_id FROM Quizzes ORDER BY quiz_id DESC")
    quiz_ids = [row[0] for row in cursor.fetchall()]
    quizzes = []
    for quiz_id in quiz_ids:
        # Get weakest topic for this quiz
        cursor.execute("""
            SELECT topic, COUNT(*) as incorrect
            FROM Quizzes
            WHERE quiz_id = ? AND mark = 0
            GROUP BY topic
            ORDER BY incorrect DESC
            LIMIT 1
        """, (quiz_id,))
        row = cursor.fetchone()
        weakest_topic = row[0] if row else "None"
        quizzes.append({"quiz_id": quiz_id, "weakest_topic": weakest_topic})
    conn.close()
    return quizzes

def get_quiz_details(quiz_id):
    conn = sql.connect("databaseFiles/database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Q.question_id, QS.question, Q.selected_answer, Q.correct_answer, Q.mark,
               QS.a, QS.b, QS.c, QS.d
        FROM Quizzes Q
        JOIN questions QS ON Q.question_id = QS.question_id
        WHERE Q.quiz_id = ?
    """, (quiz_id,))
    results = []
    for row in cursor.fetchall():
        selected_letter = row[2]
        correct_letter = row[3]
        # Map letter to answer text
        answer_map = {'a': row[5], 'b': row[6], 'c': row[7], 'd': row[8]}
        selected_text = answer_map.get(selected_letter, "")
        correct_text = answer_map.get(correct_letter, "")
        results.append({
            "question_id": row[0],
            "question": row[1],
            "selected_answer": selected_letter.upper() if selected_letter else "",
            "selected_text": selected_text,
            "correct_answer": correct_letter.upper() if correct_letter else "",
            "correct_text": correct_text,
            "mark": row[4]
        })
    conn.close()
    return results

def get_overall_weakest_topic():
    conn = sql.connect("databaseFiles/database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic, COUNT(*) as incorrect
        FROM Quizzes
        WHERE mark = 0
        GROUP BY topic
        ORDER BY incorrect DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "None"