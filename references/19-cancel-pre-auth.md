# Cancel Pre-Purchase Transaction

Cancel pre-auth (or cancel pre-authorization) is the process of releasing a temporary hold on funds placed on a customer's payment method before the final transaction is completed.

## Endpoint

```
POST /api/merchant-portal/merchant-access/online-transaction/pre-auth-cancellation
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## Important Notes

- You can only cancel a pre-authorization if the transaction is still pending; if the pre-auth has already been completed or previously cancelled, it cannot be cancelled again.
- Each transaction's pre-authorization can be cancelled only once.
- Once the cancellation is successfully processed, the transaction status will update to 'CANCELLED.'
- For ABA PAY and Card transactions, funds are instantly released back to the payer, whereas for KHQR transactions, the funds will be refunded to the payer.

## Request Parameters

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `request_time` | string | — | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss`. |
| `merchant_id` | string | 20 | Yes | A unique merchant key which provided by ABA Bank. |
| `merchant_auth` | string | — | Yes | The JSON-encoded object containing `mc_id` and `tran_id` using RSA public key encryption in chunks. The encrypted data is then concatenated and encoded in Base64 format. |
| `hash` | string | — | Yes | Base64-encoded HMAC-SHA512 hash of concatenated values: `merchant_id`, `merchant_auth`, and `request_time` with `public_key`. |

### `merchant_auth` Object (before encryption)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mc_id` | string | Yes | A unique merchant key which provided by ABA Bank. Same value as `merchant_id`. |
| `tran_id` | string | Yes | Pre-auth purcahse transaction id to cancel. |

### RSA Encryption (PHP Sample Code)

```php
// Prepare data to be encrypted
$data_object = json_encode([
    'mc_id' => $merchant_id,
    'tran_id' => $tran_id
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
        // Handle encryption failure (optional: log the error or throw an exception)
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
$b4hash = $merchant_id . $merchant_auth . $request_time;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

## Example Request

```json
{
  "request_time": "20200728093403",
  "merchant_id": "ec000002",
  "merchant_auth": "b1453eac8cd686f...c026a3f70678afd",
  "hash": "wR2bVPV...Q6/llsnJ bw=="
}
```

## Response

**HTTP 200**

| Field | Type | Description |
|-------|------|-------------|
| `grand_total` | number | The original amount authorized for pre-auth transactions. |
| `currency` | string | Original transaction currency |
| `transaction_status` | string | Status of the transaction. After successfully cancelling, its status is `CANCELLED` |
| `status.code` | string | Response code |
| `status.message` | string | Descriptive message |

### Example Success Response

```json
{
  "grand_total": 100.00,
  "currency": "USD",
  "transaction_status": "CANCELLED",
  "status": {
    "code": "00",
    "message": "Success!"
  }
}
```

### Example Exception Response

```json
{
  "status": {
    "code": "PTL36",
    "message": "Invalid transaction. Ensure that the transaction ID is correct."
  }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| `00` | Success! |
| `PTL02` | Invalid hash provided. Ensure you are using the correct hash key. |
| `PTL04` | Parameter validation failed. Verify that all required fields are correctly formatted. |
| `PTL06` | The request has expired. Please generate a new request and retry. |
| `PTL36` | Invalid transaction. Ensure that the transaction ID is correct. |
| `PTL62` | Invalid merchant information. Verify your merchant ID and try again. |
| `PTL63` | Merchant does not have a security configuration file. Contact support for assistance. |
| `PTL59` | Unable to complete or cancel Pre-auth. Check the transaction status before retrying. |
| `PTL60` | Pre-auth amount exceeds the allowed limit. Reduce the amount and try again. |
| `PTL61` | Invalid action type. Ensure you are using a valid operation type. |
| `PTL157` | An unexpected error occurred. Please try again later or contact our digital support team. |
| `PTL168` | Concurrent requests are not allowed. Wait a few seconds and retry. |
| `PTL169` | The merchant profile cannot accept payments. Settlement account is closed. |
| `USD-NOT-ALLOW` | The requested amount is not permitted. Choose a valid amount. |
| `KHR-LESS-100` | KHR amount must be greater than 100 KHR. |
| `KHR-CONTAIN-DECIMAL` | Amount for KHR currency must be a whole number (no decimals allowed). |
