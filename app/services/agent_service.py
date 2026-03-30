"""
Agent Service
-------------
The agentic loop:
1. Send user message + tools to Ollama
2. If Ollama calls a tool → run it → send result back
3. Repeat until Ollama gives a final text answer
"""

import json
import httpx
import asyncpg
from typing import List, Dict, Any
from app.core.config import get_settings
from app.services.agent_tools import TOOLS, run_tool

settings = get_settings()

MAX_ITERATIONS = 5  # prevent infinite loops


async def run_agent(
    conn: asyncpg.Connection,
    user_message: str,
) -> Dict[str, Any]:
    """
    Main agent loop.
    Keeps calling Ollama until it returns a final answer (no more tool calls).
    """

    # Conversation history — grows as tools are called
    messages = [
        {
            "role": "system",
            "content": (
                "You are a payment intelligence assistant with access to tools. "
                "Use tools to answer questions about transactions and fraud. "
                "Always use a tool if the question is about transaction data. "
                "Be concise and clear in your final answer."
            ),
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    tools_called = []  # track what tools were used

    for iteration in range(MAX_ITERATIONS):
        # Call Ollama with tools
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": messages,
                    "tools": TOOLS,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()

        message = data["message"]
        stop_reason = data.get("done_reason", "stop")

        # Add assistant response to history
        messages.append(message)

        # Check if Ollama wants to call a tool
        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            # No tool calls — this is the final answer
            return {
                "answer": message["content"],
                "tools_called": tools_called,
                "iterations": iteration + 1,
            }

        # Execute each tool call
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"].get("arguments", {})

            # Handle case where arguments come as a JSON string
            if isinstance(tool_args, str):
                try:
                    tool_args = json.loads(tool_args)
                except json.JSONDecodeError:
                    tool_args = {}

            print(f"  → Calling tool: {tool_name}({tool_args})")

            # Run the actual tool
            tool_result = await run_tool(conn, tool_name, tool_args)

            tools_called.append({
                "tool": tool_name,
                "args": tool_args,
                "result": tool_result,
            })

            # Add tool result to conversation history
            messages.append({
                "role": "tool",
                "content": tool_result,
            })

    # If we hit MAX_ITERATIONS, return what we have
    return {
        "answer": "I reached the maximum number of steps. Here's what I found: "
                  + (tools_called[-1]["result"] if tools_called else "No results."),
        "tools_called": tools_called,
        "iterations": MAX_ITERATIONS,
    }