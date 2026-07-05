# Ecommerce Checkout

## 1. Introduction

With PayWay eCommerce Checkout, you can easily **accept payments on your website or mobile app**. This solution lets your customers pay quickly and securely using **Credit/Debit Cards**, **ABA Pay & KHQR** (via ABA Mobile or other KHQR-supported banking apps), **WeChat Pay** or **Alipay** — to give them a seamless and secure checkout experience.

### Common Use Cases

- **Online shopping** -- Accept payments for products and services.
- **Wallet top-ups & digital services** -- Let users add funds or pay for digital services.
- **Subscriptions & bills** -- As a checkout to process recurring payments and utility bills.
- **On-demand services** -- Handle payments for food delivery, ride-hailing, and more.
- **Event bookings** -- Enable seamless ticket and reservation payments

## 2. How it works

1. The **customer selects a product or service** and clicks **"Pay"**.
2. They **choose a payment method**, and a **checkout modal appears**.
3. The **customer completes payment** with their chosen method (credit/debit cards, ABA Pay, KHQR, WeChat Pay, Alipay, or Google Pay).
4. Once the payment is processed, **your system receives a pushback notification** with the payment status.
5. Your system **verifies the payment** and confirms the order.

> Selling on an eCommerce platform? See our eCommerce Checkout Plugins instead!

## 3. Set up your payment selection UI

To ensure a smooth payment experience, your platform **must** include UI to accommodate the online payment acceptance. This includes:

- A section where **customers can choose a payment options** they want to pay with.
- A **"We Accept..."** area that shows the payment options you offer.

> You **must** follows PayWay eCommerce checkout guidelines to ensure seamless customer payments.

UI guidelines are available via Figma:

- **Web UI Guidelines** -- To accept payments on your website
- **Mobile UI Guidelines** -- To accept payments on your app or web app

## 4. Integration Steps

Before you start, make sure you have the following:

- **PayWay Sandbox Account** -- [Register here](https://sandbox.payway.com.kh/register-sandbox/) to test transactions.
- **Sandbox Merchant ID & API Key** -- You'll receive these via email after registering for the sandbox.

To integrate online payments on your website or mobile app, follow these steps:

### Step 1: Create a Payment Transaction

When the customer selects "Pay" and **chooses a payment method**, call the [Create Transaction API](./01-purchase.md) to generate a transaction and display it on your platform.

#### Sample Request

```html
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" />

    <!-- Remove PayWay Plugin JS if you prefer Hosted view mode. This URL is valid for both Sanbdbox and Production -->
    <script src="https://checkout.payway.com.kh/plugins/checkout2-0.js" defer></script>

  </head>
  <body>
    <form method="POST" target="aba_webservice" id="aba_merchant_request"
      action="https://checkout-sandbox.payway.com.kh/api/payment-gateway/v1/payments/purchase" >
      <input type="hidden" name="hash" value="D8SaUWAA/AhxNro00wAykb4ibeo9kM3if7ioN7cnBfihXP/38anLGwGUxHK+J6HvaiUEV8Ho+nz5nkQrzowm7g==" />
      <input id="tran_id" type="hidden" name="tran_id" value="17536691884" /><br />
      <input type="hidden" name="amount" value="0.10" />
      <input type="hidden" name="merchant_id" value="ec000002" />
      <input type="hidden" name="req_time" value="20250728022056" />

      <input type="hidden" id="payment_option" name="payment_option" value="" />

      <input type="hidden" name="currency" value="" />

      <input type="hidden" name="firstname" value="sina" />
      <input type="hidden" name="lastname" value="chhum" />
      <input type="hidden" name="phone" value="093939399" />
      <input type="submit" value="submit" />
    </form>

    <script>
      var form = document.getElementById('aba_merchant_request')
      form.addEventListener('submit', function (event) {
        event.preventDefault()
        AbaPayway.checkout() // Use it with PayWay Plugin JS to display as a bottom sheet on mobile or a modal popup on desktop // document.getElementById(form_id).submit() // Use it to display as Hosted view mode
      })
    </script>
  </body>
</html>
```

PayWay will respond with a **HTML response** that contains the checkout interface, which you must render on your website/platform for the customer to complete the payment.

#### Web Implementation

Payment method checkout UI variants for web:

| Payment Options | Checkout UI |
|---|---|
| `cards` | Credit/debit card interface |
| `abapay` | ABA Pay interface |
| `bakong` | KHQR (Bakong) interface |
| `alipay` | Alipay interface |
| `wechat` | WeChat Pay interface |
| `google_pay` | Google Pay interface |

#### Mobile Implementation

For a better user experience on mobile apps or webview, ensure you use the following parameters when you call the [Create Transaction API](./01-purchase.md):

- `view_type=hosted` -- To respond the hosted checkout page on mobile.
- `return_deeplink` -- Handles redirection for native iOS and hybrid apps, so your customers can return to your platform after making a payment in ABA Mobile.

### Step 2: Verify Payment Status

Use the [Check Transaction API](./02-check-transaction.md) to confirm whether a payment was successful.

After you create a payment, call the API with the transaction ID to check its status. Please respect the rate limit of 600 requests per second and stop checking once a result is returned.

### Step 3: (Optional) Handle Callback URL for payment status updates

Once the customer completes the payment, the details of the transaction and other important information will also sent via `return_url` URL.

This is an optional field. If left empty, it will default to the merchant profile's `return_url`. If you provide a value, ensure that your domain is whitelisted in your merchant profile.

Your `return_url` must accept HTTP `POST` method and Content-Type as `application/json`.

> We highly recommend securing this URL to ensure that only PayWay has access to it.

#### Sample Pushback Data

```json
{
    "tran_id": "17425401324",
    "apv": "619195",
    "status": "0",
    "return_params": "xxxxxxxxxx"
}
```

| Field | Description |
|---|---|
| `tran_id` | Transaction ID sent during the initial payment process. |
| `apv` | Transaction approval code. |
| `status` | Payment status |
| `return_params` | Extra information sent to the payment gateway during the payment initiation request. |
