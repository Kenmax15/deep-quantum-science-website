// Minimal PayPal Orders v2 client (no SDK). Credentials come from environment variables.
const BASE = () => (process.env.PAYPAL_ENV === 'live' ? 'https://api-m.paypal.com' : 'https://api-m.sandbox.paypal.com');

export const PRICE = { value: '29.99', currency_code: 'EUR' };

async function accessToken() {
  const id = process.env.PAYPAL_CLIENT_ID, secret = process.env.PAYPAL_CLIENT_SECRET;
  if (!id || !secret) throw new Error('PayPal credentials are not configured.');
  const res = await fetch(BASE() + '/v1/oauth2/token', {
    method: 'POST',
    headers: { Authorization: 'Basic ' + Buffer.from(id + ':' + secret).toString('base64'), 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'grant_type=client_credentials',
  });
  if (!res.ok) throw new Error('PayPal authentication failed (' + res.status + ').');
  return (await res.json()).access_token;
}

async function call(path, { method = 'GET', body, requestId } = {}) {
  const token = await accessToken();
  const headers = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };
  if (requestId) headers['PayPal-Request-Id'] = requestId;
  const res = await fetch(BASE() + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

export function createOrder() {
  return call('/v2/checkout/orders', {
    method: 'POST',
    body: {
      intent: 'CAPTURE',
      purchase_units: [{
        description: 'DeepQ Manuscript licence (1 user)',
        amount: { ...PRICE, breakdown: { item_total: PRICE } },
        items: [{ name: 'DeepQ Manuscript licence', description: 'Perpetual licence for one user', quantity: '1', unit_amount: PRICE, category: 'DIGITAL_GOODS' }],
      }],
      payment_source: { paypal: { experience_context: { brand_name: 'Deep Quantum Science', shipping_preference: 'NO_SHIPPING', user_action: 'PAY_NOW' } } },
    },
  });
}

export const captureOrder = (id) => call(`/v2/checkout/orders/${encodeURIComponent(id)}/capture`, { method: 'POST', requestId: 'capture-' + id });
export const getOrder = (id) => call(`/v2/checkout/orders/${encodeURIComponent(id)}`);

// Returns the completed capture if the order was paid in full, otherwise null.
export function paidCapture(order) {
  const unit = order?.purchase_units?.[0];
  const cap = unit?.payments?.captures?.[0];
  if (!cap || cap.status !== 'COMPLETED') return null;
  if (cap.amount?.currency_code !== PRICE.currency_code || cap.amount?.value !== PRICE.value) return null;
  return cap;
}

export function payerOf(order) {
  const p = order?.payment_source?.paypal || {};
  const email = p.email_address || order?.payer?.email_address || '';
  const n = p.name || order?.payer?.name || {};
  return { email, name: [n.given_name, n.surname].filter(Boolean).join(' ') };
}
