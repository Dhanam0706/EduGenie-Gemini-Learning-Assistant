"""Learning recommendations module.

Depends on: gemini_client.py
"""

import gemini_client


def get_learning_recommendations(topic: str) -> str:
    """Create a beginner-to-advanced learning path for a topic."""
    prompt = (
        "You are EduGenie, a learning guide. Create a structured learning path for "
        "the topic below.\n"
        "Organize it as Beginner, Intermediate and Advanced stages. For each stage "
        "list the concepts to learn, a rough time estimate, and one or two kinds of "
        "resources (for example a book, a video course or a practice site). "
        "Finish with a short tip on how to stay consistent.\n\n"
        f"Topic: {topic}"
    )
    return gemini_client.generate(prompt)
