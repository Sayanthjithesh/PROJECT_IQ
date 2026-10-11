"""
PROJECTIQ - Project Risk Radar

Produces a deterministic, evidence-based risk assessment across common
software quality dimensions. This is explicitly labeled an "Automated
Educational Project Assessment" - it is NOT a substitute for a
professional security audit.
"""

from typing import Dict, List


def _risk_entry(level: str, reason: str) -> Dict:
    return {"level": level, "reason": reason}


def analyze_risks(features: List[Dict], readme: Dict, py_report: Dict, tech: Dict) -> Dict:
    names = {f["feature"] for f in features}
    risks: Dict[str, Dict] = {}

    # Testing
    if "Testing" in names:
        risks["Testing"] = _risk_entry("Low Risk", "Automated tests were detected in the project.")
    else:
        risks["Testing"] = _risk_entry("High Risk", "No automated testing files or framework were detected.")

    # Documentation
    if readme.get("present") and readme.get("has_setup_instructions"):
        risks["Documentation"] = _risk_entry("Low Risk", "README exists with setup instructions.")
    elif readme.get("present"):
        risks["Documentation"] = _risk_entry("Medium Risk", "README exists but setup instructions appear incomplete.")
    else:
        risks["Documentation"] = _risk_entry("High Risk", "No README documentation was found.")

    # Maintainability
    syntax_errors = py_report.get("files_with_syntax_errors", [])
    if syntax_errors:
        risks["Maintainability"] = _risk_entry(
            "High Risk", f"{len(syntax_errors)} Python file(s) contain syntax errors that could not be parsed.")
    elif py_report.get("total_functions", 0) > 150:
        risks["Maintainability"] = _risk_entry(
            "Medium Risk", "A large number of functions were detected; consider modularization.")
    else:
        risks["Maintainability"] = _risk_entry("Low Risk", "No obvious maintainability red flags were detected.")

    # Scalability
    if tech.get("databases"):
        risks["Scalability"] = _risk_entry("Low Risk", "A persistent database layer supports scaling beyond memory.")
    else:
        risks["Scalability"] = _risk_entry(
            "Medium Risk", "No persistent database was detected; in-memory state may not scale.")

    # Configuration
    if "Environment Configuration" in names:
        risks["Configuration"] = _risk_entry("Low Risk", "Environment variable usage was detected.")
    else:
        risks["Configuration"] = _risk_entry(
            "Medium Risk", "No environment variable usage detected; secrets may be hardcoded.")

    # Security practices
    if "Authentication" in names:
        risks["Security Practices"] = _risk_entry(
            "Medium Risk", "Authentication code detected. Verify password hashing and token expiry independently.")
    else:
        risks["Security Practices"] = _risk_entry(
            "High Risk", "No authentication mechanism detected for a project that may need one.")

    # Error handling
    if "Error Handling" in names:
        risks["Error Handling"] = _risk_entry("Low Risk", "Structured exception handling was detected.")
    else:
        risks["Error Handling"] = _risk_entry("Medium Risk", "Limited structured error handling was detected.")

    return {
        "risks": risks,
        "disclaimer": "This is an Automated Educational Project Assessment, not a formal security audit.",
    }
