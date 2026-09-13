"""
Open-source RAG pipeline — no Pinecone, no paid vector DB.

  Embeddings : BAAI/bge-m3 (sentence-transformers, runs locally, free)
  Vector DB  : Qdrant (self-hosted via Railway's 1-click template, free/OSS)
  LLM        : Groq's hosted Llama 3.1 8B (generous free tier, very fast)

This module only handles the LIVE query path (embed question -> search
Qdrant -> ask the LLM with citations). The offline INGESTION path (PDF ->
Marker -> chunk -> embed -> upsert) lives in `scripts/ingest.py`, since it's
a one-off/batch job you run locally per textbook, not something the API
does per-request.

=====================================================================
 INTEGRATION POINT — Qdrant + Groq
=====================================================================
Set these in .env / Railway vars:
  QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
  GROQ_API_KEY, GROQ_MODEL
Then run `scripts/ingest.py` once per textbook to populate the collection
before this endpoint has anything to retrieve.
"""
from functools import lru_cache

from groq import Groq
from qdrant_client import QdrantClient

from app.config import settings

SYSTEM_PROMPT = """You are an expert academic tutor for Nigerian secondary and \
university students (WAEC, JAMB, NECO, GCE, and undergraduate courses).

Rules:
- Solve or explain step-by-step.
- Use standard LaTeX for all math: inline as \\( ... \\), block as \\[ ... \\].
- For every fact or step drawn from the provided textbook excerpts, you MUST \
append an inline citation in the exact form [Book Title, p. N].
- If the provided excerpts don't cover the question, say so plainly instead \
of guessing — never fabricate a citation.
- Match the requested depth: "simplify" = a short, plain-language explanation; \
"deep_dive" = a full worked derivation.
"""


@lru_cache(maxsize=1)
def _embedder():
    # Loaded lazily + cached: importing sentence-transformers / downloading
    # the model happens once per process, not per-request.
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _qdrant() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)


@lru_cache(maxsize=1)
def _groq() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)


def embed_text(text: str) -> list[float]:
    vector = _embedder().encode(text, normalize_embeddings=True)
    return vector.tolist()


def retrieve_chunks(query: str, subject: str | None = None, top_k: int = 5) -> list[dict]:
    """Dense vector search in Qdrant. `subject` (if given) is applied as a
    metadata filter so results stay on-topic. Qdrant also supports sparse
    vectors for true hybrid (keyword + semantic) search — add a sparse
    field during ingestion and pass it here if you need exact-term matches
    on top of semantic similarity."""
    query_vector = embed_text(query)

    query_filter = None
    if subject:
        from qdrant_client.models import FieldCondition, Filter, MatchValue
        query_filter = Filter(must=[FieldCondition(key="subject", match=MatchValue(value=subject))])

    hits = _qdrant().search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=top_k,
    )
    return [
        {
            "book": hit.payload.get("book_title", "Unknown source"),
            "chapter": hit.payload.get("chapter"),
            "page": hit.payload.get("page"),
            "snippet": hit.payload.get("text", ""),
            "score": hit.score,
        }
        for hit in hits
    ]


def ask_tutor(question: str, mode: str, subject: str | None = None) -> dict:
    chunks = retrieve_chunks(question, subject=subject)

    if not chunks:
        context_block = "No matching textbook excerpts were found in the knowledge base."
    else:
        context_block = "\n\n".join(
            f"[{c['book']}, p. {c['page']}] {c['snippet']}" for c in chunks
        )

    user_prompt = (
        f"Mode: {mode}\n\n"
        f"Student question: {question}\n\n"
        f"Textbook excerpts you may cite from:\n{context_block}"
    )

    completion = _groq().chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1200,
    )
    answer = completion.choices[0].message.content

    return {
        "answer": answer,
        "citations": [
            {"book": c["book"], "chapter": c.get("chapter"), "page": c.get("page"), "snippet": c["snippet"]}
            for c in chunks
        ],
    }
