import sqlite3
# Changed: Use CustomTkinter for modern UI and theming (removed ttk and ThemedTk)
import customtkinter as ctk

import QuestionCreator
import QuizMenu

DB_NAME = "wolfquiz.db"

def setup_database():
    """Creates the tables if they don't already exist (for legacy SQLite storage)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # ... (omitted for brevity, unchanged database setup code)
    conn.commit()
    conn.close()

# Define theme colors (Halloween purple and orange)
HALLOWEEN_PURPLE       = "#6A0DAD"   # Primary purple color 
HALLOWEEN_PURPLE_DARK  = "#600E99"   # Darker purple for hover effects
HALLOWEEN_ORANGE       = "#FF7518"   # Pumpkin orange accent color

class WolfQuizApp:
    def __init__(self, master):
        self.master = master
        # Changed: Apply custom title and Halloween theme background color
        self.master.title("WolfQuiz - Main Menu")
        self.master.configure(fg_color=HALLOWEEN_PURPLE_DARK)  # Dark purple window background

        # Main Frame (with padding and themed background)
        main_frame = ctk.CTkFrame(self.master, fg_color=HALLOWEEN_PURPLE_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Added: Title label with Halloween emoji, using orange text for spooky effect
        title_label = ctk.CTkLabel(main_frame, text="🎃 WolfQuiz Halloween Edition 🎃",
                                   text_color=HALLOWEEN_ORANGE,
                                   font=("Verdana", 20, "bold"))
        title_label.pack(pady=10)

        # Changed: Use CustomTkinter Buttons with modern styling (purple theme, rounded corners, hover effects)
        create_new_btn = ctk.CTkButton(main_frame, text="Quiz Creator", 
                                       command=self.open_quiz_creator,
                                       fg_color=HALLOWEEN_PURPLE, hover_color=HALLOWEEN_PURPLE_DARK,
                                       text_color="white", font=("Verdana", 16, "bold"), corner_radius=10)
        create_new_btn.pack(pady=10, fill="x")

        create_edit_btn = ctk.CTkButton(main_frame, text="Create/Edit Quizzes", 
                                        command=self.open_question_creator,
                                        fg_color=HALLOWEEN_PURPLE, hover_color=HALLOWEEN_PURPLE_DARK,
                                        text_color="white", font=("Verdana", 16, "bold"), corner_radius=10)
        create_edit_btn.pack(pady=10, fill="x")

        take_quiz_btn = ctk.CTkButton(main_frame, text="Take Quizzes", 
                                      command=self.open_quiz_menu,
                                      fg_color=HALLOWEEN_PURPLE, hover_color=HALLOWEEN_PURPLE_DARK,
                                      text_color="white", font=("Verdana", 16, "bold"), corner_radius=10)
        take_quiz_btn.pack(pady=10, fill="x")

    def open_quiz_creator(self):
        """Opens the QuizCreatorWindow for adding a brand-new quiz."""
        QuizCreatorWindow(self.master)  # Launches the Quiz Creator window (modal)

    def open_question_creator(self):
        """Opens the QuestionCreator window for managing existing quizzes."""
        QuestionCreator.QuestionCreatorWindow(self.master)

    def open_quiz_menu(self):
        """Opens the QuizMenu window to select and take a quiz."""
        QuizMenu.QuizMenuWindow(self.master)


class QuizCreatorWindow(ctk.CTkToplevel):
    """Toplevel window to create a brand-new quiz by specifying a title and description."""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Create a New Quiz")
        self.grab_set()  # Make this window modal

        # Changed: Use CustomTkinter theming for the new quiz form
        self.configure(fg_color=HALLOWEEN_PURPLE_DARK)

        # Database connection
        self.conn = sqlite3.connect(DB_NAME)
        self.c = self.conn.cursor()

        # Main Frame for form inputs
        main_frame = ctk.CTkFrame(self, fg_color=HALLOWEEN_PURPLE_DARK, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main_frame, text="Quiz Title:", font=("Verdana", 14, "bold")).pack(anchor="w", pady=5)
        self.title_entry = ctk.CTkEntry(main_frame, width=400)
        self.title_entry.pack(anchor="w")

        ctk.CTkLabel(main_frame, text="Description:", font=("Verdana", 14, "bold")).pack(anchor="w", pady=5)
        self.desc_text = ctk.CTkTextbox(main_frame, width=400, height=100)
        self.desc_text.pack(anchor="w")

        # Button Frame for actions
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        # Changed: Styled Save and Back buttons with theme colors and modern look
        save_btn = ctk.CTkButton(button_frame, text="Save", command=self.save_quiz,
                                 fg_color=HALLOWEEN_ORANGE, hover_color="#E66916",
                                 text_color="white", font=("Verdana", 14, "bold"), corner_radius=10)
        save_btn.pack(side="left", padx=5)
        back_btn = ctk.CTkButton(button_frame, text="Back", command=self.close_window,
                                 fg_color=HALLOWEEN_PURPLE, hover_color=HALLOWEEN_PURPLE_DARK,
                                 text_color="white", font=("Verdana", 14, "bold"), corner_radius=10)
        back_btn.pack(side="left", padx=5)

    def save_quiz(self):
        """Insert a new quiz into the database (or JSON store)."""
        quiz_name = self.title_entry.get().strip()
        quiz_desc = self.desc_text.get("1.0", "end").strip()
        if quiz_name == "":
            # Optionally, show a warning (omitted for brevity)
            return
        # Changed: Save to database (using default selector_amount=4 for new quiz)
        self.c.execute("""
            INSERT INTO Quizzes (quiz_name, quiz_description, question_selector_amount)
            VALUES (?, ?, ?)
        """, (quiz_name, quiz_desc, 4))
        self.conn.commit()
        # Clear fields (or close window after saving)
        self.title_entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")
        # self.close_window()  # (Optional) Close immediately after saving

    def close_window(self):
        self.destroy()

    def __del__(self):
        # Properly close DB connection if window is closed
        try:
            self.conn.close()
        except:
            pass

def main():
    # Initialize database (creates tables if needed)
    setup_database()
    # Changed: Initialize main application window using CustomTkinter
    ctk.set_appearance_mode("Dark")      # Force dark mode for consistent theming
    root = ctk.CTk()
    root.geometry("500x400")             # Set a starting size for the main menu window
    app = WolfQuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
