"""
Offline textbook ingestion pipeline (run locally, once per textbook).

    python scripts/ingest.py --pdf path/to/calculus1.pdf \
        --book "Calculus 1" --subject Mathematics

Pipeline:
  1. Marker converts the PDF into clean Markdown/LaTeX (preserves equations,
     tables, and — critically — page boundaries, which we use for citations).
     Install separately: `pip install marker-pdf` (heavier dependency, not
     in the main API's requirements.txt on purpose — this runs offline).
  2. LlamaIndex's SentenceSplitter chunks the text (~512 tokens/chunk) with
     Book/Chapter/Page metadata attached to every chunk.
  3. BAAI/bge-m3 embeds each chunk (same model the live query path uses in
     rag_service.py — embeddings must come from the same model on both
     sides or similarity search breaks).
  4. Upsert vectors + metadata into Qdrant.

This is intentionally a standalone script, not an API endpoint — textbook
ingestion is a batch/admin job, not something end users trigger.
"""
import argparse
import re
import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402


def parse_pdf_with_marker(pdf_path: str) -> str:
    """Runs Marker and returns the full document as Markdown with page
    markers preserved. Requires `pip install marker-pdf` locally."""
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
    except ImportError:
        raise SystemExit(
            "marker-pdf is not installed. Run: pip install marker-pdf\n"
            "(kept out of requirements.txt since ingestion runs offline, "
            "separately from the deployed API)."
        )

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(pdf_path)
    return rendered.markdown  # Marker keeps page-break markers we regex below


def chunk_with_metadata(markdown_text: str, book_title: str, chapter_hint: str | None) -> list[dict]:
    """Splits on Marker's page-break markers to track page numbers, then
    sub-chunks each page with LlamaIndex's SentenceSplitter (~512 tokens)."""
    from llama_index.core.node_parser import SentenceSplitter

    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    # Marker emits page breaks as literal "{page_number}------------" markers.
    pages = re.split(r"\{(\d+)\}-+", markdown_text)
    chunks = []
    # pages[0] is preamble before first marker; then alternates [page_num, text, page_num, text, ...]
    for i in range(1, len(pages), 2):
        page_num = int(pages[i])
        page_text = pages[i + 1] if i + 1 < len(pages) else ""
        for node in splitter.split_text(page_text):
            chunks.append({
                "text": node,
                "book_title": book_title,
                "chapter": chapter_hint,
                "page": page_num,
            })
    return chunks


def embed_and_upsert(chunks: list[dict], subject: str):
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)

    dim = model.get_sentence_embedding_dimension()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

    texts = [c["text"] for c in chunks]
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[i].tolist(),
            payload={**chunks[i], "subject": subject},
        )
        for i in range(len(chunks))
    ]
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    print(f"Upserted {len(points)} chunks into '{settings.QDRANT_COLLECTION}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--book", required=True, help="Book title, e.g. 'Calculus 1'")
    parser.add_argument("--subject", required=True, help="Subject tag used for retrieval filtering")
    parser.add_argument("--chapter", default=None)
    args = parser.parse_args()

    print(f"Parsing {args.pdf} with Marker...")
    markdown = parse_pdf_with_marker(args.pdf)

    print("Chunking with page-level metadata...")
    chunks = chunk_with_metadata(markdown, args.book, args.chapter)
    print(f"Produced {len(chunks)} chunks.")

    print("Embedding with BAAI/bge-m3 and upserting to Qdrant...")
    embed_and_upsert(chunks, args.subject)
