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

    files = list(DOCS_DIR.glob("*.pdf")) + list(DOCS_DIR.glob("*.md"))

    if not files:
        print(f"No files found in {DOCS_DIR}")
        return

    print(f"Found {len(files)} file(s)\n")

    total_chunks = 0
    for file_path in sorted(files):
        print(f"  Processing {file_path.name}...", end=" ")
        try:
            if file_path.suffix == ".pdf":
                text = extract_pdf_text(str(file_path))
            else:
                text = file_path.read_text(encoding="utf-8")
            chunks = await ingest_document(conn, file_path.name, text)
            print(f"{chunks} chunks stored ✓")
            total_chunks += chunks
        except Exception as e:
            print(f"FAILED — {e}")

    await conn.close()
    print(f"\nDone! {total_chunks} total chunks across {len(files)} documents.")
    print("You can now query at: POST /rag/ask")

if __name__ == "__main__":
    asyncio.run(main())
