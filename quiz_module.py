"""Quiz generation module.

Asks Gemini for three multiple-choice questions (four options each) as JSON,
cleans any Markdown code fences with clean_json_block(), and validates the result.

Depends on: gemini_client.py
"""

import json
import re

import gemini_client
from gemini_client import GeminiError

NUM_QUESTIONS = 3
LETTERS = "ABCD"


def clean_json_block(text: str) -> str:
    """Remove ```json ... ``` fences that models sometimes add around JSON."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _validate(data) -> list:
    """Check the parsed JSON and return a clean list of questions."""
    if isinstance(data, dict):
        data = data.get("questions", [])
    if not isinstance(data, list) or not data:
        raise ValueError("no questions")

    questions = []
    for item in data:
        question = str(item.get("question", "")).strip()
        options = item.get("options")
        answer = str(item.get("answer", "")).strip()
        if not question or not isinstance(options, list) or len(options) != 4:
            raise ValueError("bad question")
        options = [str(option).strip() for option in options]

        # The answer may be a letter (A-D) or the full text of an option.
        if answer.upper() in list(LETTERS):
            answer_index = LETTERS.index(answer.upper())
        elif answer in options:
            answer_index = options.index(answer)
        else:
            raise ValueError("answer not in options")

        questions.append(
            {"question": question, "options": options, "answer_index": answer_index}
        )
    return questions[:NUM_QUESTIONS]


def generate_quiz(source: str) -> list:
    """Generate multiple-choice questions from a topic or passage."""
    prompt = (
        f"You are EduGenie. Create exactly {NUM_QUESTIONS} multiple-choice questions "
        "from the topic or passage below. Each question needs exactly 4 plausible "
        "options and one correct answer.\n"
        "Return ONLY valid JSON in this format, with no extra text:\n"
        '[{"question": "...", "options": ["...", "...", "...", "..."], "answer": "A"}]\n'
        'The "answer" must be the letter (A, B, C or D) of the correct option.\n\n'
        f"Topic or passage:\n{source}"
    )
    raw = gemini_client.generate(prompt)
    try:
        return _validate(json.loads(clean_json_block(raw)))
    except (ValueError, AttributeError, TypeError):
        raise GeminiError(
            "EduGenie could not build a valid quiz this time. Please try again."
        )
