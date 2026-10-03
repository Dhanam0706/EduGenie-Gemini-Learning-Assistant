# EduGenie: Google Gemini Powered Learning Assistant

## Project Description

EduGenie is a lightweight AI-powered educational assistant that simplifies learning with Google Gemini. Built for students, it lets users:

* Ask questions and receive clear, concise answers (including follow-up questions)
* Understand complex concepts through structured explanations
* Generate multiple-choice quizzes from a topic or text
* Summarize long study material
* Get a beginner-to-advanced learning path for any topic

It is built with **FastAPI** for the backend and a simple **HTML + CSS** frontend.

## Scenarios

**Scenario 1:** A student asks "Which is the largest ocean?" using *Ask a question*.

**Scenario 2:** A student wants to test their understanding of "The Pythagoras Theorem" and clicks *Generate a quiz*.

**Scenario 3:** A learner exploring SQL asks for a *learning path* with beginner-to-advanced topics, timelines and resources.

## Architecture / Workflow

```
Browser (templates/index.html + static/style.css)
        |  POST JSON {text, context}
        v
FastAPI (main.py)  -- validates input -->  module for the chosen task
        |                                     qna.py / explanation_module.py / quiz_module.py
        |                                     summary_module.py / learning_path.py
        v                                     |
   JSON response  <--------------------  gemini_client.py  -->  Google Gemini API
```

## Technologies Used

Python 3.10+, FastAPI, Uvicorn, Jinja2, HTML and CSS, Google Gemini API (`google-genai`), python-dotenv, pytest.

## Pre-requisites

1. **Python 3.10+** - download from python.org (tick "Add Python to PATH"), then check with `python --version`.
2. **FastAPI, Uvicorn, Jinja2** - installed from `requirements.txt`.
3. **HTML and CSS** - basic templating used in `/templates` and `/static`.
4. **Google Gemini API key**
   1. Open [Google AI Studio](https://aistudio.google.com/) and sign in.
   2. Create an API key.
   3. Store it safely. Never commit it.

## Folder Architecture

```
EduGenie/
├── main.py                 # FastAPI app and API endpoints
├── gemini_client.py        # Shared Gemini call, API key and error handling
├── explanation_module.py   # Concept explanation logic
├── qna.py                  # Question answering (and follow-ups)
├── quiz_module.py          # Quiz generation
├── summary_module.py       # Summarization
├── learning_path.py        # Learning recommendations
├── templates/index.html    # HTML frontend
├── static/style.css        # Styling
├── tests/test_edugenie.py  # Automated tests
├── requirements.txt        # Python dependencies
├── pytest.ini              # Test configuration
├── .env.example            # Example environment variables
└── .gitignore
```

## Installation

```bash
git clone <your-repo-url>
cd EduGenie
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill it in:

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key |
| `GEMINI_MODEL` | No | Gemini model name (default `gemini-3.8-flash`). Check the [current model list](https://ai.google.dev/gemini-api/docs/models) if Google retires a model. |

`.env` is listed in `.gitignore`, so your key is never pushed to GitHub.

## Project Workflow

### Milestone 1: Model Selection and Architecture
* Gemini (via API) is used for Q&A, explanations, summarization, quiz generation and learning paths.
* `gemini_client.py` holds the single Gemini call so the key and errors are handled in one place.

### Milestone 2: Core Functionalities
* **Explanation module** - structured, beginner-friendly explanation.
* **QnA module** - answers questions; an optional `context` supports follow-ups.
* **Quiz module** - three MCQs with four options each, returned as JSON. `clean_json_block` removes Markdown fences before parsing.
* **Summary module** - short bullet-point summary for revision.
* **Learning path module** - beginner to advanced plan with resources.

**Backend API with FastAPI** - one endpoint per module:

| Method | Endpoint | Body | Returns |
|---|---|---|---|
| GET | `/` | - | The web page |
| POST | `/qa` | `{"text": "...", "context": "optional"}` | `{"result": "..."}` |
| POST | `/explain` | `{"text": "..."}` | `{"result": "..."}` |
| POST | `/quiz` | `{"text": "..."}` | `{"questions": [{"question", "options", "answer_index"}]}` |
| POST | `/summarize` | `{"text": "..."}` | `{"result": "..."}` |
| POST | `/learn/recommendations` | `{"text": "..."}` | `{"result": "..."}` |

Errors return `{"detail": "friendly message"}` with status 400 (empty or too long input), 422 (invalid request), 429 (Gemini rate limit), 500 (missing API key or unexpected error) or 502 (Gemini failure). API keys and stack traces are never shown.

### Milestone 3: Frontend Development
* `templates/index.html`: task dropdown (Explain, QnA, Quiz, Summary, Recommend Path), text area, submit button, and a follow-up checkbox for QnA.
* `static/style.css`: responsive design, styled buttons, input area and result container.
* The form sends a POST request to FastAPI and the result appears below the input box. Quiz answers turn green or red and show the correct answer when a wrong option is chosen.

### Milestone 4: Deployment

**Run locally**

```bash
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000

**Functional testing (manual)**
1. Ask a question - "What is a Turing machine?"
2. Get an explanation - "Process synchronization"
3. Generate a quiz - "Pythagoras theorem"
4. Summarize content - paste a paragraph
5. Get a learning plan - "SQL"
6. Tick *follow-up* after a question and ask "Can you give an example?"

## Testing

Automated tests use a mocked Gemini, so they need no API key or internet:

```bash
pytest
```

They cover: valid question, follow-up, empty and invalid input, summary, quiz generation, bad quiz output, Gemini API failure, missing API key, and frontend-to-backend communication.

## Team Responsibilities

| Member | Area | Main files |
|---|---|---|
| 1 | Prerequisites, setup, configuration, Gemini API setup | `requirements.txt`, `.env.example`, `.gitignore`, `gemini_client.py` |
| 2 | Core AI functionality | `qna.py`, `explanation_module.py`, `quiz_module.py`, `summary_module.py`, `learning_path.py` |
| 3 | Backend / FastAPI and API integration | `main.py` |
| 4 | Frontend / web interface | `templates/index.html`, `static/style.css` |
| 5 | Testing, local execution, documentation, future enhancements | `tests/`, `README.md`, `pytest.ini` |

## Future Enhancements

* Voice input and output
* Multilingual support
* Mobile app with offline features
* Progress tracking dashboard, badges and learning streaks
* Adaptive learning paths based on quiz results
* PDF and image input for doubt solving and summaries
* Teacher/parent dashboards and LMS integration (Moodle, Google Classroom)

## Conclusion

EduGenie combines cloud AI with a simple, low-footprint web interface to make learning easier. Its modular design keeps each feature in its own file, so it is easy to understand, test and extend.
