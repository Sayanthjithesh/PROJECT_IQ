**Understand. Evaluate. Evolve.**

ProjectIQ is an AI-powered Project Intelligence and Evolution Platform built entirely
in **Streamlit**. Upload a software project and ProjectIQ will statically analyze it,
generate a Project DNA profile, detect its technologies and features, infer its
architecture, produce an explainable ProjectIQ Score, surface feature gaps and
recommendations, compare it against similar project concepts, track its evolution
over time, and let you chat with an AI assistant that understands your project.

No uploaded code is ever executed. All analysis is static (file scanning, Python AST
parsing, regex, and dependency-manifest parsing).

---

## 1. Prerequisites

Install the following before you begin (Windows 10/11):

- **Python 3.10 – 3.12** — https://www.python.org/downloads/windows/
  During installation, check **"Add python.exe to PATH"**.
- **Git** (optional, only if you plan to clone a repository) — https://git-scm.com/download/win

You do **not** need Node.js — ProjectIQ's entire interface runs through Streamlit.

Verify your installation in **Command Prompt** or **PowerShell**:

```powershell
python --version
pip --version
```

---

## 2. Project Setup (Windows)

### Step 1 — Extract the project

Unzip `ProjectIQ.zip` to a folder of your choice, e.g. `C:\Projects\ProjectIQ`.

### Step 2 — Open a terminal in the project folder

```powershell
cd C:\Projects\ProjectIQ
```

### Step 3 — Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

Your prompt should now begin with `(venv)`.

### Step 4 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 5 — Configure environment variables

```powershell
copy .env.example .env
```

Open the new `.env` file in a text editor and set:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free Gemini API key at **https://aistudio.google.com/app/apikey**.

`GITHUB_TOKEN` is optional — leave it blank unless you want GitHub metadata lookups.
`DATABASE_URL` and `MAX_UPLOAD_MB` already have sensible local defaults.

> **ProjectIQ runs perfectly well without a Gemini API key.** Every analysis
> feature (Project DNA, technology and feature detection, ProjectIQ Score,
> gap intelligence, recommendations, risk radar, similarity, evolution
> tracking) is rule-based and works offline. Only the **AI Chatbot** page
> requires a Gemini key — without one it shows a clear message explaining
> how to enable it.

### Step 6 — Run the application

```powershell
streamlit run Home.py
```

Streamlit will print a local URL, typically:

```
Local URL: http://localhost:8501
```

Your default browser should open automatically. If not, paste that URL into
your browser.

---

## 3. Using ProjectIQ

1. **Upload Project** — upload a ZIP of your project (or paste a GitHub URL for
   reference, then download and upload its ZIP). `node_modules`, `.git`, `venv`,
   `__pycache__`, `dist`, and `build` are ignored automatically.
2. ProjectIQ extracts the archive, runs the full analysis pipeline, and saves the
   first **Analysis Version** to the local SQLite database.
3. **Project Workspace** shows the Project DNA, detected technologies and features,
   the ProjectIQ Score breakdown, feature gaps, recommendations, and outlook.
4. **Architecture**, **Similar Projects**, **Risk Radar**, **Feature Impact
   Predictor**, and **Future Simulator** each offer a focused deep dive.
5. **My Projects** lists every saved project — open, re-analyze (creates a new
   version snapshot), or delete it.
6. **Evolution Tracker** compares versions and charts score/feature growth over time.
7. **AI Chatbot** lets you ask a Project-Aware Assistant questions about your
   specific project (via a lightweight RAG pipeline), or switch to Project Mentor
   mode for general architecture/technology/learning guidance.
8. **Settings** shows which environment variables are active.

---

## 4. Testing the Application

- **Health check** — the app starting without errors at `http://localhost:8501` is
  the health check; there is no separate backend server to ping.
- **Project upload** — use the sample project structure below, zip it, and upload it
  on the **Upload Project** page.
- **Project analysis** — after upload, confirm the ProjectIQ Score, Project DNA, and
  feature list appear on **Project Workspace**.
- **Saved project history** — visit **My Projects**; your uploaded project should be
  listed with its score and maturity level.
- **Chatbot** — open **AI Chatbot**, select **Project-Aware Assistant**, and ask
  *"What is missing from my project?"*. Without a Gemini key you will see a clear
  setup message; with a key configured you will get an AI-generated answer.

A minimal example project you can zip and upload to try the app:

```
sample-app/
├── README.md
├── requirements.txt        (e.g. "fastapi\nsqlalchemy")
└── main.py                 (a small FastAPI app with a couple of @app.get routes)
```

---

## 5. Project Structure

```
projectiq/
├── Home.py                     # Streamlit entry point (landing page)
├── config.py                   # Environment & app configuration
├── ui_helpers.py                # Shared styling (60/30/10 color system) & widgets
├── pages/                       # Streamlit multipage app
│   ├── 01_Upload_Project.py
│   ├── 02_My_Projects.py
│   ├── 03_Project_Workspace.py
│   ├── 04_Architecture.py
│   ├── 05_Similar_Projects.py
│   ├── 06_Evolution_Tracker.py
│   ├── 07_AI_Chatbot.py
│   ├── 08_Feature_Impact_Predictor.py
│   ├── 09_Risk_Radar.py
│   ├── 10_Future_Simulator.py
│   └── 11_Settings.py
├── analyzers/                   # Static analysis engines
│   ├── file_scanner.py
│   ├── python_analyzer.py       # AST-based
│   ├── javascript_analyzer.py   # Regex-based
│   ├── dependency_analyzer.py
│   ├── technology_detector.py
│   ├── feature_detector.py
│   ├── architecture_analyzer.py
│   └── readme_analyzer.py
├── engine/                       # Scoring & intelligence engines
│   ├── scoring.py                # Deterministic ProjectIQ Score
│   ├── gap_intelligence.py       # Domain-aware feature gaps
│   ├── recommendations.py        # Explainable recommendations
│   ├── risk_radar.py
│   ├── feature_impact.py
│   ├── differentiation.py
│   ├── future_simulator.py
│   └── similarity.py             # TF-IDF + cosine similarity
├── ai/                            # LLM / RAG layer
│   ├── gemini_client.py
│   └── rag.py
├── services/                      # Orchestration & data access
│   ├── analysis_service.py
│   └── project_data.py
├── db/                             # Persistence layer
│   ├── models.py                   # SQLAlchemy models
│   └── database.py
├── utils/
│   └── project_loader.py           # Secure ZIP extraction
├── sample_data/
│   └── curated_projects.json       # Similarity comparison dataset
├── storage/                        # Local SQLite DB + extracted projects (gitignored)
├── .streamlit/config.toml          # Theme (60/30/10 color system)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 6. Where to Add Your API Keys

Open `.env` (created from `.env.example` in Step 5) and set:

```
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=                # optional
```

Restart the Streamlit app after changing `.env` for the new values to take effect.
Secrets are read server-side only via `config.py` and are **never** sent to the
browser or included in any client-side code — Streamlit apps render entirely
server-side, so this is safe by construction.

---

## 7. Security Notes

- Uploaded ZIP archives are validated for size, are never extracted outside their
  isolated storage folder (path-traversal protected), and their contents are only
  **read**, never executed.
- Ignored directories (`node_modules`, `.git`, `venv`, `__pycache__`, `dist`,
  `build`, etc.) and binary file types are automatically skipped during both
  extraction and analysis.
- The Risk Radar is explicitly labeled an **"Automated Educational Project
  Assessment"** — it is not a substitute for a professional security audit.

---

## 8. Migrating to PostgreSQL Later

The database layer uses plain SQLAlchemy models with no SQLite-specific
features. To switch later, install a PostgreSQL driver and change
`DATABASE_URL` in `.env`, e.g.:

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/projectiq
```

No code changes are required beyond installing `psycopg2-binary`.
