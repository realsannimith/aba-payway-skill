# Link Account API

The API returns a QR code or an ABA Mobile deeplink, enabling users to either scan the QR code or use the deeplink to automatically launches the ABA Mobile app and prompts the customer to select an ABA account to link to your platform. Once the user finished linking, PayWay will send pushback account details and token to the merchant through the `return_url`.

## Endpoint

```
POST /api/aof/request-qr
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## Prerequisites

Before using this API, please make sure your profile has enabled Account on File feature. If your merchant profile has not enabled this feature yet, please contact our merchant digital support (`digitalsupport@ababank.com`) for sandbox profile, and for a production merchant profile, please contact our merchant acquisition team (`paywaysales@ababank.com`).

## Request Parameters

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `req_time` | string | — | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | 20 | Yes | A unique merchant key which provided by ABA Bank |
| `return_param` | string | — | Yes | Extra information that you want to include when payment gateway call your `return_url` |
| `return_url` | string | — | No | Once the user has linked their account, the details of the token and other important information will be sent via this URL. This is an optional field. If left empty, it will default to the merchant profile's `pushback_url`. If you provide a value, ensure that your domain is whitelisted in your merchant profile |
| `return_deeplink` | string | — | No | After the user links their account on ABA Mobile, they will see a success screen with a **Done** button. Your return deep link will be embedded in this button. When the user taps **Done**, they will be redirected to your app |
| `hash` | string | — | Yes | Base64-encoded HMAC-SHA512 hash of the concatenated values: `merchant_id`, `req_time`, and `return_deeplink`, using the `public_key` |

### `return_url` Encoding

```php
$return_url = base64_encode("YOUR RETURN URL VALUE");
```

### `return_deeplink` Format

```php
$deeplink_format = array(
    "ios_scheme" => "{YOUR IOS DEEPLINK URL}",
    "android_scheme" => "{YOUR ANDROID DEEPLINK URL}",
);

$return_deeplink = base64_encode(json_encode($deeplink_format));
```

## Hash Generation

```php
// public key provided by ABA Bank
$api_key = "API KEY PROVIDED BY ABA BANK";

// Prepare the data to be hashed
$b4hash = $merchant_id . $req_time . $return_deeplink;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

### Request Example

```json
{
  "req_time": "20210723080525",
  "merchant_id": "ec000002",
  "return_param": "REQ0012",
  "return_url": "RBqpuvSB7BA...CX+X1Sxtg4U+==",
  "hash": "waNDRBqpuvSBACX...3+cOwJQn/eHYw=="
}
```

## Response

**HTTP 200**

| Field | Type | Description |
|-------|------|-------------|
| `deeplink` | string | If your integration is on a mobile app, either Android or iOS, you can open this deep link to redirect the user to ABA Mobile and complete the account linking process |
| `qr_string` | string | If your integration is on a web browser, you can render this QR code so that users can scan and complete the linking process |
| `qr_image` | string | Full URL of the QR image |
| `expire_in` | number | Date and time (timestamp) of the token expiry |
| `status.code` | string | Response code |
| `status.message` | string | Please see more details in the `code` property above |

Success response:

```json
{
    "status": {
        "code": "00",
        "message": "QR generated successfully"
    },
    "deeplink": "abamobilebank://ababank.com?type=account_on_file&qrcode=ABAAOFTmtAvigDc7VNoqZEW72QLdD4ZeA0rl8QcM3Shtj5w1I%3D",
    "qr_string": "ABAAOFTmtAvigDc7VNoqZEW72QLdD4ZeA0rl8QcM3Shtj5w1I=",
    "qr_image": "https://checkout-sandbox.payway.com.kh/merchants/abaqr/abaqr-63eb236a67e29...1772508119NMgtbughIp.png",
    "expire_in": 1772594519
}
```

Exception response:

```json
{
    "status": {
        "code": 4,
        "message": "Request Parameter Required"
    },
    "description": {
        "hash": [
            "Invalid hash"
        ]
    }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| `00` | Success |
| `04` | Request parameter required |
| `11` | Server-side error |
