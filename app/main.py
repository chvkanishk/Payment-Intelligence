from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import get_pool, close_pool
from app.core.cache import get_redis, close_redis
from app.api import rag
from app.api import agent 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await get_pool()
    await get_redis()
    yield
    # Shutdown
    await close_pool()
    await close_redis()


app = FastAPI(
    title="Payment Intelligence Platform",
    description="""
## Payment Intelligence Platform

**Part 1: RAG Engine** ✅ — Ask questions, get answers from real payment docs  
**Part 2: AI Agent** 🔜 — Query live transaction data in plain English  
**Part 3: Kafka Processor** 🔜 — Real-time fraud classification  
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(rag.router)
app.include_router(agent.router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "version": "1.0.0"}