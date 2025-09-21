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
   git clone https://github.com/nbrown2000/WolfQuiz.git
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

### JSON Structure
Initial Structure:
```json
{
  "quiz_id": "fd582257-1848-55fc-b82c-9ce697ae6475",
  "quiz_name": "MGT-350 Exam 1",
  "quiz_description": "Chapters 1\u20135 combined: Managing & Performing, Decision Making, History of Management, External/Internal Environments & Corporate Culture, and Ethics/CSR/Sustainability.",
  "question_selector_amount": 125,
  "questions": [
```
- `quiz_id`: The id of the quiz, leftover from database.
- `quiz_name`: Name of the quiz
- `quiz_description`: The description of what the quiz is about
- `question_selector_amount`: The amount of questions


```json
[
  {
    "question_text": "What is the capital of France?",
    "is_true_false": false,
    "correct_answer": "Paris",
    "false_answers": ["London", "Berlin", "Madrid"],
"question_id": "77fe2d7f-1e21-5992-86e9-d3e8766b09ad"
  },
  {
    "question_text": "The sky is blue.",
    "is_true_false": true,
    "correct_answer": "True",
    "false_answers": [],
    "question_id": "77fe2d7f-1e21-5992-86e9-d3e8766b09ad"
  }
]
```

- `question_text`: The question itself.
- `is_true_false`: `true` or `false` depending on question type.
- `correct_answer`: The right answer.
- `false_answers`: A list of incorrect answers (empty if it's True/False).
- `question_id`: The id of the question, this was leftover from when I had a database so I had to keep it.

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
