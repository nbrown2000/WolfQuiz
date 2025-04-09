import json
import sqlite3

DB_NAME = "wolfquiz.db"
QUIZ_NAME = "GBUS 325 Exam 3"

# Load JSON file
with open("gbus325_exam1.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

# Connect to database
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Get the quiz ID for "GBUS 325 Exam 1"
c.execute("SELECT quiz_id FROM Quizzes WHERE quiz_name = ?", (QUIZ_NAME,))
quiz_row = c.fetchone()

if quiz_row:
    quiz_id = quiz_row[0]
else:
    print(f"Error: Quiz '{QUIZ_NAME}' not found in the database.")
    conn.close()
    exit()

# Insert questions and answers
for q in questions:
    question_text = q["question_text"]
    is_true_false = q["is_true_false"]
    correct_answer = q["correct_answer"]
    false_answers = q["false_answers"]

    # Insert question
    c.execute(
        "INSERT INTO Questions (quiz_id, question_text, is_true_false) VALUES (?, ?, ?)",
        (quiz_id, question_text, is_true_false)
    )
    question_id = c.lastrowid  # Get inserted question ID

    # Insert correct answer
    c.execute(
        "INSERT INTO Answers (question_id, answer_text) VALUES (?, ?)",
        (question_id, correct_answer)
    )

    # Insert false answers (skip if True/False question)
    if not is_true_false:
        for false_answer in false_answers:
            c.execute(
                "INSERT INTO FalseAnswers (question_id, false_answer_text) VALUES (?, ?)",
                (question_id, false_answer)
            )

# Commit changes and close database
conn.commit()
conn.close()

print(f"Successfully inserted {len(questions)} questions into '{QUIZ_NAME}'.")
