"""
PROJECTIQ - Explainable Recommendations Engine

Turns detected feature gaps into fully explained recommendations:
priority, rationale, evidence, expected impact, required skills, and
estimated difficulty. Deterministic and rule-based - not LLM-generated,
so results are reproducible and auditable.
"""

from typing import Dict, List

RECOMMENDATION_LIBRARY = {
    "Authentication": {
        "why": "No authentication or session-handling code was detected.",
        "impact": "Enables per-user data, protected routes, and personalization.",
        "skills": ["JWT", "OAuth2", "Password hashing"],
        "difficulty": "Medium",
    },
    "Testing": {
        "why": "No test files or testing framework were detected.",
        "impact": "Improves reliability, prevents regressions, and builds reviewer confidence.",
        "skills": ["pytest", "Jest", "Test-driven development"],
        "difficulty": "Medium",
    },
    "Error Handling": {
        "why": "Limited or no structured exception handling was detected in the codebase.",
        "impact": "Reduces crashes and produces clearer error messages for users and developers.",
        "skills": ["Exception handling", "HTTP status codes"],
        "difficulty": "Low",
    },
    "Environment Configuration": {
        "why": "Secrets or configuration values may be hardcoded rather than externalized.",
        "impact": "Improves security and makes the project portable across environments.",
        "skills": ["dotenv", "Environment variables"],
        "difficulty": "Low",
    },
    "Documentation": {
        "why": "README is missing, or lacks clear setup and usage instructions.",
        "impact": "Makes the project accessible to reviewers, collaborators, and future you.",
        "skills": ["Technical writing", "Markdown"],
        "difficulty": "Low",
    },
    "Deployment Configuration": {
        "why": "No CI/CD or deployment configuration files were detected.",
        "impact": "Enables repeatable, automated deployment and demonstrates production readiness.",
        "skills": ["GitHub Actions", "CI/CD basics"],
        "difficulty": "Medium",
    },
    "Docker": {
        "why": "No Dockerfile or docker-compose configuration was detected.",
        "impact": "Makes the project runnable anywhere with a single command, easing evaluation.",
        "skills": ["Docker", "Containerization basics"],
        "difficulty": "Medium",
    },
    "REST API": {
        "why": "No structured API routes were detected in the backend code.",
        "impact": "Allows the frontend (and other systems) to interact with the application cleanly.",
        "skills": ["FastAPI / Flask routing", "REST conventions"],
        "difficulty": "Medium",
    },
    "Database": {
        "why": "No persistent database layer was detected.",
        "impact": "Enables data to survive restarts and supports multi-user usage.",
        "skills": ["SQL", "SQLAlchemy / ORM basics"],
        "difficulty": "Medium",
    },
    "Data Visualization": {
        "why": "No charting library or visualization code was detected.",
        "impact": "Helps users interpret data at a glance and improves perceived polish.",
        "skills": ["Recharts / Plotly", "Data storytelling"],
        "difficulty": "Low",
    },
    "Search": {
        "why": "No search functionality was detected.",
        "impact": "Improves usability for projects with growing amounts of content or data.",
        "skills": ["Query filtering", "Full-text search basics"],
        "difficulty": "Medium",
    },
    "Notifications": {
        "why": "No notification, alerting, or messaging code was detected.",
        "impact": "Keeps users informed of important events without manual checking.",
        "skills": ["Email/SMTP", "WebSockets", "Push notifications"],
        "difficulty": "Medium",
    },
    "Reports / Export": {
        "why": "No export or report-generation functionality was detected.",
        "impact": "Lets users take data out of the application for offline use or sharing.",
        "skills": ["CSV/PDF generation", "reportlab"],
        "difficulty": "Low",
    },
    "Prediction": {
        "why": "A trained model was detected, but no clear prediction-serving code was found.",
        "impact": "Turns a trained model into an actionable, user-facing capability.",
        "skills": ["Model serving", "Inference pipelines"],
        "difficulty": "Medium",
    },
    "CRUD Operations": {
        "why": "Create/Read/Update/Delete operations were not clearly detected across routes.",
        "impact": "Establishes the fundamental data-management capability most applications need.",
        "skills": ["REST conventions", "ORM basics"],
        "difficulty": "Low",
    },
}

PRIORITY_ORDER = ["high_priority", "professional", "advanced"]
PRIORITY_LABELS = {"high_priority": "High", "professional": "Professional", "advanced": "Advanced"}


def generate_recommendations(gaps: Dict) -> List[Dict]:
    recommendations = []
    for tier in PRIORITY_ORDER:
        for feature in gaps["gaps"].get(tier, []):
            meta = RECOMMENDATION_LIBRARY.get(feature)
            if not meta:
                continue
            recommendations.append({
                "recommendation": f"Add {feature}",
                "priority": PRIORITY_LABELS[tier],
                "why": meta["why"],
                "evidence": f"'{feature}' was not detected during static analysis.",
                "expected_impact": meta["impact"],
                "skills_required": meta["skills"],
                "difficulty": meta["difficulty"],
            })
    return recommendations
