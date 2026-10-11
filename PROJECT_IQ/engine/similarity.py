"""
PROJECTIQ - Similar Project Intelligence

Compares the analyzed project against a curated dataset of open-source
style project concepts using TF-IDF vectorization and cosine similarity
(scikit-learn). This is the lightweight, dependency-friendly counterpart
to the sentence-transformers/ChromaDB pipeline described in the original
specification - it runs fully offline and requires no model downloads,
which keeps local Windows setup simple and reliable.

Similarity values are always presented as ESTIMATES. ProjectIQ never
claims a project is completely unique.
"""

import json
from pathlib import Path
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CURATED_DATA_PATH = Path(__file__).resolve().parent.parent / "sample_data" / "curated_projects.json"


def _load_curated_projects() -> List[Dict]:
    with open(CURATED_DATA_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _project_text(name: str, domain: str, features: List[str], description: str = "") -> str:
    return f"{name} {domain} {description} " + " ".join(features)


def find_similar_projects(project_name: str, project_domain: str,
                           feature_names: List[str], top_k: int = 5) -> List[Dict]:
    curated = _load_curated_projects()
    corpus = [_project_text(c["name"], c["domain"], c["features"], c["description"]) for c in curated]
    query_text = _project_text(project_name, project_domain, feature_names)

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus + [query_text])
    query_vector = matrix[-1]
    corpus_matrix = matrix[:-1]

    similarities = cosine_similarity(query_vector, corpus_matrix)[0]

    results = []
    query_features = set(feature_names)
    for curated_project, score in zip(curated, similarities):
        curated_features = set(curated_project["features"])
        common = sorted(query_features & curated_features)
        missing_from_query = sorted(curated_features - query_features)
        differentiating = sorted(query_features - curated_features)

        results.append({
            "name": curated_project["name"],
            "domain": curated_project["domain"],
            "description": curated_project["description"],
            "similarity_percent": round(float(score) * 100, 1),
            "common_features": common,
            "differentiating_features": differentiating,
            "potentially_missing_features": missing_from_query,
        })

    results.sort(key=lambda r: r["similarity_percent"], reverse=True)
    return results[:top_k]
