# Receive Stripe Events with Webhooks — Stripe Documentation

## Overview

Webhooks are HTTP POST requests sent by Stripe to your server when events happen in your account. Instead of polling the Stripe API, webhooks push data to you in real time.

Use webhooks to:
- Fulfill orders when a payment succeeds
- Email customers after a refund is issued
- Update a database when a subscription changes
- Alert your team when a dispute is created
- Trigger downstream workflows based on payment events

---

## How Webhooks Work

1. An event occurs in Stripe (e.g., payment succeeds)
2. Stripe creates an Event object
3. Stripe sends a POST request to your registered webhook endpoint
4. Your endpoint returns a `200` response
5. If no `200` is received, Stripe retries with exponential backoff

---

## Register a Webhook Endpoint

In the Stripe Dashboard → Developers → Webhooks → Add endpoint. Or via API:

```python
import stripe

webhook = stripe.WebhookEndpoint.create(
    url="https://example.com/stripe/webhook",
    enabled_events=[
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
        "charge.dispute.created",
        "customer.subscription.deleted",
    ],
)
```

---

## Webhook Payload Structure

Every webhook has the same envelope structure:

```json
{
  "id": "evt_1NirD82eZvKYlo2CIvbtLWuY",
  "object": "event",
  "api_version": "2023-10-16",
  "created": 1692819038,
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_3MtwBwLkdIwHu7ix28a3tqPv",
      "object": "payment_intent",
      "amount": 2000,
      "currency": "usd",
      "status": "succeeded"
    }
  },
  "livemode": false,
  "pending_webhooks": 1,
  "request": {
    "id": "req_xxxxx",
    "idempotency_key": "xxxxx"
  }
}
```

---

## Verify Webhook Signatures

Always verify that webhook requests come from Stripe. Stripe signs every webhook with a secret:

```python
import stripe
from fastapi import Request, HTTPException

WEBHOOK_SECRET = "whsec_..."

async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        handle_payment_success(payment_intent)

    return {"status": "success"}
```

**Warning:** Stripe requires the raw request body for signature verification. Do not parse the body as JSON before verifying — this alters the raw bytes and causes verification to fail.

---

## Common Event Types

### Payment Events

| Event | Description |
|---|---|
| `payment_intent.succeeded` | Payment completed successfully |
| `payment_intent.payment_failed` | Payment attempt failed |
| `payment_intent.created` | A new PaymentIntent was created |
| `payment_intent.canceled` | PaymentIntent was canceled |
| `payment_intent.requires_action` | 3DS authentication required |

### Charge Events

| Event | Description |
|---|---|
| `charge.succeeded` | Charge succeeded |
| `charge.failed` | Charge failed |
| `charge.refunded` | Charge was refunded |
| `charge.dispute.created` | A dispute was opened |
| `charge.dispute.closed` | A dispute was resolved |

### Subscription Events

| Event | Description |
|---|---|
| `customer.subscription.created` | New subscription created |
| `customer.subscription.updated` | Subscription changed |
| `customer.subscription.deleted` | Subscription canceled |
| `invoice.paid` | Invoice payment succeeded |
| `invoice.payment_failed` | Invoice payment failed |

### Refund Events

| Event | Description |
|---|---|
| `refund.created` | Refund initiated |
| `refund.updated` | Refund status changed |
| `refund.failed` | Refund failed |

---

## Retry Behavior

If your endpoint returns anything other than a `2xx` response, Stripe retries the webhook over the following schedule:

| Attempt | Delay |
|---|---|
| 1st retry | 5 minutes |
| 2nd retry | 30 minutes |
| 3rd retry | 2 hours |
| 4th retry | 5 hours |
| 5th retry | 10 hours |

Stripe stops retrying after **3 days** and marks the event as failed.

---

## Handle Webhooks Asynchronously

Never do slow work synchronously in your webhook handler. Return `200` immediately and process in the background:

```python
from fastapi import BackgroundTasks

async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    event = verify_and_parse(request)
    
    # Return 200 immediately
    background_tasks.add_task(process_event, event)
    return {"status": "received"}

async def process_event(event):
    # Do the slow work here (DB writes, emails, etc.)
    if event["type"] == "payment_intent.succeeded":
        await fulfill_order(event["data"]["object"])
```

---

## Idempotent Webhook Handling

Stripe may send the same event more than once. Always handle webhooks idempotently:

```python
async def handle_payment_success(payment_intent_id: str):
    # Check if already processed
    existing = await db.fetch("SELECT id FROM orders WHERE payment_intent_id = $1", payment_intent_id)
    if existing:
        return  # already handled, skip

    # Process for the first time
    await db.execute("INSERT INTO orders (payment_intent_id, ...) VALUES (...)")
```

---

## Webhook Best Practices

- Return `200` before doing any processing — prevents Stripe from thinking delivery failed
- Store raw event payload in your database for auditing
- Use the event `id` as an idempotency key to deduplicate
- Never trust data in the webhook payload alone — re-fetch the object from Stripe API to confirm
- Monitor webhook failures in the Stripe Dashboard → Developers → Webhooks
- Rotate your webhook signing secret periodically
- Use HTTPS for your endpoint (required in live mode)
- Stripe webhooks support TLS v1.2 and v1.3 only

---

## Test Webhooks Locally

Use the Stripe CLI to forward events to your local server:

```bash
stripe listen --forward-to localhost:8000/stripe/webhook
```

Trigger a specific event for testing:

```bash
stripe trigger payment_intent.succeeded
```

---

## Webhook Logs

View webhook delivery attempts in the Stripe Dashboard under Developers → Webhooks → select endpoint → Events tab. Each event shows:
- Delivery status (Delivered, Pending, Failed)
- HTTP response code returned by your server
- Request and response payload
- Timestamp of delivery attempts
