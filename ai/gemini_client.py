"""
PROJECTIQ Gemini API client.

Uses the Google Gen AI SDK Interactions API. API keys are read from .env via
config.py and must never be hard-coded into source files.
"""
from __future__ import annotations

import time
from typing import Optional

from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, gemini_configured

_client = None
_init_error: Optional[str] = None


def _get_client():
    global _client, _init_error
    if _client is not None or _init_error is not None:
        return _client
    try:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as exc:  # SDK installation/configuration failure
        _init_error = f"{type(exc).__name__}: {exc}"
        _client = None
    return _client


def _friendly_error(exc: Exception) -> str:
    raw = str(exc)
    low = raw.lower()
    if "503" in low or "unavailable" in low or "high demand" in low:
        return (
            "Gemini is temporarily unavailable or experiencing high demand (503). "
            "Your project data is still saved. Please wait a little and retry."
        )
    if "429" in low or "quota" in low or "rate limit" in low or "resource_exhausted" in low:
        return (
            "Gemini API quota or rate limit was reached (429). Check your AI Studio "
            "usage/quota, wait for the limit to reset, and retry."
        )
    if "401" in low or "api key" in low or "unauthenticated" in low:
        return "Gemini authentication failed. Check GEMINI_API_KEY in your local .env file."
    if "403" in low or "permission" in low or "forbidden" in low:
        return "Gemini rejected the request. Check API access, project permissions, and quota settings."
    if "404" in low or "not found" in low:
        return (
            f'Gemini model "{GEMINI_MODEL_NAME}" was not found or is unavailable to this key. '
            "Check the model name supported by your Google AI Studio account."
        )
    if "timeout" in low or "timed out" in low or "connection" in low:
        return "Could not reach Gemini. Check your internet connection and retry."
    return f"Gemini request failed ({type(exc).__name__}): {raw[:350]}"


def generate_text(prompt: str, system_instruction: str = "") -> str:
    """Generate text with Gemini; return a clear, user-friendly error on failure."""
    if not gemini_configured():
        return (
            "Gemini is not configured yet. Copy .env.example to .env, set "
            "GEMINI_API_KEY to your own key, and restart PROJECTIQ. "
            "Basic saved project details may still be available without Gemini."
        )

    client = _get_client()
    if client is None:
        return f"Gemini client could not be initialized: {_init_error or 'unknown error'}"

    full_prompt = f"{system_instruction.strip()}\n\n{prompt}" if system_instruction.strip() else prompt
    last_error = None
    # A short bounded retry for transient service overload only.
    for attempt in range(2):
        try:
            interaction = client.interactions.create(
                model=GEMINI_MODEL_NAME,
                input=full_prompt,
            )
            answer = (getattr(interaction, "output_text", None) or "").strip()
            if answer:
                return answer
            return "Gemini responded without text. Please rephrase the question and try again."
        except Exception as exc:  # external API failures
            last_error = exc
            low = str(exc).lower()
            transient = any(token in low for token in ("503", "unavailable", "high demand", "429", "resource_exhausted"))
            if transient and attempt == 0:
                time.sleep(1.5)
                continue
            break
    return _friendly_error(last_error or RuntimeError("Unknown Gemini error"))


def gemini_status_message() -> str:
    if gemini_configured():
        return f"Gemini API key detected · model: {GEMINI_MODEL_NAME}. API availability can vary."
    return "Gemini API key not configured. Add your own GEMINI_API_KEY to .env to enable AI-generated responses."
