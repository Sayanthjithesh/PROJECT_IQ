"""
PROJECTIQ - Scoring Engine

Produces an explainable, deterministic, rule-based score out of 100.
The LLM is never used as the sole scoring mechanism - every category
score is derived from concrete static-analysis evidence.

Categories:
  Technical Complexity        20
  Feature Completeness        25
  Professional Practices      20
  Real World Value            15
  Differentiation             10
  Deployment & Scalability    10
"""

from typing import Dict, List

MATURITY_BANDS = [
    (0, 35, "Beginner"),
    (36, 65, "Developing"),
    (66, 80, "Intermediate"),
    (81, 90, "Advanced"),
    (91, 100, "Professional"),
]


def _classify_maturity(total: float) -> str:
    for low, high, label in MATURITY_BANDS:
        if low <= total <= high:
            return label
    return "Beginner"


def _score_technical_complexity(tech: Dict, py_report: Dict, architecture: Dict) -> Dict:
    score, reasons, evidence = 0, [], []

    lang_count = len(tech.get("languages", {}))
    lang_pts = min(lang_count * 2, 6)
    score += lang_pts
    if lang_count:
        reasons.append(f"{lang_count} language(s) detected across the codebase.")

    fw_count = len(tech.get("frameworks", []))
    fw_pts = min(fw_count * 2, 6)
    score += fw_pts
    if fw_count:
        reasons.append(f"{fw_count} framework(s) in use: {', '.join(tech['frameworks'][:4])}.")
        evidence.append(", ".join(tech["frameworks"][:6]))

    if py_report.get("ml_models_detected"):
        score += 5
        reasons.append("Machine learning model classes detected.")

    layer_pts = min(len(architecture.get("detected_layers", [])), 3)
    score += layer_pts
    if layer_pts:
        reasons.append(f"{layer_pts} distinct architectural layer(s) identified.")

    score = min(score, 20)
    return {"score": score, "max": 20, "reasons": reasons, "evidence": evidence}


def _score_feature_completeness(features: List[Dict]) -> Dict:
    high_value = {"REST API", "Database", "Authentication", "Machine Learning",
                  "Dashboard", "CRUD Operations", "Testing", "Error Handling"}
    matched = [f for f in features if f["feature"] in high_value]
    other = [f for f in features if f["feature"] not in high_value]

    score = min(len(matched) * 2.5, 18) + min(len(other) * 1.0, 7)
    score = round(min(score, 25), 1)

    reasons = [f"{len(features)} feature(s) detected in total."]
    if matched:
        reasons.append(f"Core features present: {', '.join(f['feature'] for f in matched[:6])}.")

    return {"score": score, "max": 25, "reasons": reasons,
            "evidence": [f["feature"] for f in features[:10]]}


def _score_professional_practices(features: List[Dict], readme: Dict) -> Dict:
    names = {f["feature"] for f in features}
    score, reasons = 0, []

    if "Testing" in names:
        score += 6
        reasons.append("Automated tests detected.")
    else:
        reasons.append("No automated testing detected.")

    if "Error Handling" in names:
        score += 4
        reasons.append("Structured error handling detected.")

    if "Environment Configuration" in names:
        score += 3
        reasons.append("Environment variable usage detected (secrets kept out of code).")

    if "Docker" in names:
        score += 3
        reasons.append("Containerization (Docker) configuration detected.")

    if readme.get("present"):
        score += 2
        reasons.append("README documentation present.")
    if readme.get("has_setup_instructions"):
        score += 2
        reasons.append("README includes setup instructions.")

    score = min(score, 20)
    return {"score": score, "max": 20, "reasons": reasons, "evidence": list(names)[:10]}


def _score_real_world_value(features: List[Dict], tech: Dict) -> Dict:
    names = {f["feature"] for f in features}
    score, reasons = 0, []

    user_facing = {"Dashboard", "Authentication", "Notifications", "Reports / Export", "Search"}
    hits = names & user_facing
    score += min(len(hits) * 2.5, 10)
    if hits:
        reasons.append(f"User-facing capabilities detected: {', '.join(hits)}.")

    if tech.get("databases"):
        score += 3
        reasons.append("Persistent data storage detected, supporting real usage.")

    if "REST API" in names:
        score += 2
        reasons.append("API layer allows integration with other systems.")

    score = min(score, 15)
    return {"score": score, "max": 15, "reasons": reasons, "evidence": list(hits)}


def _score_differentiation(differentiation: Dict) -> Dict:
    overall = differentiation.get("overall_differentiation", 50)
    score = round((overall / 100) * 10, 1)
    reasons = [f"Differentiation profile estimates {overall}/100 uniqueness relative to comparable projects."]
    return {"score": score, "max": 10, "reasons": reasons, "evidence": []}


def _score_deployment_scalability(features: List[Dict]) -> Dict:
    names = {f["feature"] for f in features}
    score, reasons = 0, []

    if "Docker" in names:
        score += 5
        reasons.append("Docker configuration supports portable deployment.")
    if "Deployment Configuration" in names:
        score += 3
        reasons.append("CI/deployment configuration files detected.")
    if "Database" in names:
        score += 2
        reasons.append("Persistent database supports scaling beyond in-memory state.")

    score = min(score, 10)
    if not reasons:
        reasons.append("No deployment or scaling configuration was detected.")
    return {"score": score, "max": 10, "reasons": reasons, "evidence": list(names)[:5]}


def compute_score(tech: Dict, py_report: Dict, features: List[Dict],
                   architecture: Dict, readme: Dict, differentiation: Dict) -> Dict:
    breakdown = {
        "Technical Complexity": _score_technical_complexity(tech, py_report, architecture),
        "Feature Completeness": _score_feature_completeness(features),
        "Professional Practices": _score_professional_practices(features, readme),
        "Real World Value": _score_real_world_value(features, tech),
        "Differentiation": _score_differentiation(differentiation),
        "Deployment and Scalability": _score_deployment_scalability(features),
    }
    total = round(sum(c["score"] for c in breakdown.values()), 1)
    maturity = _classify_maturity(total)

    return {
        "total": total,
        "max_total": 100,
        "maturity": maturity,
        "breakdown": breakdown,
    }
