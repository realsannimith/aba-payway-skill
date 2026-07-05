# Update a beneficiary status

This API allows you to update the status of a beneficiary, toggling between active and inactive status.

## Endpoint

```
POST /api/merchant-portal/merchant-access/whitelist-account/update-whitelist-status
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `application/json`

## When to Use

- To prevent a whitelisted beneficiary from receiving future funds or from being used in payout instructions.
- To resume a previously disabled beneficiary so they can start receiving funds again or be used in payout instructions.

## Request Parameters

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `request_time` | string | — | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | 20 | Yes | A unique merchant key which provided by ABA Bank |
| `merchant_auth` | string | — | Yes | The JSON-encoded object containing `mc_id`, `payee`, and `status` is encrypted using RSA public key encryption in chunks. The resulting encrypted data is then concatenated and encoded in Base64 format. |
| `hash` | string | — | Yes | Base64 encode of hash hmac sha512 encryption of concatenates values `request_time` and `merchant_auth` with `public_key` |

### `merchant_auth` Object (before encryption)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mc_id` | string | Yes | A unique merchant key which provided by ABA Bank. Same value as `merchant_id` |
| `payee` | string | Yes | Beneficiary identifier: It can be either a MID or an ABA account |
| `status` | integer | Yes | To disable the beneficiary, set the value to `0`. To activate the beneficiary, set the value to `1`. |

### RSA Encryption (PHP Sample Code)

```php
// Prepare data to be encrypted
$data_object = json_encode([
     'mc_id' => 'ec000002',
      'payee' => '318111358120004',
      'status' => 0
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
$b4hash = $request_time . $merchant_auth;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

## Example Request

```json
{
  "request_time": "20200728093403",
  "merchant_id": "ec000002",
  "merchant_auth": "39aaa43.....0c00a",
  "hash": "EVDFA2118UD0boKhkAcOb...+5KCCt+sWw=="
}
```

## Response

**HTTP 200**

### `data` Object

| Field | Type | Max Length | Description |
|-------|------|-----------|-------------|
| `name` | string | 255 | The name of the beneficiary: if the type is MID, it will be the outlet name; if it is an account, it will be the account holder's name |
| `payee` | string | 250 | This value represent the destination beneficiary it can be MID or ABA Account number |
| `currency` | string | 10 | If payee is MID, the value here will be merchant's currency and if the payee is an ABA Account holder it will return account currency |
| `type` | string | 20 | If payee is MID, the value here is `Merchant` if the payee is an ABA Account holder it will return `ABA Account` |
| `status` | integer | — | The current status of the beneficiary. `1` = Active, `0` = Inactive |
| `created_at` | string | — | Date and time that the beneficiary was created or added to the list |

### Example Success Response

```json
{
  "data": {
    "name": "Store Name",
    "payee": "318111358120004",
    "currency": "USD",
    "type": "ABA Account",
    "status": 1,
    "created_at": "2020-07-28T09:34:03"
  },
  "status": {
    "code": "00",
    "message": "Success!"
  }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| `00` | Success! |
| `PTL02` | Wrong hash |
| `PTL04` | Parameter validation required |
| `PTL46` | Merchant not found |
| `PTL149` | Invalid whitelist account |
| `PTL150` | Business profile is not found |
