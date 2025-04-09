# QuestionCreator.py
import tkinter as tk
from tkinter import ttk
import sqlite3
from ttkthemes import ThemedStyle

DB_NAME = "wolfquiz.db"

class QuestionCreatorWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Question Creator")
        self.grab_set()  # Make this window modal-like

        # Apply the Equilux theme
        style = ThemedStyle(self)
        style.set_theme("equilux")

        # Main Frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Database setup
        self.conn = sqlite3.connect(DB_NAME)
        self.c = self.conn.cursor()
        self.quizzes = self.get_all_quizzes()

        # Currently selected quiz ID
        self.selected_quiz_id = None

        # Dropdown to select quiz
        quiz_names = ["None"] + [quiz[1] for quiz in self.quizzes]  # (quiz_id, quiz_name, desc, sel_amt)
        self.quiz_var = tk.StringVar(value="None")
        self.quiz_dropdown = ttk.OptionMenu(
            main_frame,
            self.quiz_var,
            quiz_names[0],
            *quiz_names,
            command=self.on_quiz_select
        )
        self.quiz_dropdown.pack()

        # Big label for "None"
        self.select_label = ttk.Label(main_frame, text="Select a quiz to get started!", font=("Helvetica", 16, "bold"))
        self.select_label.pack(pady=20)

        # Notebook with 4 tabs
        self.notebook = ttk.Notebook(main_frame)
        self.details_frame = ttk.Frame(self.notebook, padding=10)
        self.questions_frame = ttk.Frame(self.notebook, padding=10)
        self.answers_frame = ttk.Frame(self.notebook, padding=10)
        self.falseanswers_frame = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.details_frame, text="Details")
        self.notebook.add(self.questions_frame, text="Questions")
        self.notebook.add(self.answers_frame, text="Answers")
        self.notebook.add(self.falseanswers_frame, text="False Answers")

        # Initialize each tab's UI
        self.init_details_tab()
        self.init_questions_tab()
        self.init_answers_tab()
        self.init_falseanswers_tab()

        self.notebook.pack(fill="both", expand=True)
        # Hide notebook until a quiz is selected
        self.notebook.forget()

    def get_all_quizzes(self):
        self.c.execute("SELECT quiz_id, quiz_name, quiz_description, question_selector_amount FROM Quizzes")
        return self.c.fetchall()

    def on_quiz_select(self, event=None):
        quiz_name = self.quiz_var.get()
        if quiz_name == "None":
            self.selected_quiz_id = None
            self.select_label.config(text="Select a quiz to get started!")
            self.notebook.forget()
        else:
            # Find the matching quiz_id
            for quiz in self.quizzes:
                if quiz[1] == quiz_name:
                    self.selected_quiz_id = quiz[0]
                    break

            self.load_details()
            self.load_questions()
            self.load_answers()
            self.load_false_answers()

            self.select_label.config(text="")
            self.notebook.pack(fill="both", expand=True)

    # -------------------- DETAILS TAB --------------------
    def init_details_tab(self):
        # Quiz Name
        self.name_label = ttk.Label(self.details_frame, text="Quiz Name:")
        self.name_label.pack(anchor="w")
        self.name_entry = ttk.Entry(self.details_frame, width=50)
        self.name_entry.pack(anchor="w", pady=5)

        # Description
        self.desc_label = ttk.Label(self.details_frame, text="Description:")
        self.desc_label.pack(anchor="w")
        self.desc_text = tk.Text(self.details_frame, width=50, height=4)
        self.desc_text.pack(anchor="w", pady=5)

        # Question Selector Amount
        self.qs_label = ttk.Label(self.details_frame, text="Question Selector Amount:")
        self.qs_label.pack(anchor="w")
        self.qs_spin = ttk.Spinbox(self.details_frame, from_=2, to=10, width=5)
        self.qs_spin.pack(anchor="w", pady=5)

        # Save button
        self.save_details_btn = ttk.Button(self.details_frame, text="Save Details", command=self.save_details)
        self.save_details_btn.pack(pady=10)

    def load_details(self):
        self.c.execute(
            "SELECT quiz_name, quiz_description, question_selector_amount FROM Quizzes WHERE quiz_id = ?",
            (self.selected_quiz_id,)
        )
        row = self.c.fetchone()
        if row:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, row[0])
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", row[1] if row[1] else "")
            self.qs_spin.delete(0, tk.END)
            self.qs_spin.insert(0, str(row[2]) if row[2] else "4")

    def save_details(self):
        new_name = self.name_entry.get().strip()
        new_desc = self.desc_text.get("1.0", tk.END).strip()
        new_qs = self.qs_spin.get()

        self.c.execute("""
            UPDATE Quizzes
            SET quiz_name = ?, quiz_description = ?, question_selector_amount = ?
            WHERE quiz_id = ?
        """, (new_name, new_desc, new_qs, self.selected_quiz_id))
        self.conn.commit()

        # Refresh local quiz list
        self.quizzes = self.get_all_quizzes()

    # -------------------- QUESTIONS TAB --------------------
    def init_questions_tab(self):
        # Create Button
        self.create_question_btn = ttk.Button(
            self.questions_frame, text="+ Create",
            command=self.create_question_card
        )
        self.create_question_btn.pack(anchor="e", pady=5)

        # SCROLLABLE AREA
        self.questions_canvas = tk.Canvas(self.questions_frame)
        self.questions_canvas.pack(side="left", fill="both", expand=True)

        self.questions_scrollbar = ttk.Scrollbar(self.questions_frame, orient="vertical",
                                                 command=self.questions_canvas.yview)
        self.questions_scrollbar.pack(side="right", fill="y")

        self.questions_canvas.configure(yscrollcommand=self.questions_scrollbar.set)

        # Inner frame
        self.questions_inner_frame = ttk.Frame(self.questions_canvas)
        self.questions_canvas.create_window((0, 0), window=self.questions_inner_frame, anchor="nw")

        # Bind to update scrollregion
        self.questions_inner_frame.bind("<Configure>", lambda e: self.questions_canvas.configure(
            scrollregion=self.questions_canvas.bbox("all")
        ))

    def load_questions(self):
        # Clear old cards
        for widget in self.questions_inner_frame.winfo_children():
            widget.destroy()

        self.c.execute("SELECT question_id, question_text, is_true_false FROM Questions WHERE quiz_id = ?", 
                       (self.selected_quiz_id,))
        rows = self.c.fetchall()

        for row in rows:
            self.create_question_card(existing_data=row)

    def create_question_card(self, existing_data=None):
        card_frame = ttk.Frame(self.questions_inner_frame, relief="ridge", padding=10)
        card_frame.pack(fill="x", pady=5)

        if existing_data:
            q_id, q_text, is_tf = existing_data
        else:
            q_id = None
            q_text = ""
            is_tf = 0

        # Question Text
        question_text = tk.Text(card_frame, width=60, height=3)
        question_text.pack(pady=5)
        question_text.insert("1.0", q_text)

        # True or False
        tf_var = tk.BooleanVar()
        tf_var.set(bool(is_tf))
        tf_check = ttk.Checkbutton(card_frame, text="True Or False", variable=tf_var)
        tf_check.pack()

        # Separator
        sep = ttk.Separator(card_frame, orient="horizontal")
        sep.pack(fill="x", pady=5)

        def save_question():
            text_val = question_text.get("1.0", tk.END).strip()
            tf_val = tf_var.get()
            if q_id is None:
                # Insert new
                self.c.execute("""
                    INSERT INTO Questions (quiz_id, question_text, is_true_false)
                    VALUES (?, ?, ?)
                """, (self.selected_quiz_id, text_val, 1 if tf_val else 0))
                self.conn.commit()
                self.load_questions()
            else:
                # Update existing
                self.c.execute("""
                    UPDATE Questions
                    SET question_text = ?, is_true_false = ?
                    WHERE question_id = ?
                """, (text_val, 1 if tf_val else 0, q_id))
                self.conn.commit()

        save_btn = ttk.Button(card_frame, text="Save", command=save_question)
        save_btn.pack(anchor="e")

    # -------------------- ANSWERS TAB --------------------
    def init_answers_tab(self):
        # Create Button
        self.create_answer_btn = ttk.Button(
            self.answers_frame, text="+ Create",
            command=self.create_answer_card
        )
        self.create_answer_btn.pack(anchor="e", pady=5)

        # SCROLLABLE AREA
        self.answers_canvas = tk.Canvas(self.answers_frame)
        self.answers_canvas.pack(side="left", fill="both", expand=True)

        self.answers_scrollbar = ttk.Scrollbar(self.answers_frame, orient="vertical",
                                               command=self.answers_canvas.yview)
        self.answers_scrollbar.pack(side="right", fill="y")

        self.answers_canvas.configure(yscrollcommand=self.answers_scrollbar.set)

        # Inner frame
        self.answers_inner_frame = ttk.Frame(self.answers_canvas)
        self.answers_canvas.create_window((0, 0), window=self.answers_inner_frame, anchor="nw")

        # Bind to update scrollregion
        self.answers_inner_frame.bind("<Configure>", lambda e: self.answers_canvas.configure(
            scrollregion=self.answers_canvas.bbox("all")
        ))

    def load_answers(self):
        # Clear
        for widget in self.answers_inner_frame.winfo_children():
            widget.destroy()

        self.c.execute("""
            SELECT A.answer_id, A.question_id, A.answer_text
            FROM Answers A
            JOIN Questions Q ON A.question_id = Q.question_id
            WHERE Q.quiz_id = ?
        """, (self.selected_quiz_id,))
        rows = self.c.fetchall()

        for row in rows:
            self.create_answer_card(existing_data=row)

    def create_answer_card(self, existing_data=None):
        card_frame = ttk.Frame(self.answers_inner_frame, relief="ridge", padding=10)
        card_frame.pack(fill="x", pady=5)

        # Get all questions for the dropdown
        self.c.execute("SELECT question_id, question_text, is_true_false FROM Questions WHERE quiz_id = ?", (self.selected_quiz_id,))
        question_list = self.c.fetchall()

        if existing_data:
            ans_id, q_id, ans_text = existing_data
        else:
            ans_id = None
            q_id = None
            ans_text = ""

        # Answer text
        answer_label = ttk.Label(card_frame, text="Answer:")
        answer_label.pack(anchor="w")
        answer_entry = ttk.Entry(card_frame, width=50)
        answer_entry.pack(anchor="w")
        answer_entry.insert(0, ans_text)

        # ID dropdown
        id_label = ttk.Label(card_frame, text="Question ID:")
        id_label.pack(anchor="w")
        question_ids = [str(q[0]) for q in question_list]
        q_var = tk.StringVar(value=str(q_id) if q_id else (question_ids[0] if question_ids else ""))
        id_dropdown = ttk.OptionMenu(card_frame, q_var, q_var.get(), *question_ids)
        id_dropdown.pack(anchor="w")

        def save_answer():
            selected_q_id = q_var.get()
            if not selected_q_id:
                return

            # Check if T/F
            self.c.execute("SELECT is_true_false FROM Questions WHERE question_id=?", (selected_q_id,))
            row = self.c.fetchone()
            is_tf = row[0] if row else 0

            text_val = answer_entry.get().strip()
            if is_tf:
                # Only allow "True" or "False"
                if text_val.lower() not in ("true", "false"):
                    answer_entry.delete(0, tk.END)
                    answer_entry.insert(0, "True or False only!")
                    return

            if ans_id is None:
                # Insert new answer
                self.c.execute("""
                    INSERT INTO Answers (question_id, answer_text)
                    VALUES (?, ?)
                """, (selected_q_id, text_val))
            else:
                # Update existing
                self.c.execute("""
                    UPDATE Answers
                    SET question_id = ?, answer_text = ?
                    WHERE answer_id = ?
                """, (selected_q_id, text_val, ans_id))

            self.conn.commit()
            self.load_answers()

        save_btn = ttk.Button(card_frame, text="Save", command=save_answer)
        save_btn.pack(anchor="e")

    # -------------------- FALSE ANSWERS TAB --------------------
    def init_falseanswers_tab(self):
        # Create Button
        self.create_false_btn = ttk.Button(
            self.falseanswers_frame, text="+ Create",
            command=self.create_falseanswer_card
        )
        self.create_false_btn.pack(anchor="e", pady=5)

        # SCROLLABLE AREA
        self.falseanswers_canvas = tk.Canvas(self.falseanswers_frame)
        self.falseanswers_canvas.pack(side="left", fill="both", expand=True)

        self.falseanswers_scrollbar = ttk.Scrollbar(self.falseanswers_frame, orient="vertical",
                                                    command=self.falseanswers_canvas.yview)
        self.falseanswers_scrollbar.pack(side="right", fill="y")

        self.falseanswers_canvas.configure(yscrollcommand=self.falseanswers_scrollbar.set)

        # Inner frame
        self.falseanswers_inner_frame = ttk.Frame(self.falseanswers_canvas)
        self.falseanswers_canvas.create_window((0, 0), window=self.falseanswers_inner_frame, anchor="nw")

        # Bind to update scrollregion
        self.falseanswers_inner_frame.bind("<Configure>", lambda e: self.falseanswers_canvas.configure(
            scrollregion=self.falseanswers_canvas.bbox("all")
        ))

    def load_false_answers(self):
        for widget in self.falseanswers_inner_frame.winfo_children():
            widget.destroy()

        self.c.execute("""
            SELECT F.falseanswer_id, F.question_id, F.false_answer_text
            FROM FalseAnswers F
            JOIN Questions Q ON F.question_id = Q.question_id
            WHERE Q.quiz_id = ?
        """, (self.selected_quiz_id,))
        rows = self.c.fetchall()

        for row in rows:
            self.create_falseanswer_card(existing_data=row)

    def create_falseanswer_card(self, existing_data=None):
        card_frame = ttk.Frame(self.falseanswers_inner_frame, relief="ridge", padding=10)
        card_frame.pack(fill="x", pady=5)

        # Get all questions
        self.c.execute("SELECT question_id, question_text, is_true_false FROM Questions WHERE quiz_id = ?", (self.selected_quiz_id,))
        question_list = self.c.fetchall()

        if existing_data:
            fa_id, q_id, fa_text = existing_data
        else:
            fa_id = None
            q_id = None
            fa_text = ""

        # false answer text
        false_label = ttk.Label(card_frame, text="False Answer:")
        false_label.pack(anchor="w")
        false_entry = ttk.Entry(card_frame, width=50)
        false_entry.pack(anchor="w")
        false_entry.insert(0, fa_text)

        # ID dropdown
        id_label = ttk.Label(card_frame, text="Question ID:")
        id_label.pack(anchor="w")
        question_ids = [str(q[0]) for q in question_list]
        q_var = tk.StringVar(value=str(q_id) if q_id else (question_ids[0] if question_ids else ""))
        id_dropdown = ttk.OptionMenu(card_frame, q_var, q_var.get(), *question_ids)
        id_dropdown.pack(anchor="w")

        def save_falseanswer():
            selected_q_id = q_var.get()
            if not selected_q_id:
                return

            # Check T/F
            self.c.execute("SELECT is_true_false FROM Questions WHERE question_id=?", (selected_q_id,))
            row = self.c.fetchone()
            is_tf = row[0] if row else 0

            text_val = false_entry.get().strip()
            if is_tf:
                # Typically we don't add false answers to True/False questions
                false_entry.delete(0, tk.END)
                false_entry.insert(0, "Not applicable for T/F!")
                return

            if fa_id is None:
                # Insert new
                self.c.execute("""
                    INSERT INTO FalseAnswers (question_id, false_answer_text)
                    VALUES (?, ?)
                """, (selected_q_id, text_val))
            else:
                # Update
                self.c.execute("""
                    UPDATE FalseAnswers
                    SET question_id = ?, false_answer_text = ?
                    WHERE falseanswer_id = ?
                """, (selected_q_id, text_val, fa_id))

            self.conn.commit()
            self.load_false_answers()

        save_btn = ttk.Button(card_frame, text="Save", command=save_falseanswer)
        save_btn.pack(anchor="e")

    def __del__(self):
        # Properly close DB connection if this window closes
        try:
            self.conn.close()
        except:
            pass
