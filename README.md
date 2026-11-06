# Deep Quantum Science website

Website of Deep Quantum Science Consulting (https://deep-quantum-science.com) with automatic
licence sales for **DeepQ Manuscript** (29,99 €, PayPal).

## Structure

| Path | What it is |
|---|---|
| `site/` | The published website (HTML, fonts, images). No build step. |
| `netlify/functions/` | Serverless checkout: `config`, `create-order`, `capture-order`. |
| `netlify/functions/lib/licence.mjs` | Creates `DQM1.` licence keys exactly like `issue_license.py` (RSA-3072, SHA-256). |
| `tests/` | Offline test of the checkout with a **throwaway test key** (not the real licence key). Run `npm test`. |

## How a sale works

1. The buyer enters the licence name, accepts the terms and clicks **Continue to payment**; only then is PayPal loaded.
2. `create-order` creates a PayPal order for exactly 29.99 EUR.
3. After payment, `capture-order` captures it, checks amount and currency, creates the licence key,
   shows it on the page, emails it with a receipt (§ 19 UStG) via Resend, and notifies the owner.
   Orders are stored in Netlify Blobs (store `orders`). Calling it twice never charges twice.

## Environment variables (Netlify → Project configuration → Environment variables)

| Name | Value | Secret? |
|---|---|---|
| `PAYPAL_ENV` | `sandbox` for testing, `live` for real sales | no |
| `PAYPAL_CLIENT_ID` | from developer.paypal.com → Apps & Credentials | no |
| `PAYPAL_CLIENT_SECRET` | from the same PayPal app | **yes** |
| `LICENSE_PRIVATE_KEY` | the complete contents of `private_key.json` | **yes** |
| `RESEND_API_KEY` | Resend → API keys (sending access, domain deep-quantum-science.com) | **yes** |
| `MAIL_FROM` | `DeepQ Manuscript <licence@deep-quantum-science.com>` | no |
| `OWNER_EMAIL` | where sale notifications go, also the reply-to address | no |

Never commit `private_key.json` or any secret to this repository.

## Hosting on Cloudflare Pages

The same site and checkout also run on Cloudflare Pages (free, unlimited deploys):

- Build output directory: `site` (no build command). `wrangler.toml` sets `nodejs_compat`.
- `functions/api/*.js` wrap the checkout handlers above; Cloudflare passes the project's
  variables and secrets (same names as in the table) into them.
- Orders are stored in a KV namespace bound as `ORDERS` instead of Netlify Blobs.
- Headers come from `site/_headers`.
