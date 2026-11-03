// Offline test of the checkout: PayPal and Resend are simulated, a throwaway RSA key signs.
// Run: npm test   (needs tests/test_private.json, a test key that is NOT the real licence key)
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { createPublicKey, verify } from 'node:crypto';
import { useMemoryStore } from '../netlify/functions/lib/store.mjs';

const priv = fs.readFileSync(new URL('./test_private.json', import.meta.url), 'utf8');
Object.assign(process.env, { PAYPAL_CLIENT_ID: 'test-id', PAYPAL_CLIENT_SECRET: 'test-secret', PAYPAL_ENV: 'sandbox',
  LICENSE_PRIVATE_KEY: priv, RESEND_API_KEY: 're_test', OWNER_EMAIL: 'owner@example.com' });
const mem = useMemoryStore();

let amount = '29.99', mails = [], captureCalls = 0, declined = false;
globalThis.fetch = async (url, opts = {}) => {
  const j = (d, s = 200) => new Response(JSON.stringify(d), { status: s, headers: { 'Content-Type': 'application/json' } });
  if (url.endsWith('/v1/oauth2/token')) return j({ access_token: 'tok' });
  if (url.endsWith('/v2/checkout/orders') && opts.method === 'POST') {
    const b = JSON.parse(opts.body); assert.equal(b.purchase_units[0].amount.value, '29.99'); assert.equal(b.purchase_units[0].amount.currency_code, 'EUR');
    return j({ id: 'ORDER' + Math.floor(Math.random() * 1e9) }, 201);
  }
  if (url.includes('/capture')) {
    captureCalls++;
    if (declined) return j({ details: [{ issue: 'INSTRUMENT_DECLINED' }] }, 422);
    return j({ status: 'COMPLETED', payment_source: { paypal: { email_address: 'buyer@example.com', name: { given_name: 'Jane', surname: 'Doe' } } },
      purchase_units: [{ payments: { captures: [{ id: 'CAP123456789', status: 'COMPLETED', amount: { currency_code: 'EUR', value: amount } }] } }] }, 201);
  }
  if (url === 'https://api.resend.com/emails') { mails.push(JSON.parse(opts.body)); return j({ id: 'mail' }); }
  throw new Error('unexpected fetch ' + url);
};

const { default: create } = await import('../netlify/functions/create-order.mjs');
const { default: capture } = await import('../netlify/functions/capture-order.mjs');
const { default: cfg } = await import('../netlify/functions/config.mjs');
const call = async (fn, body) => { const r = await fn(new Request('https://x/api', { method: 'POST', body: JSON.stringify(body) })); return { status: r.status, data: await r.json() }; };

// config
assert.deepEqual((await (await cfg()).json()).ready, true);
// validation
assert.equal((await call(create, { name: 'J', consent: true })).status, 400);
assert.equal((await call(create, { name: 'Jane Doe', consent: false })).status, 400);
// happy path
const o = await call(create, { name: '  Dr. Jürgen   Müller ', consent: true }); assert.equal(o.status, 200);
const c1 = await call(capture, { orderID: o.data.id }); assert.equal(c1.status, 200, JSON.stringify(c1.data));
assert.ok(c1.data.key.startsWith('DQM1.')); assert.equal(c1.data.email, 'buyer@example.com'); assert.equal(c1.data.emailSent, true);
const [, p, s] = c1.data.key.split('.'); const dec = (x) => Buffer.from(x.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
const payload = JSON.parse(dec(p).toString()); assert.equal(payload.customer, 'Dr. Jürgen Müller'); assert.equal(payload.product, 'deepq-manuscript');
const pub = createPublicKey(fs.readFileSync(new URL('./test.pem', import.meta.url)));
assert.ok(verify('sha256', dec(p), pub, dec(s)), 'signature must verify');
assert.equal(mails.length, 2); assert.equal(mails[0].to[0], 'buyer@example.com'); assert.ok(mails[0].text.includes(c1.data.key)); assert.ok(mails[0].text.includes('§ 19 UStG'));
// idempotent: second call returns same key without capturing again
const before = captureCalls; const c2 = await call(capture, { orderID: o.data.id });
assert.equal(c2.data.key, c1.data.key); assert.equal(captureCalls, before); assert.equal(mails.length, 2);
// wrong amount is rejected
amount = '0.01'; const o2 = await call(create, { name: 'Cheap Trick', consent: true });
assert.equal((await call(capture, { orderID: o2.data.id })).status, 402); amount = '29.99';
// declined card
declined = true; const o3 = await call(create, { name: 'Declined Person', consent: true });
const d3 = await call(capture, { orderID: o3.data.id }); assert.equal(d3.status, 402); assert.match(d3.data.error, /declined/); declined = false;
// unknown order
assert.equal((await call(capture, { orderID: 'NOTEXISTING1' })).status, 404);
console.log('All checkout tests passed. Stored orders:', mem.map.size);
