from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import asyncpg
import time
import tempfile
import os

from app.core.database import get_db
from app.services.rag_service import answer_question, ingest_document, extract_pdf_text

router = APIRouter(prefix="/rag", tags=["RAG"])


# ─── Models ───────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str

    model_config = {
        "json_schema_extra": {
            "example": {"question": "What is the chargeback process?"}
        }
    }

class SourceItem(BaseModel):
    doc_name: str
    similarity: float
    excerpt: str

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    cache_hit: bool
    response_time: float


# ─── Endpoints ────────────────────────────────────────────

@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    conn: asyncpg.Connection = Depends(get_db),
):
    """Ask a question — get an answer grounded in your payment docs."""
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start = time.perf_counter()
    result = await answer_question(conn, body.question)
    elapsed = round(time.perf_counter() - start, 3)

    # Log request
    try:
        await conn.execute(
            """
            INSERT INTO request_logs (endpoint, question, response_time, cache_hit)
            VALUES ($1, $2, $3, $4)
            """,
            "/rag/ask",
            body.question,
            elapsed,
            result.get("cache_hit", False),
        )
    except Exception:
        pass

    return AskResponse(
        answer=result["answer"],
        sources=[SourceItem(**s) for s in result["sources"]],
        cache_hit=result.get("cache_hit", False),
        response_time=elapsed,
    )


@router.post("/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    conn: asyncpg.Connection = Depends(get_db),
):
    """Upload a PDF to add to the knowledge base."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    # Save upload to temp file (pdfplumber needs a real file path)
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        text = extract_pdf_text(tmp_path)
        chunks_stored = await ingest_document(conn, file.filename, text)
    finally:
        os.unlink(tmp_path)  # clean up temp file

    return {
        "doc_name": file.filename,
        "chunks_stored": chunks_stored,
        "message": f"Successfully ingested {file.filename} into {chunks_stored} chunks."
    }


@router.get("/docs")
async def list_docs(conn: asyncpg.Connection = Depends(get_db)):
    """List all documents currently in the knowledge base."""
    rows = await conn.fetch(
        """
        SELECT doc_name, COUNT(*) as chunks, MAX(created_at) as ingested_at
        FROM document_chunks
        GROUP BY doc_name
        ORDER BY ingested_at DESC
        """
    )
    return [dict(r) for r in rows]