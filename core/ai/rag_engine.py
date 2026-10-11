"""Lightweight project-aware retrieval for the Streamlit edition.

This keeps retrieval local and sends only the most relevant source snippets to the
LLM. It intentionally does not execute uploaded project code.
"""
from pathlib import Path
import re
from core.analyzers.file_scanner import scan


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r'[A-Za-z0-9_+#.-]{3,}', text) if w.lower() not in {'the', 'and', 'for', 'with', 'from', 'that', 'this'}}


def retrieve(project_path, query: str, limit: int = 6, chars_per_file: int = 5000) -> str:
    if not project_path or not Path(project_path).exists():
        return ''
    query_words = _tokens(query)
    scored = []
    for item in scan(project_path):
        text = item['text']
        words = _tokens(text)
        overlap = len(query_words & words)
        exact_bonus = sum(text.lower().count(w) for w in query_words)
        name_bonus = sum(3 for w in query_words if w in item['path'].lower())
        score = overlap * 10 + min(exact_bonus, 20) + name_bonus
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    chunks = [f"FILE: {item['path']}\n{item['text'][:chars_per_file]}" for _, item in scored[:limit]]
    return '\n\n'.join(chunks)
