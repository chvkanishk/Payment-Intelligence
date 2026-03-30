import asyncpg
from typing import Optional
from app.services.rag_service import answer_question


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_transactions",
            "description": "Search transactions in the database by status, minimum amount, or date. Use this when the user asks about payments, transactions, or financial activity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status: 'completed', 'pending', 'suspicious', 'failed'",
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum transaction amount in USD",
                    },
                    "max_amount": {
                        "type": "number",
                        "description": "Maximum transaction amount in USD",
                    },
                    "location": {
                        "type": "string",
                        "description": "Filter by country or location e.g. 'Nigeria', 'USA'",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fraud_stats",
            "description": "Get aggregated fraud statistics — total suspicious transactions, flagged count, high value amounts. Use this when the user asks for summaries or stats.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "flag_transaction",
            "description": "Flag a transaction for human review. Use this when the user asks to flag or mark a transaction as suspicious.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction ID to flag e.g. 'txn_001'",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for flagging the transaction",
                    },
                },
                "required": ["transaction_id", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search payment documentation to answer policy questions about refunds, disputes, webhooks, PCI compliance, or error codes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to search documentation for",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


async def query_transactions(
    conn: asyncpg.Connection,
    status: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    location: Optional[str] = None,
) -> str:
    conditions = []
    params = []
    idx = 1

    if status:
        conditions.append(f"status = ${idx}")
        params.append(status)
        idx += 1
    if min_amount is not None:
        conditions.append(f"amount >= ${idx}")
        params.append(min_amount)
        idx += 1
    if max_amount is not None:
        conditions.append(f"amount <= ${idx}")
        params.append(max_amount)
        idx += 1
    if location:
        conditions.append(f"location ILIKE ${idx}")
        params.append(f"%{location}%")
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT transaction_id, amount, merchant, status, location, flagged
        FROM transactions {where}
        ORDER BY amount DESC LIMIT 20
    """
    rows = await conn.fetch(query, *params)

    if not rows:
        return "No transactions found matching the criteria."

    results = []
    for r in rows:
        flagged = " [FLAGGED]" if r["flagged"] else ""
        results.append(
            f"- {r['transaction_id']}: ${r['amount']} at {r['merchant']} "
            f"({r['status']}, {r['location']}){flagged}"
        )
    return f"Found {len(rows)} transaction(s):\n" + "\n".join(results)


async def get_fraud_stats(conn: asyncpg.Connection) -> str:
    row = await conn.fetchrow(
        """
        SELECT
            COUNT(*)                                        AS total,
            COUNT(*) FILTER (WHERE status = 'suspicious')  AS suspicious,
            COUNT(*) FILTER (WHERE flagged = TRUE)          AS flagged,
            COUNT(*) FILTER (WHERE status = 'completed')    AS completed,
            COUNT(*) FILTER (WHERE status = 'pending')      AS pending,
            COALESCE(SUM(amount) FILTER (
                WHERE status = 'suspicious'), 0)            AS suspicious_volume,
            COALESCE(MAX(amount), 0)                        AS largest_transaction
        FROM transactions
        """
    )
    return (
        f"Transaction Statistics:\n"
        f"- Total transactions: {row['total']}\n"
        f"- Suspicious: {row['suspicious']}\n"
        f"- Flagged for review: {row['flagged']}\n"
        f"- Completed: {row['completed']}\n"
        f"- Pending: {row['pending']}\n"
        f"- Suspicious volume: ${row['suspicious_volume']:,.2f}\n"
        f"- Largest transaction: ${row['largest_transaction']:,.2f}"
    )


async def flag_transaction(
    conn: asyncpg.Connection,
    transaction_id: str,
    reason: str,
) -> str:
    result = await conn.execute(
        """
        UPDATE transactions
        SET flagged = TRUE, risk_reason = $1
        WHERE transaction_id = $2
        """,
        reason,
        transaction_id,
    )
    rows_affected = int(result.split()[-1])
    if rows_affected == 0:
        return f"Transaction {transaction_id} not found."
    return f"Transaction {transaction_id} has been flagged. Reason: {reason}"


async def search_docs_tool(conn: asyncpg.Connection, query: str) -> str:
    result = await answer_question(conn, query)
    return result["answer"]


async def run_tool(
    conn: asyncpg.Connection,
    tool_name: str,
    tool_args: dict,
) -> str:
    if tool_name == "query_transactions":
        return await query_transactions(conn, **tool_args)
    elif tool_name == "get_fraud_stats":
        return await get_fraud_stats(conn)
    elif tool_name == "flag_transaction":
        return await flag_transaction(conn, **tool_args)
    elif tool_name == "search_docs":
        return await search_docs_tool(conn, **tool_args)
    else:
        return f"Unknown tool: {tool_name}"