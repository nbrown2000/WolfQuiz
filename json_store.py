
import os
import json
import uuid
from typing import Dict, List, Optional, Tuple

# Directory where all quizzes live.
QUIZZES_DIR = os.path.join(os.path.dirname(__file__), "quizzes")

def _ensure_dir() -> None:
    os.makedirs(QUIZZES_DIR, exist_ok=True)

def _slugify(name: str) -> str:
    return (
        name.strip().lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("\\", "-")
    )

def _quiz_path(slug: str) -> str:
    _ensure_dir()
    return os.path.join(QUIZZES_DIR, f"{slug}.json")

def list_quizzes() -> List[Dict]:
    """Return a list of quiz dicts (without loading every question's heavy data)."""
    _ensure_dir()
    quizzes = []
    for fn in os.listdir(QUIZZES_DIR):
        if fn.endswith(".json"):
            p = os.path.join(QUIZZES_DIR, fn)
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # normalize minimal keys
                    quizzes.append({
                        "quiz_id": data.get("quiz_id"),
                        "quiz_name": data.get("quiz_name", os.path.splitext(fn)[0]),
                        "quiz_description": data.get("quiz_description", ""),
                        "question_selector_amount": int(data.get("question_selector_amount", 4)),
                        "slug": os.path.splitext(fn)[0],
                        "question_count": len(data.get("questions", [])),
                    })
            except Exception:
                # skip broken files
                continue
    return quizzes

def load_quiz_by_id(quiz_id: str) -> Optional[Dict]:
    _ensure_dir()
    for fn in os.listdir(QUIZZES_DIR):
        if fn.endswith(".json"):
            with open(os.path.join(QUIZZES_DIR, fn), "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("quiz_id") == quiz_id:
                    return data
    return None

def load_quiz_by_slug(slug: str) -> Optional[Dict]:
    p = _quiz_path(slug)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def load_quiz_by_name(name: str) -> Optional[Dict]:
    slug = _slugify(name)
    return load_quiz_by_slug(slug)

def save_quiz(quiz: Dict) -> Dict:
    """Write quiz JSON back to disk. Returns the saved quiz (with ensured fields)."""
    _ensure_dir()
    if not quiz.get("quiz_id"):
        quiz["quiz_id"] = str(uuid.uuid4())
    if "quiz_name" not in quiz:
        raise ValueError("quiz must include 'quiz_name'")
    if "questions" not in quiz:
        quiz["questions"] = []
    if "question_selector_amount" not in quiz:
        quiz["question_selector_amount"] = 4
    if "quiz_description" not in quiz:
        quiz["quiz_description"] = ""
    slug = _slugify(quiz["quiz_name"])
    quiz["slug"] = slug
    path = _quiz_path(slug)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(quiz, f, indent=2, ensure_ascii=False)
    return quiz

def create_quiz(name: str, description: str = "", question_selector_amount: int = 4) -> Dict:
    quiz = {
        "quiz_id": str(uuid.uuid4()),
        "quiz_name": name.strip(),
        "quiz_description": description.strip(),
        "question_selector_amount": int(question_selector_amount),
        "questions": []
    }
    return save_quiz(quiz)

def update_quiz_fields(slug: str, *, name: Optional[str] = None, description: Optional[str] = None, selector_amount: Optional[int] = None) -> Dict:
    quiz = load_quiz_by_slug(slug)
    if quiz is None:
        raise FileNotFoundError(f"Quiz '{slug}' not found")
    if name is not None:
        quiz["quiz_name"] = name.strip()
    if description is not None:
        quiz["quiz_description"] = description.strip()
    if selector_amount is not None:
        quiz["question_selector_amount"] = int(selector_amount)
    return save_quiz(quiz)

def list_questions(slug: str) -> List[Dict]:
    quiz = load_quiz_by_slug(slug)
    if quiz is None:
        return []
    return quiz.get("questions", [])

def add_or_update_question(slug: str, question_id: Optional[str], question_text: str, is_true_false: bool, answer: str, false_answers: List[str]) -> Dict:
    quiz = load_quiz_by_slug(slug)
    if quiz is None:
        raise FileNotFoundError(f"Quiz '{slug}' not found")
    questions = quiz.setdefault("questions", [])
    if question_id is None:
        q = {
            "question_id": str(uuid.uuid4()),
            "question_text": question_text.strip(),
            "is_true_false": bool(is_true_false),
            "answer": answer.strip(),
            "false_answers": [] if is_true_false else [fa.strip() for fa in false_answers if fa.strip()]
        }
        questions.append(q)
    else:
        for q in questions:
            if q.get("question_id") == question_id:
                q["question_text"] = question_text.strip()
                q["is_true_false"] = bool(is_true_false)
                q["answer"] = answer.strip()
                q["false_answers"] = [] if is_true_false else [fa.strip() for fa in false_answers if fa.strip()]
                break
        else:
            # If not found, add as new
            q = {
                "question_id": question_id,
                "question_text": question_text.strip(),
                "is_true_false": bool(is_true_false),
                "answer": answer.strip(),
                "false_answers": [] if is_true_false else [fa.strip() for fa in false_answers if fa.strip()]
            }
            questions.append(q)
    return save_quiz(quiz)

def get_question(slug: str, question_id: str) -> Optional[Dict]:
    quiz = load_quiz_by_slug(slug)
    if quiz is None:
        return None
    for q in quiz.get("questions", []):
        if q.get("question_id") == question_id:
            return q
    return None
