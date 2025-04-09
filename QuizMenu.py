# QuizMenu.py
import tkinter as tk
from tkinter import ttk
import sqlite3
from ttkthemes import ThemedTk
import QuestionCreator
import QuizTake

DB_NAME = "wolfquiz.db"

class QuizMenuWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Quiz Menu")
        self.grab_set()  # Make this window modal-like

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        self.conn = sqlite3.connect(DB_NAME)
        self.c = self.conn.cursor()

        # Get quizzes
        quizzes = self.get_quizzes()
        if not quizzes:
            # If no quizzes, open QuestionCreator directly (as per the requirement)
            QuestionCreator.QuestionCreatorWindow(self.master)
            self.destroy()
            return

        # Create a tree-like layout or just frames
        for quiz in quizzes:
            quiz_id = quiz[0]
            quiz_name = quiz[1]
            quiz_desc = quiz[2] if quiz[2] else ""
            # Count questions
            self.c.execute("SELECT COUNT(*) FROM Questions WHERE quiz_id = ?", (quiz_id,))
            question_count = self.c.fetchone()[0]

            # Build a clickable frame
            quiz_frame = ttk.Frame(main_frame, relief="groove", padding=10)
            quiz_frame.pack(fill="x", pady=5)

            # Name in bold
            name_label = ttk.Label(quiz_frame, text=quiz_name, font=("Helvetica", 12, "bold"))
            name_label.grid(row=0, column=0, sticky="w")

            # Description in smaller font
            desc_label = ttk.Label(quiz_frame, text=quiz_desc, font=("Helvetica", 10))
            desc_label.grid(row=1, column=0, sticky="w")

            # Question count on the right
            count_label = ttk.Label(quiz_frame, text=str(question_count), font=("Helvetica", 10))
            count_label.grid(row=0, column=1, sticky="e", rowspan=2)

            # Make entire frame clickable
            quiz_frame.bind("<Button-1>", lambda e, q_id=quiz_id: self.open_quiz_take(q_id))
            name_label.bind("<Button-1>", lambda e, q_id=quiz_id: self.open_quiz_take(q_id))
            desc_label.bind("<Button-1>", lambda e, q_id=quiz_id: self.open_quiz_take(q_id))
            count_label.bind("<Button-1>", lambda e, q_id=quiz_id: self.open_quiz_take(q_id))

    def get_quizzes(self):
        self.c.execute("SELECT quiz_id, quiz_name, quiz_description FROM Quizzes")
        return self.c.fetchall()

    def open_quiz_take(self, quiz_id):
        # Open QuizTake
        QuizTake.QuizTakeWindow(self.master, quiz_id)
        self.destroy()

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass
