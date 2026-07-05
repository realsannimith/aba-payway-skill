# QR API

Supported payment options:
- Transaction currency KHR: ABA PAY, KHQR
- Transaction currency USD: ABA PAY, KHQR, WeChat and Alipay

## Endpoint

```
POST /api/payment-gateway/v1/payments/generate-qr
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## Request Parameters

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `req_time` | string | — | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | 30 | Yes | A unique merchant key which provided by ABA Bank |
| `tran_id` | string | 20 | Yes | This is the unique transaction ID that identifies the transaction |
| `amount` | string | — | Yes | The total transaction amount as a formatted decimal string (e.g. `"1.00"` for USD, `"4000"` for KHR). Must match the value used in hash computation. Minimum: **100 KHR** or **0.01 USD** |
| `currency` | string | 3 | Yes | Supported transaction currencies: `KHR` and `USD`. Not case-sensitive |
| `payment_option` | string | 20 | Yes | Supported payment options: `abapay_khqr` (Payway will response ABA KHQR), `wechat` (PayWay will respond with a WeChat QR, only for USD transactions), `alipay` (PayWay will respond with an Alipay QR, only for USD transactions) |
| `lifetime` | integer | — | Yes | Transaction lifetime in minutes. Default: 30 days. Minimum: 3 mins. Maximum: 30 days |
| `qr_image_template` | string | 20 | Yes | The QR image comes with various options to suit your needs |
| `hash` | string | — | Yes | Base64 encode of hash hmac sha512 encryption of concatenated values `req_time`, `merchant_id`, `tran_id`, `amount`, `items`, `first_name`, `last_name`, `email`, `phone`, `purchase_type`, `payment_option`, `callback_url`, `return_deeplink`, `currency`, `custom_fields`, `return_params`, `payout`, `lifetime`, and `qr_image_template` |
| `first_name` | string | 20 | No | Payer's first name |
| `last_name` | string | 20 | No | Payer's last name |
| `email` | string | 50 | No | Payer's email address |
| `phone` | string | 20 | No | Payer's phone number |
| `purchase_type` | string | 20 | No | Supported values: `pre-auth` and `purchase`. If the merchant does not provide a value, the default will be `purchase`. Note: Alipay & WeChat do not support pre-auth |
| `items` | string | 500 | No | Item list description in Base64-encoded JSON format. Maximum of 10 items |
| `callback_url` | string | 255 | No | URL to receive callbacks upon payment completion, encrypted with Base64 |
| `return_deeplink` | string | 255 | No | Base64-encoded JSON with `android_scheme` and `ios_scheme` keys |
| `custom_fields` | string | 255 | No | Additional custom fields to attach to the QR, encrypted with Base64 |
| `return_params` | string | — | No | Additional information to include in the pushback once the payment is completed |
| `payout` | string | 255 | No | Payout instructions in a Base64-encoded JSON string |

## Hash Generation

> **Note:** The hash field order differs from the parameter table order above. The explicit concatenation order is:
>
> `req_time, merchant_id, tran_id, amount, items, first_name, last_name, email, phone, purchase_type, payment_option, callback_url, return_deeplink, currency, custom_fields, return_params, payout, lifetime, qr_image_template`

**PHP Sample Code**

```php
$api_key = 'API KEY PROVIDED BY ABA BANK';

$b4hash = $req_time . $merchant_id . $tran_id . $amount .
$items . $first_name . $last_name . $email . $phone . $purchase_type .
$payment_option . $callback_url . $return_deeplink . $currency .
$custom_fields . $return_params . $payout . $lifetime .
$qr_image_template;

$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

## Field Encoding Examples

### Items (Base64-encoded JSON)

```php
$items = base64_encode('[
    {"name":"Item 1","quantity":1,"price":1.00},
    {"name":"Item 2","quantity":1,"price":4.00}
]');
```

### Callback URL (Base64-encoded)

```php
$callback_url = base64_encode('YOUR CALL BACK URL');
```

### Return Deeplink (Base64-encoded JSON)

```php
$return_deeplink = base64_encode('{"android_scheme": "{YOUR ANDROID SCHEME}", "ios_scheme":"{YOUR IOS SCHEME}"}');
```

### Custom Fields (Base64-encoded JSON)

```php
$custom_fields = base64_encode('{"Province":"ABC", "Province": "Male" }');
```

### Return Params (JSON)

```php
$return_params = '{"key_1": "Value 1","key_2": "Value 2"}';
```

### Payout (Base64-encoded JSON)

```php
$payout = base64_encode('[
    {"account":"201030101","amount":1.72},
    {"account":"012538302","amount":1.72}
]');
```

## Request Example

```json
{
  "req_time": "20250312095439",
  "merchant_id": "keng.dara.online",
  "tran_id": "20250311033231",
  "first_name": "ABA",
  "last_name": "Bank",
  "email": "aba.bank@gmail.com",
  "phone": "012345678",
  "amount": "0.01",
  "purchase_type": "purchase",
  "payment_option": "abapay_khqr",
  "items": "W3sibmFtZSI6IicgVU5JT04gU0VMRUNUIG51bGwsIHZlcnNpb24oKSwgbnVsbCAtLSIsInF1YW50aXR5IjozLCJwcmljZSI6MTAwLjAxfV0=",
  "currency": "USD",
  "callback_url": "aHR0cHM6Ly9hcGkuY2FsbGJhY2suY29tL25vdGlmeQ==",
  "return_deeplink": null,
  "custom_fields": null,
  "return_params": null,
  "payout": null,
  "lifetime": 6,
  "qr_image_template": "template3_color",
  "hash": "ZyDmMe/kznbY2e...ZB6tMnqv57V06T13du8807dcbPTg=="
}
```

## Response

**HTTP 200**

| Field | Type | Description |
|-------|------|-------------|
| `status.code` | string | Response code |
| `status.message` | string | Descriptive message |
| `status.trace_id` | string | A unique identifier assigned to a request to help track its journey through a system |
| `amount` | number | Transaction amount |
| `currency` | string | Transaction currency |
| `qrString` | string | QR content as string |
| `qrImage` | string | QR as base64 image |
| `abapay_deeplink` | string | ABA Mobile Deeplink. You can use this deeplink to automatically open ABA Mobile so that customer can confirm payment |
| `app_store` | string | If you try to open `abapay_deeplink` and the payer does not have ABA Mobile installed, you can redirect the user to the app store to download ABA Mobile |
| `play_store` | string | If you try to open `abapay_deeplink` and the payer does not have ABA Mobile installed, you can redirect the user to the play store to download ABA Mobile |

### Success Response

```json
{
  "status": {
    "code": "0",
    "message": "Success",
    "trace_id": "abc-123-def"
  },
  "amount": 1.00,
  "currency": "USD",
  "qrString": "00020101021229...",
  "qrImage": "data:image/png;base64,...",
  "abapay_deeplink": "abamobilebank://ababank.com?type=payway&qrcode=...",
  "app_store": "https://apps.apple.com/kh/app/aba-mobile/id...",
  "play_store": "https://play.google.com/store/apps/details?id=..."
}
```

## Status Codes

| Code | Description |
|------|-------------|
| `0` | Success. |
| `1` | Wrong Hash. |
| `6` | Requested Domain is not in whitelist. |
| `8` | Something went wrong. Please reach out to our digital support team for assistance |
| `12` | Payment currency is not allowed. |
| `16` | Invalid First Name. It must not contain numbers or special characters or not more than 100 characters. |
| `17` | Invalid Last Name. It must not contain numbers or special characters or not more than 100 characters. |
| `18` | Invalid Phone Number. |
| `19` | Invalid Email. |
| `21` | End of API lifetime. |
| `23` | Selected Payment Option is not enabled for this Merchant Profile. |
| `32` | Service is not enable. |
| `35` | Payout Info is invalid. |
| `44` | Purchase amount has reached transaction limit. |
| `47` | KHR Amount must be greater than 100 KHR. |
| `48` | Something went wrong with requested parameters. Please try again or contact the merchant for help. |
| `96` | Invalid merchant data |
| `102` | The URL is not in the whitelist. |
| `403` | Duplicated Transaction ID |
| `429` | You've reached the maximum attempt limit. Please try again in (min) |
