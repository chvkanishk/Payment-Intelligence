from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import time

from app.core.database import get_db
from app.services.agent_service import run_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


# ─── Models ───────────────────────────────────────────────

class AgentRequest(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Are there any suspicious transactions over $5000?"
            }
        }
    }


class ToolCall(BaseModel):
    tool: str
    args: dict
    result: str


class AgentResponse(BaseModel):
    answer: str
    tools_called: List[ToolCall]
    iterations: int
    response_time: float


# ─── Endpoint ─────────────────────────────────────────────

@router.post("/", response_model=AgentResponse)
async def agent(
    body: AgentRequest,
    conn: asyncpg.Connection = Depends(get_db),
):
    """
    AI Agent endpoint — send a plain English message,
    the agent decides which tools to call and returns an answer.
    """
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    start = time.perf_counter()
    result = await run_agent(conn, body.message)
    elapsed = round(time.perf_counter() - start, 3)

    # Log request
    try:
        await conn.execute(
            """
            INSERT INTO request_logs (endpoint, question, response_time)
            VALUES ($1, $2, $3)
            """,
            "/agent",
            body.message,
            elapsed,
        )
    except Exception:
        pass

    return AgentResponse(
        answer=result["answer"],
        tools_called=[ToolCall(**t) for t in result["tools_called"]],
        iterations=result["iterations"],
        response_time=elapsed,
    )