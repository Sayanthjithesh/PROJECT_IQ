"""Gemini-only provider layer retained for compatibility with older modules."""
from __future__ import annotations

from core.config import GEMINI_API_KEY, GEMINI_MODEL


class ProviderError(RuntimeError):
    """Raised when Gemini cannot provide an answer."""


class GeminiProvider:
    name = "Gemini"

    def __init__(self):
        self.key = GEMINI_API_KEY
        self.model = GEMINI_MODEL

    def available(self) -> bool:
        return bool(self.key)

    def health_check(self) -> tuple[bool, str]:
        if not self.key:
            return False, "GEMINI_API_KEY is not configured in .env."
        try:
            from google import genai
            client = genai.Client(api_key=self.key)
            response = client.interactions.create(
                model=self.model,
                input="Reply with exactly: PROJECTIQ_OK",
            )
            if not (getattr(response, "output_text", None) or "").strip():
                return False, "Gemini returned an empty response."
            return True, f"Gemini is reachable using {self.model}."
        except Exception as exc:
            return False, _friendly_error(exc)

    def generate(self, prompt: str, context: str = "", history: list[dict] | None = None) -> str:
        if not self.key:
            raise ProviderError("Gemini API key is missing. Add GEMINI_API_KEY to .env.")
        recent_history = (history or [])[-8:]
        history_text = "\n".join(
            f"{item.get('role', 'user').upper()}: {item.get('content', '')}"
            for item in recent_history
        )
        full_prompt = (
            "You are PROJECTIQ, a project-intelligence assistant. Use supplied evidence; "
            "never invent files, technologies, features, or architecture. If evidence is insufficient, say so.\n\n"
            f"PROJECT EVIDENCE:\n{context[:30000]}\n\n"
            f"RECENT CHAT:\n{history_text[-12000:]}\n\nUSER QUESTION:\n{prompt}"
        )
        try:
            from google import genai
            client = genai.Client(api_key=self.key)
            response = client.interactions.create(model=self.model, input=full_prompt)
            answer = (getattr(response, "output_text", None) or "").strip()
            if not answer:
                raise ProviderError("Gemini returned an empty response.")
            return answer
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(_friendly_error(exc)) from exc


def _friendly_error(exc: Exception) -> str:
    raw = str(exc)
    low = raw.lower()
    if "503" in low or "unavailable" in low or "high demand" in low:
        return "Gemini is temporarily unavailable (503). Wait briefly and retry; saved project data is unaffected."
    if "429" in low or "quota" in low or "rate limit" in low or "resource_exhausted" in low:
        return "Gemini API quota/rate limit reached (429). Check AI Studio usage and retry after the limit resets."
    if "401" in low or "api key" in low or "unauthenticated" in low:
        return "Gemini authentication failed. Check GEMINI_API_KEY in .env."
    if "403" in low or "permission" in low or "forbidden" in low:
        return "Gemini denied the request. Check API access and quota settings."
    if "404" in low or "not found" in low:
        return f'Gemini model "{GEMINI_MODEL}" is unavailable for this key. Check the model name.'
    return f"Gemini request failed: {raw[:350]}"


def get_provider(name: str | None = None) -> GeminiProvider:
    """Always return Gemini; local model providers are intentionally disabled."""
    return GeminiProvider()


def generate_with_fallback(
    prompt: str, context: str = "", history: list[dict] | None = None
) -> tuple[str, str]:
    """Compatibility wrapper: Gemini only, with no local-model fallback."""
    provider = GeminiProvider()
    try:
        return provider.generate(prompt, context, history), provider.name
    except ProviderError:
        raise
