"""
PROJECTIQ - Project Future Simulator

Generates a personalized version-by-version roadmap toward a chosen
goal, along with a readiness percentage for that goal.
"""

from typing import Dict, List

GOAL_REQUIREMENTS = {
    "College Submission": {
        "required": ["Documentation", "Error Handling"],
        "target_score": 45,
    },
    "Portfolio Ready": {
        "required": ["Documentation", "Error Handling", "Authentication", "Database", "Dashboard"],
        "target_score": 70,
    },
    "Startup MVP": {
        "required": ["Authentication", "Database", "REST API", "Error Handling",
                      "Environment Configuration", "Testing"],
        "target_score": 82,
    },
    "Production Ready": {
        "required": ["Authentication", "Database", "REST API", "Testing", "Error Handling",
                      "Environment Configuration", "Docker", "Deployment Configuration"],
        "target_score": 92,
    },
}


def _next_version_number(current: float) -> List[str]:
    return ["1.1", "2.0", "3.0"]


def simulate_future(goal: str, current_score: float, detected_features: List[str],
                     missing_gaps: Dict[str, List[str]]) -> Dict:
    profile = GOAL_REQUIREMENTS.get(goal, GOAL_REQUIREMENTS["Portfolio Ready"])
    required = profile["required"]

    remaining = [f for f in required if f not in detected_features]
    readiness = round(max(0, 100 - (len(remaining) / max(len(required), 1)) * 100), 1)

    all_missing = (missing_gaps.get("high_priority", []) + missing_gaps.get("professional", []) +
                   missing_gaps.get("advanced", []))
    # Deduplicate while preserving priority order, then split into three roadmap stages.
    ordered_missing = []
    for item in all_missing:
        if item not in ordered_missing:
            ordered_missing.append(item)

    third = max(1, len(ordered_missing) // 3) if ordered_missing else 0
    v1_1 = ordered_missing[:third] or ["Improve validation and error handling"]
    v2_0 = ordered_missing[third:third * 2] or ["Add authentication and API refinements"]
    v3_0 = ordered_missing[third * 2:] or ["Add testing, Docker, and deployment configuration"]

    roadmap = [
        {"version": "Current", "focus": "Existing functionality", "changes": []},
        {"version": "v1.1", "focus": "Stability & fundamentals", "changes": v1_1},
        {"version": "v2.0", "focus": "Core capability expansion", "changes": v2_0},
        {"version": "v3.0", "focus": "Production polish", "changes": v3_0},
    ]

    return {
        "goal": goal,
        "readiness_percent": readiness,
        "remaining_gap_percent": round(100 - readiness, 1),
        "still_needed": remaining,
        "roadmap": roadmap,
        "target_score_for_goal": profile["target_score"],
    }
