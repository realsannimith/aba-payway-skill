# Purchase API

The Purchase API is used to initiate a payment transaction between a customer and a merchant through PayWay. It allows merchants to request a payment by providing transaction details such as the amount, currency, item list, and other relevant data.

Once the API is called, the customer is redirected to PayWay's hosted checkout page, bottom sheet, or modal popup—depending on your integration option—where they can complete the payment using the available methods (e.g., card, ABA PAY, KHQR, digital wallets). After the transaction is completed, PayWay will return the transaction result to the merchant via the configured return URL or callback.

## Endpoint

```
POST /api/payment-gateway/v1/payments/purchase
```

**Base URL**: `https://checkout-sandbox.payway.com.kh/` (sandbox) | `https://checkout.payway.com.kh/` (production)

**Content-Type**: `multipart/form-data`

## Request Parameters

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `req_time` | string | — | Yes | Request date and time in UTC format as `YYYYMMDDHHmmss` |
| `merchant_id` | string | 30 | Yes | A unique merchant key which provided by ABA Bank |
| `tran_id` | string | 20 | Yes | A unique transaction identifier for the payment |
| `amount` | number | — | Yes | Purchase amount |
| `hash` | string | — | Yes | Base64-encoded HMAC-SHA512 hash (see [Hash Generation](#hash-generation)) |
| `firstname` | string | 100 | No | Buyer's first name |
| `lastname` | string | 100 | No | Buyer's last name |
| `email` | string | 50 | No | Buyer's email |
| `phone` | string | 20 | No | Buyer's phone |
| `type` | string | 20 | No | Type of the transaction, default value is `purchase`. Supported values: `pre-auth` (for pre purchase), `purchase` (for full purchase). Note: pre-auth only supports ABA PAY, KHQR and Card Payment |
| `payment_option` | string | 20 | No | Payment method for the transaction (see [Payment Options](#payment-options)) |
| `items` | string | 500 | No | A base64-encoded JSON array describing the items being purchased (see [Items Example](#items-example)). **Note: This is only description/remark. The price or quantity in this info will not be used for calculation or any validation purposes** |
| `shipping` | number | — | No | Shipping fee |
| `currency` | string | — | No | Transaction currency of the payment. If you don't pass any value, it will take default value from your merchant profile (the currency of the first account you registered). Supported values are `KHR` or `USD` |
| `return_url` | string | — | No | URL to receive callbacks upon payment completion, encrypted with Base64 |
| `cancel_url` | string | — | No | The URL to redirect to after the user closes the payment dialog or when user cancel the payment |
| `skip_success_page` | integer | — | No | Skip success page can be configured on checkout service level. We also provide option via the API for you to override the setting too. If you don't pass this param, it will follow the configuration on the profile level. Supported values: `0` (don't skip success pages), `1` (skip success page). Once you skip success page, `continue_success_url` on profile level will be used to redirect user to the specific location if you don't pass value of `continue_success_url` in the request |
| `continue_success_url` | string | — | No | The URL to redirect to after a successful payment |
| `return_deeplink` | string | — | No | The deep link for redirecting to the app after a successful payment from ABA Mobile. Must be base64-encoded and include both iOS and Android schemes. This field is mandatory for mobile integration (see [Return Deeplink Example](#return-deeplink-example)) |
| `custom_fields` | string | — | No | Additional information that you want to attach to the transaction. This information will appear in the transaction list, transaction details and export report. It's base64-encoded JSON info (see [Custom Fields Example](#custom-fields-example)) |
| `return_params` | string | — | No | Information to include when PayWay calls your return URL after a successful payment |
| `view_type` | string | — | No | Defines the view type for the payment page. `hosted_view` (redirect payer to a new tab), `popup` (display as a bottom sheet on mobile web browsers and as a modal popup on desktop web browsers) |
| `payment_gate` | integer | — | No | If your merchant profile also supports the QR Payment API service, please set this parameter to `0` to use the Checkout service |
| `payout` | string | — | No | Base64-encoded JSON string representing payout details (see [Payout Example](#payout-example)) |
| `additional_params` | string | — | No | Currently, we support WeChat Mini Program. These are the values key `wechat_sub_appid` and `wechat_sub_openid` (see [Additional Params Example](#additional-params-example)) |
| `lifetime` | integer | — | No | The payment's lifetime in minutes, once it exceeds customer will not be allowed to make payment. Default value is 30 days. Min: 3 mins, Max: 30 days. For ABA PAY or Card: Transaction will not go through. KHQR: In case payment happens after exceeded lifetime, PayWay will also reject. Fund will be reversed back to payer. WeChat & Alipay: No reversal |
| `google_pay_token` | string | — | No | This field is required if `payment_option` is set to `google_pay` and the payment selection is managed by the merchant |

### Payment Options

| Value | Description |
|-------|-------------|
| `cards` | For card payments |
| `abapay_khqr` | QR payment that can be scanned and paid using ABA PAY and other KHQR member banks |
| `abapay_khqr_deeplink` | Allows customers to pay using ABA PAY and other KHQR member banks. The payment gateway will respond with a JSON object containing `qr_string`, `abapay_deeplink`, and `checkout_qr_url`. See the sample response in the [Response](#response) section below |
| `alipay` | Allows customers to pay using Alipay Wallet |
| `wechat` | Allows customers to pay using WeChat Wallet |
| `google_pay` | Allows customers to pay using Google Pay Wallet |

If no value is provided, the payment gateway will automatically display the supported payment options based on your profile, allowing the customer to choose a preferred payment method.

### Items Example

```php
$item = base64_encode(json_encode([
    ["name" => "product 1","quantity" => 1,"price" => 1.00],
    ["name" => "product 2","quantity" => 2, "price" => 4.00]
]));
```

### Return Deeplink Example

```php
$return_deeplink = base64_encode(json_encode([
    "ios_scheme" => "DEEPLINK TO RETURN TO YOUR IOS APP",
    "android_scheme" => "DEEPLINK TO RETURN TO YOUR ANDROID APP"
]));
```

### Custom Fields Example

```php
$custom_field = base64_encode(json_encode([
    "field1" => "myvalue1",
    "field2" => "myvalue2"
]));
```

### Payout Example

```php
$payout = base64_encode(json_encode([
    ["acc" => "000133879","amt"=> 1],
    ["acc" => "000133880","amt" => 1]
]));
```

### Additional Params Example

```php
$additional_params = base64_encode(json_encode([
    'wechat_sub_appid' => 'YOUR WECHAT APP ID',
    'wechat_sub_openid' => 'YOUR WECHAT OPEN ID'
]));
```

## Hash Generation

Base64 encode of hash hmac sha512 encryption of concatenated values `req_time`, `merchant_id`, `tran_id`, `amount`, `items`, `shipping`, `firstname`, `lastname`, `email`, `phone`, `type`, `payment_option`, `return_url`, `cancel_url`, `continue_success_url`, `return_deeplink`, `currency`, `custom_fields`, `return_params`, `payout`, `lifetime`, `additional_params`, `google_pay_token` and `skip_success_page` with `public_key`.

> **Note:** The hash field order differs from the parameter table order above. The explicit concatenation order is shown below. `view_type` and `payment_gate` are **not** included in the hash.

```php
// public key provided by ABA Bank
$api_key = "API KEY PROVIDED BY ABA BANK";

// Prepare the data to be hashed
$b4hash = $req_time . $merchant_id . $tran_id . $amount . $items . $shipping . $firstname . $lastname . $email . $phone . $type . $payment_option . $return_url . $cancel_url . $continue_success_url . $return_deeplink . $currency . $custom_fields . $return_params . $payout . $lifetime . $additional_params . $google_pay_token . $skip_success_page;

// Generate the HMAC hash using SHA-512 and encode it in Base64
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

## Response

### Success Response (hosted checkout)

**HTTP 200** — Returns an HTML page for PayWay's hosted checkout:

```html
<!DOCTYPE html>
<html data-capo="">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalab
<title>PayWay - Checkout</title>
...
</head>
<body>
...
</body>
</html>
```

### Success Response (abapay_khqr_deeplink)

When `payment_option` is set to `abapay_khqr_deeplink`, the response is a JSON object:

```json
{
    "status": {
        "code": "00",
        "message": "Success!",
        "tran_id": "trx-20201019130949"
    },
    "qr_string": "00020101021230510016abaakhppxxx@abaa01153250212100849350208ABA Bank520410165...",
    "abapay_deeplink": "abamobilebank://ababank.com?type=payway&qrcode=00020101021230510016...",
    "checkout_qr_url": "https://checkout-uat.payway.com.kh/eyJzdGF0dXMiOnsiY29kZSI6IjAwIiw..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status.code` | string | Response code (`00` for success) |
| `status.message` | string | Response message |
| `status.tran_id` | string | Transaction identifier |
| `qr_string` | string | QR code string for KHQR payment |
| `abapay_deeplink` | string | Deep link for ABA Mobile payment |
| `checkout_qr_url` | string | URL to the checkout QR page |

### Exception Response

```json
{
    "status": {
        "code": 1,
        "message": "Wrong hash"
    }
}
```

## Error Codes

| Code | Message |
|------|---------|
| `0` | Success |
| `1` | Wrong hash |
| `2` | Invalid transaction ID |
| `3` | Invalid transaction amount |
| `4` | Duplicated transaction ID |
| `5` | Transaction not found |
| `6` | Requested domain is not in whitelist |
| `7` | Wrong return param |
| `8` | Something went wrong while saving data. Please try again later or contact merchant for help. |
| `10` | Wrong shipping price |
| `11` | Something went wrong. Try again or contact the merchant for help. |
| `12` | Payment currency is not allowed |
| `13` | Invalid items |
| `14` | Invalid credit multi acc |
| `15` | Invalid or missing channel values from smart merchant |
| `16` | Invalid first name. It must not contain numbers or special characters or not more than 100 characters. |
| `17` | Invalid last name. It must not contain numbers or special characters or not more than 100 characters. |
| `18` | Invalid phone number |
| `19` | Invalid email |
| `20` | Something went wrong. Please contact merchant. |
| `21` | End of API lifetime |
| `22` | Pre-auth transaction is not enabled |
| `23` | Selected payment option is not enabled for this merchant profile |
| `24` | Cannot decrypt data |
| `25` | Allow maximum 10 payout per requests |
| `26` | Invalid merchant profile |
| `27` | Invalid ctid |
| `28` | Invalid pwt |
| `29` | Invalid pwt or ctid |
| `30` | Merchant is not enabled COF |
| `31` | Unsecure 3Ds page |
| `33` | Cannot identify cardOrigin |
| `34` | Exchange rate data is invalid |
| `35` | Payout info is invalid |
| `36` | Payout account or amount is invalid |
| `37` | Payout accounts are not in whitelist |
| `38` | Payout contain invalid transaction ID |
| `39` | Payout contain duplicated account |
| `40` | Payout contain duplicated transaction ID |
| `41` | Payout info contain mid not link with any merchant profile |
| `42` | Payout info contain account invalid status |
| `43` | Merchant profile's MID is missing. Please try again or contact merchant for help. |
| `44` | Purchase amount has reached transaction limit |
| `45` | Purchase with zero amount is not allowed |
| `46` | Purchase amount for KHR currency could not contain decimal place |
| `47` | KHR amount must be greater than 100 KHR |
| `48` | Something went wrong with requested parameters. Please try again or contact merchant for help. |
| `49` | Invalid start date |
| `50` | Invalid end date |
| `51` | Invalid date range |
| `52` | Maximum date range is allowed only 3 days |
| `53` | Invalid amount range |
| `54` | Transaction is expired. Please try again or contact the merchant for help. |
| `55` | We are unable to request QR from Wechat system. Please try again or contact merchant for help. |
| `56` | We are unable to validate your transaction with Wechat system. Please try again or contact merchant for help. |
| `57` | We are unable to validate your card source. Please try again or contact merchant for help. |
| `58` | Provide invalid card number |
| `59` | Payout info can not be fixed with MID and ABA account |
| `60` | Something went wrong with QR String. Please try again or contact merchant for help. |
| `61` | Something went wrong. Please try again or contact merchant for help. |
| `62` | QR is already in used |
| `63` | Transaction is already exist in core banking. Please perform new transaction or contact merchant for help. |
| `64` | Payer's account is same as merchant profile's account. Please choose different account. |
| `65` | Merchant profile's MID is not found in core banking. Please try again or contact merchant for help. |
| `66` | Something went wrong. Please try again or contact merchant for help. |
| `67` | QR on invoice is currently not available for this merchant profile. |
| `68` | Transaction is expired. Please re-initiate the transaction. |
| `69` | Transaction lifetime can not be less than 3 minutes. |
| `70` | Total purchase amount has reached daily limit. Please use difference account. |
| `71` | Payout for card payment is not allowed to ABA account. |
| `72` | The merchant profile cannot accept payment because its settlement account is closed. |
| `73` | Invalid transaction status |
| `74` | Invalid tran_id or merchant_id |
| `75` | tran_id not found |
| `76` | Invalid additional parameters |
| `77` | Merchant transactions do not support transaction fees |
| `78` | Card payout transactions are not compatible with the discount program. |
| `79` | Payment token missing in Google Pay |
| `80` | Failed to decrypt the payment token provided by Google Pay |
| `81` | The return URL is not in the whitelist |
| `82` | The payout has exceeded the maximum allowable amount per transaction |
| `83` | Payment credential is disabled |
| `84` | Payment credential is expired |
| `85` | Purchase reach limit amount per transaction |
| `86` | Unsupported merchant purchase mode |
| `87` | Payment credential is removed |
| `200` | Payment was canceled |
| `201` | Payment was declined |
| `401` | Unauthorized access |
| `403` | Something went wrong. Try again or contact the merchant for help. |
| `429` | Too many request, please try again in 1min. |
| `503` | System under maintenance |
