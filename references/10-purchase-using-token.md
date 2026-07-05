# Purchase Using Token API

This API supports both card tokens and account tokens.

## Endpoint

```
POST /api/payment-gateway/v1/payments/purchase
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## Request Parameters

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `req_time` | string | — | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | 20 | Yes | A unique merchant key provided by ABA Bank |
| `tran_id` | string | 20 | Yes | A unique transaction ID for the payment |
| `amount` | number | — | Yes | Total purchase amount (exclude shipping fee) |
| `hash` | string | — | Yes | Base64-encoded HMAC-SHA512 hash of concatenated values `req_time`, `merchant_id`, `tran_id`, `amount`, `items`, `shipping`, `ctid`, `pwt`, `firstname`, `lastname`, `email`, `phone`, `type`, `return_url`, `currency`, `custom_fields`, `return_params`, and `payout`, using `public_key` |
| `ctid` | string | 255 | Yes* | Your consumer token |
| `pwt` | string | 255 | Yes* | PayWay-issued token |
| `firstname` | string | 100 | No | Buyer's first name |
| `lastname` | string | 100 | No | Buyer's last name |
| `email` | string | 50 | No | Buyer's email |
| `phone` | string | 20 | No | Buyer's phone |
| `type` | string | 20 | No | The type of transaction. The default value is `purchase`. Supported values: `pre-auth` (pre-authorization), `purchase` (full purchase transaction) |
| `items` | string | 500 | No | A base64-encoded JSON array listing the items included in the transaction |
| `shipping` | number | — | No | Shipping fee |
| `return_url` | string | — | No | URL to receive callbacks upon payment completion, encrypted with Base64 |
| `custom_fields` | string | — | No | Additional information you want to attach to the transaction. This information appears in transaction details, lists, and export reports. Must be base64-encoded JSON |
| `return_params` | string | — | No | Information to include when PayWay calls your return URL after payment completed |
| `payout` | string | — | No | Base64-encoded JSON string representing payout details |

> *Both `ctid` and `pwt` are nullable but must be provided for token-based purchases.

### Items Encoding (PHP)

```php
$item = base64_encode(json_encode([
    ["name" => "product 1","quantity" => 1,"price" => 1.00],
    ["name" => "product 2","quantity" => 2, "price" => 4.00]
]));
```

> This is for description purposes only. The price or quantity in this information will not be used for calculations or validation.

### Payout Encoding (PHP)

```php
$payout = base64_encode(json_encode([
    ["acc" => "000133879","amt"=> 1],
    ["acc" => "000133880","amt" => 1]
]));
```

## Hash Generation

```php
// public key provided by ABA Bank
$api_key = "API KEY PROVIDED BY ABA BANK";

// Prepare the data to be hashed
$b4hash = $req_time . $merchant_id . $tran_id . $amount .
$items . $shipping . $ctid . $pwt . $firstname . $lastname .
$email . $phone . $type  . $return_url . $currency .
$custom_fields . $return_params . $payout;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

### Request Example

```json
{
  "req_time": "20250312075529",
  "merchant_id": "xxxxx",
  "type": "pre-auth",
  "items": "Nlx1MTc5NFx1MTdiY...MDAwLjAwIn1d",
  "amount": 60000,
  "tran_id": "17417661239",
  "continue_success_url": "demo-payway-uat.ababank.com",
  "return_url": "aHR0cHM6Ly9kZW1vLXBheXdhe..NzY2MTIzOQ==",
  "return_param": "OTg0OQ==",
  "hash": "QRzyIlknvaVA..jXvkA==",
  "custom_fields": "eyJteV9jdXN0bMSI6I..lfY3VzdG9tX2ZpZWDE3NjYxMjl9",
  "firstname": "QA",
  "lastname": "Sakada",
  "phone": "017582717",
  "email": "sakadaqa@gmail.com"
}
```

## Response

### Success Response

**HTTP 200**

```json
{
  "tran_id": "trx-20201019130949",
  "payment_status": {
    "status": "0",
    "code": "CDA00",
    "description": "OK",
    "pw_tran_id": "trx-20201019130949"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `tran_id` | string | Your unique transaction id |
| `payment_status.status` | string | `0` represent success payment |
| `payment_status.code` | string | Code `CDA00` for success payment |
| `payment_status.description` | string | Please see the property response `code` for the details |
| `payment_status.pw_tran_id` | string | Your unique transaction id |

### Exception Response

**HTTP 200**

```json
{
  "status": {
    "code": 26,
    "message": "Invalid Merchant Profile."
  }
}
```

### Error Response

**HTTP 403**

```json
{
  "status": {
    "code": "26",
    "message": "Invalid Merchant Profile."
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `1` | Wrong Hash |
| `2` | Invalid Transaction ID |
| `3` | Invalid Transaction Amount |
| `4` | Duplicated Transaction ID |
| `5` | Transaction not found |
| `6` | Requested Domain is not in whitelist |
| `7` | Wrong return param |
| `8` | Something went wrong while saving Data. Please try again later or contact merchant for help |
| `10` | Wrong shipping price |
| `11` | Something went wrong. Try again or contact the merchant for help |
| `12` | Payment currency is not allowed |
| `13` | Invalid items |
| `14` | Invalid Credit Multi Acc |
| `15` | Invalid or missing channel values from Smart merchant |
| `16` | Invalid First Name. It must not contain numbers or special characters or more than 100 characters |
| `17` | Invalid Last Name. It must not contain numbers or special characters or more than 100 characters |
| `18` | Invalid Phone Number |
| `19` | Invalid Email |
| `20` | Something went wrong. Please contact the merchant |
| `21` | End of API lifetime |
| `22` | Pre-Auth Transaction is not enabled |
| `23` | Selected Payment Option is not enabled for this Merchant Profile |
| `24` | Can not decrypt data |
| `25` | Allow maximum 10 payout per requests |
| `26` | Invalid Merchant Profile |
| `27` | Invalid ctid |
| `28` | Invalid pwt |
| `29` | Invalid pwt or ctid |
| `30` | Merchant is not enabled COF |
| `31` | Unsecure 3Ds page |
| `32` | Cannot identify cardOrigin |
| `33` | Exchange rate data is invalid |
| `34` | Payout Info is invalid |
| `35` | Payout account or amount is invalid |
| `36` | Payout accounts are not in whitelist |
| `37` | Payout contain invalid Transaction ID |
| `38` | Payout contain Duplicated Account |
| `39` | Payout contain Duplicated Transaction ID |
| `40` | Payout info contain mid not linked with any Merchant Profile |
| `41` | Payout info contain account invalid status |
| `42` | Merchant Profile's MID is missing. Please try again or contact the merchant for help |
| `43` | Purchase amount has reached transaction limit |
| `44` | Purchase with zero amount is not allowed |
| `45` | Purchase amount for KHR currency could not contain decimal place |
| `46` | KHR Amount must be greater than 100 KHR |
| `47` | Something went wrong with requested parameters. Please try again or contact the merchant for help |
| `48` | Invalid Start Date |
| `49` | Invalid End Date |
| `50` | Invalid Date Range |
| `51` | Maximum date range is allowed only 3 days |
| `52` | Invalid Amount Range |
| `53` | Transaction is expired. Please try again or contact the merchant for help |
| `54` | We are unable to request QR from Wechat system. Please try again or contact the merchant for help |
| `55` | We are unable to validate your transaction with Wechat system. Please try again or contact the merchant for help |
| `56` | We are unable to validate your card source. Please try again or contact the merchant for help |
| `57` | Provide invalid card number |
| `58` | Payout info can not be fixed with MID and ABA Account |
| `59` | Something went wrong with QR String. Please try again or contact the merchant for help |
| `60` | Something went wrong. Please try again or contact the merchant for help |
| `61` | QR is already in use |
| `62` | Transaction is already exist in core banking. Please perform new transaction or contact the merchant for help |
| `63` | Payer's account is same as Merchant Profile's account. Please choose different account |
| `64` | Merchant Profile's MID is not found in core banking. Please try again or contact the merchant for help |
| `65` | Something went wrong. Please try again or contact the merchant for help |
| `66` | QR on Invoice is currently not available for this Merchant Profile |
| `67` | Transaction is expired. Please re-initiate the transaction |
| `68` | Transaction Lifetime can not be less than 3 minutes |
| `69` | Total purchase amount has reached daily limit. Please use difference account |
| `70` | Purchase amount has reached transaction limit |
| `71` | The merchant profile cannot accept payment because its settlement account is closed |
| `72` | Invalid Transaction Status |
| `73` | Invalid tran_id or merchant_id |
| `74` | tran_id not found |
| `75` | Invalid Additional Parameters |
| `76` | Merchant transactions do not support transaction fees |
| `77` | Card payment transactions are not compatible with the discount program |
| `78` | Payment Token missing in Google Pay |
| `79` | Failed to decrypt the payment token provided by Google Pay |
| `80` | The return URL is not in the whitelist |
| `81` | The payout has exceeded the maximum allowable amount per transaction |
| `82` | Payment credential is disabled |
| `83` | Payment credential is expired |
| `84` | Purchase reach limit amount per transaction |
| `85` | Unsupported merchant purchase mode |
| `86` | Payment credential is removed |
| `200` | Payment was canceled |
| `201` | Payment was declined |
| `401` | Unauthorized access |
| `403` | Something went wrong. Try again or contact the merchant for help |
| `429` | Too many requests, please try again in 1 minute |
| `503` | System Under Maintenance |
