import customtkinter as ctk
import json_store
import QuizTake
import instantfeedback
import QuestionCreator

# Define theme colors for this window
BG_MAIN          = "#2b1a5c"   # Dark purple background
QUIZ_CARD_COLOR  = "#40278a"   # Slightly lighter purple for quiz item cards
ACCENT_ORANGE    = "#FF7518"   # Orange accent color
ACCENT_ORANGE_HOVER = "#E66916" # Darker orange for hover

class QuizMenuWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Quiz Menu")
        self.grab_set()
        # Changed: Apply dark purple background to the window
        self.configure(fg_color=BG_MAIN)

        main_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Load all quizzes (from JSON store) and display each as a selectable card
        quizzes = json_store.list_quizzes()
        if not quizzes:
            # If no quizzes exist, open the Quiz Creator to prompt creation
            QuestionCreator.QuestionCreatorWindow(self.master)
            self.destroy()
            return

        for quiz in quizzes:
            quiz_name = quiz["quiz_name"]
            quiz_desc = quiz.get("quiz_description", "") or ""
            count = quiz.get("question_count", 0)
            slug = quiz["slug"]

            # Changed: Each quiz entry is displayed as a CTkFrame "card" with themed styling
            quiz_frame = ctk.CTkFrame(main_frame, fg_color=QUIZ_CARD_COLOR, corner_radius=10)
            quiz_frame.pack(fill="x", pady=5, padx=5)

            name_label = ctk.CTkLabel(quiz_frame, text=quiz_name, font=("Verdana", 14, "bold"))
            desc_label = ctk.CTkLabel(quiz_frame, text=quiz_desc, font=("Verdana", 12))
            count_label = ctk.CTkLabel(quiz_frame, text=str(count), font=("Verdana", 12))
            # Layout labels in a grid for alignment
            name_label.grid(row=0, column=0, sticky="w")
            desc_label.grid(row=1, column=0, sticky="w")
            count_label.grid(row=0, column=1, rowspan=2, sticky="e", padx=10)

            # Make entire quiz_frame (and labels) clickable to open the quiz
            for widget in (quiz_frame, name_label, desc_label, count_label):
                widget.bind("<Button-1>", lambda e, s=slug: self.open_quiz_take(s))

            # Changed: "Instant Feedback" button styled with orange accent, on each quiz card
            inst_btn = ctk.CTkButton(quiz_frame, text="Instant Feedback",
                                     command=lambda s=slug: self.open_instant_feedback(s),
                                     fg_color=ACCENT_ORANGE, hover_color=ACCENT_ORANGE_HOVER,
                                     text_color="white", font=("Verdana", 12, "bold"), corner_radius=8,
                                     width=120, height=30)
            inst_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=5)

    def open_quiz_take(self, slug):
        QuizTake.QuizTakeWindow(self.master, slug)
        self.destroy()

    def open_instant_feedback(self, slug):
        instantfeedback.InstantFeedbackWindow(self.master, slug)
        self.destroy()
