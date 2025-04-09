# WolfQuiz.py
import tkinter as tk
from tkinter import ttk
import sqlite3

# For the dark theme (Equilux)
from ttkthemes import ThemedTk, ThemedStyle

import QuestionCreator
import QuizMenu

DB_NAME = "wolfquiz.db"


def setup_database():
    """
    Creates the tables if they don't already exist.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create Quizzes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Quizzes (
            quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_name TEXT NOT NULL,
            quiz_description TEXT,
            question_selector_amount INTEGER DEFAULT 4
        )
    ''')

    # Create Questions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_text TEXT NOT NULL,
            is_true_false BOOLEAN DEFAULT 0
        )
    ''')

    # Create Answers table (for correct answers)
    c.execute('''
        CREATE TABLE IF NOT EXISTS Answers (
            answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            answer_text TEXT NOT NULL
        )
    ''')

    # Create FalseAnswers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS FalseAnswers (
            falseanswer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            false_answer_text TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


class WolfQuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("WolfQuiz - Main Menu")

        # Main Frame
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Button: Create a Brand-New Quiz
        create_new_quiz_btn = ttk.Button(main_frame, text="Quiz Creator", command=self.open_quiz_creator)
        create_new_quiz_btn.pack(pady=10)

        # Button: Create/Edit Quizzes (existing question/answer editor)
        create_edit_btn = ttk.Button(main_frame, text="Create/Edit Quizzes", command=self.open_question_creator)
        create_edit_btn.pack(pady=10)

        # Button: Take Quizzes
        quizzes_btn = ttk.Button(main_frame, text="Take Quizzes", command=self.open_quiz_menu)
        quizzes_btn.pack(pady=10)

    def open_quiz_creator(self):
        """Opens the QuizCreatorWindow for adding a brand-new quiz."""
        QuizCreatorWindow(self.master)

    def open_question_creator(self):
        """Opens the QuestionCreator window (existing)."""
        QuestionCreator.QuestionCreatorWindow(self.master)

    def open_quiz_menu(self):
        """Opens the QuizMenu window (existing)."""
        QuizMenu.QuizMenuWindow(self.master)


class QuizCreatorWindow(tk.Toplevel):
    """
    A simple Toplevel window that allows the user to create a
    brand-new quiz by specifying a title and description.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Create a New Quiz")
        self.grab_set()  # Make this window modal-like

        # Apply the Equilux theme to this Toplevel
        style = ThemedStyle(self)
        style.set_theme("equilux")

        # Database connection
        self.conn = sqlite3.connect(DB_NAME)
        self.c = self.conn.cursor()

        # Main Frame
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text="Quiz Title:").pack(anchor="w", pady=5)
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.pack(anchor="w")

        # Description
        ttk.Label(main_frame, text="Description:").pack(anchor="w", pady=5)
        self.desc_text = tk.Text(main_frame, width=50, height=5)
        self.desc_text.pack(anchor="w")

        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        # Save Button
        save_btn = ttk.Button(button_frame, text="Save", command=self.save_quiz)
        save_btn.pack(side="left", padx=5)

        # Back Button
        back_btn = ttk.Button(button_frame, text="Back", command=self.close_window)
        back_btn.pack(side="left", padx=5)

    def save_quiz(self):
        """Insert a new quiz into the database."""
        quiz_name = self.title_entry.get().strip()
        quiz_desc = self.desc_text.get("1.0", tk.END).strip()

        if quiz_name == "":
            # You might want to show a warning or something similar
            return

        # Insert the new quiz with default question_selector_amount = 4 (you can customize)
        self.c.execute("""
            INSERT INTO Quizzes (quiz_name, quiz_description, question_selector_amount)
            VALUES (?, ?, ?)
        """, (quiz_name, quiz_desc, 4))
        self.conn.commit()

        # Optionally clear the fields or close the window
        self.title_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)

        # You could also close immediately after saving:
        # self.close_window()

    def close_window(self):
        self.destroy()

    def __del__(self):
        # Properly close DB connection if this window closes
        try:
            self.conn.close()
        except:
            pass


def main():
    # Initialize DB (creates tables if needed)
    setup_database()

    # Create root window with Equilux theme
    root = ThemedTk(theme="equilux")
    app = WolfQuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
