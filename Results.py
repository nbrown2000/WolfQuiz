# Results.py
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

class ResultsWindow(tk.Toplevel):
    def __init__(self, master, result_data):
        super().__init__(master)
        self.title("Quiz Results")
        self.grab_set()          # Make modal
        self.state("zoomed")     # Fullscreen like QuizTake.py
        self.result_data = result_data

        DARK_BG = "#1c1c1c"
        self.configure(bg=DARK_BG)

        # Set up ttk style so that frames and labels share our dark background.
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=DARK_BG)
        style.configure("TLabel", background=DARK_BG, foreground="white")
        style.configure("Vertical.TScrollbar", background=DARK_BG, troughcolor=DARK_BG)

        # Helper function that finds the largest font size (within min/max limits)
        # so that the given text fits within max_width.
        def fit_font(text, max_width, family="Helvetica", weight="normal", min_size=8, max_size=36):
            low = min_size
            high = max_size
            best = min_size
            while low <= high:
                mid = (low + high) // 2
                font_candidate = tkFont.Font(family=family, size=mid, weight=weight)
                if font_candidate.measure(text) <= max_width:
                    best = mid
                    low = mid + 1
                else:
                    high = mid - 1
            return tkFont.Font(family=family, size=best, weight=weight)

        # Use 80% of the screen width as maximum allowed width for our labels.
        screen_width = self.winfo_screenwidth()
        max_label_width = int(screen_width * 0.8)

        # Calculate score percentage and determine grade.
        total = len(self.result_data)
        correct = sum(1 for item in self.result_data if item[3])
        percentage = (correct / total * 100) if total else 0.0
        if percentage <= 59:
            grade = "F"
        elif percentage <= 69:
            grade = "D"
        elif percentage <= 79:
            grade = "C"
        elif percentage <= 89:
            grade = "B"
        elif percentage <= 99:
            grade = "A"
        else:
            grade = "A+"

        # --- Header ---
        header_frame = ttk.Frame(self, padding=10, style="TFrame")
        header_frame.pack(fill="x")
        header_text = f"{percentage:.1f}%   Grade: {grade}"
        header_font = fit_font(header_text, max_label_width, family="Helvetica", weight="bold", min_size=18, max_size=36)
        header_label = ttk.Label(header_frame, text=header_text, font=header_font, anchor="center")
        header_label.pack(fill="x")

        # --- Main container for scrollable content ---
        container = ttk.Frame(self, padding=10, style="TFrame")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=DARK_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scroll_frame = ttk.Frame(canvas, style="TFrame")
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Enable mousewheel scrolling when the mouse is over the canvas.
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # --- Populate Results with Dynamic Font Sizing ---
        for i, (q_text, user_ans, correct_ans, is_correct) in enumerate(self.result_data, start=1):
            card_frame = ttk.Frame(self.scroll_frame, relief="ridge", padding=10, style="TFrame")
            card_frame.pack(fill="x", expand=True, pady=5)

            # Question
            question_text = f"Q{i}: {q_text}"
            q_font = fit_font(question_text, max_label_width, family="Helvetica", weight="bold", min_size=10, max_size=36)
            ttk.Label(card_frame, text=question_text, font=q_font).pack(anchor="w", pady=2)

            # User Answer
            user_text = f"Your Answer: {user_ans}"
            ua_font = fit_font(user_text, max_label_width, family="Helvetica", weight="normal", min_size=8, max_size=30)
            ttk.Label(card_frame, text=user_text, font=ua_font).pack(anchor="w")

            # Correct Answer
            correct_text = f"Correct Answer: {correct_ans}"
            ca_font = fit_font(correct_text, max_label_width, family="Helvetica", weight="normal", min_size=8, max_size=30)
            ttk.Label(card_frame, text=correct_text, font=ca_font).pack(anchor="w")

            # Result indicator
            result_text = "Correct ✅" if is_correct else "Incorrect ❌"
            r_font = fit_font(result_text, max_label_width, family="Helvetica", weight="normal", min_size=8, max_size=30)
            ttk.Label(card_frame, text=result_text, foreground=("green" if is_correct else "red"), font=r_font).pack(anchor="w")

        # --- Back Button ---
        back_btn = ttk.Button(self.scroll_frame, text="Back To Quizzes", command=self.go_back_to_quizzes)
        back_btn.pack(pady=10, anchor="center")

    def go_back_to_quizzes(self):
        self.destroy()
