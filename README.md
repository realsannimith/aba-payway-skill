# ABA PayWay Skill

An [Agent Skill](https://code.claude.com/docs/en/skills) that gives Claude (or any
skill-compatible agent) a complete, offline reference and helper toolkit for integrating the
**ABA PayWay** payment gateway (ABA Bank, Cambodia) — KHQR/Bakong QR, cards, ABA PAY, WeChat Pay,
Alipay, and Google Pay.

Integrating PayWay is mostly plain REST — what actually trips people up is (1) building the
`hash` (HMAC-SHA512) in the exact required field order and (2) RSA-encrypting fields like
`merchant_auth` / `beneficiaries`. This skill bundles ABA's docs as structured references and
ships tested PHP/Python helpers so an agent (or you) don't have to reverse-engineer either one
from scratch.

## What's inside

```
SKILL.md              Entry point: when to use this skill, the core hashing/RSA recipe,
                       flow selection guide, error-code cheatsheet.
references/
  api-index.md         Start here — every endpoint's path, content-type, hash field order,
                        RSA requirement, and rate limit in one table.
  00-overview.md        Auth, environments, RSA pattern, sandbox test cards.
  01-23-*.md            One file per endpoint: params, request/response examples, error codes
                        (Purchase, Check/Get Transaction, Refund, Link Card/Account, Pre-Auth,
                        Payout, Beneficiaries, Payment Links, Exchange Rate, ...).
  24-khqr-guideline.md  KHQR data-object spec + payment webhook.
  25-ecommerce-checkout-guide.md   End-to-end web/mobile checkout + pushback handling.
  26-resources.md       Sandbox test cards, plugins.
scripts/
  payway.py             hash_for(...), rsa_encrypt(...), req_time(), endpoint_url(...),
                        HASH_ORDERS / ENDPOINTS dicts, and example request builders.
  payway.php            Same helpers as a PayWay class (openssl_public_encrypt / hash_hmac),
                        drop-in for Laravel or vanilla PHP.
```

## Using it as a Claude Skill

Copy (or symlink) this repo into your skills directory, e.g.:

```bash
git clone git@github.com:realsannimith/ABA-Payway-Skill.git ~/.claude/skills/aba-payway
```

Claude will automatically pull in `SKILL.md` and the bundled references whenever a conversation
touches ABA PayWay, PayWay, ABA Pay, KHQR/Bakong QR, or ABA Bank online payments — building a
checkout, generating the `hash`, RSA-encrypting `merchant_auth`/`beneficiaries`, verifying a
transaction, handling `return_url`/webhooks, refunds, tokenization, pre-auth, payouts, payment
links, exchange rates, or debugging a "Wrong hash" (code 1) / "domain not whitelisted" (code 6)
error.

## Using the helpers directly

You don't need an agent to benefit from `scripts/` — they're plain, dependency-light hash/RSA
helpers you can import directly.

**Python** (`pip install cryptography` for the RSA-based APIs):

```python
from payway import make_hash, req_time, HASH_ORDERS

params = {"req_time": req_time(), "merchant_id": "ec000002", "tran_id": "20260705120000"}
h = make_hash(params, HASH_ORDERS["check_transaction"], api_key="YOUR_API_KEY")
```

**PHP**:

```php
require 'payway.php';

$hash = PayWay::hashFor('check_transaction', [
    'req_time'    => PayWay::reqTime(),
    'merchant_id' => 'ec000002',
    'tran_id'     => '20260705120000',
], $apiKey);
```

See `SKILL.md` for the full hashing/RSA recipe, currency rules, and a guide to picking the right
API flow (checkout, KHQR, tokenized/recurring payments, pre-auth, payouts, payment links).

## Credentials

You'll need, per merchant profile, from ABA: `merchant_id`, an API key (HMAC secret), and — for
the RSA-based APIs (refund, pre-auth, payout, payment links, beneficiaries) — an RSA public key.
Sandbox and production use separate base URLs, dashboards, and credentials. Register a sandbox
account at `sandbox.payway.com.kh`; request production access via `paywaysales@ababank.com`.

**Never commit real credentials to this repo or expose the API key / RSA key client-side** —
keep them server-side only.

## License

MIT — see [LICENSE](LICENSE).
