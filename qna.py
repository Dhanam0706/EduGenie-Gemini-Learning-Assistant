"""Question answering module.

Answers academic questions and optional follow-up questions.

Depends on: gemini_client.py
"""

import gemini_client


def answer_question(question: str, context: str = "") -> str:
    """Answer a student's question. `context` is the previous answer when the
    student asks a follow-up question."""
    prompt = (
        "You are EduGenie, a patient learning assistant for students.\n"
        "Answer the question below clearly and accurately. Keep it concise but "
        "complete, use short paragraphs or bullet points, and add a small example "
        "when it helps. If the question is not an academic or learning question, "
        "politely steer the student back to learning.\n\n"
    )
    if context.strip():
        prompt += (
            "This is a follow-up question. Here is the earlier conversation for context:\n"
            f"{context.strip()}\n\n"
        )
    prompt += f"Question: {question}"
    return gemini_client.generate(prompt)
