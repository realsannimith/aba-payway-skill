"""
ABA PayWay helper library (Python).

Handles the two things that are easy to get wrong when integrating ABA PayWay:

  1. HMAC-SHA512 hash generation -- the exact field order matters, and every
     field that participates must be concatenated in its slot even when it is
     empty/omitted. A missing slot is the #1 cause of "Wrong hash" (code 1).

  2. RSA chunked encryption of the `merchant_auth` / `beneficiaries` fields,
     used by the refund, pre-auth, payout, payment-link and beneficiary APIs.

This is dependency-light: it uses `hmac`/`hashlib` from the stdlib for hashing,
and `cryptography` for RSA (install with `pip install cryptography`).

IMPORTANT: The canonical field orders below are transcribed from the official
docs bundled in ../references/. ABA occasionally lists a different order in the
parameter table than in the hash concatenation -- the orders here follow the
*hash concatenation* text, which is what the server verifies. Always confirm
against the specific reference file for the endpoint you are calling, because
ABA adds fields over time.
"""

import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Time helper
# ---------------------------------------------------------------------------

def req_time() -> str:
    """Return the current UTC time as 'YYYYMMDDHHmmss' (the format PayWay wants)."""
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def _b64_hmac_sha512(b4hash: str, api_key: str) -> str:
    """base64( HMAC-SHA512(b4hash, api_key) ) -- the ABA default for almost all APIs."""
    digest = hmac.new(api_key.encode("utf-8"), b4hash.encode("utf-8"), hashlib.sha512).digest()
    return base64.b64encode(digest).decode("utf-8")


def _hex_hmac_sha512(b4hash: str, api_key: str) -> str:
    """hex( HMAC-SHA512(b4hash, api_key) ) -- only the Payout doc shows this variant."""
    return hmac.new(api_key.encode("utf-8"), b4hash.encode("utf-8"), hashlib.sha512).hexdigest()


def make_hash(params: dict, order: list, api_key: str, *, hex_output: bool = False) -> str:
    """
    Build the ABA hash by concatenating `params[field]` for each field in `order`,
    then HMAC-SHA512 with `api_key`.

    Every field in `order` is included in its slot. Missing/None values become the
    empty string -- this is intentional and required. Numbers are stringified as-is,
    so pass amounts as strings if you need to control formatting (e.g. "1.00").

    Set hex_output=True only for the Payout API, whose doc shows a hex digest.
    """
    b4hash = "".join(_stringify(params.get(f)) for f in order)
    return _hex_hmac_sha512(b4hash, api_key) if hex_output else _b64_hmac_sha512(b4hash, api_key)


def _stringify(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "1" if v else "0"
    return str(v)


# Canonical hash concatenation orders, keyed by a short API name.
# Transcribed from ../references/. `rsa` marks fields that must be RSA-encrypted first.
HASH_ORDERS = {
    # Checkout
    "purchase": [
        "req_time", "merchant_id", "tran_id", "amount", "items", "shipping",
        "firstname", "lastname", "email", "phone", "type", "payment_option",
        "return_url", "cancel_url", "continue_success_url", "return_deeplink",
        "currency", "custom_fields", "return_params", "payout", "lifetime",
        "additional_params", "google_pay_token", "skip_success_page",
    ],  # view_type and payment_gate are NOT hashed
    "purchase_token": [
        "req_time", "merchant_id", "tran_id", "amount", "items", "shipping",
        "ctid", "pwt", "firstname", "lastname", "email", "phone", "type",
        "return_url", "currency", "custom_fields", "return_params", "payout",
    ],
    "check_transaction": ["req_time", "merchant_id", "tran_id"],
    "transaction_detail": ["req_time", "merchant_id", "tran_id"],
    "transaction_list": [
        "req_time", "merchant_id", "from_date", "to_date",
        "from_amount", "to_amount", "status", "page", "pagination",
    ],
    "close_transaction": ["req_time", "merchant_id", "tran_id"],
    "exchange_rate": ["req_time", "merchant_id"],
    "transactions_by_ref": ["req_time", "merchant_id", "merchant_ref"],
    # QR
    "generate_qr": [
        "req_time", "merchant_id", "tran_id", "amount", "items", "first_name",
        "last_name", "email", "phone", "purchase_type", "payment_option",
        "callback_url", "return_deeplink", "currency", "custom_fields",
        "return_params", "payout", "lifetime", "qr_image_template",
    ],
    # Credentials on File
    "link_account": ["merchant_id", "req_time", "return_deeplink"],
    "link_card": ["merchant_id", "ctid", "return_param"],
    "remove_account_token": ["merchant_id", "req_time", "ctid", "pwt"],
    "remove_card_token": ["merchant_id", "ctid", "pwt"],
    "linked_account_details": ["merchant_id", "req_time", "return_param"],
    # RSA-based (hash uses the already-encrypted merchant_auth / beneficiaries string)
    "refund": ["request_time", "merchant_id", "merchant_auth"],
    "payment_link_create": ["request_time", "merchant_id", "merchant_auth"],
    "payment_link_detail": ["request_time", "merchant_id", "merchant_auth"],
    "pre_auth_complete": ["merchant_auth", "request_time", "merchant_id"],
    "pre_auth_complete_payout": ["merchant_auth", "request_time", "merchant_id"],
    "pre_auth_cancel": ["merchant_id", "merchant_auth", "request_time"],
    "add_beneficiary": ["request_time", "merchant_auth"],
    "update_beneficiary_status": ["request_time", "merchant_auth"],
    "payout": ["merchant_id", "tran_id", "beneficiaries", "amount", "custom_fields", "currency"],
}


def hash_for(api: str, params: dict, api_key: str) -> str:
    """
    Convenience wrapper: look up the canonical order for a known API name and hash.
    Payout uses hex output per its doc; everything else uses base64.
    """
    if api not in HASH_ORDERS:
        raise KeyError(f"Unknown api '{api}'. Known: {sorted(HASH_ORDERS)}")
    return make_hash(params, HASH_ORDERS[api], api_key, hex_output=(api == "payout"))


# ---------------------------------------------------------------------------
# Base64 field encoding (items, custom_fields, return_deeplink, payout, urls)
# ---------------------------------------------------------------------------

def b64_json(value) -> str:
    """Base64-encode a JSON-serializable value (used for items, custom_fields, payout, etc.)."""
    return base64.b64encode(json.dumps(value, separators=(",", ":")).encode("utf-8")).decode("utf-8")


def b64_str(value: str) -> str:
    """Base64-encode a raw string (used for return_url / callback_url)."""
    return base64.b64encode(value.encode("utf-8")).decode("utf-8")


# ---------------------------------------------------------------------------
# RSA chunked encryption (merchant_auth / beneficiaries)
# ---------------------------------------------------------------------------

def rsa_encrypt(data, rsa_public_key_pem: str, chunk_size: int = 117) -> str:
    """
    Encrypt `data` (dict/list -> JSON, or a raw string) with the merchant's RSA public
    key, in `chunk_size`-byte chunks with PKCS#1 v1.5 padding, then base64 the
    concatenated ciphertext. Mirrors ABA's PHP openssl_public_encrypt() sample.

    chunk_size=117 assumes a 1024-bit key (as ABA's docs state). If ABA issues you a
    2048-bit key, use chunk_size=245.
    """
    try:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
    except ImportError as e:
        raise ImportError("RSA encryption needs the 'cryptography' package: pip install cryptography") from e

    if not isinstance(data, (str, bytes)):
        data = json.dumps(data, separators=(",", ":"))
    if isinstance(data, str):
        data = data.encode("utf-8")

    key = load_pem_public_key(rsa_public_key_pem.encode("utf-8"))
    out = b""
    for i in range(0, len(data), chunk_size):
        out += key.encrypt(data[i:i + chunk_size], padding.PKCS1v15())
    return base64.b64encode(out).decode("utf-8")


# ---------------------------------------------------------------------------
# Endpoints & base URLs
# ---------------------------------------------------------------------------

BASE_URLS = {
    "sandbox": "https://checkout-sandbox.payway.com.kh",
    "production": "https://checkout.payway.com.kh",
}

ENDPOINTS = {
    "purchase": "/api/payment-gateway/v1/payments/purchase",
    "purchase_token": "/api/payment-gateway/v1/payments/purchase",
    "check_transaction": "/api/payment-gateway/v1/payments/check-transaction-2",
    "transaction_detail": "/api/payment-gateway/v1/payments/transaction-detail",
    "transaction_list": "/api/payment-gateway/v1/payments/transaction-list-2",
    "close_transaction": "/api/payment-gateway/v1/payments/close-transaction",
    "refund": "/api/merchant-portal/merchant-access/online-transaction/refund",
    "exchange_rate": "/api/payment-gateway/v1/exchange-rate",
    "link_account": "/api/aof/request-qr",
    "link_card": "/api/payment-gateway/v1/cof/initial",
    "remove_account_token": "/api/aof/remove-account",
    "remove_card_token": "/api/payment-gateway/v1/cof/remove",
    "linked_account_details": "/api/aof/pushback-status",
    "generate_qr": "/api/payment-gateway/v1/payments/generate-qr",
    "payment_link_create": "/api/merchant-portal/merchant-access/payment-link/create",
    "payment_link_detail": "/api/merchant-portal/merchant-access/payment-link/detail",
    "pre_auth_complete": "/api/merchant-portal/merchant-access/online-transaction/pre-auth-completion",
    "pre_auth_complete_payout": "/api/merchant-portal/merchant-access/online-transaction/pre-auth-completion",
    "pre_auth_cancel": "/api/merchant-portal/merchant-access/online-transaction/pre-auth-cancellation",
    "payout": "/api/payment-gateway/v2/direct-payment/merchant/payout",
    "add_beneficiary": "/api/merchant-portal/merchant-access/whitelist-account/add-whitelist-payout",
    "update_beneficiary_status": "/api/merchant-portal/merchant-access/whitelist-account/update-whitelist-status",
    "transactions_by_ref": "/api/payment-gateway/v1/payments/get-transactions-by-mc-ref",
}


def endpoint_url(api: str, env: str = "sandbox") -> str:
    return BASE_URLS[env] + ENDPOINTS[api]


# ---------------------------------------------------------------------------
# Example builders (demonstrate correct assembly for the two most common calls)
# ---------------------------------------------------------------------------

def build_purchase(*, merchant_id, api_key, tran_id, amount, currency="USD",
                   firstname="", lastname="", email="", phone="", payment_option="",
                   items=None, shipping="", return_url_plain="", **extra) -> dict:
    """
    Assemble a Purchase request body (fields for multipart/form-data POST).
    `amount` should be a string you control (e.g. "1.00"); KHR must have no decimals.
    `items` is a list of {name, quantity, price} dicts (encoded here).
    `return_url_plain` is your raw callback URL (base64-encoded here).
    Extra optional fields (type, cancel_url, lifetime, ...) can be passed as kwargs.
    """
    params = {
        "req_time": req_time(),
        "merchant_id": merchant_id,
        "tran_id": tran_id,
        "amount": amount,
        "items": b64_json(items) if items else "",
        "shipping": shipping,
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "phone": phone,
        "type": extra.get("type", ""),
        "payment_option": payment_option,
        "return_url": b64_str(return_url_plain) if return_url_plain else "",
        "cancel_url": extra.get("cancel_url", ""),
        "continue_success_url": extra.get("continue_success_url", ""),
        "return_deeplink": extra.get("return_deeplink", ""),
        "currency": currency,
        "custom_fields": extra.get("custom_fields", ""),
        "return_params": extra.get("return_params", ""),
        "payout": extra.get("payout", ""),
        "lifetime": extra.get("lifetime", ""),
        "additional_params": extra.get("additional_params", ""),
        "google_pay_token": extra.get("google_pay_token", ""),
        "skip_success_page": extra.get("skip_success_page", ""),
    }
    params["hash"] = hash_for("purchase", params, api_key)
    # view_type / payment_gate are sent but not hashed:
    for k in ("view_type", "payment_gate"):
        if k in extra:
            params[k] = extra[k]
    return params


def build_check_transaction(*, merchant_id, api_key, tran_id) -> dict:
    params = {"req_time": req_time(), "merchant_id": merchant_id, "tran_id": tran_id}
    params["hash"] = hash_for("check_transaction", params, api_key)
    return params


if __name__ == "__main__":
    # Self-test with the worked example from references/25-ecommerce-checkout-guide.md.
    # That sample used req_time=20250728022056, tran_id=17536691884, amount=0.10,
    # merchant_id=ec000002, firstname=sina, lastname=chhum, phone=093939399, everything
    # else empty. We can't reproduce the exact published hash (the API key is secret),
    # but we can confirm hashing is deterministic and stable.
    demo_key = "demo_secret_key"
    p = {
        "req_time": "20250728022056", "merchant_id": "ec000002", "tran_id": "17536691884",
        "amount": "0.10", "items": "", "shipping": "", "firstname": "sina", "lastname": "chhum",
        "email": "", "phone": "093939399", "type": "", "payment_option": "", "return_url": "",
        "cancel_url": "", "continue_success_url": "", "return_deeplink": "", "currency": "",
        "custom_fields": "", "return_params": "", "payout": "", "lifetime": "",
        "additional_params": "", "google_pay_token": "", "skip_success_page": "",
    }
    h1 = hash_for("purchase", p, demo_key)
    h2 = hash_for("purchase", p, demo_key)
    assert h1 == h2, "hash not deterministic"
    print("purchase hash (demo key):", h1)
    print("check_transaction hash:", hash_for("check_transaction",
          {"req_time": "20250213065545", "merchant_id": "ec000002", "tran_id": "17394277693"}, demo_key))
    print("req_time() now:", req_time())
    print("b64_json items:", b64_json([{"name": "product 1", "quantity": 1, "price": 1.00}]))
    print("OK")
