from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
from flask import session
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging

import userManagement as dbHandler


app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = "_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)


# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)


@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    return render_template("index.html")

@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("privacy.html")


# example CSRF protected form
@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        email = request.form["email"]
        text = request.form["text"]
        return render_template("form.html")
    else:
        return render_template("form.html")


# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"

# @app.route("/PDHPE", methods=["GET", "POST"])
# def pdhpe():
#     feedback = None

#     # Always reset on GET (new quiz)
#     if request.method == "GET":
#         session["correct_answers"] = 0
#         session["questions_asked"] = 0
#         session["asked_questions"] = []

#     if request.method == "POST":
#         selected = request.form.get("answer")
#         correct = session.get("current_correct")
#         if correct and selected == correct:
#             session["correct_answers"] += 1
#             feedback = "Correct!"
#         elif correct:
#             feedback = f"Wrong! The correct answer was {correct.upper()}."
#         session["questions_asked"] += 1

#     # Now check if 15 questions have been asked
#     if session["questions_asked"] >= 15:
#         correct = session["correct_answers"]
#         session.pop("questions_asked", None)
#         session.pop("correct_answers", None)
#         session.pop("current_correct", None)
#         session.pop("asked_questions", None)
#         return render_template("results.html", correct=correct, total=15)

#     # Get a new question, excluding already asked ones
#     asked_ids = session["asked_questions"]
#     question = dbHandler.get_question(asked_ids)
#     if question:
#         asked_ids.append(question["id"])
#         session["asked_questions"] = asked_ids
#         session["current_correct"] = question["correct_answer"]
#     else:
#         # No more questions available
#         return render_template("results.html", correct=session.get("correct_answers", 0), total=session.get("questions_asked", 0))

#     return render_template(
#         "PDHPE.html",
#         question=question,
#         feedback=feedback,
#         correct_answers=session["correct_answers"]
#     )

@app.route("/PDHPE", methods=["GET", "POST"])
def pdhpe():
    feedback = None

    # Initialize session variables if missing
    if "correct_answers" not in session:
        session["correct_answers"] = 0
    if "questions_asked" not in session:
        session["questions_asked"] = 0
    if "asked_questions" not in session:
        session["asked_questions"] = []

    if request.method == "POST":
        selected = request.form.get("answer")
        correct = session.get("current_correct")
        if correct and selected == correct:
            session["correct_answers"] += 1
            feedback = "Correct!"
        elif correct:
            feedback = f"Wrong! The correct answer was {correct.upper()}."
        session["questions_asked"] += 1

        # Only after answering, append the previous question's ID
        prev_id = session.get("current_id")
        if prev_id is not None and prev_id not in session["asked_questions"]:
            session["asked_questions"].append(prev_id)

    # Now check if 15 questions have been asked
    if session["questions_asked"] >= 15:
        correct = session["correct_answers"]
        session.pop("questions_asked", None)
        session.pop("correct_answers", None)
        session.pop("current_correct", None)
        session.pop("current_id", None)
        session.pop("asked_questions", None)
        return render_template("results.html", correct=correct, total=15)

    # Get a new question, excluding already asked ones
    asked_ids = session["asked_questions"]
    question = dbHandler.get_question(asked_ids)
    if question:
        session["current_correct"] = question["correct_answer"]
        session["current_id"] = question["id"]
    else:
        # No more questions available
        return render_template("results.html", correct=session.get("correct_answers", 0), total=session.get("questions_asked", 0))

    return render_template(
        "PDHPE.html",
        question=question,
        feedback=feedback,
        correct_answers=session["correct_answers"]
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)