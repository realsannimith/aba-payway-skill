---
name: aba-payway
description: >-
  Complete reference and helper toolkit for integrating the ABA PayWay payment gateway (ABA Bank,
  Cambodia). Use whenever the user works with ABA PayWay, PayWay, ABA Pay, KHQR/Bakong QR, or ABA
  Bank online payments in any way — building a checkout, generating the required `hash` (HMAC-SHA512),
  RSA-encrypting `merchant_auth`/`beneficiaries`, creating or verifying a transaction, handling the
  pushback/return_url or webhook, refunds, tokenizing cards/accounts (credentials on file /
  auto-payments), pre-auth hold & capture, payouts, payment links, exchange rate, or debugging a
  "Wrong hash" (code 1) or "domain not in whitelist" (code 6) error. Trigger even when the user only
  mentions merchant_id + tran_id + api_key, `checkout.payway.com.kh`, `payment-gateway/v1/payments`,
  or pastes ABA PHP sample code — in any language (PHP, Python, Node, Go, Java, Laravel, etc.). Don't
  rely on memory for ABA PayWay endpoints, hash field orders, or error codes; they're exact, so
  consult the bundled references here.
---

# ABA PayWay Integration

ABA PayWay is Cambodia's leading online payment gateway (by ABA Bank). It accepts ABA KHQR/Bakong,
credit/debit cards (Visa, Mastercard, JCB, UPI), ABA PAY, WeChat Pay, Alipay, and Google Pay.

Integrating it is mostly straightforward REST — the parts that trip people up are (1) building the
`hash` correctly and (2) RSA-encrypting a few fields. This skill exists because those two things are
exact and unforgiving: one wrong character and the server returns `Wrong hash`. The bundled
`references/` folder is the authoritative, offline copy of ABA's docs; `scripts/` has tested helpers.

## Before writing any code

Open **`references/api-index.md` first.** It's a one-screen table giving every endpoint's path,
content-type, exact hash field order, whether it needs RSA, and its rate limit. You'll save yourself
from guessing. Then open the specific numbered reference (e.g. `references/01-purchase.md`) for the
full parameter list, request/response examples, and that endpoint's error codes.

The four credentials ABA issues per merchant profile:

- **`merchant_id`** — public merchant key (goes in every request).
- **API key** — the secret HMAC key. ABA's PHP samples call it `$api_key` / `public_key`; it is the
  same secret. Never expose it client-side.
- **RSA public key** — used to encrypt `merchant_auth` / `beneficiaries` on the RSA-based APIs only.
- **Sandbox vs production base URL** — `checkout-sandbox.payway.com.kh` vs `checkout.payway.com.kh`.

Everything is **POST**. GET returns 405. The merchant's domain/IP must be **whitelisted** by ABA or
requests fail with error code `6` — this is a common first-integration surprise, not a code bug.

## The one recipe behind (almost) every API

Every signed request follows the same shape:

1. Assemble your parameters (`req_time` = current UTC as `YYYYMMDDHHmmss`, `merchant_id`, `tran_id`, …).
2. Concatenate specific fields **in the exact documented order** into one string (`b4hash`).
3. `hash = base64( HMAC_SHA512( b4hash, api_key ) )`.
4. Send the parameters **plus** `hash`.

The single most important rule, and the cause of most "Wrong hash" errors:

> **Every field in the hash order occupies its slot even when you omit it — as an empty string.**
> If the order is `…, email, phone, type, …` and you have no email, you still concatenate `""` in
> email's position. You never skip a field; you only ever substitute an empty string. Optional fields
> you don't send are empty slots, not absent slots.

Two more gotchas that cost hours:

- **The hash order is per-API and sometimes differs from the parameter-table order** shown for the
  same endpoint (Purchase and QR both call this out explicitly). Trust the *hash concatenation* order
  in the reference / in `api-index.md`, not the table.
- **`base64(binary HMAC)` is the norm.** The one documented exception is **Payout (20)**, whose PHP
  sample produces a **hex** digest (`hash_hmac(..., $key)` with no `true` flag, no base64). Follow the
  Payout reference exactly for that call, and if you get `Wrong hash` on payout, try the other form.

Don't hand-roll this. Use the helpers:

- **`scripts/payway.py`** (Python) — `hash_for(api, params, api_key)`, `rsa_encrypt(...)`,
  `req_time()`, `b64_json(...)`, `b64_str(...)`, `endpoint_url(api, env)`, plus `HASH_ORDERS` and
  `ENDPOINTS` dicts, and `build_purchase(...)` / `build_check_transaction(...)` examples.
- **`scripts/payway.php`** (PHP) — the same, mirroring ABA's official `openssl_public_encrypt` /
  `hash_hmac` samples so it drops into a Laravel/vanilla-PHP codebase. Class `PayWay` with
  `PayWay::hashFor(...)`, `PayWay::rsaEncrypt(...)`, `PayWay::reqTime()`, etc.

For **other languages** (Node/JS, Go, Java, C#, Dart…), don't look for an ABA SDK — reimplement this
recipe. The building blocks exist everywhere: HMAC-SHA512, base64, and PKCS#1 v1.5 RSA. Use
`scripts/payway.py` as the spec to port from, keeping the field order identical. A correct Node hash is
just `crypto.createHmac('sha512', apiKey).update(b4hash).digest('base64')`.

## Fields that must be Base64-encoded before hashing

Several fields are themselves Base64 blobs, and you hash the **encoded** value (not the raw JSON):
`items`, `custom_fields`, `payout`, `return_deeplink`, `additional_params` (Base64 of JSON) and
`return_url` / `callback_url` (Base64 of the raw URL string). Encode first, then place the encoded
string into the hash. `items` is description-only — ABA never uses its prices for calculation.

## The RSA-encrypted APIs (merchant_auth / beneficiaries)

Refund (06), Payment Link (15, 16), Pre-Auth complete/cancel (17, 18, 19), Payout (20), and
Beneficiary (21, 22) don't send their sensitive fields in the clear. Instead you:

1. Build a small JSON object/array (e.g. refund's `{mc_id, tran_id, refund_amount}`).
2. **RSA-encrypt it in chunks** with the merchant's RSA public key (117-byte chunks for a 1024-bit
   key — ABA's default; 245 for 2048-bit), concatenate the ciphertext, and Base64-encode the result.
   That Base64 string is `merchant_auth` (or `beneficiaries`).
3. Then compute the `hash` — and note the hash for these APIs is over the **already-encrypted**
   `merchant_auth` string, and its position in the order varies (e.g. Pre-Auth completion puts
   `merchant_auth` *first*). Check `api-index.md`.

`payway.rsa_encrypt(data, rsa_public_key_pem)` / `PayWay::rsaEncrypt($data, $rsaPublicKey)` do step 2.

## Amount & currency rules (enforced server-side)

- Currencies are **`USD`** and **`KHR`** only. If omitted, your profile's default currency is used.
- **KHR amounts must have no decimal places** (error 46) and be **> 100 KHR** (error 47).
- USD minimum is **0.01**. Zero-amount purchases are rejected (error 45).
- Control formatting yourself: pass `amount` as a string like `"1.00"` (USD) or `"4000"` (KHR) and
  make sure the *same string* is what you hashed. A mismatch between the hashed amount and the sent
  amount is another silent "Wrong hash" cause.

## Choosing the right flow

Ask what the user is actually building, then route:

- **Accept a payment on a website / app (most common)** → Purchase (01) + the eCommerce Checkout
  Guide (25). Pick a `view_type`: `hosted_view` (redirect/new tab) or `popup` (bottom-sheet on
  mobile web, modal on desktop, via the PayWay plugin JS `checkout2-0.js` + `AbaPayway.checkout()`).
  On mobile apps/webview use `view_type=hosted` and pass `return_deeplink` so the payer returns to
  your app from ABA Mobile. Set `payment_option` to preselect a method, or omit it to let PayWay show
  the picker.
- **KHQR / ABA PAY with your own QR or deeplink** → Purchase with `payment_option=abapay_khqr_deeplink`
  returns `{qr_string, abapay_deeplink, checkout_qr_url}`; or use the QR API (14) to get a rendered
  `qrImage` + `abapay_deeplink`. KHQR spec & the payment webhook are in the KHQR Guideline (24).
- **Confirm a payment succeeded** → **always verify server-side.** Call Check Transaction (02) with
  the `tran_id` (works for 7 days; use Get Transaction Details (03) for older, but note its hard
  10/min cap). Stop polling once a terminal status returns; respect 600 req/sec. Also handle the
  `return_url` pushback (`{tran_id, apv, status, return_params}`, POSTed as JSON) and, for KHQR, the
  webhook (24). Never trust a client-side "success" — reconcile against the API.
- **Refund** → Refund (06). Full or partial, within 30 days, on COMPLETED transactions; RSA-encrypted.
- **Store a card/account for later or recurring billing (auto-payments)** → Link Card (09) / Link
  Account (08) to tokenize, then Purchase Using Token (10) with `ctid` + `pwt`. Remove with 11/12.
- **Hold funds now, capture later (pre-auth)** → Purchase with `type=pre-auth`, then Complete
  Pre-Auth (17), Complete with Payout (18), or Cancel (19). Pre-auth supports ABA PAY, KHQR, and Card
  only.
- **Split/route funds to sellers or ABA accounts** → whitelist beneficiaries (21/22), then Payout
  (20). Max 10 beneficiaries per request; remember the hex-hash caveat.
- **Shareable payment link** → Create Payment Link (15) / Get details (16).
- **Live FX rate** → Exchange Rate (07).

## Testing

Register a sandbox account (`sandbox.payway.com.kh`), and ABA emails your sandbox `merchant_id` +
API key. Sandbox and production use different base URLs and separate dashboards. Sandbox test cards
(success + declined, some 3DS) are in `references/00-overview.md` and `references/26-resources.md`;
the 3DS OTP is sent to your registered email. Get production credentials via `paywaysales@ababank.com`;
technical help is `digitalsupport@ababank.com`.

## Handling responses & errors

Success is code `0` or the string `"00"` (Check Transaction returns `"00"` as a string but error
codes as numbers — compare loosely). Each reference file lists that endpoint's full error table;
the big Purchase table in `references/01-purchase.md` is the most complete. The ones you'll hit most:
`1` wrong hash (recheck field order, empty slots, and that the hashed amount == sent amount),
`6` domain not whitelisted (ask ABA to whitelist your domain/IP + return_url), `4` duplicated
tran_id (generate a fresh unique id per attempt), `81` return URL not whitelisted.

When you write integration code, wire in idempotency (unique `tran_id` per order attempt), store the
`tran_id`↔order mapping, verify server-side before fulfilling, and keep the API key and RSA key on the
server only.

## Reference map

- `references/api-index.md` — start here: every endpoint's path, content-type, hash order, RSA, limits.
- `references/00-overview.md` — auth, environments, RSA pattern, test cards, full API index.
- `references/01`–`23` — one file per endpoint (params, examples, error codes).
- `references/24-khqr-guideline.md` — KHQR data-object spec + payment webhook.
- `references/25-ecommerce-checkout-guide.md` — end-to-end web/mobile checkout + pushback.
- `references/26-resources.md` — test cards, plugins.
- `scripts/payway.py`, `scripts/payway.php` — tested hash / RSA / encoding helpers.
