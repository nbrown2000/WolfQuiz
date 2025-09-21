# Results.py (fixed for customtkinter fonts)
import customtkinter as ctk
import tkinter.font as tkFont

BG_MAIN         = "#2b1a5c"   # Dark purple
CARD_BG_COLOR   = "#40278a"   # Card purple
TEXT_COLOR      = "#ffffff"
ACCENT_ORANGE   = "#FF7518"

def _fit_font_size(text, max_width, family="Verdana", weight="normal", min_size=8, max_size=36):
    """Return the largest integer font size whose measured width fits max_width."""
    low, high = min_size, max_size
    best = min_size
    while low <= high:
        mid = (low + high) // 2
        f = tkFont.Font(family=family, size=mid, weight=weight)
        if f.measure(text) <= max_width:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best

class ResultsWindow(ctk.CTkToplevel):
    def __init__(self, master, result_data):
        super().__init__(master)
        self.title("Quiz Results")
        self.grab_set()
        self.state("zoomed")
        self.configure(fg_color=BG_MAIN)
        self.result_data = result_data

        screen_width = self.winfo_screenwidth()
        max_label_width = int(screen_width * 0.8)

        # Score & grade
        total = len(self.result_data)
        correct = sum(1 for _, _, _, ok in self.result_data if ok)
        percentage = (correct / total * 100) if total else 0.0
        if percentage <= 59: grade = "F"
        elif percentage <= 69: grade = "D"
        elif percentage <= 79: grade = "C"
        elif percentage <= 89: grade = "B"
        elif percentage <= 99: grade = "A"
        else: grade = "A+"

        header_text = f"{percentage:.1f}%   Grade: {grade}"
        h_size = _fit_font_size(header_text, max_label_width, family="Verdana", weight="bold", min_size=18, max_size=36)
        header_font = ctk.CTkFont(family="Verdana", size=h_size, weight="bold")
        header_label = ctk.CTkLabel(self, text=header_text, font=header_font,
                                    text_color=ACCENT_ORANGE, anchor="center")
        header_label.pack(fill="x", pady=10)

        # Scrollable area
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        for i, (q_text, user_ans, correct_ans, is_correct) in enumerate(self.result_data, start=1):
            card = ctk.CTkFrame(scroll, fg_color=CARD_BG_COLOR, corner_radius=10)
            card.pack(fill="x", expand=True, pady=5, padx=5)

            # Question
            q_str = f"Q{i}: {q_text}"
            q_size = _fit_font_size(q_str, max_label_width, family="Verdana", weight="bold", min_size=10, max_size=36)
            q_font = ctk.CTkFont(family="Verdana", size=q_size, weight="bold")
            ctk.CTkLabel(card, text=q_str, font=q_font, text_color=TEXT_COLOR).pack(anchor="w", pady=2)

            # Your Answer
            ua_str = f"Your Answer: {user_ans}"
            ua_size = _fit_font_size(ua_str, max_label_width, family="Verdana", min_size=8, max_size=30)
            ua_font = ctk.CTkFont(family="Verdana", size=ua_size)
            ctk.CTkLabel(card, text=ua_str, font=ua_font, text_color=TEXT_COLOR).pack(anchor="w")

            # Correct Answer
            ca_str = f"Correct Answer: {correct_ans}"
            ca_size = _fit_font_size(ca_str, max_label_width, family="Verdana", min_size=8, max_size=30)
            ca_font = ctk.CTkFont(family="Verdana", size=ca_size)
            ctk.CTkLabel(card, text=ca_str, font=ca_font, text_color=TEXT_COLOR).pack(anchor="w")

            # Result
            res_str = "Correct ✅" if is_correct else "Incorrect ❌"
            r_size = _fit_font_size(res_str, max_label_width, family="Verdana", min_size=8, max_size=30)
            r_font = ctk.CTkFont(family="Verdana", size=r_size)
            ctk.CTkLabel(card, text=res_str, font=r_font,
                         text_color=("green" if is_correct else "red")).pack(anchor="w")

        back_btn = ctk.CTkButton(scroll, text="Back To Quizzes", command=self.destroy,
                                 fg_color="#6A0DAD", hover_color="#600E99",
                                 text_color="white", font=ctk.CTkFont("Verdana", 14, "bold"),
                                 corner_radius=8)
        back_btn.pack(pady=10)
