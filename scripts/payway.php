<?php
/**
 * ABA PayWay helper library (PHP).
 *
 * ABA's official code samples are all PHP, so this mirrors them exactly while
 * fixing the two error-prone parts of an integration:
 *
 *   1. HMAC-SHA512 hash generation. The field order matters and every field in
 *      the order participates in its slot even when empty -- a skipped optional
 *      field is the #1 cause of "Wrong hash" (code 1).
 *   2. RSA chunked encryption of merchant_auth / beneficiaries (refund, pre-auth,
 *      payout, payment-link and beneficiary APIs).
 *
 * Canonical field orders are transcribed from the docs in ../references/. ABA
 * sometimes lists a different order in the parameter table than in the hash
 * text; these follow the hash text, which is what the server verifies. Confirm
 * against the specific reference file, since ABA adds fields over time.
 */

class PayWay
{
    const BASE_SANDBOX    = 'https://checkout-sandbox.payway.com.kh';
    const BASE_PRODUCTION = 'https://checkout.payway.com.kh';

    /** Current UTC time as YYYYMMDDHHmmss. */
    public static function reqTime(): string
    {
        return gmdate('YmdHis');
    }

    /**
     * base64( HMAC-SHA512(b4hash, apiKey) ) -- ABA default for nearly all APIs.
     * Matches: base64_encode(hash_hmac('sha512', $b4hash, $api_key, true))
     */
    public static function hashB64(string $b4hash, string $apiKey): string
    {
        return base64_encode(hash_hmac('sha512', $b4hash, $apiKey, true));
    }

    /** hex( HMAC-SHA512 ) -- only the Payout doc shows this variant. */
    public static function hashHex(string $b4hash, string $apiKey): string
    {
        return hash_hmac('sha512', $b4hash, $apiKey);
    }

    /**
     * Concatenate $params[$field] for each $field in $order (missing -> ''), then hash.
     * Set $hex=true only for the Payout API.
     */
    public static function makeHash(array $params, array $order, string $apiKey, bool $hex = false): string
    {
        $b4 = '';
        foreach ($order as $f) {
            $v = $params[$f] ?? '';
            if (is_bool($v)) { $v = $v ? '1' : '0'; }
            $b4 .= (string) $v;
        }
        return $hex ? self::hashHex($b4, $apiKey) : self::hashB64($b4, $apiKey);
    }

    /** Base64-encode a JSON-serializable value (items, custom_fields, payout, ...). */
    public static function b64Json($value): string
    {
        return base64_encode(json_encode($value));
    }

    /** Base64-encode a raw string (return_url / callback_url). */
    public static function b64Str(string $value): string
    {
        return base64_encode($value);
    }

    /**
     * RSA chunked encryption for merchant_auth / beneficiaries. Encrypts $data
     * (array -> JSON, or raw string) in 117-byte chunks (1024-bit key), concatenates
     * the ciphertext, and base64-encodes it. This is ABA's exact openssl pattern.
     * For a 2048-bit key, pass $maxlength = 245.
     */
    public static function rsaEncrypt($data, string $rsaPublicKey, int $maxlength = 117): string
    {
        $source = is_string($data) ? $data : json_encode($data);
        $output = '';
        while ($source !== '') {
            $chunk  = substr($source, 0, $maxlength);
            $source = substr($source, $maxlength);
            if (!openssl_public_encrypt($chunk, $encrypted, $rsaPublicKey)) {
                throw new RuntimeException('RSA encryption failed for a data chunk.');
            }
            $output .= $encrypted;
        }
        return base64_encode($output);
    }

    /** Canonical hash concatenation orders (see ../references/). */
    public static function order(string $api): array
    {
        $orders = [
            'purchase' => ['req_time','merchant_id','tran_id','amount','items','shipping',
                'firstname','lastname','email','phone','type','payment_option','return_url',
                'cancel_url','continue_success_url','return_deeplink','currency','custom_fields',
                'return_params','payout','lifetime','additional_params','google_pay_token','skip_success_page'],
            'purchase_token' => ['req_time','merchant_id','tran_id','amount','items','shipping',
                'ctid','pwt','firstname','lastname','email','phone','type','return_url','currency',
                'custom_fields','return_params','payout'],
            'check_transaction' => ['req_time','merchant_id','tran_id'],
            'transaction_detail' => ['req_time','merchant_id','tran_id'],
            'transaction_list' => ['req_time','merchant_id','from_date','to_date','from_amount','to_amount','status','page','pagination'],
            'close_transaction' => ['req_time','merchant_id','tran_id'],
            'exchange_rate' => ['req_time','merchant_id'],
            'transactions_by_ref' => ['req_time','merchant_id','merchant_ref'],
            'generate_qr' => ['req_time','merchant_id','tran_id','amount','items','first_name',
                'last_name','email','phone','purchase_type','payment_option','callback_url',
                'return_deeplink','currency','custom_fields','return_params','payout','lifetime','qr_image_template'],
            'link_account' => ['merchant_id','req_time','return_deeplink'],
            'link_card' => ['merchant_id','ctid','return_param'],
            'remove_account_token' => ['merchant_id','req_time','ctid','pwt'],
            'remove_card_token' => ['merchant_id','ctid','pwt'],
            'linked_account_details' => ['merchant_id','req_time','return_param'],
            'refund' => ['request_time','merchant_id','merchant_auth'],
            'payment_link_create' => ['request_time','merchant_id','merchant_auth'],
            'payment_link_detail' => ['request_time','merchant_id','merchant_auth'],
            'pre_auth_complete' => ['merchant_auth','request_time','merchant_id'],
            'pre_auth_complete_payout' => ['merchant_auth','request_time','merchant_id'],
            'pre_auth_cancel' => ['merchant_id','merchant_auth','request_time'],
            'add_beneficiary' => ['request_time','merchant_auth'],
            'update_beneficiary_status' => ['request_time','merchant_auth'],
            'payout' => ['merchant_id','tran_id','beneficiaries','amount','custom_fields','currency'],
        ];
        if (!isset($orders[$api])) {
            throw new InvalidArgumentException("Unknown api '$api'");
        }
        return $orders[$api];
    }

    /** Look up the order for a known API and hash. Payout uses hex output. */
    public static function hashFor(string $api, array $params, string $apiKey): string
    {
        return self::makeHash($params, self::order($api), $apiKey, $api === 'payout');
    }
}

// Minimal self-test when run from CLI: php payway.php
if (PHP_SAPI === 'cli' && isset($argv[0]) && realpath($argv[0]) === __FILE__) {
    $key = 'demo_secret_key';
    $p = [
        'req_time' => '20250728022056', 'merchant_id' => 'ec000002', 'tran_id' => '17536691884',
        'amount' => '0.10', 'firstname' => 'sina', 'lastname' => 'chhum', 'phone' => '093939399',
    ];
    echo "purchase hash (demo key): " . PayWay::hashFor('purchase', $p, $key) . "\n";
    echo "req_time: " . PayWay::reqTime() . "\n";
    echo "OK\n";
}
