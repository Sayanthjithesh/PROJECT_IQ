"""
PROJECTIQ - Feature Gap Intelligence

Compares detected features against a DOMAIN-AWARE expectation profile
rather than one generic checklist for every project. Expectation
profiles are selected using the project's inferred domain and existing
technology signals.
"""

from typing import Dict, List

# Baseline expectations that apply broadly, layered with domain-specific additions.
BASELINE_GAPS = {
    "high_priority": ["Error Handling", "Environment Configuration"],
    "professional": ["Authentication", "Testing", "Documentation"],
    "advanced": ["Deployment Configuration", "Docker"],
}

DOMAIN_PROFILES = {
    "AI/ML Web Application": {
        "high_priority": ["Prediction", "Data Visualization"],
        "professional": ["Reports / Export", "Search"],
        "advanced": ["Notifications"],
    },
    "Web Application": {
        "high_priority": ["CRUD Operations", "Database"],
        "professional": ["Search", "Notifications"],
        "advanced": ["Reports / Export"],
    },
    "API Service": {
        "high_priority": ["REST API", "Database", "Error Handling"],
        "professional": ["Authentication", "Testing"],
        "advanced": ["Deployment Configuration"],
    },
    "Data Dashboard": {
        "high_priority": ["Dashboard", "Data Visualization"],
        "professional": ["Reports / Export", "Search"],
        "advanced": ["Notifications"],
    },
}


def _merge_unique(*lists: List[str]) -> List[str]:
    seen, out = set(), []
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen.add(item)
                out.append(item)
    return out


def analyze_feature_gaps(project_type: str, detected_features: List[Dict]) -> Dict:
    detected_names = {f["feature"] for f in detected_features}
    profile = DOMAIN_PROFILES.get(project_type, DOMAIN_PROFILES["Web Application"])

    gaps = {
        "high_priority": [f for f in _merge_unique(profile["high_priority"], BASELINE_GAPS["high_priority"])
                           if f not in detected_names],
        "professional": [f for f in _merge_unique(profile["professional"], BASELINE_GAPS["professional"])
                          if f not in detected_names],
        "advanced": [f for f in _merge_unique(profile["advanced"], BASELINE_GAPS["advanced"])
                     if f not in detected_names],
    }

    total_expected = sum(len(v) for v in profile.values()) + sum(len(v) for v in BASELINE_GAPS.values())
    total_missing = sum(len(v) for v in gaps.values())
    completeness_percent = round(max(0, 100 - (total_missing / max(total_expected, 1)) * 100), 1)

    return {
        "project_type_used": project_type,
        "gaps": gaps,
        "completeness_percent": completeness_percent,
    }
