# Complete Pre-Auth Transaction with Payout

A complete pre-auth refers to the action where the merchant proceeds with capturing the funds after the initial authorization, typically at the time the product or service is provided.

## Endpoint

```
POST /api/merchant-portal/merchant-access/online-transaction/pre-auth-completion
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## Key Conditions

- You can only complete the pre-auth once.
- Pre-auth cannot be completed on transactions that have already expired or been canceled.
- For card payments, you can complete the pre-auth with an additional 10% above the original pre-auth amount.

## Request Parameters

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `request_time` | string | — | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss`. |
| `merchant_id` | string | 20 | Yes | A unique merchant key provided by ABA Bank. |
| `merchant_auth` | string | — | Yes | The JSON-encoded object contains the fields `mc_id`, `tran_id`, `complete_amount`, and `payout` which are encrypted using RSA public key encryption in chunks. The encrypted data is then concatenated and encoded in Base64 format. |
| `hash` | string | — | Yes | Base64-encoded HMAC-SHA512 hash of concatenated values: `merchant_auth`, `request_time`, and `merchant_id` with `public_key`. |

### `merchant_auth` Object (before encryption)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mc_id` | string | Yes | A unique merchant key which provided by ABA Bank. Same value as `merchant_id`. |
| `tran_id` | string | Yes | Pre-auth purcahse transaction id to complete. |
| `complete_amount` | decimal | Yes | Amount to complete. |
| `payout` | array | Yes | Payout distribution instructions. Each item contains `acc` (ABA account or MID) and `amt` (amount). |

### RSA Encryption (PHP Sample Code)

```php
// Prepare data to be encrypted for complete pre auth with payout
$data_object = json_encode([
    'mc_id' => $merchant_id,
    'tran_id' => $tran_id,
    'complete_amount' => $complete_amount,
    'payout' => [
        [
            'acc' => $aba_account,
            'amt' => $amount
        ], [
            'acc' => $mid,
            'amt' => $amount
        ],
        .....
    ]
]);

// RSA public key provided by the bank
$rsa_public_key = "RSA PUBLIC KEY PROVIDED BY ABA BANK";

// Maximum length for encryption chunks
$maxlength = 117;

// Initialize output for encrypted data
$encrypted_output = '';

// Encrypt data in chunks
while ($data_object !== '') {
    // Extract a substring of the allowed maximum length
    $chunk = substr($data_object, 0, $maxlength);
    $data_object = substr($data_object, $maxlength);
    // Encrypt the chunk using the public key
    if (openssl_public_encrypt($chunk, $encrypted_chunk, $rsa_public_key)) {
        $encrypted_output .= $encrypted_chunk;
    } else {
        // Handle encryption failure
        throw new Exception('Encryption failed for a data chunk.');
    }
}

// Encode the concatenated encrypted output in Base64
$merchant_auth = base64_encode($encrypted_output);
```

### Hash Generation (PHP Sample Code)

```php
// public key provided by ABA Bank
$api_key = "API KEY PROVIDED BY ABA BANK";

// Prepare the data to be hashed
$b4hash = $merchant_auth . $request_time . $merchant_id;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

## Example Request

```json
{
  "request_time": "20200728093403",
  "merchant_id": "ec000002",
  "merchant_auth": "b1453eac8cd686f90542c9d7dc026a3f70678afd",
  "hash": "wR2bVPVKY9M4WmeGoQUUcmtrJYFofFuMrgTMBLj/g8kPfXgnpK/qpjptO+1D0nKbpFktqM/iPWEyQ6/llsnJbw=="
}
```

## Response

**HTTP 200**

| Field | Type | Description |
|-------|------|-------------|
| `grand_total` | number | The original amount authorized for pre-auth transactions. |
| `currency` | string | Original transaction currency |
| `transaction_status` | string | Transaction status. Once successfully completed, the status will be `COMPLETED` |
| `status.code` | string | Response code |
| `status.message` | string | Descriptive message |

### Example Success Response

```json
{
  "grand_total": 100.00,
  "currency": "USD",
  "transaction_status": "COMPLETED",
  "status": {
    "code": "00",
    "message": "Transaction successful"
  }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| `00` | Transaction successful. |
| `PTL02` | Invalid hash value. |
| `PTL04` | Parameter validation failed. |
| `PTL06` | The request has expired. |
| `PTL36` | Invalid transaction. |
| `PTL62` | Merchant information is invalid. |
| `PTL63` | The merchant does not have a security configuration file. |
| `PTL59` | Unable to complete or cancel the pre-authorization. |
| `PTL60` | Pre-authorization completion amount exceeds the authorized limit. |
| `PTL61` | Invalid action type. |
| `PTL153` | Completing pre-authorization fees for a merchant with multiple settlement accounts is not allowed. |
| `PTL157` | An unexpected error occurred. Please try again later or contact our digital support team. |
| `PTL168` | Concurrent requests are not allowed for this operation. Please try again in a few seconds. |
| `PTL169` | The merchant profile cannot accept payments because the settlement account is closed. |
| `USD-NOT-ALLOW` | The requested amount is not allowed for USD transactions. |
| `KHR-LESS-100` | The transaction amount in KHR must be at least 100 KHR. |
| `KHR-CONTAIN-DECIMAL` | KHR transaction amounts cannot contain decimal places. |
