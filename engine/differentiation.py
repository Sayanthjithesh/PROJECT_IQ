"""
PROJECTIQ - Differentiation Profile

Computes how much a project's feature and technology combination stands
out relative to its closest matches in the curated comparison set.
"""

from typing import Dict, List


def compute_differentiation(similar_projects: List[Dict], feature_names: List[str],
                             technology_names: List[str]) -> Dict:
    if not similar_projects:
        return {
            "common_features_percent": 0,
            "differentiating_features_percent": 100,
            "technology_combination_percent": 100,
            "overall_differentiation": 70,
            "explanation": "No comparable projects were found in the curated dataset, "
                            "so differentiation defaults to a moderate estimate.",
        }

    closest = similar_projects[0]
    total_features = max(len(feature_names), 1)

    common_pct = round((len(closest["common_features"]) / total_features) * 100, 1)
    diff_pct = round((len(closest["differentiating_features"]) / total_features) * 100, 1)

    # Technology combination uniqueness: fewer overlaps with common single-purpose
    # stacks (e.g. plain CRUD) implies a more distinctive technical combination.
    tech_pct = round(min(100, len(technology_names) * 9), 1)

    overall = round((diff_pct * 0.45) + (tech_pct * 0.35) + ((100 - common_pct) * 0.20), 1)
    overall = max(0, min(overall, 100))

    return {
        "common_features_percent": common_pct,
        "differentiating_features_percent": diff_pct,
        "technology_combination_percent": tech_pct,
        "overall_differentiation": overall,
        "closest_match": closest["name"],
        "explanation": (
            f"Compared to its closest match ('{closest['name']}'), this project shares "
            f"{common_pct}% of typical features while introducing {diff_pct}% distinguishing "
            f"functionality. Technology combination breadth contributes {tech_pct}% to the score."
        ),
    }
