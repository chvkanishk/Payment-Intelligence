"""
Seed Kafka with fake transactions for testing.

Usage:
    python scripts/seed_kafka.py
"""

import json
import time
import random
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "transactions"

# Sample transactions — mix of risk levels
TRANSACTIONS = [
    {
        "transaction_id": "txn_k001",
        "amount": 4.99,
        "merchant": "Netflix",
        "location": "USA",
        "status": "pending",
        "card_type": "credit",
        "hour": 14,
    },
    {
        "transaction_id": "txn_k002",
        "amount": 8750.00,
        "merchant": "XYZ Corp",
        "location": "Nigeria",
        "status": "pending",
        "card_type": "new",
        "hour": 3,
    },
    {
        "transaction_id": "txn_k003",
        "amount": 250.00,
        "merchant": "Best Buy",
        "location": "USA",
        "status": "pending",
        "card_type": "debit",
        "hour": 15,
    },
    {
        "transaction_id": "txn_k004",
        "amount": 12500.00,
        "merchant": "Unknown LLC",
        "location": "Russia",
        "status": "pending",
        "card_type": "prepaid",
        "hour": 2,
    },
    {
        "transaction_id": "txn_k005",
        "amount": 35.00,
        "merchant": "Starbucks",
        "location": "USA",
        "status": "pending",
        "card_type": "credit",
        "hour": 8,
    },
    {
        "transaction_id": "txn_k006",
        "amount": 3200.00,
        "merchant": "Electronics Hub",
        "location": "China",
        "status": "pending",
        "card_type": "credit",
        "hour": 23,
    },
    {
        "transaction_id": "txn_k007",
        "amount": 89.99,
        "merchant": "Amazon",
        "location": "USA",
        "status": "pending",
        "card_type": "credit",
        "hour": 11,
    },
    {
        "transaction_id": "txn_k008",
        "amount": 15000.00,
        "merchant": "Crypto Exchange",
        "location": "Ukraine",
        "status": "pending",
        "card_type": "new",
        "hour": 4,
    },
]


def main():
    print(f"Connecting to Kafka at {BOOTSTRAP_SERVERS}...")
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    print(f"Publishing {len(TRANSACTIONS)} transactions to '{TOPIC}'...\n")

    for txn in TRANSACTIONS:
        producer.send(TOPIC, value=txn)
        print(f"  ✓ Published {txn['transaction_id']} — ${txn['amount']} at {txn['merchant']} ({txn['location']})")
        time.sleep(0.5)

    producer.flush()
    producer.close()
    print(f"\nDone! {len(TRANSACTIONS)} transactions published.")
    print("Now run the consumer to classify them:")
    print("  python -m app.kafka.consumer")


if __name__ == "__main__":
    main()
