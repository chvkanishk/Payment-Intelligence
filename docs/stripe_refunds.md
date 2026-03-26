# Refund and Cancel Payments — Stripe Documentation

## Overview

Stripe allows you to refund charges that have been created but not yet refunded. Refunds can be issued for the full amount or a partial amount. Multiple partial refunds can be issued up to the full amount of the original charge.

Refunds are processed immediately but the time it takes for the funds to appear in the customer's account depends on their bank. Credit card refunds typically take 5–10 business days.

---

## Create a Refund

To refund a charge, create a Refund object with the charge ID:

```python
import stripe
refund = stripe.Refund.create(charge="ch_1NirD82eZvKYlo2CIvbtLWuY")
```

Alternatively refund using a PaymentIntent ID:

```python
refund = stripe.Refund.create(payment_intent="pi_3MtwBwLkdIwHu7ix28a3tqPv")
```

---

## Refund Reasons

You can optionally set a reason for the refund:

| Reason | Description |
|---|---|
| `duplicate` | The charge is a duplicate of another charge |
| `fraudulent` | The charge is fraudulent |
| `requested_by_customer` | The customer has requested a refund |

Setting a reason of `fraudulent` marks the payment as fraudulent and adds the card to the block list.

---

## Partial Refunds

Partial refunds allow you to refund a specific amount rather than the full charge. You can issue multiple partial refunds as long as the total doesn't exceed the original charge amount.

```python
refund = stripe.Refund.create(
    charge="ch_1NirD82eZvKYlo2CIvbtLWuY",
    amount=2500  # amount in cents — refunds $25.00
)
```

---

## Refund Statuses

| Status | Description |
|---|---|
| `pending` | Refund is being processed |
| `succeeded` | Refund completed successfully |
| `failed` | Refund failed — funds returned to Stripe balance |
| `canceled` | Refund was canceled before processing |
| `requires_action` | Additional action required to complete refund |

---

## Refund Timing by Payment Method

| Payment Method | Timing |
|---|---|
| Credit / Debit Card | 5–10 business days |
| ACH Direct Debit | 3–5 business days |
| SEPA Direct Debit | 5–10 business days |
| Klarna | 5–7 business days |
| Afterpay / Clearpay | 3–10 business days |
| Bank transfer | 3–5 business days |

---

## Refund Failures

Refunds can fail if:
- The customer's bank account has been closed
- The card has expired or been canceled
- The account is blocked

When a refund fails, its status is set to `failed`. Stripe returns the funds to your Stripe balance. You must arrange an alternative form of payment to return funds to the customer.

---

## Cancel a Refund

You can cancel a refund while it is in `pending` status:

```python
stripe.Refund.cancel("re_1NirD82eZvKYlo2CIvbtLWuY")
```

Once a refund is `succeeded`, it cannot be canceled.

---

## Refund Metadata

Add metadata to a refund to track it in your system:

```python
refund = stripe.Refund.create(
    charge="ch_1NirD82eZvKYlo2CIvbtLWuY",
    metadata={"order_id": "ord_12345", "reason_detail": "item not received"}
)
```

---

## Webhooks for Refunds

Listen for these events in your webhook handler:

| Event | Description |
|---|---|
| `charge.refunded` | A charge has been refunded |
| `refund.created` | A refund has been created |
| `refund.updated` | A refund has been updated |
| `refund.failed` | A refund has failed |

---

## Refund Fees

Stripe's processing fees are non-refundable. When you issue a refund, you get back the charge amount minus the original processing fee. 

For example, if you process a $100 payment with a 2.9% + $0.30 fee, Stripe collected $3.20 in fees. If you refund the $100, you receive $96.80 back to your balance — not the full $100.

---

## Instant Refunds

Eligible merchants on Stripe can offer Instant Refunds, which return funds to the customer's debit card within 30 minutes. Instant refunds require:
- US-issued Visa or Mastercard debit card
- Merchant must be enabled for instant payouts
- Refund must be initiated within 180 days of the original charge

---

## Best Practices

- Always check if a refund is still `pending` before attempting to cancel it
- Use `idempotency_key` when creating refunds to prevent duplicate refunds
- Store the refund ID in your database immediately after creation
- Listen to `refund.failed` webhooks to handle failed refunds proactively
- For subscription refunds, consider using Credit Notes instead of direct refunds
