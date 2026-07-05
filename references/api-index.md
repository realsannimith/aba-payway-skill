# ABA PayWay — API Quick Index

One-line lookup for every endpoint. **"Hash order" is the exact concatenation used to
build the `hash` field** — build the string in this order (empty string for any omitted
field), then `base64(HMAC-SHA512(string, api_key))` unless noted. For full request/response
schemas and error codes, open the numbered reference file.

Base URLs: sandbox `https://checkout-sandbox.payway.com.kh` · production `https://checkout.payway.com.kh`
All requests are **POST**. `api_key` is the secret HMAC key; `public_key` in ABA's docs = this same api_key.

## Checkout

| API | Ref | Endpoint | Content-Type | Hash order | RSA | Rate limit |
|-----|-----|----------|--------------|-----------|-----|-----------|
| Purchase | 01 | `/api/payment-gateway/v1/payments/purchase` | multipart/form-data | req_time, merchant_id, tran_id, amount, items, shipping, firstname, lastname, email, phone, type, payment_option, return_url, cancel_url, continue_success_url, return_deeplink, currency, custom_fields, return_params, payout, lifetime, additional_params, google_pay_token, skip_success_page | No | — |
| Check Transaction | 02 | `/api/payment-gateway/v1/payments/check-transaction-2` | application/json | req_time, merchant_id, tran_id | No | 600/sec |
| Get Transaction Details | 03 | `/api/payment-gateway/v1/payments/transaction-detail` | application/json | req_time, merchant_id, tran_id | No | **10/min (hard cap)** |
| Get Transaction List | 04 | `/api/payment-gateway/v1/payments/transaction-list-2` | application/json | req_time, merchant_id, from_date, to_date, from_amount, to_amount, status, page, pagination | No | — |
| Close Transaction | 05 | `/api/payment-gateway/v1/payments/close-transaction` | application/json | req_time, merchant_id, tran_id | No | — |
| Refund | 06 | `/api/merchant-portal/merchant-access/online-transaction/refund` | application/json | request_time, merchant_id, merchant_auth | **Yes** (merchant_auth = mc_id, tran_id, refund_amount) | 500/sec |
| Exchange Rate | 07 | `/api/payment-gateway/v1/exchange-rate` | application/json | req_time, merchant_id | No | — |
| Get Transactions by Merchant Ref | 23 | `/api/payment-gateway/v1/payments/get-transactions-by-mc-ref` | application/json | req_time, merchant_id, merchant_ref | No | **10/min (hard cap)** |

## QR & Payment Link

| API | Ref | Endpoint | Content-Type | Hash order | RSA |
|-----|-----|----------|--------------|-----------|-----|
| QR API (generate QR) | 14 | `/api/payment-gateway/v1/payments/generate-qr` | application/json | req_time, merchant_id, tran_id, amount, items, first_name, last_name, email, phone, purchase_type, payment_option, callback_url, return_deeplink, currency, custom_fields, return_params, payout, lifetime, qr_image_template | No |
| Create Payment Link | 15 | `/api/merchant-portal/merchant-access/payment-link/create` | multipart/form-data | request_time, merchant_id, merchant_auth | **Yes** |
| Get Payment Link Details | 16 | `/api/merchant-portal/merchant-access/payment-link/detail` | application/json | request_time, merchant_id, merchant_auth | **Yes** |

## Credentials on File (tokenization / auto-payments)

| API | Ref | Endpoint | Content-Type | Hash order | RSA |
|-----|-----|----------|--------------|-----------|-----|
| Link Account | 08 | `/api/aof/request-qr` | application/json | merchant_id, req_time, return_deeplink | No |
| Link Card | 09 | `/api/payment-gateway/v1/cof/initial` | multipart/form-data | merchant_id, ctid, return_param | No |
| Purchase Using Token | 10 | `/api/payment-gateway/v1/payments/purchase` | application/json | req_time, merchant_id, tran_id, amount, items, shipping, ctid, pwt, firstname, lastname, email, phone, type, return_url, currency, custom_fields, return_params, payout | No |
| Remove Account Token | 11 | `/api/aof/remove-account` | application/json | merchant_id, req_time, ctid, pwt | No |
| Remove Card Token | 12 | `/api/payment-gateway/v1/cof/remove` | application/json | merchant_id, ctid, pwt | No |
| Get Linked Account Details | 13 | `/api/aof/pushback-status` | application/json | merchant_id, req_time, return_param | No |

## Pre-Auth (hold & capture)

| API | Ref | Endpoint | Content-Type | Hash order | RSA (merchant_auth fields) |
|-----|-----|----------|--------------|-----------|-----|
| Complete Pre-Auth | 17 | `/api/merchant-portal/merchant-access/online-transaction/pre-auth-completion` | application/json | merchant_auth, request_time, merchant_id | **Yes** (mc_id, tran_id, complete_amount) |
| Complete Pre-Auth with Payout | 18 | `/api/merchant-portal/merchant-access/online-transaction/pre-auth-completion` | application/json | merchant_auth, request_time, merchant_id | **Yes** (mc_id, tran_id, complete_amount, payout) |
| Cancel Pre-Auth | 19 | `/api/merchant-portal/merchant-access/online-transaction/pre-auth-cancellation` | application/json | merchant_id, merchant_auth, request_time | **Yes** (mc_id, tran_id) |

## Payout & Beneficiaries

| API | Ref | Endpoint | Content-Type | Hash order | RSA | Notes |
|-----|-----|----------|--------------|-----------|-----|-------|
| Payout | 20 | `/api/payment-gateway/v2/direct-payment/merchant/payout` | application/json | merchant_id, tran_id, beneficiaries, amount, custom_fields, currency | **Yes** (beneficiaries array) | **Doc shows HEX hash output, not base64.** Max 10 beneficiaries. |
| Add Beneficiary to Whitelist | 21 | `/api/merchant-portal/merchant-access/whitelist-account/add-whitelist-payout` | application/json | request_time, merchant_auth | **Yes** (mc_id, payee) | Whitelist before payout |
| Update Beneficiary Status | 22 | `/api/merchant-portal/merchant-access/whitelist-account/update-whitelist-status` | application/json | request_time, merchant_auth | **Yes** (mc_id, payee, status) | |

## Guides (no endpoint)

- **24 — KHQR Guideline**: KHQR/Bakong QR data-object spec, webhook payload for QR/ABA PAY payments.
- **25 — eCommerce Checkout Guide**: end-to-end web/mobile checkout flow, pushback (`return_url`) payload, PayWay plugin JS.
- **26 — Resources**: test cards, checkout plugins.
