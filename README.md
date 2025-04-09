# WolfQuiz

**WolfQuiz** is a fully GUI-based Python quiz application using `tkinter`, `ttkthemes`, and `customtkinter`. You can create quizzes, edit questions and answers, take quizzes with styled multiple-choice questions, and view your results in a fullscreen view. You can also bulk-import quizzes from a JSON file using the included `import.py` script.

---

## 🚀 Features

- Create and manage multiple quizzes with different questions
- Support for multiple-choice and True/False questions
- View results with automatic grading and visual feedback
- Import quiz data using `import.py`
- Stylish modern UI using `customtkinter`

---

## 📦 Installation

1. **Clone or Download the Repo**:

   ```bash
   git clone https://github.com/your-username/WolfQuiz.git
   cd WolfQuiz
   ```

2. **Install Dependencies**:

   ```bash
   pip install customtkinter ttkthemes
   ```

3. **Run the App**:

   ```bash
   python WolfQuiz.py
   ```

---

## 📥 Importing a Quiz from JSON

You can use `import.py` to import questions into an existing quiz in the database.

### How to Use

1. Make sure a quiz with the target name already exists in the app by using the quiz creator button.
2. Open `import.py` and locate this line:

   ```python
   QUIZ_NAME = "GBUS 325 Exam 3"
   ```

   Replace the value with the exact name of the quiz you want to import into.

3. Your JSON file should be named `gbus325_exam1.json` or you can modify the filename in the script:

   ```python
   with open("gbus325_exam1.json", "r", encoding="utf-8") as file:
   ```

   *You can keep the name as-is if you like, or change it to your filename.*

4. Run:

   ```bash
   python import.py
   ```

### JSON Structure

```json
[
  {
    "question_text": "What is the capital of France?",
    "is_true_false": false,
    "correct_answer": "Paris",
    "false_answers": ["London", "Berlin", "Madrid"]
  },
  {
    "question_text": "The sky is blue.",
    "is_true_false": true,
    "correct_answer": "True",
    "false_answers": []
  }
]
```

- `question_text`: The question itself.
- `is_true_false`: `true` or `false` depending on question type.
- `correct_answer`: The right answer.
- `false_answers`: A list of incorrect answers (empty if it's True/False).

---

## 🧠 Using the App

1. Launch the app:

   ```bash
   python WolfQuiz.py
   ```

2. Choose from the main menu:
   - **Quiz Creator**: Create a new quiz (title + description).
   - **Create/Edit Quizzes**: Manage questions, answers, and false answers.
   - **Take Quizzes**: Select a quiz to take. Answers are multiple-choice, with visual feedback.

3. After completing a quiz, you’ll see your score, letter grade, and detailed results.

---

## 🧑‍💻 Contributions

Feel free to fork this repo and enhance the application. PRs welcome!

---

## 📄 License

MIT License. Use freely for educational or personal projects.

---
