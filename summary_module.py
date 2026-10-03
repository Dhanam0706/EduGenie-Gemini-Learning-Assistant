"""Summarization module.

Depends on: gemini_client.py
"""

import gemini_client


def summarize_text(text: str) -> str:
    """Summarize study material into its important points."""
    prompt = (
        "You are EduGenie, a study assistant. Summarize the study material below "
        "for quick revision.\n"
        "Include only the important points as short bullet points, keep key terms "
        "and definitions, and leave out repetition and unnecessary detail. "
        "Do not add facts that are not in the material.\n\n"
        f"Study material:\n{text}"
    )
    return gemini_client.generate(prompt)
