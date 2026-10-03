"""EduGenie tests. Gemini is mocked, so no real API key or internet is needed.

Run with:  pytest
"""

import json

import pytest
from fastapi.testclient import TestClient

import gemini_client
from main import app

client = TestClient(app)

QUIZ_JSON = json.dumps(
    [
        {"question": f"Question {i}?", "options": ["One", "Two", "Three", "Four"], "answer": "B"}
        for i in range(1, 4)
    ]
)


def fake_gemini(reply):
    """Return a replacement for gemini_client.generate that gives a fixed reply."""
    calls = []

    def _fake(prompt):
        calls.append(prompt)
        return reply

    _fake.calls = calls
    return _fake


# 1. valid question
def test_valid_question(monkeypatch):
    fake = fake_gemini("A Turing machine is a model of computation.")
    monkeypatch.setattr(gemini_client, "generate", fake)
    response = client.post("/qa", json={"text": "What is a Turing machine?"})
    assert response.status_code == 200
    assert "Turing machine" in response.json()["result"]
    assert "What is a Turing machine?" in fake.calls[0]


def test_follow_up_question_sends_context(monkeypatch):
    fake = fake_gemini("Sure, here is more detail.")
    monkeypatch.setattr(gemini_client, "generate", fake)
    response = client.post(
        "/qa", json={"text": "Can you give an example?", "context": "EduGenie answered: Binary search halves the range."}
    )
    assert response.status_code == 200
    assert "Binary search halves the range" in fake.calls[0]


def test_explain_and_learning_path(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", fake_gemini("some answer"))
    assert client.post("/explain", json={"text": "Process synchronization"}).status_code == 200
    assert client.post("/learn/recommendations", json={"text": "SQL"}).json()["result"] == "some answer"


# 2. empty input
@pytest.mark.parametrize("path", ["/qa", "/explain", "/quiz", "/summarize", "/learn/recommendations"])
def test_empty_input_is_rejected(path):
    response = client.post(path, json={"text": "   "})
    assert response.status_code == 400
    assert "enter" in response.json()["detail"].lower()


def test_invalid_request_is_rejected():
    response = client.post("/qa", json={"wrong_field": "hello"})
    assert response.status_code == 422
    assert "Invalid request" in response.json()["detail"]


def test_too_long_input_is_rejected():
    response = client.post("/summarize", json={"text": "a" * 9000})
    assert response.status_code == 400
    assert "too long" in response.json()["detail"]


# 3. summary request
def test_summary(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", fake_gemini("- Point one\n- Point two"))
    response = client.post("/summarize", json={"text": "A long paragraph about photosynthesis."})
    assert response.status_code == 200
    assert "Point one" in response.json()["result"]


# 4. quiz generation
def test_quiz_generation(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", fake_gemini(QUIZ_JSON))
    response = client.post("/quiz", json={"text": "Pythagoras theorem"})
    assert response.status_code == 200
    questions = response.json()["questions"]
    assert len(questions) == 3
    assert len(questions[0]["options"]) == 4
    assert questions[0]["answer_index"] == 1


def test_quiz_handles_markdown_fences(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", fake_gemini("```json\n" + QUIZ_JSON + "\n```"))
    response = client.post("/quiz", json={"text": "Pythagoras theorem"})
    assert response.status_code == 200
    assert len(response.json()["questions"]) == 3


def test_quiz_with_unexpected_response(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", fake_gemini("Sorry, I cannot make a quiz."))
    response = client.post("/quiz", json={"text": "Pythagoras theorem"})
    assert response.status_code == 502
    assert "valid quiz" in response.json()["detail"]


# 5. Gemini API failure
def test_gemini_api_failure(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")

    class BrokenClient:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("secret internal details")

    monkeypatch.setattr(gemini_client.genai, "Client", BrokenClient)
    response = client.post("/qa", json={"text": "What is a Turing machine?"})
    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "Could not reach Gemini" in detail
    assert "secret internal details" not in detail
    assert "test-key-123" not in detail


def test_empty_gemini_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")

    class FakeModels:
        def generate_content(self, model, contents):
            return type("Response", (), {"text": ""})()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.models = FakeModels()

    monkeypatch.setattr(gemini_client.genai, "Client", FakeClient)
    response = client.post("/qa", json={"text": "What is a Turing machine?"})
    assert response.status_code == 502
    assert "empty answer" in response.json()["detail"]


# 6. missing API key
def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post("/qa", json={"text": "What is a Turing machine?"})
    assert response.status_code == 500
    assert "GEMINI_API_KEY" in response.json()["detail"]


# 7. backend / frontend communication
def test_home_page_has_form_and_hides_key():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text
    assert "<form" in response.text
    assert "/learn/recommendations" in response.text  # frontend knows every endpoint
    assert "GEMINI_API_KEY" not in response.text


def test_static_css_is_served():
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_frontend_to_backend_round_trip(monkeypatch):
    """The frontend sends JSON {text, context} and reads {result} back."""
    monkeypatch.setattr(gemini_client, "generate", fake_gemini("Binary search example."))
    response = client.post(
        "/explain",
        json={"text": "Explain binary search with an example.", "context": ""},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json() == {"result": "Binary search example."}
