"""
PROJECTIQ - Architecture Analyzer

Infers a project's architecture layers from static evidence and compares
it against a recommended layered architecture for its type. This is
explicitly a static-analysis inference, not a runtime trace.
"""

from typing import Dict, List

from analyzers.file_scanner import ScanResult

LAYER_DEFINITIONS = [
    ("Frontend", r"src/(components|pages)|\.jsx$|\.tsx$|package\.json"),
    ("API Layer", r"route|api/|@app\.(get|post)|router\."),
    ("Service Layer", r"service|services/"),
    ("ML Model", r"model|train|predict|\.pkl$|\.h5$|\.joblib$"),
    ("Database", r"models\.py|schema\.sql|database|\.db$|sqlalchemy"),
    ("External APIs", r"requests\.(get|post)|fetch\(|axios\.|httpx\."),
]


def _layer_present(scan: ScanResult, pattern: str) -> bool:
    import re
    rx = re.compile(pattern, re.IGNORECASE)
    for f in scan.files:
        if rx.search(f.relative_path):
            return True
    for f in scan.files[:400]:  # cap for performance on large projects
        if f.content and rx.search(f.content[:4000]):
            return True
    return False


def analyze_architecture(scan: ScanResult) -> Dict:
    detected_layers: List[str] = []
    for name, pattern in LAYER_DEFINITIONS:
        if _layer_present(scan, pattern):
            detected_layers.append(name)

    recommended_order = ["Frontend", "API Layer", "Service Layer", "ML Model", "Database"]
    recommended_layers = [layer for layer in recommended_order if layer in detected_layers or layer in ("API Layer", "Service Layer", "Database")]

    gaps = [layer for layer in recommended_order if layer not in detected_layers]

    current_diagram = " -> ".join(detected_layers) if detected_layers else "No clear layered structure detected"
    recommended_diagram = " -> ".join(recommended_order)

    return {
        "detected_layers": detected_layers,
        "current_diagram": current_diagram,
        "recommended_diagram": recommended_diagram,
        "gaps": gaps,
        "disclaimer": (
            "Architecture inference is based on static file and code analysis. "
            "It approximates structure and may not represent full runtime behavior."
        ),
    }
