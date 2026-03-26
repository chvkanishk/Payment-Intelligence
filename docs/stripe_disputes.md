# Disputes and Chargebacks — Stripe Documentation

## Overview

A dispute (also called a chargeback) occurs when a customer questions a charge with their card issuer. The card issuer creates a formal dispute and immediately reverses the payment, pulling the funds back from your Stripe balance. Stripe notifies you of the dispute and you have the opportunity to submit evidence to contest it.

Disputes are one of the most important issues to manage in a payment platform. An elevated dispute rate can result in card network monitoring programs and potential account termination.

---

## Dispute Process

1. **Customer contacts their bank** — they claim a charge is unauthorized, fraudulent, or that the product/service was not delivered
2. **Bank creates a chargeback** — the funds are immediately reversed from your account
3. **Stripe notifies you** — via webhook and Dashboard
4. **You submit evidence** — you have a deadline (typically 7–21 days depending on card network) to respond
5. **Bank makes a decision** — the bank reviews your evidence and rules in favor of you or the customer
6. **Outcome** — if you win, funds are returned; if you lose, the reversal stands and a dispute fee is charged

---

## Dispute Reasons

| Reason | Description |
|---|---|
| `fraudulent` | Customer claims they didn't authorize the charge |
| `duplicate` | Customer claims they were charged twice |
| `product_not_received` | Customer claims they didn't receive the product or service |
| `product_unacceptable` | Customer claims product was defective, damaged, or not as described |
| `credit_not_processed` | Customer claims a refund was promised but not issued |
| `subscription_canceled` | Customer claims they were charged after canceling a subscription |
| `unrecognized` | Customer doesn't recognize the charge |
| `general` | Doesn't fit into other categories |

---

## Dispute Statuses

| Status | Description |
|---|---|
| `warning_needs_response` | Early fraud warning — respond to avoid a formal dispute |
| `warning_under_review` | Response submitted, under review |
| `warning_closed` | Warning resolved without a formal chargeback |
| `needs_response` | You need to submit evidence |
| `under_review` | Evidence submitted, bank is reviewing |
| `charge_refunded` | You issued a refund before the dispute was decided |
| `won` | You won the dispute, funds returned |
| `lost` | You lost the dispute, funds not returned |

---

## Responding to a Dispute

### Retrieve a dispute

```python
import stripe
dispute = stripe.Dispute.retrieve("dp_1NirD82eZvKYlo2CIvbtLWuY")
```

### Submit evidence

```python
stripe.Dispute.modify(
    "dp_1NirD82eZvKYlo2CIvbtLWuY",
    evidence={
        "customer_name": "Jane Doe",
        "customer_email_address": "jane@example.com",
        "product_description": "SaaS subscription - annual plan",
        "shipping_documentation": "file_xxxxx",
        "receipt": "file_xxxxx",
        "customer_communication": "file_xxxxx",
        "uncategorized_text": "Customer signed up on 2024-01-15 and used the service through 2024-12-31."
    },
    submit=True  # set to False to save as draft first
)
```

---

## Evidence Types

Submit as much relevant evidence as possible:

| Evidence Field | Best For |
|---|---|
| `receipt` | Proof of purchase |
| `customer_communication` | Emails showing customer acknowledged the purchase |
| `shipping_documentation` | Tracking number and delivery confirmation |
| `refund_policy` | Screenshot or text of your refund/cancellation policy |
| `service_documentation` | Proof the digital service was accessed/used |
| `cancellation_policy` | Proof customer agreed to your cancellation terms |
| `customer_signature` | Signed contracts or order forms |
| `duplicate_charge_documentation` | Proof the other charge was refunded or legitimate |

---

## Dispute Fees

When you lose a dispute, Stripe charges a **$15 dispute fee** (this varies by country). This fee is non-refundable even if you win. However, if you win the dispute, the $15 fee is refunded to you.

---

## Early Fraud Warnings (EFW)

Visa and Mastercard issue Early Fraud Warnings before a formal dispute is filed. When you receive an EFW:
- Stripe notifies you via the `radar.early_fraud_warning.created` webhook
- You have the option to issue a refund proactively to avoid the formal chargeback
- Proactive refunds reduce your dispute rate and avoid the $15 fee

---

## Dispute Rate Thresholds

Card networks monitor dispute rates carefully:

| Program | Threshold | Consequence |
|---|---|---|
| Visa Dispute Monitoring Program (VDMP) | > 0.9% dispute rate | Monitoring — escalating fees |
| Visa Fraud Monitoring Program (VFMP) | > 0.9% fraud rate | Enhanced monitoring |
| Mastercard Excessive Chargeback Program | > 1.0% dispute rate | Fines starting at $1,000/month |

Dispute rate = (disputes in month / transactions in month) × 100

---

## Webhooks for Disputes

| Event | Description |
|---|---|
| `charge.dispute.created` | A dispute has been created |
| `charge.dispute.updated` | A dispute has been updated |
| `charge.dispute.closed` | A dispute has been closed (won or lost) |
| `charge.dispute.funds_withdrawn` | Disputed funds withdrawn from balance |
| `charge.dispute.funds_reinstated` | Funds reinstated after winning a dispute |
| `radar.early_fraud_warning.created` | Early fraud warning received |

---

## Preventing Disputes

- Use Stripe Radar to block high-risk transactions
- Enable 3D Secure (3DS) for high-value transactions — shifts liability to the bank
- Send clear payment descriptors so customers recognize charges
- Respond quickly to customer complaints before they escalate to disputes
- Use `customer_name` and email in charges so statements are recognizable
- Implement a clear, easy-to-find refund policy

---

## Accepting a Dispute

If you believe the customer's claim is valid, you can accept the dispute rather than contest it:

```python
stripe.Dispute.modify(
    "dp_1NirD82eZvKYlo2CIvbtLWuY",
    evidence={},
    submit=True
)
```

Accepting a dispute avoids spending time on evidence but does not avoid the $15 dispute fee.
