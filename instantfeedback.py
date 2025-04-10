# instantfeedback.py
import customtkinter as ctk
import sqlite3
import random
import Results
from QuizTake import (
    BG_MAIN, QUESTION_BOX_BG, TEXT_COLOR,
    ANSWER_NORMAL, ANSWER_HOVER, ANSWER_SELECTED, OFFSET_COLOR,
    QUESTION_FONT, ANSWER_FONT,
    QuestionBox, AnswerRectangle
)

DB_NAME = "wolfquiz.db"

class InstantFeedbackWindow(ctk.CTkToplevel):
    def __init__(self, master, quiz_id):
        super().__init__(master)
        self.title("Instant Feedback Quiz")
        self.quiz_id = quiz_id
        self.state('zoomed')
        self.configure(bg=BG_MAIN)
        self.grab_set()

        # New DB connection per window
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "SELECT question_id, question_text, is_true_false "
            "FROM Questions WHERE quiz_id = ?", (quiz_id,)
        )
        self.questions = c.fetchall()
        conn.close()

        self.current = 0
        self.user_answers = []

        # Layout
        self.main = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.main.pack(fill="both", expand=True)

        self.qbox = QuestionBox(self.main,
                                width=self.winfo_screenwidth(),
                                height=150)
        self.qbox.pack(pady=20)

        self.ans_frame = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        self.ans_frame.pack(pady=20)

        self.load_question()

    def load_question(self):
        # Clear previous
        for w in self.ans_frame.winfo_children():
            w.destroy()
        self.answer_widgets = []

        q_id, q_text, is_tf = self.questions[self.current]
        display = f"Question {self.current+1}/{len(self.questions)}:\n{q_text}"
        self.qbox.set_text(display)

        # Fetch options
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        if is_tf:
            options = ["True", "False"]
        else:
            c.execute("SELECT answer_text FROM Answers WHERE question_id=?", (q_id,))
            correct = c.fetchone()[0]
            c.execute("SELECT false_answer_text FROM FalseAnswers WHERE question_id=?", (q_id,))
            false_opts = [row[0] for row in c.fetchall()]
            options = [correct] + false_opts
            random.shuffle(options)
        conn.close()

        # Build buttons (larger size)
        for idx, opt in enumerate(options):
            w = AnswerRectangle(
                self.ans_frame,
                text=opt,
                command=lambda widget, opts=options: self.on_click(widget, opts),
                width=350, height=120
            )
            r, c = divmod(idx, 2)
            w.grid(row=r, column=c, padx=30, pady=30)
            self.answer_widgets.append(w)

    def on_click(self, widget, options):
        # Mark selection darker immediately
        widget.select(True)

        chosen = widget.label.cget("text")
        self.user_answers.append(chosen)

        # Determine correct answer now
        q_id, _, _ = self.questions[self.current]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT answer_text FROM Answers WHERE question_id=?", (q_id,))
        correct = c.fetchone()[0]
        conn.close()

        # Disable further clicks
        for w in self.answer_widgets:
            w.inner.unbind("<Button-1>")
            w.label.unbind("<Button-1>")
            w.label_shadow.unbind("<Button-1>")

        # After 2 s, show feedback
        self.after(1000, lambda: self.show_feedback(correct))

    def show_feedback(self, correct):
        for w in self.answer_widgets:
            txt = w.label.cget("text")
            if txt == correct:
                w.set_color("green")
            else:
                w.set_color("red")
        # After 5 s more, advance
        self.after(3000, self.next_or_finish)

    def next_or_finish(self):
        self.current += 1
        if self.current < len(self.questions):
            self.load_question()
        else:
            self.finish()

    def finish(self):
        # Compile results
        result_data = []
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        for i, (q_id, q_text, is_tf) in enumerate(self.questions):
            user = self.user_answers[i]
            c.execute("SELECT answer_text FROM Answers WHERE question_id=?", (q_id,))
            correct = c.fetchone()[0]
            result_data.append((q_text, user, correct, user == correct))
        conn.close()

        Results.ResultsWindow(self.master, result_data)
        self.destroy()
