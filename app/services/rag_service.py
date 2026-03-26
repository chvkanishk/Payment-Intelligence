import json
import pdfplumber
import asyncpg
import httpx
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings
from app.core.cache import cache_get, cache_set, make_cache_key

settings = get_settings()

# Load once at startup — stays in memory
print("Loading embedding model (first run downloads ~90MB)...")
_embedder = SentenceTransformer(settings.embedding_model)
print("Embedding model ready.")


# ─────────────────────────────────────────────
# 1. PDF Extraction
# ─────────────────────────────────────────────

def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract all text from a PDF file page by page.
    pdfplumber handles real-world PDFs (Stripe docs, PCI guides) reliably.
    """
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text and text.strip():
                # Label each page so chunks know where they came from
                text_parts.append(f"[Page {page_num}]\n{text.strip()}")

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        raise ValueError(f"Could not extract text from {pdf_path}. "
                        f"The PDF may be scanned/image-based.")

    return full_text


# ─────────────────────────────────────────────
# 2. Chunking
# ─────────────────────────────────────────────

def chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks.
    Tries to break at sentence boundaries so meaning is preserved.
    """
    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Prefer splitting at a sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")
            if last_period > chunk_size // 2:
                end = start + last_period + 1
                chunk = text[start:end]

        chunk = chunk.strip()
        if len(chunk) > 50:  # skip tiny fragments
            chunks.append(chunk)

        start = end - overlap

    return chunks


# ─────────────────────────────────────────────
# 3. Embedding (100% local, free)
# ─────────────────────────────────────────────

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Convert text to 384-dim vectors using local sentence-transformers."""
    vectors = _embedder.encode(texts, convert_to_numpy=True)
    return vectors.tolist()

def embed_single(text: str) -> List[float]:
    return embed_texts([text])[0]


# ─────────────────────────────────────────────
# 4. Ingest document into pgvector
# ─────────────────────────────────────────────

async def ingest_document(
    conn: asyncpg.Connection,
    doc_name: str,
    content: str,
) -> int:
    """
    Chunk → embed → store in document_chunks.
    Returns number of chunks stored.
    """
    # Clear old version of this doc
    await conn.execute(
        "DELETE FROM document_chunks WHERE doc_name = $1", doc_name
    )

    chunks = chunk_text(content)
    if not chunks:
        return 0

    # Embed all chunks at once (batch is faster than one-by-one)
    embeddings = embed_texts(chunks)

    rows = [
        (doc_name, idx, chunk, json.dumps(embedding))
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    await conn.executemany(
        """
        INSERT INTO document_chunks (doc_name, chunk_index, content, embedding)
        VALUES ($1, $2, $3, $4::vector)
        """,
        rows,
    )

    return len(chunks)


# ─────────────────────────────────────────────
# 5. Semantic search
# ─────────────────────────────────────────────

async def search_docs(
    conn: asyncpg.Connection,
    query: str,
    top_k: int = None,
) -> List[Dict[str, Any]]:
    """
    Embed the query then find top-k most similar chunks in pgvector.
    """
    top_k = top_k or settings.top_k_results

    # Cache embeddings for 24h — same question = same vector
    cache_key = make_cache_key("emb", query)
    query_embedding = await cache_get(cache_key)
    if not query_embedding:
        query_embedding = embed_single(query)
        await cache_set(cache_key, query_embedding, ttl=86400)

    embedding_str = json.dumps(query_embedding)

    rows = await conn.fetch(
        """
        SELECT
            doc_name,
            chunk_index,
            content,
            1 - (embedding <=> $1::vector) AS similarity
        FROM document_chunks
        ORDER BY embedding <=> $1::vector
        LIMIT $2
        """,
        embedding_str,
        top_k,
    )

    return [
        {
            "doc_name": r["doc_name"],
            "chunk_index": r["chunk_index"],
            "content": r["content"],
            "similarity": round(float(r["similarity"]), 4),
        }
        for r in rows
    ]


# ─────────────────────────────────────────────
# 6. Generate answer with Ollama
# ─────────────────────────────────────────────

async def answer_question(
    conn: asyncpg.Connection,
    question: str,
) -> Dict[str, Any]:
    """
    Full RAG pipeline:
    search → build context → ask Ollama → cache → return
    """
    # Check cache first — skip Ollama if already answered
    cache_key = make_cache_key("rag", question)
    cached = await cache_get(cache_key)
    if cached:
        cached["cache_hit"] = True
        return cached

    # Retrieve relevant chunks
    chunks = await search_docs(conn, question)

    if not chunks:
        return {
            "answer": "No documents loaded yet. Run the ingestion script first.",
            "sources": [],
            "cache_hit": False,
        }

    # Build context block
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['doc_name']}]\n{chunk['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are a payment systems expert assistant.
Answer the question using ONLY the documentation excerpts provided below.
Always cite which source you used (e.g. "According to Source 1...").
If the answer is not in the documentation, say "I don't have documentation on that topic."
Do not make up information.

Documentation:
{context}

Question: {question}

Answer:"""

    # Call Ollama (running locally in Docker)
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        answer_text = response.json()["response"]

    result = {
        "answer": answer_text,
        "sources": [
            {
                "doc_name": c["doc_name"],
                "similarity": c["similarity"],
                "excerpt": c["content"][:200] + "..."
                           if len(c["content"]) > 200 else c["content"],
            }
            for c in chunks
        ],
        "cache_hit": False,
    }

    # Cache the answer for 1 hour
    await cache_set(cache_key, result)
    return result
