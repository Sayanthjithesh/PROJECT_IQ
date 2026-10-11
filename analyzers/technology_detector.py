"""
PROJECTIQ - Technology Detector

Detects languages, frameworks, and libraries using MULTIPLE signals:
file extensions, import/require statements, and dependency manifests.
No single signal is trusted alone.
"""

import re
from typing import Dict, List, Set

from analyzers.dependency_analyzer import analyze_dependencies
from analyzers.file_scanner import ScanResult, language_distribution

FRAMEWORK_SIGNATURES = {
    "React": {"deps": {"react"}, "patterns": [r"from ['\"]react['\"]", r"import React"]},
    "Next.js": {"deps": {"next"}, "patterns": [r"from ['\"]next"]},
    "Vue": {"deps": {"vue"}, "patterns": [r"from ['\"]vue['\"]"]},
    "FastAPI": {"deps": {"fastapi"}, "patterns": [r"from fastapi import", r"import fastapi"]},
    "Flask": {"deps": {"flask"}, "patterns": [r"from flask import", r"import flask"]},
    "Django": {"deps": {"django"}, "patterns": [r"from django", r"import django"]},
    "Streamlit": {"deps": {"streamlit"}, "patterns": [r"import streamlit"]},
    "Express": {"deps": {"express"}, "patterns": [r"require\(['\"]express['\"]\)", r"from ['\"]express['\"]"]},
    "Node.js": {"deps": set(), "patterns": [r"require\("]},
}

LIBRARY_SIGNATURES = {
    "Pandas": {"deps": {"pandas"}, "patterns": [r"import pandas"]},
    "NumPy": {"deps": {"numpy"}, "patterns": [r"import numpy"]},
    "Scikit-learn": {"deps": {"scikit-learn", "sklearn"}, "patterns": [r"from sklearn", r"import sklearn"]},
    "TensorFlow": {"deps": {"tensorflow"}, "patterns": [r"import tensorflow"]},
    "PyTorch": {"deps": {"torch"}, "patterns": [r"import torch"]},
    "SQLAlchemy": {"deps": {"sqlalchemy"}, "patterns": [r"from sqlalchemy", r"import sqlalchemy"]},
    "Axios": {"deps": {"axios"}, "patterns": [r"from ['\"]axios['\"]", r"require\(['\"]axios['\"]\)"]},
    "Tailwind CSS": {"deps": {"tailwindcss"}, "patterns": [r"tailwind\.config"]},
    "Chart / Recharts / Plotly": {"deps": {"recharts", "chart.js", "plotly"}, "patterns": [r"from ['\"]recharts['\"]", r"import plotly"]},
    "JWT / Auth libraries": {"deps": {"pyjwt", "python-jose", "passport", "next-auth", "jsonwebtoken"}, "patterns": [r"jsonwebtoken", r"jose"]},
    "ChromaDB": {"deps": {"chromadb"}, "patterns": [r"import chromadb"]},
    "Sentence Transformers": {"deps": {"sentence-transformers"}, "patterns": [r"sentence_transformers"]},
    "Google Generative AI": {"deps": {"google-generativeai"}, "patterns": [r"google\.generativeai", r"import genai"]},
    "Docker": {"deps": set(), "patterns": []},
}


def _search_any(patterns: List[str], corpus: str) -> bool:
    return any(re.search(p, corpus, re.IGNORECASE) for p in patterns)


def detect_languages(scan: ScanResult) -> Dict[str, int]:
    return language_distribution(scan)


def detect_technologies(scan: ScanResult) -> Dict:
    deps = analyze_dependencies(scan)
    all_declared: Set[str] = set(deps["python_packages"]) | set(deps["node_dependencies"]) | set(deps["node_dev_dependencies"])

    code_corpus = "\n".join(f.content for f in scan.files if f.extension in {".py", ".js", ".jsx", ".ts", ".tsx"})

    frameworks: List[str] = []
    for name, sig in FRAMEWORK_SIGNATURES.items():
        dep_hit = bool(sig["deps"] & all_declared)
        pattern_hit = _search_any(sig["patterns"], code_corpus) if sig["patterns"] else False
        if dep_hit or pattern_hit:
            frameworks.append(name)

    libraries: List[str] = []
    for name, sig in LIBRARY_SIGNATURES.items():
        dep_hit = bool(sig["deps"] & all_declared)
        pattern_hit = _search_any(sig["patterns"], code_corpus) if sig["patterns"] else False
        if name == "Docker":
            dep_hit = bool(scan.find_by_name("dockerfile", "docker-compose.yml", "docker-compose.yaml"))
        if dep_hit or pattern_hit:
            libraries.append(name)

    database = []
    db_signals = {
        "SQLite": [r"sqlite", r"\.db\b"],
        "PostgreSQL": [r"postgres", r"psycopg2"],
        "MySQL": [r"mysql", r"pymysql"],
        "MongoDB": [r"mongo", r"pymongo", r"mongoose"],
    }
    manifest_corpus = "\n".join(deps["python_packages"] + deps["node_dependencies"])
    for name, patterns in db_signals.items():
        if _search_any(patterns, code_corpus) or _search_any(patterns, manifest_corpus):
            database.append(name)

    return {
        "languages": detect_languages(scan),
        "frameworks": sorted(frameworks),
        "libraries": sorted(libraries),
        "databases": sorted(database),
        "dependencies": deps,
    }
