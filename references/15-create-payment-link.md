# Create Payment Link

This API allows you to create a payment link from your application.

## Endpoint

```
POST /api/merchant-portal/merchant-access/payment-link/create
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `multipart/form-data`

## Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_time` | string | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | Yes | A unique merchant key provided by ABA Bank |
| `merchant_auth` | string | Yes | A JSON string representing a JSON object, encrypted using OpenSSL with an RSA public key |
| `image` | binary | No | An image associated with the payment link. Maximum file size: 3MB. Supported file formats: JPG, JPEG, PNG |
| `hash` | string | Yes | Base64-encoded HMAC SHA-512 hash of the concatenated values: `request_time`, `merchant_id`, and `merchant_auth` with `public_key` |

### `merchant_auth` Object (before encryption)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mc_id` | string | Yes | The same value as merchant_id |
| `title` | string | Yes | Title of the payment link. Max. Lenght 250 |
| `amount` | string | Yes | Payment link amount. Must be at least 100 KHR or 0.01 USD. Cannot be null or zero |
| `currency` | string | Yes | Transaction currency code (Mandatory). Supported values: `KHR` or `USD` |
| `description` | string | No | Description of the payment link. Optional. Max. Lenght 250 |
| `payment_limit` | string | No | Maximum number of transactions allowed for this payment link (Optional). If left blank, there is no limit. |
| `expired_date` | string | Yes | Expiration date of the payment link. A null value means no expiry date |
| `return_url` | string | Yes | Once a payment is made on the payment link, the payment gateway will call this URL to send the payment details. This URL must be encrypted in Base64 |
| `merchant_ref_no` | string | No | Your payment link ID. We suggest using a unique ID. PayWay does not validate duplicates. This ID will be included in the callback when the payment is completed. Max length: 50 |
| `payout` | string | No | Payout instruction of the payment link. Total payout amount must equal to payment link amount |

## Encryption

**PHP Sample Code**

```php
function opensslEncryption($source, $publicKey)
{
    $maxlength = 117;
    $output = '';
    while (!empty($source)) {
        $input = substr($source, 0, $maxlength);
        openssl_public_encrypt($input, $encrypted, $publicKey);
        $output .= $encrypted;
        $source = substr($source, $maxlength);
    }
    return base64_encode($output);
}

$rsa_public_key = "RSA PUBLIC KEY PROVIDED BY ABA BANK";

$data = json_encode([
    'mc_id' => $merchant_id,
    'title' => 'Test curl 001',
    'amount' => 0.03,
    'currency' => 'USD',
    'description' => 'Payment link created from curl',
    'payment_limit' => 5,
    'expired_date' => time(),
    'return_url' => base64_encode('https://domain.com'),
    'merchant_ref_no' => 'ref00001',
    'payout' => '[
        {"acc":"122092016015926","amt":0.01},
        {"acc":"122091511120425","amt":0.02}
    ]',
]);

$merchant_auth = opensslEncryption($data, $rsa_public_key);
```

## Hash Computation

**PHP Sample Code**

```php
// public key provided by ABA Bank
$api_key = "API KEY PROVIDED BY ABA BANK";

// Prepare the data to be hashed
$b4hash = $request_time . $merchant_id . $merchant_auth;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

## Response

### Success Response

```json
{
  "data": {
    "id": "UD/8Hl***Ht1xQdhlw==",
    "title": "Test curl 001",
    "image": {
      "image": "",
      "filename": "",
      "size": 0
    },
    "amount": "0.03",
    "currency": "USD",
    "status": "OPEN",
    "description": "Payment link created from curl",
    "payment_limit": 5,
    "total_amount_org": 0,
    "total_refund": 0,
    "total_amount": 0,
    "total_trxn": 0,
    "created_at": "2023-04-13 03:43:30",
    "updated_at": "2023-04-13 03:43:30",
    "expired_date": 1681357409,
    "return_url": "https://domain.com",
    "merchant_ref_no": "ref00001",
    "outlet_id": "xknY***QfbOCJA==",
    "outlet_name": "Book Store",
    "payment_link": "https://dpayment-euat.payway.com.kh/JT4630l"
  },
  "payout": [
    {
      "acc": "000***222",
      "amt": "0.01",
      "acc_name": "Red cafe online"
    },
    {
      "acc": "122***425",
      "amt": "0.02",
      "acc_name": "Red Cafe 02 by K.S"
    }
  ],
  "status": {
    "code": "00",
    "message": "Success!"
  },
  "tran_id": 1681357410
}
```

### Exception Response

```json
{
  "status": {
    "code": "PTL02",
    "message": "Wrong Hash"
  },
  "tran_id": 1681357410
}
```

### `data` Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | A unique payment link ID generated by the payment gateway |
| `title` | string | The title of your payment link |
| `image` | object | Image associated with the payment link |
| `image.image` | string | Full URL of the image |
| `image.filename` | string | The filename of the image, including its extension |
| `image.size` | number | Image size in KB |
| `amount` | number | Payment link amount |
| `currency` | string | Payment link currency. Supported values: `KHR`, `USD` |
| `status` | string | Once the payment link is created, its status is "OPEN" |
| `description` | string | A description of your payment link |
| `payment_limit` | number | The maximum number of transactions allowed for this payment link |
| `total_amount_org` | string | Total payment amount before refund |
| `total_amount` | number | Total amount after refund |
| `total_refund` | number | Total refunded amount |
| `total_trxn` | number | The total number of completed payment transactions. A newly created payment link will have a value of 0 |
| `created_at` | string | Date and time when the payment link was created in the payment gateway |
| `updated_at` | string | The last updated date and time of the payment link |
| `expired_date` | number | The expiration timestamp for this payment link |
| `return_url` | string | The URL that the payment gateway will call to send payment status updates |
| `merchant_ref_no` | string | The payment link reference number |
| `outlet_id` | string | A unique outlet identifier |
| `outlet_name` | string | The outlet name |
| `payment_link` | string | Full URL of the payment link |

### `payout` Array Items

| Field | Type | Description |
|-------|------|-------------|
| `acc` | string | The ABA account number or MID of the beneficiary |
| `amt` | number | The payout amount. The currency will follow the payment link currency |
| `acc_name` | string | The name of the beneficiary. If the beneficiary is an ABA account number, it will show the account holder's name. If the beneficiary is a MID (ABA Merchant), it will show the outlet name associated with that MID |

### Other Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `tran_id` | string | A unique log ID generated by the payment gateway |

## Status Codes

| Code | Description |
|------|-------------|
| `PTL02` | Wrong Hash |
| `PTL05` | Parameter Invalid Format |
| `PTL99` | Merchant invalid currency. |
| `PTL132` | Invalid payment link. |
