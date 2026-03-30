"""
Transaction Classifier
----------------------
Classifies transactions as low/medium/high risk using:
- Fast rules for obvious cases (cheap, no AI needed)
- Ollama for ambiguous cases
"""

import httpx
import json
from typing import Dict, Any
from app.core.config import get_settings

settings = get_settings()

# Known safe merchants — skip AI for these
TRUSTED_MERCHANTS = {
    "amazon", "starbucks", "netflix", "spotify",
    "uber", "walmart", "target", "apple", "google"
}

# High risk countries
HIGH_RISK_COUNTRIES = {
    "nigeria", "russia", "belarus", "iran",
    "north korea", "venezuela", "ukraine", "romania"
}


def rules_check(transaction: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Fast rule-based classification.
    Returns a result if rules apply, None if AI is needed.
    """
    amount = float(transaction.get("amount", 0))
    merchant = transaction.get("merchant", "").lower()
    location = transaction.get("location", "").lower()

    # Definitely low risk
    if amount < 100 and merchant in TRUSTED_MERCHANTS:
        return {
            "risk_level": "low",
            "confidence": 0.99,
            "reason": "Small amount at trusted merchant",
            "used_ai": False,
        }

    # Definitely high risk
    if amount > 10000 and location in HIGH_RISK_COUNTRIES:
        return {
            "risk_level": "high",
            "confidence": 0.97,
            "reason": f"Large amount from high-risk country: {location}",
            "used_ai": False,
        }

    # Needs AI
    return None


async def classify_with_ai(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send transaction to Ollama for risk classification.
    Returns risk level, confidence, and reason.
    """
    prompt = f"""You are a fraud detection system. Classify this payment transaction.

Transaction:
- Amount: ${transaction.get('amount')}
- Merchant: {transaction.get('merchant')}
- Location: {transaction.get('location')}
- Status: {transaction.get('status')}
- Card Type: {transaction.get('card_type', 'unknown')}
- Hour: {transaction.get('hour', 'unknown')}

Respond ONLY with a JSON object like this:
{{
  "risk_level": "low" | "medium" | "high",
  "confidence": 0.0 to 1.0,
  "reason": "brief explanation"
}}

No other text. Just the JSON."""

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        raw = response.json()["response"].strip()

    # Parse JSON from Ollama response
    try:
        # Handle case where Ollama wraps in markdown
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
        result["used_ai"] = True
        return result
    except json.JSONDecodeError:
        # Fallback if parsing fails
        return {
            "risk_level": "medium",
            "confidence": 0.5,
            "reason": "Could not parse AI response — defaulting to medium risk",
            "used_ai": True,
        }


async def classify_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main classification function.
    Tries rules first, falls back to AI.
    """
    # Try fast rules first
    result = rules_check(transaction)
    if result:
        print(f"  [RULES] {transaction.get('transaction_id')} → {result['risk_level']}")
        return result

    # Use AI for ambiguous cases
    result = await classify_with_ai(transaction)
    print(f"  [AI]    {transaction.get('transaction_id')} → {result['risk_level']} ({result['confidence']:.0%})")
    return result