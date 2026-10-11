"""Check PROJECTIQ's Gemini connection using the configured model."""
from config import GEMINI_MODEL_NAME, gemini_configured
from ai.gemini_client import generate_text

print(f"Model: {GEMINI_MODEL_NAME}")
if not gemini_configured():
    print("ERROR: GEMINI_API_KEY was not loaded from .env")
    raise SystemExit(1)

answer = generate_text("Reply with exactly: PROJECTIQ Gemini connection successful.")
if answer.startswith("Gemini ") or "could not" in answer.lower() or "quota" in answer.lower():
    print("GEMINI ERROR:", answer)
    raise SystemExit(1)

print("SUCCESS: Gemini is responding.")
print(answer)
