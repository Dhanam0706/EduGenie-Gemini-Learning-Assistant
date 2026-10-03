"""EduGenie: Google Gemini Powered Learning Assistant - FastAPI app.

Run with:  uvicorn main:app --reload
Open:      http://127.0.0.1:8000

Each endpoint validates the input and calls the matching module.

Depends on: gemini_client.py, qna.py, explanation_module.py, quiz_module.py,
            summary_module.py, learning_path.py, templates/index.html, static/style.css
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from explanation_module import explain_concept
from gemini_client import GeminiError
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

logger = logging.getLogger("edugenie")

BASE_DIR = Path(__file__).resolve().parent
MAX_INPUT_CHARS = 8000

app = FastAPI(title="EduGenie: Google Gemini Powered Learning Assistant")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class UserRequest(BaseModel):
    text: str
    context: str = ""  # previous answer, used for follow-up questions on /qa


# ---------- error handling ----------

@app.exception_handler(GeminiError)
async def gemini_error_handler(request: Request, exc: GeminiError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request. Please send your text as a string in the 'text' field."},
    )


def _validated_text(request_body: UserRequest) -> str:
    text = request_body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Please enter a question or topic first.")
    if len(text) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"Your input is too long. Please keep it under {MAX_INPUT_CHARS} characters.",
        )
    return text


def _run(func, *args):
    """Call a module function; hide unexpected errors behind a friendly message."""
    try:
        return func(*args)
    except GeminiError:
        raise
    except Exception:
        logger.exception("Unexpected error in %s", getattr(func, "__name__", "module"))
        raise GeminiError("Something unexpected went wrong. Please try again.", status_code=500)


# ---------- pages ----------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


# ---------- API endpoints (one per module) ----------

@app.post("/qa")
async def qa(body: UserRequest):
    text = _validated_text(body)
    return {"result": _run(answer_question, text, body.context[:MAX_INPUT_CHARS])}


@app.post("/explain")
async def explain(body: UserRequest):
    text = _validated_text(body)
    return {"result": _run(explain_concept, text)}


@app.post("/quiz")
async def quiz(body: UserRequest):
    text = _validated_text(body)
    return {"questions": _run(generate_quiz, text)}


@app.post("/summarize")
async def summarize(body: UserRequest):
    text = _validated_text(body)
    return {"result": _run(summarize_text, text)}


@app.post("/learn/recommendations")
async def learn_recommendations(body: UserRequest):
    text = _validated_text(body)
    return {"result": _run(get_learning_recommendations, text)}
