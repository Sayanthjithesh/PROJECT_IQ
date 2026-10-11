"""Command-line diagnostic for PROJECTIQ's Gemini-only chatbot."""
from config import GEMINI_MODEL_NAME, gemini_configured
from ai.gemini_client import generate_text

print("PROJECTIQ AI diagnostic")
print(f"Gemini model: {GEMINI_MODEL_NAME}")
if not gemini_configured():
    print("NOT READY: GEMINI_API_KEY is missing. Set it in .env.")
    raise SystemExit(1)

answer = generate_text("Reply with exactly: PROJECTIQ_OK")
if answer.startswith("Gemini ") or "could not" in answer.lower() or "quota" in answer.lower():
    print(f"NOT READY: {answer}")
    raise SystemExit(1)
print("OK: Gemini responded.")
print(answer)
