# KHQR Guideline

## What is ABA KHQR?

A standardized QR code payment system overseen by the National Bank of Cambodia. It facilitates cashless transactions by allowing consumers and businesses to make and receive payments seamlessly using mobile banking apps or e-wallets. The system promotes digital payments, enhances financial inclusion, and ensures interoperability among different banks and payment service providers, making financial transactions more efficient and accessible across the country.

> Merchants who implement KHQR are required to make adjustments or changes upon request by ABA or in compliance with the National Bank of Cambodia's requirements. Failure to do so may result in the suspension or termination of the service.

## Benefits of KHQR

### For Customers:

- No more confusion with multiple QR codes at checkout—just scan a single KHQR code.
- Simply look for the **KHQR label** when making payments.
- Use your preferred payment app, including the **Bakong App**, to pay at any location that supports KHQR.

### For Merchants:

- **Save counter space**—display just one KHQR stand instead of multiple QR labels.
- **Simple, fast, and secure** payment solution.
- Accept payments from **anyone and any bank app** without the need for multiple bilateral contracts with different acquirers.

## How to Implement

### Notations Convention

| Abbreviation | Description |
|---|---|
| ans | Alphanumeric Special. The Alphanumeric Special alphabet includes ninety-six (96) characters in total and includes the numeric alphabet and punctuation. |
| C | Conditional |
| CDCVM | Consumer Device Cardholder Verification Method |
| CRC | Cyclic Redundancy Check |
| ECI | Extended Channel Interpretation |
| ID | Identifier of the data object |
| ISO | International Standards Organization |
| M | Mandatory |
| N | Numeric. Values that can be represented by all digits, from "0" to "9". |
| QR Code | Quick Response Code |
| RFU | Reserved for Future Use |
| S | String. Values represented by any precomposed character(s) defined in [Unicode]. |
| Var. | Variable |

### Data Object

#### Data Objects Under the Root of a QR Code

| Name | ID | Format | Length | Presence | Comment |
|---|---|---|---|---|---|
| Payload Format Indicator | "00" | N | "02" | M | 01 |
| Point of Initial Method | "01" | N | "02" | M | `11` for Static QR (without amount); `12` for Dynamic QR (with amount) |
| Merchant Account Information | "30" | N | var. up to "99" | M | Provide By ABA |
| Merchant Category Code | "52" | ans | var. up to "99" | M | At least one Merchant Account Information data object shall be present. |
| Transaction Currency | "53" | N | "03" | M | `116` for KHR, `840` for USD |
| Transaction Amount | "54" | ans | var. up to "13" | C | Do not use decimal places for `KHR` amounts. |
| Country Code | "58" | ans | "02" | M | |
| Merchant Name | "59" | ans | var. up to "25" | M | The display name shown when a mobile banking app scans the QR. Please ensure it matches the name on your ABA registered profile. |
| Merchant City | "60" | ans | var. up to "15" | M | Available `Battambang`, `BMC` short cut for *Banteay MeanChey*, `Kampong Cham`, `Kampong Chhnang`, `Kampong Speu`, `Kampong Thom`, `Kandal`, `Kep`, `Koh Kong`, `Kratie`, `Mondolkiri`, `Oddor Meanchey`, `Pailin`, `Pady Paet`, `Phnom Penh`, `Preah Vihear`, `Prey Veng`, `Pursat`, `Ratanakiri`, `Siem Reap`, `Sihanouk Ville`, `Steung Treng`, `Svay Rieng`, `Takeo`, `Tboung Khmum`. |
| Additional Data Field Template | "62" | S | var. up to "99" | M | The Additional Data Field Template includes information that may be provided by the Merchant. |
| Additional Data Field | "99" | S | var. up to "99" | M | Additional info used by Bakong. |
| CRC | "63" | ans | "04" | M | Cyclic Redundancy Check |

#### Data Objects for Additional Data Field Template (ID "62")

| Name | ID | Format | Length | Presence | Comment |
|---|---|---|---|---|---|
| Merchant Reference Number | "01" | ans | var. up to "25" | M | |
| PayWay Data Field Template | "68" | S | var. up to "99" | M | Provide By ABA |

### Example

```
00020101021230510016abaakhppxxx@abaa01151250212145328460208ABA Bank52045987530311654031005802KH5925OLD ME 25 CHAR WINNER IP26010Phnom Penh62570115MC-REF-KH-1500068340010PAYWAY@ABA0208104514230604A2279934001317598053453370113175980552533763049FBD
```

#### Data Objects Under the Root of a QR Code

| ID | Sub Tag | Length | Value | Descripiton |
|---|---|---|---|---|
| 00 | | 02 | 01 | Verstion 1 |
| 01 | | 02 | 12 | Indicate it's dynamic QR |
| 30 | | 51 | | Merchant info |
| | 00 | 16 | abaakhppxxx@abaa | Acquiring Bakong ID. |
| | 01 | 15 | 125021214532846 | Your MID provided by ABA Bank |
| | 02 | 08 | ABA Bank | Name of acquiring Bank |
| 52 | | 04 | 5987 | Merchant Category Code |
| 53 | | 03 | 116 | `KHR` transaction Currency |
| 54 | | 03 | 100 | Transaction Amount |
| 58 | | 02 | KH | Country Code |
| 59 | | 25 | OLD ME 25 CHAR WINNER IP2 | Merchant Name |
| 60 | | 10 | PHNOM PENH | Merchant City |
| 62 | | 57 | | Additional data. |
| | 01 | 15 | MC-REF-KH-15000 | Merchant reference # |
| | 68 | 34 | 0010PAYWAY@ABA0208104514230604A227 | Provide by ABA Bank |
| 99 | | 34 | | Additional data use by Bakong |
| | 00 | 13 | 1759805345337 | Creation timestamp |
| | 01 | 13 | 1759805345337 | Expriry timestamp |
| 63 | | 04 | 9FBD | CRC |

> QR can be paid multiple times.

### Receiving Payment Notification via Webhook

Merchant have to provide the webhook url to PayWay to receive payment notification once the payment is successful paid by the customer. Below is the sample data that will be posted to the webhook.

```json
{
   "transaction_id": "3309DCD5BCB94CBD820046CE9",
   "transaction_date": "2025-10-10 16:03:26",
   "original_currency": "KHR",
   "original_amount": 100,
   "bank_ref": "100FT30153179430",
   "apv": "341136",
   "payment_status_code": 0,
   "payment_status": "APPROVED",
   "payment_currency": "KHR",
   "payment_amount": 100.0,
   "payment_type": "ABA Pay",
   "payer_account": "*898",
   "bank_name": "ABA Bank",
   "merchant_ref": "3309DCD5BCB94CBD820046CE9"
}
```

### Webhook Fields

| Name | Description |
|---|---|
| `transaction_id` | Unique transaction ID that generate by PayWay. |
| `merchant_ref` | Information from QR subtag 62.01. |
| `datetime` | Date and time of the transaction. |
| `bank_ref` | Core banking booking entry |
| `status` | `0` represent the success payment |
| `description` | Payment status description in word. |
| `apv` | Approval code. It has 6 digits length |
| `original_amount` | The amount that merchant received |
| `original_currency` | Merchant currency |
| `payment_amount` | Payer payment amount. |
| `payment_currency` | Payer payment currency. It can be `KHR` or `USD`. |
| `payment_type` | `ABA PAY` or `KHQR` |
| `payer_account` | Mask account number of the payer. |
| `payer_name` | Payer name. |
| `bank_name` | Issuer bank name |

Webhook must use `POST` method, `HTTPS` encryption.
