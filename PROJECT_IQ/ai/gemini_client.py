"""
PROJECTIQ - Gemini API Client

Thin wrapper around google-generativeai. The application must keep
working when no API key is configured - callers always receive a
clearly labeled fallback message instead of a crash.
"""

from typing import List, Optional

from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, gemini_configured

_model = None
_init_error: Optional[str] = None


def _get_model():
    global _model, _init_error
    if _model is not None or _init_error is not None:
        return _model
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    except Exception as exc:  # pragma: no cover - depends on external package/network
        _init_error = str(exc)
        _model = None
    return _model


def generate_text(prompt: str, system_instruction: str = "") -> str:
    """Generate a single response from Gemini. Returns a graceful fallback
    string (never raises) if the API key is missing or a call fails."""
    if not gemini_configured():
        return (
            "The AI Chatbot requires a GEMINI_API_KEY. Add your key to the `.env` "
            "file (see `.env.example`) and restart the application to enable "
            "AI-generated responses. In the meantime, ProjectIQ's rule-based "
            "analysis, scores, and recommendations remain fully available."
        )

    model = _get_model()
    if model is None:
        return (
            "The Gemini client could not be initialized "
            f"({_init_error or 'unknown error'}). Please verify your GEMINI_API_KEY "
            "and internet connection."
        )

    try:
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        return (response.text or "").strip() or "The model returned an empty response. Please try rephrasing your question."
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        return f"The AI request could not be completed: {exc}"


def gemini_status_message() -> str:
    if gemini_configured():
        return "Gemini API key detected. AI Chatbot and AI-assisted explanations are enabled."
    return "No Gemini API key configured. Add GEMINI_API_KEY to your .env file to enable the AI Chatbot."
