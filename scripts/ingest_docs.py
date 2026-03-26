import asyncio
import asyncpg
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.services.rag_service import extract_pdf_text, ingest_document

settings = get_settings()
DOCS_DIR = Path(__file__).parent.parent / "docs"


async def main():
    print(f"Connecting to database...")
    conn = await asyncpg.connect(settings.database_url)

    pdf_files = list(DOCS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {DOCS_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF(s)\n")

    total_chunks = 0
    for pdf_path in sorted(pdf_files):
        print(f"  Processing {pdf_path.name}...", end=" ")
        try:
            text = extract_pdf_text(str(pdf_path))
            chunks = await ingest_document(conn, pdf_path.name, text)
            print(f"{chunks} chunks stored ✓")
            total_chunks += chunks
        except Exception as e:
            print(f"FAILED — {e}")

    await conn.close()
    print(f"\nDone! {total_chunks} total chunks across {len(pdf_files)} documents.")
    print("You can now query at: POST /rag/ask")


if __name__ == "__main__":
    asyncio.run(main())
