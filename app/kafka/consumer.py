"""
Kafka Consumer — Real-time Transaction Classifier
-------------------------------------------------
Reads transactions from Kafka, classifies them,
stores results in PostgreSQL, publishes alerts for high risk.
"""

import asyncio
import json
import asyncpg
from kafka import KafkaConsumer, KafkaProducer
from app.core.config import get_settings
from app.services.classifier import classify_transaction

settings = get_settings()


async def process_transaction(
    conn: asyncpg.Connection,
    producer: KafkaProducer,
    transaction: dict,
):
    """Classify one transaction and store the result."""
    txn_id = transaction.get("transaction_id")
    print(f"\nProcessing: {txn_id} — ${transaction.get('amount')} at {transaction.get('merchant')}")

    # Classify (rules or AI)
    classification = await classify_transaction(transaction)

    risk_level = classification["risk_level"]
    confidence = classification.get("confidence", 0.0)
    reason = classification.get("reason", "")

    # Store classification in PostgreSQL
    await conn.execute(
        """
        INSERT INTO transactions (
            transaction_id, amount, merchant, status,
            location, risk_level, risk_reason
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (transaction_id) DO UPDATE SET
            risk_level   = EXCLUDED.risk_level,
            risk_reason  = EXCLUDED.risk_reason
        """,
        txn_id,
        float(transaction.get("amount", 0)),
        transaction.get("merchant"),
        transaction.get("status", "pending"),
        transaction.get("location"),
        risk_level,
        reason,
    )

    # Publish alert if high risk
    if risk_level == "high":
        alert = {
            "transaction_id": txn_id,
            "amount": transaction.get("amount"),
            "merchant": transaction.get("merchant"),
            "location": transaction.get("location"),
            "risk_level": risk_level,
            "confidence": confidence,
            "reason": reason,
        }
        producer.send(
            settings.kafka_alerts_topic,
            value=json.dumps(alert).encode("utf-8"),
        )
        producer.flush()
        print(f"  🚨 ALERT published for {txn_id}")


async def run_consumer():
    """Main consumer loop — reads from Kafka indefinitely."""
    print("Connecting to database...")
    conn = await asyncpg.connect(settings.database_url)

    print(f"Connecting to Kafka at {settings.kafka_bootstrap_servers}...")
    consumer = KafkaConsumer(
        settings.kafka_transactions_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="payment-classifier",
        consumer_timeout_ms=1000,
    )

    producer = KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
    )

    print(f"Listening on topic: '{settings.kafka_transactions_topic}'")
    print("Waiting for transactions...\n")

    try:
        while True:
            # Poll for messages
            records = consumer.poll(timeout_ms=1000)
            for topic_partition, messages in records.items():
                for message in messages:
                    await process_transaction(conn, producer, message.value)

            # Small sleep to avoid CPU spinning
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    finally:
        consumer.close()
        producer.close()
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_consumer())