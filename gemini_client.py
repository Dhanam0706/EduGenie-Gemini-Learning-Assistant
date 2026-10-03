"""Shared Gemini helper used by every EduGenie module.

The Common Template calls Gemini separately inside each module. To keep the
API key handling and error messages in one place, the call itself lives here
and the modules (qna.py, quiz_module.py, ...) only build prompts.

Depends on: .env (GEMINI_API_KEY, optional GEMINI_MODEL), google-genai, python-dotenv
"""

import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv()  # reads .env if present; real environment variables still win

logger = logging.getLogger("edugenie")

DEFAULT_MODEL = "gemini-3.8-flash"


class GeminiError(Exception):
    """An error whose message is safe to show to the user."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def generate(prompt: str) -> str:
    """Send a prompt to Gemini and return the response text."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiError(
            "The Gemini API key is missing. Add GEMINI_API_KEY to your .env file "
            "and restart the server.",
            status_code=500,
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=get_model_name(), contents=prompt)
    except genai_errors.APIError as exc:
        code = getattr(exc, "code", None)
        logger.warning("Gemini API error (code=%s)", code)
        if code in (401, 403):
            raise GeminiError(
                "The Gemini API key was rejected. Please check GEMINI_API_KEY.",
                status_code=502,
            )
        if code == 429:
            raise GeminiError(
                "Gemini is receiving too many requests right now. Please wait a moment and try again.",
                status_code=429,
            )
        raise GeminiError("Gemini could not complete the request. Please try again.")
    except Exception:
        # Network problems and anything unexpected. Details stay in the server log only.
        logger.exception("Could not reach Gemini")
        raise GeminiError(
            "Could not reach Gemini. Check your internet connection and try again."
        )

    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise GeminiError("Gemini returned an empty answer. Please try rephrasing your request.")
    return text.strip()
