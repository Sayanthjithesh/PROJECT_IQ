# PROJECTIQ repair notes

## What was changed
- Removed the duplicate legacy page scripts from the root `pages/` directory. The canonical pages are now the 11 zero-padded files (`01_...` through `11_...`), each with a unique Streamlit URL path.
- Made `app.py` use the same entry-point implementation as `Home.py`, so either documented launch command starts the same application.
- Removed unresolved Git merge-conflict markers from the root README, dependency list, environment example, and ignore file.
- Rebuilt `requirements.txt` as a valid dependency list and switched the active Gemini client to the Google Gen AI SDK Interactions API.
- Set Gemini as the only provider. Removed the Ollama/local-model fallback and provider selector from the active chatbot path.
- Added clearer Gemini error messages for temporary 503 outages, quota/rate limits (429), invalid keys, and unavailable models.
- Added a short, bounded retry for transient Gemini failures.
- Added local/offline answers for basic project purpose, feature, and technology questions based on the saved project analysis. These questions do not need a Gemini request.
- Replaced the exposed credential in `.env.example` with a placeholder and ensured `.env` is ignored by Git.
- Updated diagnostic scripts to test Gemini only.

## Setup on Windows
1. Open PowerShell in the folder containing `Home.py`.
2. Create your local environment file if it does not exist:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Edit `.env` and set your own valid key:
   ```env
   GEMINI_API_KEY=your_new_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Test Gemini:
   ```powershell
   python gemini_check.py
   ```
6. Start the app:
   ```powershell
   python -m streamlit run Home.py
   ```
   `python -m streamlit run app.py` is also supported.

## Security action required
The uploaded source archive contained a credential-like value in `.env.example`. It has been removed from the corrected source. If that value was a real Gemini API key, revoke it in Google AI Studio and create a new key. Do not paste the new key into chat or commit it to Git.

## Validation performed
- Python syntax compilation passed for the source tree.
- No Git merge-conflict markers remain in the inspected text/source files.
- The root `pages/` folder now has 11 unique page filenames/URL slugs.
- No Ollama references remain in Python files.
- No Gemini-style API key pattern remains in the corrected text/source files.

## Validation limitation
This repair environment did not have Streamlit or the Google Gen AI SDK installed, and it cannot verify your API key or Google's live service status. Therefore a live Streamlit launch and live Gemini request still need to be tested on your Windows machine using the commands above. A real Gemini 503 is a service-side availability issue; the application now gives a clearer message and can answer the basic saved-project questions locally.
