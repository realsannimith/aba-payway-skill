# ABA PayWay API Overview

## Introduction

ABA PayWay provides a comprehensive platform for integrating secure online payment solutions in Cambodia. Accept payments for your business with PayWay's simple and flexible payment methods including ABA KHQR, credit/debit cards (Visa, Mastercard, JCB, UPI), WeChat Pay, Alipay, and Google Pay.

## Core Capabilities

### Accept Payments
Accept online payments on website and mobile app with multiple payment methods:
- Supported methods: ABA KHQR, credit/debit cards, WeChat Pay, and Alipay
- Dynamic QR code generation for display or printing across various systems
- API-based payment link creation and distribution for faster collection

### Auto-Payments (Credentials on File)
Collect payment automatically by storing your customers' ABA accounts or card details for future use:
- Automatic subscription billing using stored payment information
- Customer account and card storage functionality
- On-demand charging with previously saved payment methods

### Hold Payments (Pre-Auth)
Temporarily hold customers' funds and release them later to ensure flexible and secure transactions:
- Payment holding with deferred charging upon service completion
- Hold-settle-payout workflows distributing funds to multiple stakeholders

### Multi-Party Payouts
Automatically split and distribute payments to multiple accounts in real-time:
- Real-time beneficiary payments on demand
- Automatic payment splitting among multiple recipients

## Environments

| Environment | Base URL |
|-------------|----------|
| Sandbox | `https://checkout-sandbox.payway.com.kh/` |
| Production | `https://checkout.payway.com.kh/` |

## Authentication

All API requests require:
1. **Merchant ID** (`merchant_id`): Unique identifier provided by ABA Bank
2. **API Key**: Secret key for HMAC hash generation
3. **RSA Public Key**: For encrypting sensitive data (refund, payout, pre-auth APIs)
4. **Hash**: HMAC-SHA512 signature of request parameters, Base64-encoded

### Hash Generation Pattern (PHP)
```php
$api_key = "API KEY PROVIDED BY ABA BANK";
$b4hash = $param1 . $param2 . $param3; // concatenated parameters vary per API
$hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));
```

### RSA Encryption Pattern (PHP)
Used for `merchant_auth` and `beneficiaries` fields:
```php
$data_object = json_encode($data);
$rsa_public_key = "RSA PUBLIC KEY PROVIDED BY ABA BANK";
$maxlength = 117;
$encrypted_output = '';
while ($data_object !== '') {
    $chunk = substr($data_object, 0, $maxlength);
    $data_object = substr($data_object, $maxlength);
    if (openssl_public_encrypt($chunk, $encrypted_chunk, $rsa_public_key)) {
        $encrypted_output .= $encrypted_chunk;
    }
}
$result = base64_encode($encrypted_output);
```

## Important Requirements

- **Domain Whitelisting**: Your domain/IP must be approved by PayWay's integration team before making API requests. Unauthorized access returns error code `6: wrong domain`.
- **HTTP Method**: All APIs require `POST` requests. GET requests return `405 Method Not Allowed`.
- **Content-Type**: Either `application/json` or `multipart/form-data` depending on the API endpoint.
- **Optional Parameters**: May be omitted when not applicable to your use case.

## Getting Started

1. Register for a PayWay Sandbox Account at `sandbox.payway.com.kh`
2. Receive Sandbox Merchant ID and API Key via email
3. Implement using the API documentation
4. Test transactions in sandbox
5. Contact `paywaysales@ababank.com` for production credentials

## Support

- Technical support: `digitalsupport@ababank.com`
- Sales/onboarding: `paywaysales@ababank.com`

## Test Cards (Sandbox Only)

### Success Cards
| Card Type | Number | Expiry | CVV | 3DS |
|-----------|--------|--------|-----|-----|
| Mastercard | 5156 8399 3770 6777 | 01/30 | 993 | No |
| Visa | 4286 0900 0000 0206 | 04/30 | 777 | Yes |

### Declined Cards
| Card Type | Number | Expiry | CVV | 3DS |
|-----------|--------|--------|-----|-----|
| Mastercard | 5156 8302 7256 1029 | 04/30 | 777 | Yes |
| Visa | 4156 8399 3770 6777 | 01/30 | 993 | No |

> **Note**: OTP pin for verifying 3D Secure is sent to your registered email address.

## API Index

| # | API | Endpoint | Category |
|---|-----|----------|----------|
| 1 | [Purchase](./01-purchase.md) | `POST /api/payment-gateway/v1/payments/purchase` | Checkout |
| 2 | [Check Transaction](./02-check-transaction.md) | `POST /api/payment-gateway/v1/payments/check-transaction-2` | Checkout |
| 3 | [Get Transaction Details](./03-get-transaction-details.md) | `POST /api/payment-gateway/v1/payments/transaction-detail` | Checkout |
| 4 | [Get Transaction List](./04-get-transaction-list.md) | `POST /api/payment-gateway/v1/payments/transaction-list-2` | Checkout |
| 5 | [Close Transaction](./05-close-transaction.md) | `POST /api/payment-gateway/v1/payments/close-transaction` | Checkout |
| 6 | [Refund](./06-refund.md) | `POST /api/merchant-portal/merchant-access/online-transaction/refund` | Checkout |
| 7 | [Exchange Rate](./07-exchange-rate.md) | `POST /api/payment-gateway/v1/exchange-rate` | Checkout |
| 8 | [Link Account](./08-link-account.md) | `POST /api/aof/request-qr` | Credentials on File |
| 9 | [Link Card](./09-link-card.md) | `POST /api/payment-gateway/v1/cof/initial` | Credentials on File |
| 10 | [Purchase Using Token](./10-purchase-using-token.md) | `POST /api/payment-gateway/v1/payments/purchase` | Credentials on File |
| 11 | [Remove Account Token](./11-remove-account-token.md) | `POST /api/aof/remove-account` | Credentials on File |
| 12 | [Remove Card Token](./12-remove-card-token.md) | `POST /api/payment-gateway/v1/cof/remove` | Credentials on File |
| 13 | [Get Linked Account Details](./13-get-linked-account-details.md) | `POST /api/aof/pushback-status` | Credentials on File |
| 14 | [QR API (Generate QR)](./14-qr-api.md) | `POST /api/payment-gateway/v1/payments/generate-qr` | ABA QR |
| 15 | [Create Payment Link](./15-create-payment-link.md) | `POST /api/merchant-portal/merchant-access/payment-link/create` | Payment Link |
| 16 | [Get Payment Link Details](./16-get-payment-link-details.md) | `POST /api/merchant-portal/merchant-access/payment-link/detail` | Payment Link |
| 17 | [Complete Pre-Auth](./17-complete-pre-auth.md) | `POST /api/merchant-portal/merchant-access/online-transaction/pre-auth-completion` | Pre-Auth |
| 18 | [Complete Pre-Auth with Payout](./18-complete-pre-auth-with-payout.md) | `POST /api/merchant-portal/merchant-access/online-transaction/pre-auth-completion` | Pre-Auth |
| 19 | [Cancel Pre-Auth](./19-cancel-pre-auth.md) | `POST /api/merchant-portal/merchant-access/online-transaction/pre-auth-cancellation` | Pre-Auth |
| 20 | [Payout](./20-payout.md) | `POST /api/payment-gateway/v2/direct-payment/merchant/payout` | Payout |
| 21 | [Add Beneficiary to Whitelist](./21-add-beneficiary.md) | `POST /api/merchant-portal/merchant-access/whitelist-account/add-whitelist-payout` | Payout |
| 22 | [Update Beneficiary Status](./22-update-beneficiary-status.md) | `POST /api/merchant-portal/merchant-access/whitelist-account/update-whitelist-status` | Payout |
| 23 | [Get Transactions by Merchant Ref](./23-get-transactions-by-ref.md) | `POST /api/payment-gateway/v1/payments/get-transactions-by-mc-ref` | Checkout |
