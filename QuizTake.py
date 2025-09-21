import customtkinter as ctk
import random
import Results
import json_store

# ============== THEME & STYLE CONSTANTS ==============
BG_MAIN          = "#2b1a5c"   # Dark purple background for the quiz windows
QUESTION_BOX_BG  = "#000000"   # Black background for question text box (high contrast)
TEXT_COLOR       = "#ffffff"   # White text on dark backgrounds

# Color scheme for answer buttons (orange theme with hover/selection variations)
ANSWER_NORMAL    = "#FF7518"   # Orange default for answers
ANSWER_HOVER     = "#E66916"   # Darker orange on hover
ANSWER_SELECTED  = "#CC5E13"   # Deep orange/brown when selected (pressed)
OFFSET_COLOR     = "#D35400"   # Offset shadow color (slightly darker orange)

# Color scheme for navigation buttons (purple theme)
NAV_NORMAL       = "#6A0DAD"   # Purple default for nav buttons (Back/Next)
NAV_HOVER        = "#600E99"   # Darker purple on hover
NAV_OFFSET       = "#580E8A"   # Offset shadow color for nav buttons (deep purple)

# Font styles (modern, larger fonts for clarity on screen)
QUESTION_FONT    = ("Verdana", 24, "bold")
ANSWER_FONT      = ("Verdana", 16, "bold")
NAV_FONT         = ("Verdana", 14, "bold")

class QuestionBox(ctk.CTkCanvas):
    """A custom Canvas to display the question text with a shadow effect."""
    def __init__(self, parent, width, height, **kwargs):
        super().__init__(parent, width=width, height=height, bg=QUESTION_BOX_BG,
                         highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
    def set_text(self, text):
        self.delete("all")
        x = self.width // 2
        y = self.height // 2
        wrap_width = self.width - 40
        # Draw shadowed text: a gray shadow slightly offset, then white text on top
        self.create_text(x+2, y+2, text=text, font=QUESTION_FONT, fill="gray",
                         anchor="center", width=wrap_width, justify="center")
        self.create_text(x, y, text=text, font=QUESTION_FONT, fill=TEXT_COLOR,
                         anchor="center", width=wrap_width, justify="center")

class AnswerRectangle(ctk.CTkFrame):
    """A custom widget representing an answer option as a clickable rectangle with hover/selection effects."""
    def __init__(self, parent, text, command, width=300, height=100, corner_radius=15):
        super().__init__(parent, width=width, height=height, fg_color=BG_MAIN, corner_radius=corner_radius)
        self.command = command
        self.selected = False
        # Colors for different states
        self.normal_color = ANSWER_NORMAL
        self.hover_color = ANSWER_HOVER
        self.selected_color = ANSWER_SELECTED

        # Offset shadow layer (creates a drop-shadow effect below the answer rectangle)
        self.offset_frame = ctk.CTkFrame(self, width=width, height=height,
                                         fg_color=OFFSET_COLOR, corner_radius=corner_radius)
        self.offset_frame.place(x=0, y=3)  # Slight offset downwards for shadow

        # Inner frame (actual answer button surface)
        self.inner = ctk.CTkFrame(self.offset_frame, width=width, height=height,
                                   fg_color=self.normal_color, corner_radius=corner_radius)
        self.inner.place(x=0, y=0, relwidth=1, relheight=1)

        # Answer text label with a slight shadow (duplicate text offset by 2px)
        self.label_shadow = ctk.CTkLabel(self.inner, text=text, font=ANSWER_FONT,
                                         fg_color=self.normal_color, text_color="gray",
                                         wraplength=width-20, justify="center")
        self.label_shadow.place(relx=0.5, rely=0.5, anchor="center", x=2, y=2)
        self.label = ctk.CTkLabel(self.inner, text=text, font=ANSWER_FONT,
                                  fg_color=self.normal_color, text_color=TEXT_COLOR,
                                  wraplength=width-20, justify="center")
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        # Bind hover and click events to inner frame and text for interactivity
        for widget in (self.inner, self.label, self.label_shadow):
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", self.on_click)
            # Added: Change cursor to hand pointer on hover to indicate clickability
            widget.configure(cursor="hand2")

    def on_enter(self, event):
        if not self.selected:
            self.set_color(self.hover_color)
    def on_leave(self, event):
        if not self.selected:
            self.set_color(self.normal_color)
    def on_click(self, event):
        # When clicked, notify the parent command (e.g., to record selection)
        self.command(self)
    def set_color(self, color):
        # Update the colors of inner frame and labels
        self.inner.configure(fg_color=color)
        self.label.configure(fg_color=color)
        self.label_shadow.configure(fg_color=color)
    def select(self, selected=True):
        # Mark this answer as selected or deselected
        self.selected = selected
        self.set_color(self.selected_color if selected else self.normal_color)
        # Changed: If selected, remove shadow offset (button appears pressed); if not, restore shadow
        self.offset_frame.place_configure(y=(0 if selected else 3))

class NavButton(ctk.CTkFrame):
    """A custom widget for navigation buttons (Back/Next) with similar style to AnswerRectangle."""
    def __init__(self, parent, text, command, width=120, height=50, corner_radius=10):
        super().__init__(parent, width=width, height=height, fg_color=BG_MAIN, corner_radius=corner_radius)
        self.command = command
        # Colors for nav button (no selected state, just normal/hover)
        self.normal_color = NAV_NORMAL
        self.hover_color = NAV_HOVER

        self.offset_frame = ctk.CTkFrame(self, width=width, height=height,
                                         fg_color=NAV_OFFSET, corner_radius=corner_radius)
        self.offset_frame.place(x=0, y=3)
        self.inner = ctk.CTkFrame(self.offset_frame, width=width, height=height,
                                   fg_color=self.normal_color, corner_radius=corner_radius)
        self.inner.place(x=0, y=0, relwidth=1, relheight=1)

        self.label_shadow = ctk.CTkLabel(self.inner, text=text, font=NAV_FONT,
                                         fg_color=self.normal_color, text_color="gray")
        self.label_shadow.place(relx=0.5, rely=0.5, anchor="center", x=1, y=1)
        self.label = ctk.CTkLabel(self.inner, text=text, font=NAV_FONT,
                                  fg_color=self.normal_color, text_color=TEXT_COLOR)
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        for widget in (self.inner, self.label, self.label_shadow):
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", self.on_click)
            widget.configure(cursor="hand2")  # Hand cursor on hover

    def on_enter(self, event):
        self.set_color(self.hover_color)
    def on_leave(self, event):
        self.set_color(self.normal_color)
    def on_click(self, event):
        self.command()
    def set_color(self, color):
        self.inner.configure(fg_color=color)
        self.label.configure(fg_color=color)
        self.label_shadow.configure(fg_color=color)
    def update_text(self, text):
        self.label.configure(text=text)
        self.label_shadow.configure(text=text)

class QuizTakeWindow(ctk.CTkToplevel):
    def __init__(self, master, quiz_slug: str):
        super().__init__(master)
        self.title("Take Quiz")
        self.quiz_slug = quiz_slug
        self.state('zoomed')  # Fullscreen (maximized) for game show effect
        # Changed: Set dark themed background for full window
        self.configure(fg_color=BG_MAIN)
        self.grab_set()

        quiz = json_store.load_quiz_by_slug(quiz_slug)
        self.questions = quiz.get("questions", []) if quiz else []
        self.current_index = 0
        self.user_answers = [None] * len(self.questions)
        self.answer_widgets = []

        self.main_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.main_frame.pack(fill="both", expand=True)

        # Question display box (with shadowed text canvas)
        self.question_box = QuestionBox(self.main_frame, width=self.winfo_screenwidth(), height=150)
        # Changed: Add horizontal padding so question box isn't flush against screen edges
        self.question_box.pack(padx=20, pady=20)

        # Frame to hold answer option widgets
        self.answers_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_MAIN)
        self.answers_frame.pack(pady=20)

        # Navigation buttons (Back/Next) at bottom
        self.nav_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_MAIN)
        self.nav_frame.pack(fill="x", pady=20)
        self.back_btn = NavButton(self.nav_frame, text="Back", command=self.go_back, width=120, height=50)
        self.next_btn = NavButton(self.nav_frame, text="Next", command=self.go_next, width=120, height=50)
        self.back_btn.pack(side="left", padx=20)
        self.next_btn.pack(side="right", padx=20)

        # Load the first question
        self.load_question(0)
        self.update_nav_buttons()

    def on_answer_click(self, selected_widget):
        # When an answer is clicked, mark it selected and store the answer text
        for widget in self.answer_widgets:
            widget.select(False)
        selected_widget.select(True)
        self.user_answers[self.current_index] = selected_widget.label.cget("text")

    def load_question(self, index):
        # Clear previous answer option widgets
        for widget in self.answers_frame.winfo_children():
            widget.destroy()
        self.answer_widgets = []

        q = self.questions[index]
        q_text = q.get("question_text", "")
        is_tf = bool(q.get("is_true_false", False))

        # Display the question text with numbering
        display_text = f"Question {index+1} out of {len(self.questions)}:\n{q_text}"
        self.question_box.set_text(display_text)

        # Determine answer options (True/False vs multiple choice)
        if is_tf:
            options = ["True", "False"]
        else:
            correct = q.get("answer", "")
            false_answers = list(q.get("false_answers", []))
            options = [correct] + false_answers
            random.shuffle(options)

        # Create AnswerRectangle widgets for each option
        if len(options) == 2:
            for i, opt in enumerate(options):
                widget = AnswerRectangle(self.answers_frame, text=opt, command=self.on_answer_click, width=350, height=120)
                widget.grid(row=0, column=i, padx=30, pady=30)
                self.answer_widgets.append(widget)
                # Restore selection state if navigating back to a question
                if self.user_answers[self.current_index] == opt:
                    widget.select(True)
        else:
            for i, opt in enumerate(options):
                row = i // 2
                col = i % 2
                widget = AnswerRectangle(self.answers_frame, text=opt, command=self.on_answer_click, width=350, height=120)
                widget.grid(row=row, column=col, padx=30, pady=30)
                self.answer_widgets.append(widget)
                if self.user_answers[self.current_index] == opt:
                    widget.select(True)

    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_question(self.current_index)
            self.update_nav_buttons()

    def go_next(self):
        if self.current_index == len(self.questions) - 1:
            self.finish_quiz()
            return
        self.current_index += 1
        self.load_question(self.current_index)
        self.update_nav_buttons()

    def update_nav_buttons(self):
        # Hide or show the Back button appropriately
        if self.current_index == 0:
            self.back_btn.pack_forget()
        else:
            self.back_btn.pack(side="left", padx=20)
        # Update Next button text to "Finish" on last question
        self.next_btn.update_text("Finish" if self.current_index == len(self.questions) - 1 else "Next")

    def finish_quiz(self):
        # Compile results data and open the Results window
        result_data = []
        for i, q in enumerate(self.questions):
            user_ans = self.user_answers[i]
            correct_ans = q.get("answer", "")
            result_data.append((q.get("question_text", ""), user_ans, correct_ans, user_ans == correct_ans))
        Results.ResultsWindow(self.master, result_data)
        self.destroy()

# (If run standalone for testing, initialize a CTk root and create a QuizTakeWindow)
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    root = ctk.CTk()
    root.withdraw()
    # Example usage: QuizTakeWindow(root, quiz_slug="sample-quiz")
    root.mainloop()
