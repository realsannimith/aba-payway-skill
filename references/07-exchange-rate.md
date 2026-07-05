# Exchange Rate API

With the Exchange rate API you can fetch the latest exchange rate from ABA bank, the exchange rates are exactly like the prices you will find on https://www.ababank.com/en/forex-exchange

## Endpoint

```
POST /api/payment-gateway/v1/exchange-rate
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `req_time` | string | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | Yes | A unique merchant key which provided by ABA Bank |
| `hash` | string | Yes | Base64 encode of hash hmac sha512 encryption of concatenates values `req_time`, and `merchant_id` with `public_key` |

## Hash Generation

```php
// public key provided by ABA Bank
$api_key = "API KEY PROVIDED BY ABA BANK";

// Prepare the data to be hashed
$b4hash = $req_time . $merchant_id;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

### Request Example

```json
{
  "req_time": "20250212104216",
  "merchant_id": "ec000002",
  "hash": "2P+5NrSb5g2XyITaxttsnjW...JVKguqghoQrq4y4C3tbUiA=="
}
```

## Response

**HTTP 200**

### Exchange Rates Object

Each currency object contains `sell` and `buy` rates as strings.

### Supported Currencies

| Code | Currency |
|------|----------|
| `aud` | Australian Dollar |
| `sgd` | Singapore Dollar |
| `eur` | Euro |
| `gbp` | Pound Sterling |
| `myr` | Malaysian Ringgit |
| `thb` | Thai Baht |
| `hkd` | Hong Kong Dollar |
| `cny` | Chinese Yuan |
| `cad` | Canadian Dollar |
| `krw` | South Korean Won |
| `jpy` | Japanese Yen |
| `vnd` | Vietnamese Dong |

Success response:

```json
{
    "status": {
        "code": "00",
        "message": "Success!"
    },
    "exchange_rates": {
        "aud": { "sell": "2719.38", "buy": "2540.49" },
        "sgd": { "sell": "3113.18", "buy": "2914.72" },
        "eur": { "sell": "4461.07", "buy": "4258.34" },
        "gbp": { "sell": "5333.51", "buy": "5064.89" },
        "myr": { "sell": "943.65", "buy": "839.94" },
        "thb": { "sell": "122.14", "buy": "118.18" },
        "hkd": { "sell": "531.57", "buy": "473.15" },
        "cny": { "sell": "577.35", "buy": "521.23" },
        "cad": { "sell": "2956.91", "buy": "2666.82" },
        "krw": { "sell": "3.0151", "buy": "2.6634" },
        "jpy": { "sell": "27.1139", "buy": "25.0701" },
        "vnd": { "sell": "0.1631", "buy": "0.1509" }
    }
}
```

Exception response:

```json
{
    "status": {
        "code": "26",
        "message": "Invalid merchant profile",
        "tran_id": "1729573626"
    }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| `00` | Success! |
| `1` | Wrong hash |
| `26` | Invalid merchant profile |
