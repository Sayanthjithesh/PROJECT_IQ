"""
PROJECTIQ - Project Outlook Analysis

Answers "what does this project currently expose to users?" and
"what might users expect next?" The recommendation set depends on the
project's domain and the features it already has, not a fixed list.
"""

import re
from typing import Dict, List

from analyzers.file_scanner import ScanResult

NEXT_FEATURE_MAP = {
    "Authentication": ["User Profile", "Password Reset", "Role-Based Access"],
    "Dashboard": ["Settings", "Notifications Center", "Activity History"],
    "Database": ["Search", "Reports / Export", "Data Filtering"],
    "REST API": ["API Documentation", "Rate Limiting", "Webhooks"],
    "Machine Learning": ["Model Explanation", "Confidence Display", "Feedback Loop"],
    "CRUD Operations": ["Bulk Actions", "Undo / Audit Trail"],
    "File Upload": ["File Preview", "Version History"],
    "Prediction": ["Historical Predictions View", "Batch Prediction"],
}


def _detect_pages_and_routes(scan: ScanResult) -> List[str]:
    pages = set()
    for f in scan.files:
        match = re.search(r"pages/([A-Za-z0-9_-]+)\.(jsx|tsx|js|ts|py)$", f.relative_path)
        if match:
            pages.add(match.group(1))
    return sorted(pages)


def analyze_outlook(scan: ScanResult, detected_feature_names: List[str], domain: str) -> Dict:
    pages = _detect_pages_and_routes(scan)

    recommended: List[str] = []
    for feature in detected_feature_names:
        for suggestion in NEXT_FEATURE_MAP.get(feature, []):
            if suggestion not in recommended and suggestion not in detected_feature_names:
                recommended.append(suggestion)

    return {
        "detected_pages_or_modules": pages,
        "detected_user_facing_features": [f for f in detected_feature_names
                                           if f in {"Dashboard", "Authentication", "Search",
                                                     "Notifications", "Reports / Export", "File Upload"}],
        "recommended_next_features": recommended[:8],
        "domain_context": domain,
    }
