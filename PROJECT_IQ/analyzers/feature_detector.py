"""
PROJECTIQ - Feature Detector

Detects which application-level features already exist in a project.
Each feature is scored with a confidence percentage and includes the
evidence and file(s) that triggered the detection so results are
explainable rather than a black box.
"""

import re
from typing import Dict, List

from analyzers.file_scanner import ScanResult

FeatureEvidence = Dict[str, object]


def _evidence(name: str, confidence: int, evidence: str, files: List[str]) -> FeatureEvidence:
    return {
        "feature": name,
        "confidence": min(confidence, 99),
        "evidence": evidence,
        "files": files[:5],
    }


def detect_features(scan: ScanResult, tech: Dict, py_report: Dict, js_report: Dict, readme: Dict) -> List[FeatureEvidence]:
    features: List[FeatureEvidence] = []
    all_code = "\n".join(f.content for f in scan.files if f.extension in
                          {".py", ".js", ".jsx", ".ts", ".tsx"})
    file_names = [f.relative_path for f in scan.files]

    def files_matching(pattern: str) -> List[str]:
        rx = re.compile(pattern, re.IGNORECASE)
        return [p for p in file_names if rx.search(p)]

    # Authentication
    auth_hits = files_matching(r"auth|login|jwt|session")
    if auth_hits or re.search(r"jwt|passport|oauth|bcrypt|password_hash", all_code, re.IGNORECASE):
        features.append(_evidence("Authentication", 80 if auth_hits else 60,
                                   "Auth-related files or password/JWT handling code detected.", auth_hits))

    # Database
    if tech.get("databases") or scan.find_by_name("models.py", "schema.sql"):
        features.append(_evidence("Database", 90, "Database engine or ORM models detected.",
                                   files_matching(r"model|schema|database")))

    # CRUD / REST API
    routes = (py_report.get("api_routes") or []) + (js_report.get("backend_routes") or [])
    if routes:
        features.append(_evidence("REST API", 92, f"{len(routes)} API route definitions detected.",
                                   files_matching(r"route|api|controller")))
        verbs = {r.split()[0].upper() for r in routes if r.split()}
        if {"GET", "POST", "PUT", "DELETE"} & verbs and len(verbs) >= 3:
            features.append(_evidence("CRUD Operations", 85,
                                       "Multiple HTTP verbs (GET/POST/PUT/DELETE) detected across routes.",
                                       files_matching(r"route|api|controller")))

    # Dashboard
    dash_hits = files_matching(r"dashboard")
    if dash_hits or "Recharts" in tech.get("libraries", []) or "Chart / Recharts / Plotly" in tech.get("libraries", []):
        features.append(_evidence("Dashboard", 75 if dash_hits else 55,
                                   "Dashboard-named files or charting libraries detected.", dash_hits))

    # Machine Learning / Prediction
    ml_models = py_report.get("ml_models_detected", [])
    if ml_models:
        features.append(_evidence("Machine Learning", 92,
                                   f"Model classes detected: {', '.join(ml_models[:4])}.",
                                   files_matching(r"model|train|predict")))
        if re.search(r"\.predict\(|predict_proba", all_code):
            features.append(_evidence("Prediction", 88, "`.predict()` calls detected in source code.",
                                       files_matching(r"predict|infer")))

    # Data Visualization
    if any(lib in tech.get("libraries", []) for lib in ["Chart / Recharts / Plotly"]) or "plotly" in all_code.lower():
        features.append(_evidence("Data Visualization", 70, "Charting library imports detected.", []))

    # File Upload
    if re.search(r"upload|multipart|UploadFile|FormData", all_code):
        features.append(_evidence("File Upload", 78, "File upload handling code detected.",
                                   files_matching(r"upload")))

    # Search
    if re.search(r"def search|search_query|\.filter\(.*icontains|elasticsearch|whoosh", all_code, re.IGNORECASE):
        features.append(_evidence("Search", 65, "Search-related functions or queries detected.", []))

    # Notifications
    if re.search(r"notification|toast|send_email|smtp|websocket", all_code, re.IGNORECASE):
        features.append(_evidence("Notifications", 60, "Notification, email, or websocket code detected.", []))

    # Reports / Export
    if re.search(r"export_csv|to_csv|generate_report|reportlab|export_pdf", all_code, re.IGNORECASE):
        features.append(_evidence("Reports / Export", 68, "Export/report generation functions detected.", []))

    # Error Handling
    if re.search(r"try\s*:|except\s|HTTPException|catch\s*\(", all_code):
        features.append(_evidence("Error Handling", 72, "Exception handling blocks detected in source code.", []))

    # Testing
    test_hits = files_matching(r"test_|_test\.|tests/|spec\.")
    if test_hits or "pytest" in tech.get("dependencies", {}).get("python_packages", []):
        features.append(_evidence("Testing", 82, "Test files or a testing framework dependency detected.", test_hits))

    # Docker
    docker_hits = files_matching(r"dockerfile|docker-compose")
    if docker_hits:
        features.append(_evidence("Docker", 95, "Docker configuration files detected.", docker_hits))

    # Environment variables
    env_hits = files_matching(r"\.env|env\.example")
    if env_hits or re.search(r"os\.getenv|process\.env", all_code):
        features.append(_evidence("Environment Configuration", 80,
                                   "Environment variable usage detected.", env_hits))

    # Deployment configuration
    deploy_hits = files_matching(r"vercel\.json|netlify\.toml|procfile|\.github/workflows")
    if deploy_hits:
        features.append(_evidence("Deployment Configuration", 78, "Deployment/CI configuration detected.", deploy_hits))

    # Documentation
    if readme.get("present"):
        conf = 60
        if readme.get("has_setup_instructions"):
            conf += 20
        if readme.get("has_usage_section"):
            conf += 10
        features.append(_evidence("Documentation", conf, "README file found with project documentation.", []))

    return sorted(features, key=lambda f: f["confidence"], reverse=True)
