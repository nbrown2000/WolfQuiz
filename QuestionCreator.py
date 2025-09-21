
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import json_store

class QuestionCreatorWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Question Creator")
        self.grab_set()

        style = ThemedStyle(self)
        style.set_theme("equilux")

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Load quizzes
        self.quizzes = json_store.list_quizzes()
        self.selected_slug = None

        quiz_names = ["None"] + [q["quiz_name"] for q in self.quizzes]
        self.quiz_var = tk.StringVar(value="None")
        self.quiz_dropdown = ttk.OptionMenu(main_frame, self.quiz_var, quiz_names[0], *quiz_names, command=self.on_quiz_select)
        self.quiz_dropdown.pack()

        self.select_label = ttk.Label(main_frame, text="Select a quiz to get started!", font=("Helvetica", 16, "bold"))
        self.select_label.pack(pady=20)

        self.notebook = ttk.Notebook(main_frame)
        self.details_frame = ttk.Frame(self.notebook, padding=10)
        self.questions_frame = ttk.Frame(self.notebook, padding=10)
        self.answers_frame = ttk.Frame(self.notebook, padding=10)
        self.falseanswers_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.details_frame, text="Details")
        self.notebook.add(self.questions_frame, text="Questions")
        self.notebook.add(self.answers_frame, text="Answers")
        self.notebook.add(self.falseanswers_frame, text="False Answers")

        self.init_details_tab()
        self.init_questions_tab()
        self.init_answers_tab()
        self.init_falseanswers_tab()

        self.notebook.pack(fill="both", expand=True)
        self.notebook.forget()

    def _refresh_quizzes(self):
        self.quizzes = json_store.list_quizzes()

    def _find_slug_by_name(self, name: str):
        for q in self.quizzes:
            if q["quiz_name"] == name:
                return q["slug"]
        return None

    def on_quiz_select(self, _=None):
        name = self.quiz_var.get()
        if name == "None":
            self.selected_slug = None
            self.select_label.config(text="Select a quiz to get started!")
            self.notebook.forget()
            return
        self.selected_slug = self._find_slug_by_name(name)
        self.load_details()
        self.load_questions()
        self.load_answers()
        self.load_false_answers()
        self.select_label.config(text="")
        self.notebook.pack(fill="both", expand=True)

    # -------- DETAILS TAB --------
    def init_details_tab(self):
        self.name_label = ttk.Label(self.details_frame, text="Quiz Name:"); self.name_label.pack(anchor="w")
        self.name_entry = ttk.Entry(self.details_frame, width=50); self.name_entry.pack(anchor="w", pady=5)

        self.desc_label = ttk.Label(self.details_frame, text="Description:"); self.desc_label.pack(anchor="w")
        self.desc_text = tk.Text(self.details_frame, width=50, height=4); self.desc_text.pack(anchor="w", pady=5)

        self.qs_label = ttk.Label(self.details_frame, text="Question Selector Amount:"); self.qs_label.pack(anchor="w")
        self.qs_spin = ttk.Spinbox(self.details_frame, from_=2, to=10, width=5); self.qs_spin.pack(anchor="w", pady=5)

        self.save_details_btn = ttk.Button(self.details_frame, text="Save Details", command=self.save_details)
        self.save_details_btn.pack(pady=10)

    def load_details(self):
        quiz = json_store.load_quiz_by_slug(self.selected_slug)
        if not quiz:
            return
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, quiz.get("quiz_name",""))
        self.desc_text.delete("1.0", tk.END); self.desc_text.insert("1.0", quiz.get("quiz_description",""))
        self.qs_spin.delete(0, tk.END); self.qs_spin.insert(0, str(quiz.get("question_selector_amount", 4)))

    def save_details(self):
        if not self.selected_slug: return
        new_name = self.name_entry.get().strip()
        new_desc = self.desc_text.get("1.0", tk.END).strip()
        new_qs = int(self.qs_spin.get())
        quiz = json_store.load_quiz_by_slug(self.selected_slug)
        if not quiz: return
        # If name changes, slug will change.
        updated = json_store.update_quiz_fields(self.selected_slug, name=new_name, description=new_desc, selector_amount=new_qs)
        self._refresh_quizzes()
        # Update selection to the new slug if name changed
        self.selected_slug = updated["slug"]

    # -------- QUESTIONS TAB --------
    def init_questions_tab(self):
        self.create_question_btn = ttk.Button(self.questions_frame, text="+ Create", command=self.create_question_card)
        self.create_question_btn.pack(anchor="e", pady=5)

        self.questions_canvas = tk.Canvas(self.questions_frame); self.questions_canvas.pack(side="left", fill="both", expand=True)
        self.questions_scrollbar = ttk.Scrollbar(self.questions_frame, orient="vertical", command=self.questions_canvas.yview)
        self.questions_scrollbar.pack(side="right", fill="y")
        self.questions_canvas.configure(yscrollcommand=self.questions_scrollbar.set)
        self.questions_inner_frame = ttk.Frame(self.questions_canvas)
        self.questions_canvas.create_window((0, 0), window=self.questions_inner_frame, anchor="nw")
        self.questions_inner_frame.bind("<Configure>", lambda e: self.questions_canvas.configure(scrollregion=self.questions_canvas.bbox("all")))

    def load_questions(self):
        for w in self.questions_inner_frame.winfo_children():
            w.destroy()
        quiz = json_store.load_quiz_by_slug(self.selected_slug)
        if not quiz: return
        for q in quiz.get("questions", []):
            self.create_question_card(existing=q)

    def create_question_card(self, existing=None):
        card = ttk.Frame(self.questions_inner_frame, relief="ridge", padding=10)
        card.pack(fill="x", pady=5)

        q_id = existing.get("question_id") if existing else None
        q_text_val = existing.get("question_text","") if existing else ""
        is_tf_val = bool(existing.get("is_true_false", False)) if existing else False

        question_text = tk.Text(card, width=60, height=3); question_text.pack(pady=5); question_text.insert("1.0", q_text_val)
        tf_var = tk.BooleanVar(value=is_tf_val)
        tf_check = ttk.Checkbutton(card, text="True Or False", variable=tf_var); tf_check.pack()

        sep = ttk.Separator(card, orient="horizontal"); sep.pack(fill="x", pady=5)

        def save_question():
            if not self.selected_slug: return
            text_val = question_text.get("1.0", tk.END).strip()
            tf = bool(tf_var.get())
            # Preserve existing answer / false answers if present; handled in other tabs.
            # For convenience, ensure an answer exists; if blank, set placeholder.
            ans = ""
            fa = []
            if existing:
                ans = existing.get("answer","")
                fa = existing.get("false_answers", [])
            json_store.add_or_update_question(self.selected_slug, q_id, text_val, tf, ans, fa)
            self.load_questions()

        ttk.Button(card, text="Save", command=save_question).pack(anchor="e")

    # -------- ANSWERS TAB --------
    def init_answers_tab(self):
        self.create_answer_btn = ttk.Button(self.answers_frame, text="+ Create", command=self.create_answer_card)
        self.create_answer_btn.pack(anchor="e", pady=5)

        self.answers_canvas = tk.Canvas(self.answers_frame); self.answers_canvas.pack(side="left", fill="both", expand=True)
        self.answers_scrollbar = ttk.Scrollbar(self.answers_frame, orient="vertical", command=self.answers_canvas.yview)
        self.answers_scrollbar.pack(side="right", fill="y")
        self.answers_canvas.configure(yscrollcommand=self.answers_scrollbar.set)
        self.answers_inner_frame = ttk.Frame(self.answers_canvas)
        self.answers_canvas.create_window((0, 0), window=self.answers_inner_frame, anchor="nw")
        self.answers_inner_frame.bind("<Configure>", lambda e: self.answers_canvas.configure(scrollregion=self.answers_canvas.bbox("all")))

    def load_answers(self):
        for w in self.answers_inner_frame.winfo_children():
            w.destroy()
        quiz = json_store.load_quiz_by_slug(self.selected_slug)
        if not quiz: return
        questions = quiz.get("questions", [])
        for q in questions:
            self.create_answer_card(existing=q)

    def create_answer_card(self, existing=None):
        card = ttk.Frame(self.answers_inner_frame, relief="ridge", padding=10)
        card.pack(fill="x", pady=5)

        quiz = json_store.load_quiz_by_slug(self.selected_slug)
        questions = quiz.get("questions", []) if quiz else []
        question_ids = [q["question_id"] for q in questions]

        current_q_id = existing.get("question_id") if existing else (question_ids[0] if question_ids else None)
        ans_text_val = existing.get("answer","") if existing else ""

        ttk.Label(card, text="Answer:").pack(anchor="w")
        answer_entry = ttk.Entry(card, width=50); answer_entry.pack(anchor="w"); answer_entry.insert(0, ans_text_val)

        ttk.Label(card, text="Question ID:").pack(anchor="w")
        q_var = tk.StringVar(value=current_q_id or "")
        id_dropdown = ttk.OptionMenu(card, q_var, q_var.get(), *question_ids); id_dropdown.pack(anchor="w")

        def save_answer():
            qid = q_var.get().strip()
            if not qid: return
            # find question
            q = next((x for x in questions if x["question_id"] == qid), None)
            if not q: return
            is_tf = bool(q.get("is_true_false", False))
            text_val = answer_entry.get().strip()
            if is_tf and text_val.lower() not in ("true","false"):
                answer_entry.delete(0, tk.END); answer_entry.insert(0, "True or False only!"); return
            json_store.add_or_update_question(self.selected_slug, qid, q.get("question_text",""), is_tf, text_val, q.get("false_answers", []))
            self.load_answers()

        ttk.Button(card, text="Save", command=save_answer).pack(anchor="e")

    # -------- FALSE ANSWERS TAB --------
    def init_falseanswers_tab(self):
        self.create_false_btn = ttk.Button(self.falseanswers_frame, text="+ Create", command=self.create_falseanswer_card)
        self.create_false_btn.pack(anchor="e", pady=5)

        self.falseanswers_canvas = tk.Canvas(self.falseanswers_frame); self.falseanswers_canvas.pack(side="left", fill="both", expand=True)
        self.falseanswers_scrollbar = ttk.Scrollbar(self.falseanswers_frame, orient="vertical", command=self.falseanswers_canvas.yview)
        self.falseanswers_scrollbar.pack(side="right", fill="y")
        self.falseanswers_canvas.configure(yscrollcommand=self.falseanswers_scrollbar.set)
        self.falseanswers_inner_frame = ttk.Frame(self.falseanswers_canvas)
        self.falseanswers_canvas.create_window((0, 0), window=self.falseanswers_inner_frame, anchor="nw")
        self.falseanswers_inner_frame.bind("<Configure>", lambda e: self.falseanswers_canvas.configure(scrollregion=self.falseanswers_canvas.bbox("all")))

    def load_false_answers(self):
        for w in self.falseanswers_inner_frame.winfo_children():
            w.destroy()
        quiz = json_store.load_quiz_by_slug(self.selected_slug)
        if not quiz: return
        for q in quiz.get("questions", []):
            self.create_falseanswer_card(existing=q)

    def create_falseanswer_card(self, existing=None):
        card = ttk.Frame(self.falseanswers_inner_frame, relief="ridge", padding=10)
        card.pack(fill="x", pady=5)

        quiz = json_store.load_quiz_by_slug(self.selected_slug)
        questions = quiz.get("questions", []) if quiz else []
        question_ids = [q["question_id"] for q in questions]

        current_q_id = existing.get("question_id") if existing else (question_ids[0] if question_ids else None)
        fa_text_val = ", ".join(existing.get("false_answers", [])) if existing else ""

        ttk.Label(card, text="False Answers (comma-separated):").pack(anchor="w")
        false_entry = ttk.Entry(card, width=60); false_entry.pack(anchor="w"); false_entry.insert(0, fa_text_val)

        ttk.Label(card, text="Question ID:").pack(anchor="w")
        q_var = tk.StringVar(value=current_q_id or "")
        id_dropdown = ttk.OptionMenu(card, q_var, q_var.get(), *question_ids); id_dropdown.pack(anchor="w")

        def save_falseanswer():
            qid = q_var.get().strip()
            if not qid: return
            q = next((x for x in questions if x["question_id"] == qid), None)
            if not q: return
            is_tf = bool(q.get("is_true_false", False))
            if is_tf:
                false_entry.delete(0, tk.END); false_entry.insert(0, "Not applicable for T/F!"); return
            parts = [p.strip() for p in false_entry.get().split(",")]
            json_store.add_or_update_question(self.selected_slug, qid, q.get("question_text",""), is_tf, q.get("answer",""), parts)
            self.load_false_answers()

        ttk.Button(card, text="Save", command=save_falseanswer).pack(anchor="e")
