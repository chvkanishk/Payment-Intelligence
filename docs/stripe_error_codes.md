# Stripe API Error Codes — Stripe Documentation

## Overview

Stripe uses conventional HTTP response codes to indicate the success or failure of an API request. Codes in the `2xx` range indicate success. Codes in the `4xx` range indicate an error from the provided information. Codes in the `5xx` range indicate a Stripe server error.

When an API error occurs, the response includes an `error` object with details.

---

## Error Object Structure

```json
{
  "error": {
    "code": "card_declined",
    "decline_code": "insufficient_funds",
    "doc_url": "https://stripe.com/docs/error-codes/card-declined",
    "message": "Your card has insufficient funds.",
    "param": null,
    "payment_intent": { ... },
    "request_log_url": "https://dashboard.stripe.com/logs/req_xxxxx",
    "type": "card_error"
  }
}
```

---

## Error Types

| Type | Description |
|---|---|
| `api_error` | Stripe server error — retry the request |
| `card_error` | Card was declined — show message to customer |
| `idempotency_error` | Idempotency key reused with different parameters |
| `invalid_request_error` | Invalid parameters in your request |

---

## HTTP Status Codes

| Status | Meaning |
|---|---|
| `200 OK` | Request succeeded |
| `400 Bad Request` | Invalid request parameters |
| `401 Unauthorized` | Invalid API key |
| `402 Payment Required` | Parameters valid but payment failed |
| `403 Forbidden` | No permission for this action |
| `404 Not Found` | Resource not found |
| `409 Conflict` | Idempotency key conflict |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Stripe server error |

---

## Card Error Codes (code field)

| Code | Description | Resolution |
|---|---|---|
| `card_declined` | Card was declined | Use `decline_code` for specifics |
| `expired_card` | Card has expired | Ask customer for new card |
| `incorrect_cvc` | CVC is incorrect | Ask customer to re-enter CVC |
| `incorrect_number` | Card number is incorrect | Ask customer to check card number |
| `incorrect_zip` | ZIP code failed validation | Ask customer to check ZIP |
| `insufficient_funds` | Card has insufficient funds | Ask customer to use different card |
| `invalid_cvc` | CVC format is invalid | Validate CVC format on your form |
| `invalid_expiry_month` | Expiry month is invalid | Check expiry month format |
| `invalid_expiry_year` | Expiry year is invalid | Check expiry year format |
| `invalid_number` | Card number format invalid | Validate card number on your form |
| `processing_error` | Error while processing | Retry the charge |

---

## Decline Codes (decline_code field)

Decline codes are returned when `code` is `card_declined`:

| Decline Code | Meaning | Next Step |
|---|---|---|
| `authentication_required` | 3DS required | Retry with 3D Secure authentication |
| `approve_with_id` | Payment cannot be authorized | Retry once. If still declined, contact bank |
| `call_issuer` | Card declined for unknown reason | Customer must call their bank |
| `card_not_supported` | Card doesn't support this type of purchase | Use a different card |
| `card_velocity_exceeded` | Too many transactions on this card | Wait and retry later |
| `currency_not_supported` | Card doesn't support the currency | Use a different card or currency |
| `do_not_honor` | Generic decline | Customer must contact their bank |
| `do_not_try_again` | Do not retry | Customer must use a different card |
| `duplicate_transaction` | Same transaction submitted twice | Check if transaction already succeeded |
| `expired_card` | Card has expired | Use a different card |
| `fraudulent` | Suspected fraudulent card | Do not retry |
| `generic_decline` | Generic decline with no other information | Customer must contact their bank |
| `insufficient_funds` | Not enough funds | Use a different card |
| `invalid_account` | Account invalid or not set up | Customer must contact their bank |
| `invalid_amount` | Amount invalid or exceeds allowed amount | Check the amount |
| `issuer_not_available` | Issuer bank not reachable | Retry later |
| `lost_card` | Card reported lost | Do not retry, contact customer |
| `merchant_blacklist` | Card on merchant block list | Do not retry |
| `new_account_information_available` | Card has been replaced | Ask customer for new card |
| `no_action_taken` | Decline with no other information | Customer must contact their bank |
| `not_permitted` | Payment not permitted | Customer must contact their bank |
| `online_or_offline_pin_required` | PIN required | Use card in person |
| `pickup_card` | Card should be confiscated | Do not retry |
| `pin_try_exceeded` | Too many PIN attempts | Customer must contact their bank |
| `restricted_card` | Card restricted for this type of purchase | Customer must contact their bank |
| `revocation_of_all_authorizations` | All authorizations revoked | Customer must contact their bank |
| `revocation_of_authorization` | Authorization revoked | Customer must contact their bank |
| `security_violation` | Security violation | Customer must contact their bank |
| `service_not_allowed` | Service not allowed | Customer must contact their bank |
| `stolen_card` | Card reported stolen | Do not retry, contact customer |
| `stop_payment_order` | Stop payment order issued | Customer must contact their bank |
| `transaction_not_allowed` | Transaction type not allowed | Customer must contact their bank |
| `try_again_later` | Temporary issue | Retry once after a brief delay |
| `withdrawal_count_limit_exceeded` | Withdrawal limit exceeded | Use a different card |

---

## Invalid Request Error Codes

| Code | Description |
|---|---|
| `account_closed` | Customer bank account is closed |
| `account_country_invalid_address` | Business address country doesn't match account country |
| `amount_too_large` | Amount exceeds the maximum allowed |
| `amount_too_small` | Amount is below the minimum — typically $0.50 USD |
| `api_key_expired` | API key has expired — rotate your keys |
| `authentication_required` | Request requires authentication |
| `balance_insufficient` | Stripe balance is insufficient for the payout |
| `bank_account_exists` | Bank account already added to this customer |
| `bank_account_unverified` | Bank account not yet verified |
| `charge_already_captured` | Charge has already been captured |
| `charge_already_refunded` | Charge has already been fully refunded |
| `charge_disputed` | Charge has been disputed |
| `charge_exceeds_source_limit` | Charge exceeds allowed transaction limit |
| `charge_expired_for_capture` | Charge authorization has expired |
| `country_unsupported` | Country is not supported |
| `coupon_expired` | Coupon has expired |
| `customer_max_payment_methods` | Customer has reached the maximum number of payment methods |
| `email_invalid` | Email address is invalid |
| `idempotency_key_in_use` | Idempotency key is being used by another request |
| `invoice_no_customer_line_items` | Invoice has no customer-related line items |
| `invoice_not_editable` | Invoice can no longer be edited |
| `invoice_payment_intent_requires_action` | Invoice payment requires additional action |
| `missing` | Required parameter missing |
| `parameter_invalid_empty` | Required parameter is empty |
| `parameter_invalid_integer` | Parameter expected to be an integer |
| `parameter_invalid_string_blank` | Parameter is blank |
| `parameter_missing` | Required parameter not provided |
| `parameter_unknown` | Unknown parameter sent — check for typos |
| `payment_intent_action_required` | PaymentIntent requires customer action |
| `payment_intent_authentication_failure` | Authentication failed |
| `payment_intent_incompatible_payment_method` | Payment method not compatible |
| `payment_intent_invalid_parameter` | Invalid PaymentIntent parameter |
| `payment_method_unactivated` | Payment method not yet activated |
| `postal_code_invalid` | Postal code is invalid |
| `product_inactive` | Product is no longer active |
| `rate_limit` | Too many requests — back off and retry |
| `resource_already_exists` | Resource already created |
| `resource_missing` | Resource not found |
| `routing_number_invalid` | Bank routing number is invalid |
| `secret_key_required` | Request requires secret key, not publishable key |
| `setup_attempt_failed` | Payment method setup failed |
| `setup_intent_authentication_failure` | Authentication failed for SetupIntent |
| `tax_id_invalid` | Tax ID is invalid |
| `testmode_charges_only` | Account can only make test mode charges |
| `token_already_used` | Token has already been used |
| `token_in_use` | Token is currently being used |
| `transfer_source_balance_parameters_mismatch` | Balance parameters mismatch |
| `transfers_not_allowed` | Transfers not allowed on this account |
| `url_invalid` | URL is invalid |

---

## Handling Errors in Code

```python
import stripe

try:
    charge = stripe.Charge.create(
        amount=2000,
        currency="usd",
        source="tok_visa",
    )
except stripe.error.CardError as e:
    # Card was declined
    body = e.json_body
    err = body.get("error", {})
    print(f"Card declined: {err.get('decline_code')}")
    print(f"Message: {err.get('message')}")

except stripe.error.RateLimitError:
    # Too many requests — implement exponential backoff
    pass

except stripe.error.InvalidRequestError as e:
    # Invalid parameters
    print(f"Invalid param: {e.param}")

except stripe.error.AuthenticationError:
    # Invalid API key
    pass

except stripe.error.APIConnectionError:
    # Network error — retry
    pass

except stripe.error.StripeError:
    # Generic Stripe error
    pass
```

---

## Idempotency Keys

Use idempotency keys to safely retry failed requests without creating duplicate charges:

```python
import stripe
import uuid

idempotency_key = str(uuid.uuid4())  # or use your own order ID

charge = stripe.Charge.create(
    amount=2000,
    currency="usd",
    source="tok_visa",
    idempotency_key=idempotency_key
)
```

If the same request is made with the same idempotency key within 24 hours, Stripe returns the original response without creating a new charge.
