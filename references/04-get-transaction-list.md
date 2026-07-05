# Get Transaction List API

This API allows merchants to retrieve a list of transactions filtered by specific criteria, such as transaction date, amount, payment type, and more. It supports pagination and is designed for both in-store and online profiles, providing secure and efficient access to recent transaction records.

## Endpoint

```
POST /api/payment-gateway/v1/payments/transaction-list-2
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## Constraints

- Both instore and online profile
- Allow only by outlet, cannot get all transaction from all outlet which is under one business profile
- Can filter from any date range in the past to current day with maximum 3 days (included today)
- All parameters used in the hash string must follow the exact sequence defined in the API documentation
- Maximum request per minute: 50 requests

## Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `req_time` | string | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | Yes | A unique merchant key which provided by ABA Bank |
| `from_date` | string | No | Start date for filtering transactions, in the format `YYYY-MM-DD HH:mm:ss`. Default value is today at `00:00:00` |
| `to_date` | string | No | End date for filtering transactions, in the format `YYYY-MM-DD HH:mm:ss`. Default value is today at `23:59:59` |
| `from_amount` | string | No | Search transaction that has purchased amount from |
| `to_amount` | string | No | Search transaction that has purchased amount to |
| `status` | string | No | Possible values: `APPROVED`, `PRE-AUTH`, `REFUNDED`, `PENDING`, `DECLINED`, `CANCELLED`. No case sensitive, if you want to query multiple values please separate value by comma |
| `page` | string | No | Current page index. Default value: `1` |
| `pagination` | string | No | Total number of records per page. Default value `40`, maximum value is `1000` |
| `hash` | string | Yes | Base64 encode of hash hmac sha512 encryption of concatenates values `req_time`, `merchant_id`, `from_date`, `to_date`, `from_amount`, `to_amount`, `status`, `page`, and `pagination` with `public_key` |

## Hash Generation

**PHP Sample Code**

```php
// public key provided by ABA Bank
$api_key = "API KEY PROVIDED BY ABA BANK";

// Prepare the data to be hashed
$b4hash = $req_time . $merchant_id . $from_date . $to_date . $from_amount . $to_amount . $status . $page . $pagination;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

### Request Example

```json
{
  "req_time": "20250213081756",
  "merchant_id": "ec000002",
  "from_date": null,
  "to_date": null,
  "from_amount": "0.01",
  "to_amount": "1000",
  "status": null,
  "page": "1",
  "pagination": "40",
  "hash": "o1mDvIjTyzoFcN7zvm7...aUYAGXjsx4Ej0E6P2CoxtOQ=="
}
```

## Response

**HTTP 200**

Success response:

```json
{
    "data": [
        {
            "transaction_id": "9495966779",
            "transaction_date": "2025-10-08 09:55:15",
            "original_currency": "USD",
            "bank_ref": "",
            "apv": "",
            "discount_amount": 0,
            "payment_status": "PENDING",
            "payment_amount": 0,
            "last_name": "",
            "payment_currency": "",
            "payment_type": "N/A",
            "payer_account": "",
            "total_amount": 0.01,
            "phone": "010417430",
            "original_amount": 0.01,
            "payment_status_code": 2,
            "bank_name": "",
            "refund_amount": 0,
            "first_name": "",
            "email": "john@example.com",
            "card_source": ""
        }
    ],
    "pagination": "10",
    "page": "1",
    "status": {
        "code": "00",
        "tran_id": "163172901816084",
        "message": "Success!"
    }
}
```

Exception response:

```json
{
    "status": {
        "code": "8",
        "message": "Invalid Merchant Profile",
        "tran_id": "1729573626"
    }
}
```

### `data` Array — Transaction Object

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | string | Transaction id |
| `transaction_date` | string | Created date & time of the transaction |
| `apv` | string | Transaction approval code |
| `payment_status` | string | `APPROVED` – Transaction successfully completed with the full purchase amount, `PRE-AUTH` – Transaction successfully processed with a pre-authorization hold on funds pending final capture, `REFUNDED` – Transaction has been fully or partially refunded, `PENDING` – Transaction is awaiting payment completion by the payer, `DECLINED` – Transaction has been declined, `CANCELLED` – Merchant canceled the pre-authorization or closed the transaction |
| `payment_status_code` | integer | `0` = APPROVED/PRE-AUTH, `2` = PENDING, `3` = DECLINED, `4` = REFUNDED, `7` = CANCELLED |
| `original_amount` | number | Original amount of the transaction (before discount) |
| `original_currency` | string | Original transaction currency. `KHR` for Khmer Riel transaction, `USD` for US Dollar transaction |
| `total_amount` | number | Amount to pay after discount. Its currency follow original currency |
| `discount_amount` | number | Discounted amount. Its currency follow original currency |
| `refund_amount` | number | Total refunded amount |
| `payment_amount` | number | The amount that the customer has paid. Example: Customer supposed to pay 1$, but customer paid from his KHR account then this payment amount will be 4,000.00 |
| `payment_currency` | string | Payment currency. Empty string `""` when the transaction is `PENDING` (no payment made yet). Once paid, reflects the actual currency used — e.g. if the customer was billed in USD but paid from a KHR account, this will be `KHR` |
| `first_name` | string | Payer first name. This value only exist in the API response if configure on profile |
| `last_name` | string | Payer last name. This value only exist in the API response if configure on profile |
| `email` | string | Payer email. This value only exist in the API response if configure on profile |
| `phone` | string | Payer phone. This value only exist in the API response if configure on profile |
| `bank_ref` | string | Unique booking entry id from ABA core banking. This value only exist in the API response if configure on profile |
| `payer_account` | string | Masked ABA Account Number or Masked Card PAN. For other payment options, it will be blank |
| `bank_name` | string | If payment is made with ABA Pay, it will show ABA Bank or if payment made using KHQR it will show issuer bank name |
| `card_source` | string | Only for payment with card: `ONUS` – Transaction made with ABA Card, `OFFUS_DOMESTIC` – Transaction made with local card issue by other banks, `OFFUS_INTERNATIONAL` – Transaction made with international card |
| `payment_type` | string | Payment method that the customer use to make payment. This value only exist in the API response if configure on profile. Possible values: `N/A` (those pending for payment), `ABA Pay` (Transaction made with ABA Account/ABA Mobile), `Alipay` (Transaction made with Alipay), `Wechat` (Transaction made with WeChat Pay), `KHQR` (Transaction made with KHQR), `VISA` (Transaction made with Visa card), `MC` (Transaction made with Mastercard), `JCB` (Transaction made with JCB card), `CUP` (Transaction made with UPI card) |

### Pagination Fields

| Field | Type | Description |
|-------|------|-------------|
| `page` | string | Current page index |
| `pagination` | string | Total number of records per page. Default: `40` and maximum of `1000` |

### `status` Object

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Response code. See status codes below |
| `message` | string | Please see the property response `code` for the details |
| `tran_id` | string | Request reference generated by payment gateway |

## Status Codes

| Code | Description |
|------|-------------|
| `00` | Success! |
| `1` | Wrong hash |
| `8` | Invalid merchant profile |
| `11` | Internal server error |
| `429` | Rate limit exceeded |
