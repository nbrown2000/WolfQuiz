import customtkinter as ctk
import random
import Results
import json_store
# Import shared styles and components from QuizTake
from QuizTake import (BG_MAIN, QUESTION_BOX_BG, TEXT_COLOR,
                      ANSWER_NORMAL, ANSWER_HOVER, ANSWER_SELECTED, OFFSET_COLOR,
                      QUESTION_FONT, ANSWER_FONT,
                      QuestionBox, AnswerRectangle)

class InstantFeedbackWindow(ctk.CTkToplevel):
    def __init__(self, master, quiz_slug: str):
        super().__init__(master)
        self.title("Instant Feedback Quiz")
        self.quiz_slug = quiz_slug
        self.state('zoomed')
        # Changed: Apply same background as standard quiz window
        self.configure(fg_color=BG_MAIN)
        self.grab_set()

        quiz = json_store.load_quiz_by_slug(quiz_slug)
        self.questions = quiz.get("questions", []) if quiz else []
        self.current = 0
        self.user_answers = []

        # Main container frames
        self.main = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.main.pack(fill="both", expand=True)
        self.qbox = QuestionBox(self.main, width=self.winfo_screenwidth(), height=150)
        self.qbox.pack(pady=20)
        self.ans_frame = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        self.ans_frame.pack(pady=20)

        self.load_question()

    def load_question(self):
        # Clear previous answers
        for w in self.ans_frame.winfo_children():
            w.destroy()
        self.answer_widgets = []

        q = self.questions[self.current]
        q_text = q.get("question_text", "")
        is_tf = bool(q.get("is_true_false", False))
        display = f"Question {self.current+1}/{len(self.questions)}:\n{q_text}"
        self.qbox.set_text(display)

        # Prepare answer options
        if is_tf:
            options = ["True", "False"]
        else:
            correct = q.get("answer", "")
            false_opts = list(q.get("false_answers", []))
            options = [correct] + false_opts
            random.shuffle(options)

        # Create answer rectangles (grid them in two columns)
        for idx, opt in enumerate(options):
            btn = AnswerRectangle(self.ans_frame, text=opt,
                                  command=lambda widget, _opts=options: self.on_click(widget),
                                  width=350, height=120)
            r, c = divmod(idx, 2)
            btn.grid(row=r, column=c, padx=30, pady=30)
            self.answer_widgets.append(btn)

    def on_click(self, widget):
        # On answer click: mark selected and store answer
        widget.select(True)
        chosen_text = widget.label.cget("text")
        self.user_answers.append(chosen_text)
        q = self.questions[self.current]
        correct = q.get("answer", "")

        # Disable further clicks on all answer widgets
        for w in self.answer_widgets:
            w.inner.unbind("<Button-1>")
            w.label.unbind("<Button-1>")
            w.label_shadow.unbind("<Button-1>")

        # After a short delay, show feedback coloring (green/red)
        self.after(1000, lambda: self.show_feedback(correct))

    def show_feedback(self, correct):
        # Color all answer options: green for correct answer, red for others
        for w in self.answer_widgets:
            txt = w.label.cget("text")
            w.set_color("green" if txt == correct else "red")
        # After a delay, proceed to next question or finish
        self.after(3000, self.next_or_finish)

    def next_or_finish(self):
        self.current += 1
        if self.current < len(self.questions):
            self.load_question()
        else:
            self.finish()

    def finish(self):
        # Compile results and show the results window
        result_data = []
        for i, q in enumerate(self.questions):
            user_ans = self.user_answers[i]
            correct = q.get("answer", "")
            result_data.append((q.get("question_text", ""), user_ans, correct, user_ans == correct))
        Results.ResultsWindow(self.master, result_data)
        self.destroy()
