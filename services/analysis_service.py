"""
PROJECTIQ - Analysis Orchestration Service

Runs every analyzer and engine in the correct order, assembles the
Project DNA profile, and persists a new AnalysisVersion snapshot for
the given project. This is the single entry point pages should call
to (re)analyze a project.
"""

from pathlib import Path
from typing import Dict, List

from analyzers.architecture_analyzer import analyze_architecture
from analyzers.feature_detector import detect_features
from analyzers.file_scanner import scan_project
from analyzers.javascript_analyzer import analyze_js_files
from analyzers.python_analyzer import analyze_python_files
from analyzers.readme_analyzer import analyze_readme
from analyzers.technology_detector import detect_technologies
from db.database import get_session
from db.models import AnalysisVersion, Project
from engine.differentiation import compute_differentiation
from engine.feature_impact import predict_feature_impact  # noqa: F401  (re-exported for pages)
from engine.future_simulator import simulate_future
from engine.gap_intelligence import analyze_feature_gaps
from engine.outlook import analyze_outlook
from engine.recommendations import generate_recommendations
from engine.risk_radar import analyze_risks
from engine.scoring import compute_score
from engine.similarity import find_similar_projects

PROJECT_TYPE_RULES = [
    ("AI/ML Web Application", lambda feats: "Machine Learning" in feats or "Prediction" in feats),
    ("Data Dashboard", lambda feats: "Dashboard" in feats and "Data Visualization" in feats),
    ("API Service", lambda feats: "REST API" in feats and "Dashboard" not in feats),
    ("Web Application", lambda feats: True),
]

DOMAIN_KEYWORDS = {
    "FinTech": ["finance", "expense", "budget", "payment", "fraud", "invoice", "wallet"],
    "HealthTech": ["health", "patient", "medical", "appointment", "clinic"],
    "EdTech": ["course", "student", "learning", "quiz", "education"],
    "E-Commerce": ["cart", "checkout", "product", "order", "shop", "store"],
    "Developer Tools": ["ci", "pipeline", "deploy", "monitor", "log"],
    "Social / Productivity": ["chat", "task", "todo", "social", "post", "comment"],
}


def _infer_project_type(feature_names: List[str]) -> str:
    for label, rule in PROJECT_TYPE_RULES:
        if rule(feature_names):
            return label
    return "Web Application"


def _infer_domain(project_name: str, readme_summary: str, feature_names: List[str]) -> str:
    corpus = f"{project_name} {readme_summary}".lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in corpus for kw in keywords):
            return domain
    return "General Purpose"


def _infer_complexity(tech: Dict, features: List[Dict]) -> str:
    signal = len(tech.get("frameworks", [])) + len(tech.get("libraries", [])) + len(features)
    if signal >= 16:
        return "Advanced"
    if signal >= 9:
        return "Intermediate"
    if signal >= 4:
        return "Developing"
    return "Beginner"


def build_project_dna(project_name: str, tech: Dict, features: List[Dict], readme: Dict) -> Dict:
    feature_names = [f["feature"] for f in features]
    domain = _infer_domain(project_name, readme.get("summary_text", ""), feature_names)
    project_type = _infer_project_type(feature_names)
    complexity = _infer_complexity(tech, features)

    return {
        "project_name": project_name,
        "domain": domain,
        "project_type": project_type,
        "languages": list(tech.get("languages", {}).keys()),
        "frameworks": tech.get("frameworks", []),
        "libraries": tech.get("libraries", []),
        "databases": tech.get("databases", []),
        "detected_features": feature_names,
        "complexity": complexity,
        "main_purpose": readme.get("summary_text", "")[:280] or "Not stated in README.",
    }


def run_full_analysis(project_name: str, storage_path: str, goal: str = "Portfolio Ready") -> Dict:
    """Executes the complete ProjectIQ pipeline against an extracted project directory."""
    root = Path(storage_path)
    scan = scan_project(root)

    tech = detect_technologies(scan)
    py_report = analyze_python_files(scan)
    js_report = analyze_js_files(scan)
    readme = analyze_readme(scan)
    architecture = analyze_architecture(scan)
    features = detect_features(scan, tech, py_report, js_report, readme)
    feature_names = [f["feature"] for f in features]

    dna = build_project_dna(project_name, tech, features, readme)

    similar = find_similar_projects(project_name, dna["domain"], feature_names)
    differentiation = compute_differentiation(similar, feature_names,
                                               tech.get("frameworks", []) + tech.get("libraries", []))

    gaps = analyze_feature_gaps(dna["project_type"], features)
    recommendations = generate_recommendations(gaps)
    risks = analyze_risks(features, readme, py_report, tech)
    outlook = analyze_outlook(scan, feature_names, dna["domain"])
    score = compute_score(tech, py_report, features, architecture, readme, differentiation)
    roadmap = simulate_future(goal, score["total"], feature_names, gaps["gaps"])

    file_stats = {
        "total_files": scan.total_files,
        "total_size_bytes": scan.total_size_bytes,
        "directories": len(scan.directories),
        "python_files": py_report["file_count"],
        "js_files": js_report["file_count"],
    }

    return {
        "project_dna": dna,
        "technologies": tech,
        "features": features,
        "architecture": architecture,
        "outlook": outlook,
        "gaps": gaps,
        "recommendations": recommendations,
        "risk_radar": risks,
        "differentiation": {**differentiation, "similar_projects": similar},
        "score": score,
        "roadmap": roadmap,
        "file_stats": file_stats,
        "readme": readme,
        "python_report": {k: v for k, v in py_report.items() if k != "reports"},
        "javascript_report": js_report,
    }


def persist_analysis(project_id: int, analysis: Dict) -> int:
    """Saves a new AnalysisVersion snapshot and updates the parent Project row.
    Returns the new version number."""
    import datetime as dt

    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found.")

        next_version = len(project.versions) + 1

        version = AnalysisVersion(
            project_id=project_id,
            version_number=next_version,
            score_total=analysis["score"]["total"],
            score_breakdown=analysis["score"]["breakdown"],
            maturity_level=analysis["score"]["maturity"],
            project_dna=analysis["project_dna"],
            technologies=analysis["technologies"],
            features=analysis["features"],
            architecture=analysis["architecture"],
            outlook=analysis["outlook"],
            gaps=analysis["gaps"],
            recommendations=analysis["recommendations"],
            risk_radar=analysis["risk_radar"],
            differentiation=analysis["differentiation"],
            file_stats=analysis["file_stats"],
        )
        session.add(version)

        project.current_score = analysis["score"]["total"]
        project.current_maturity = analysis["score"]["maturity"]
        project.description = analysis["project_dna"]["main_purpose"]
        project.last_analyzed_date = dt.datetime.utcnow()

        session.flush()
        return next_version
