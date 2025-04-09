# QuizTake.py
import customtkinter as ctk
import tkinter as tk
import sqlite3
import random
import Results

DB_NAME = "wolfquiz.db"

# ========================
# CONSTANTS & STYLE CONFIG
# ========================
BG_MAIN = "#1c1c1c"          # Background for area below the question box
QUESTION_BOX_BG = "#000000"  # Pure black for the question box
TEXT_COLOR = "#ffffff"       # White for most text

# Colors for answer option rectangles:
ANSWER_NORMAL   = "#3498db"  # Normal blue
ANSWER_HOVER    = "#2980b9"  # Darker blue on hover
ANSWER_SELECTED = "#1c5980"  # Even darker when selected
OFFSET_COLOR    = "#2c7fc5"  # Slightly darker blue for the drop-shadow

# Colors for navigation buttons:
NAV_NORMAL   = "#3498db"
NAV_HOVER    = "#2980b9"

# Fonts
QUESTION_FONT = ("Helvetica", 24, "bold")
ANSWER_FONT   = ("Helvetica", 16, "bold")
NAV_FONT      = ("Helvetica", 14, "bold")

# ========================
# CUSTOM WIDGET CLASSES
# ========================

class QuestionBox(tk.Canvas):
    """A canvas that displays the question text in bold white with a drop shadow,
    on a black background (the question box)."""
    def __init__(self, parent, width, height, **kwargs):
        super().__init__(parent, width=width, height=height, bg=QUESTION_BOX_BG, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height

    def set_text(self, text):
        self.delete("all")
        x = self.width // 2
        y = self.height // 2
        wrap_width = self.width - 40  # wrap slightly within canvas width
        # Draw shadow text (offset by 2 pixels)
        self.create_text(
            x+2, y+2, text=text, font=QUESTION_FONT, fill="gray",
            anchor="center", width=wrap_width, justify="center"
        )
        # Draw main text on top
        self.create_text(x, y, text=text, font=QUESTION_FONT, fill=TEXT_COLOR, anchor="center", 
                     width=wrap_width, justify="center")



class AnswerRectangle(ctk.CTkFrame):
    """
    A custom clickable “rectangle” (answer option) using customtkinter.
    The outer container uses the BG_MAIN so no extra black box appears.
    An offset frame with OFFSET_COLOR is placed at x=0, y=3 to serve as the drop-shadow,
    and the inner frame (the actual button face) sits on top.
    """
    def __init__(self, parent, text, command, width=300, height=100, corner_radius=10):
        # Outer container blends with the background.
        super().__init__(parent, width=width, height=height, fg_color=BG_MAIN, corner_radius=corner_radius)
        self.command = command
        self.selected = False
        self.normal_color = ANSWER_NORMAL
        self.hover_color = ANSWER_HOVER
        self.selected_color = ANSWER_SELECTED

        # Create the offset (drop-shadow) frame with the darker blue.
        self.offset_frame = ctk.CTkFrame(self, width=width, height=height, fg_color=OFFSET_COLOR, corner_radius=corner_radius)
        self.offset_frame.place(x=0, y=3)  # Now placed 3 pixels BELOW the main face

        # Create the inner button frame (the main face) on top of the offset.
        self.inner = ctk.CTkFrame(self.offset_frame, width=width, height=height, fg_color=self.normal_color, corner_radius=corner_radius)
        self.inner.place(x=0, y=0, relwidth=1, relheight=1)

        # Create text labels for the answer text (with a slight text shadow)
        self.label_shadow = ctk.CTkLabel(
            self.inner, text=text, font=ANSWER_FONT,
            fg_color=self.normal_color, text_color="gray",
            wraplength=width - 20,  # Add wraplength here
            justify="center"        # Add justify here
        )
        self.label_shadow.place(relx=0.5, rely=0.5, anchor="center", x=2, y=2)
        self.label = ctk.CTkLabel(
            self.inner, text=text, font=ANSWER_FONT,
            fg_color=self.normal_color, text_color=TEXT_COLOR,
            wraplength=width - 20,  # Add wraplength here
            justify="center"        # Add justify="center" here
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        # Bind hover and click events
        self.inner.bind("<Enter>", self.on_enter)
        self.inner.bind("<Leave>", self.on_leave)
        self.inner.bind("<Button-1>", self.on_click)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        self.label_shadow.bind("<Enter>", self.on_enter)
        self.label_shadow.bind("<Leave>", self.on_leave)
        self.label_shadow.bind("<Button-1>", self.on_click)

    def on_enter(self, event):
        if not self.selected:
            self.set_color(self.hover_color)

    def on_leave(self, event):
        if not self.selected:
            self.set_color(self.normal_color)

    def on_click(self, event):
        self.command(self)

    def set_color(self, color):
        self.inner.configure(fg_color=color)
        self.label.configure(fg_color=color)
        self.label_shadow.configure(fg_color=color)

    def select(self, selected=True):
        self.selected = selected
        if selected:
            self.set_color(self.selected_color)
        else:
            self.set_color(self.normal_color)


class NavButton(ctk.CTkFrame):
    """
    A custom navigation button (Back/Next) using customtkinter.
    Uses the same technique as AnswerRectangle: an outer container (with BG_MAIN),
    an offset frame (the drop-shadow) with OFFSET_COLOR placed at x=0, y=3,
    and an inner button frame.
    """
    def __init__(self, parent, text, command, width=120, height=50, corner_radius=10):
        super().__init__(parent, width=width, height=height, fg_color=BG_MAIN, corner_radius=corner_radius)
        self.command = command
        self.normal_color = NAV_NORMAL
        self.hover_color = NAV_HOVER

        self.offset_frame = ctk.CTkFrame(self, width=width, height=height, fg_color=OFFSET_COLOR, corner_radius=corner_radius)
        self.offset_frame.place(x=0, y=3)  # Offset placed 3 pixels below the main face
        self.inner = ctk.CTkFrame(self.offset_frame, width=width, height=height, fg_color=self.normal_color, corner_radius=corner_radius)
        self.inner.place(x=0, y=0, relwidth=1, relheight=1)

        self.label_shadow = ctk.CTkLabel(self.inner, text=text, font=NAV_FONT, fg_color=self.normal_color, text_color="gray")
        self.label_shadow.place(relx=0.5, rely=0.5, anchor="center", x=1, y=1)
        self.label = ctk.CTkLabel(self.inner, text=text, font=NAV_FONT, fg_color=self.normal_color, text_color=TEXT_COLOR)
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        self.inner.bind("<Enter>", self.on_enter)
        self.inner.bind("<Leave>", self.on_leave)
        self.inner.bind("<Button-1>", self.on_click)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        self.label_shadow.bind("<Enter>", self.on_enter)
        self.label_shadow.bind("<Leave>", self.on_leave)
        self.label_shadow.bind("<Button-1>", self.on_click)

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

    def update_text(self, new_text):
        self.label.configure(text=new_text)
        self.label_shadow.configure(text=new_text)


class QuizTakeWindow(ctk.CTkToplevel):
    def __init__(self, master, quiz_id):
        super().__init__(master)
        self.title("Take Quiz")
        self.quiz_id = quiz_id
        self.state('zoomed')  # Windowed fullscreen
        self.configure(bg=BG_MAIN)
        self.grab_set()  # Make modal

        self.conn = sqlite3.connect(DB_NAME)
        self.c = self.conn.cursor()

        # Get all questions for this quiz
        self.c.execute("SELECT question_id, question_text, is_true_false FROM Questions WHERE quiz_id = ?", (self.quiz_id,))
        self.questions = self.c.fetchall()  # List of (q_id, q_text, is_tf)

        self.current_index = 0  # Current question index
        self.user_answers = [None] * len(self.questions)  # Store user selections
        self.answer_widgets = []  # Will store our AnswerRectangle widgets

        # Main layout frame
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.main_frame.pack(fill="both", expand=True)

        # Question box at the top
        self.question_box = QuestionBox(self.main_frame, width=self.winfo_screenwidth(), height=150)
        self.question_box.pack(pady=20)

        # Frame for answer options
        self.answers_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_MAIN)
        self.answers_frame.pack(pady=20)

        # Navigation frame (Back on left, Next/Finish on right)
        self.nav_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_MAIN)
        self.nav_frame.pack(fill="x", pady=20)
        self.back_btn = NavButton(self.nav_frame, text="Back", command=self.go_back, width=120, height=50)
        self.next_btn = NavButton(self.nav_frame, text="Next", command=self.go_next, width=120, height=50)
        self.back_btn.pack(side="left", padx=20)
        self.next_btn.pack(side="right", padx=20)

        self.load_question(0)
        self.update_nav_buttons()

    def on_answer_click(self, selected_widget):
        """Called when an answer rectangle is clicked. Deselect all and mark the chosen one."""
        for widget in self.answer_widgets:
            widget.select(False)
        selected_widget.select(True)
        # Save the answer (the text in the widget) for the current question.
        self.user_answers[self.current_index] = selected_widget.label.cget("text")

    def load_question(self, index):
        # Clear any previous answer options
        for widget in self.answers_frame.winfo_children():
            widget.destroy()
        self.answer_widgets = []

        q_id, q_text, is_tf = self.questions[index]
        display_text = f"Question {index+1} out of {len(self.questions)}:\n{q_text}"
        self.question_box.set_text(display_text)

        # Build answer options:
        if is_tf:
            options = ["True", "False"]
        else:
            self.c.execute("SELECT answer_text FROM Answers WHERE question_id = ?", (q_id,))
            row = self.c.fetchone()
            correct_answer = row[0] if row else ""
            self.c.execute("SELECT false_answer_text FROM FalseAnswers WHERE question_id = ?", (q_id,))
            false_answers = [fa[0] for fa in self.c.fetchall()]
            options = [correct_answer] + false_answers
            random.shuffle(options)
        
        num_options = len(options)
        # For True/False (2 options), display them in one centered row.
        if num_options == 2:
            for i, opt in enumerate(options):
                widget = AnswerRectangle(self.answers_frame, text=opt, command=self.on_answer_click)
                widget.grid(row=0, column=i, padx=20, pady=20)
                self.answer_widgets.append(widget)
                if self.user_answers[self.current_index] == opt:
                    widget.select(True)
        else:
            # Assume 4 options – arrange them in a 2x2 grid.
            for i, opt in enumerate(options):
                row = i // 2
                col = i % 2
                widget = AnswerRectangle(self.answers_frame, text=opt, command=self.on_answer_click)
                widget.grid(row=row, column=col, padx=20, pady=20)
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
        if self.current_index == 0:
            self.back_btn.pack_forget()
        else:
            self.back_btn.pack(side="left", padx=20)
        if self.current_index == len(self.questions) - 1:
            self.next_btn.update_text("Finish")
        else:
            self.next_btn.update_text("Next")

    def finish_quiz(self):
        result_data = []
        for i, (q_id, q_text, is_tf) in enumerate(self.questions):
            user_ans = self.user_answers[i]
            if is_tf:
                self.c.execute("SELECT answer_text FROM Answers WHERE question_id=?", (q_id,))
                row = self.c.fetchone()
                correct_ans = row[0] if row else ""
            else:
                self.c.execute("SELECT answer_text FROM Answers WHERE question_id=?", (q_id,))
                row = self.c.fetchone()
                correct_ans = row[0] if row else ""
            is_correct = (user_ans == correct_ans)
            result_data.append((q_text, user_ans, correct_ans, is_correct))
        self.conn.close()
        Results.ResultsWindow(self.master, result_data)
        self.destroy()


# ---------------------
# To test this module, run the following:
if __name__ == "__main__":
    root = ctk.CTk()  # Main customtkinter window
    root.withdraw()
    QuizTakeWindow(root, quiz_id=1)
    root.mainloop()
