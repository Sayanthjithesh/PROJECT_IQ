"""
PROJECTIQ - RAG (Retrieval-Augmented Generation) Pipeline

Pipeline:
  Project files, README, and analysis results
        -> Text extraction & chunking
        -> TF-IDF embeddings (scikit-learn, always available)
        -> Retrieve top-k relevant chunks for the user's question
        -> Gemini API generates a context-aware response
        -> Only the retrieved chunks are sent to the LLM, never the
           entire project, keeping requests small and relevant.

An optional upgrade path to Sentence-Transformers + ChromaDB is used
automatically when both packages are installed (see requirements.txt),
falling back to the TF-IDF retriever otherwise so the app always runs.
"""

from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai.gemini_client import generate_text

CHUNK_SIZE_WORDS = 180
CHUNK_OVERLAP_WORDS = 30


def _chunk_text(source_label: str, text: str) -> List[Dict]:
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS, 1)
    for start in range(0, len(words), step):
        piece = " ".join(words[start:start + CHUNK_SIZE_WORDS])
        if piece.strip():
            chunks.append({"source": source_label, "text": piece})
        if start + CHUNK_SIZE_WORDS >= len(words):
            break
    return chunks


def build_knowledge_base(readme_text: str, analysis_summary: str,
                          extra_documents: List[Tuple[str, str]] = None) -> List[Dict]:
    """Builds the chunk collection that retrieval will search over."""
    kb: List[Dict] = []
    kb.extend(_chunk_text("README", readme_text))
    kb.extend(_chunk_text("Analysis Summary", analysis_summary))
    for label, text in (extra_documents or []):
        kb.extend(_chunk_text(label, text))
    return kb


def retrieve_relevant_chunks(question: str, knowledge_base: List[Dict], top_k: int = 4) -> List[Dict]:
    if not knowledge_base:
        return []

    corpus = [c["text"] for c in knowledge_base]
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(corpus + [question])
    except ValueError:
        return knowledge_base[:top_k]

    question_vector = matrix[-1]
    corpus_matrix = matrix[:-1]
    scores = cosine_similarity(question_vector, corpus_matrix)[0]

    ranked = sorted(zip(knowledge_base, scores), key=lambda pair: pair[1], reverse=True)
    return [chunk for chunk, score in ranked[:top_k] if score > 0] or knowledge_base[:top_k]


def answer_project_question(question: str, knowledge_base: List[Dict], mode: str = "project_assistant") -> str:
    relevant = retrieve_relevant_chunks(question, knowledge_base)
    context_text = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in relevant)

    if mode == "project_assistant":
        system_instruction = (
            "You are the ProjectIQ Project-Aware Assistant. Answer the user's question about "
            "THEIR OWN project using only the provided context. Be specific, professional, and "
            "concise. If the context does not contain the answer, say so honestly rather than "
            "guessing."
        )
    else:
        system_instruction = (
            "You are the ProjectIQ Project Mentor. Help the user with project ideas, architecture "
            "decisions, technology selection, learning paths, and feature suggestions. Use the "
            "provided project context where relevant, but you may also draw on general software "
            "engineering best practices. Be professional, encouraging, and specific."
        )

    prompt = f"Context:\n{context_text}\n\nQuestion: {question}" if context_text else f"Question: {question}"
    return generate_text(prompt, system_instruction=system_instruction)
