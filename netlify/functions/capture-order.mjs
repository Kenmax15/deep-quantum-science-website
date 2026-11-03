// POST /api/capture-order {orderID} -> {key, email}
// Captures the PayPal payment, checks the amount, creates the licence key,
// emails it to the buyer and the owner, and stores the order. Safe to call twice.
import { captureOrder, getOrder, paidCapture, payerOf } from './lib/paypal.mjs';
import { issueLicence, loadPrivateKey } from './lib/licence.mjs';
import { sendMail, licenceEmail } from './lib/mail.mjs';
import { orders } from './lib/store.mjs';

const fail = (error, status = 400) => Response.json({ error }, { status });

export default async (req) => {
  if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 });
  let body = {};
  try { body = await req.json(); } catch {}
  const id = String(body.orderID || '');
  if (!/^[A-Z0-9]{5,40}$/.test(id)) return fail('Invalid order.');

  const store = await orders();
  const record = await store.get(id);
  if (!record) return fail('This order is unknown. Please start again.', 404);
  if (record.status === 'completed') return Response.json({ key: record.key, email: record.email, emailSent: record.emailSent });

  // Capture (idempotent at PayPal thanks to the PayPal-Request-Id header).
  let r = await captureOrder(id);
  if (!r.ok && r.data?.details?.[0]?.issue === 'ORDER_ALREADY_CAPTURED') r = await getOrder(id);
  if (!r.ok) {
    console.error('capture failed', id, r.status, JSON.stringify(r.data).slice(0, 500));
    const declined = r.data?.details?.[0]?.issue === 'INSTRUMENT_DECLINED';
    return fail(declined ? 'PayPal declined the payment method. Please choose another one.' : 'The payment could not be completed. You have not been charged.', 402);
  }
  const cap = paidCapture(r.data);
  if (!cap) {
    console.error('payment not completed or wrong amount', id, JSON.stringify(r.data).slice(0, 500));
    return fail('The payment is not complete yet. If money was taken, please contact us and we will send your key.', 402);
  }

  const payer = payerOf(r.data);
  const name = record.name || payer.name || 'DeepQ Manuscript customer';
  let key;
  try { key = issueLicence(loadPrivateKey(), name); }
  catch (e) {
    console.error('licence error', e);
    await store.set(id, { ...record, status: 'paid-no-key', captureId: cap.id, email: payer.email, paidAt: new Date().toISOString() });
    return fail('Payment received, but the key could not be created automatically. We will email it to you shortly.', 500);
  }

  const now = new Date();
  const date = now.toISOString().slice(0, 10);
  const receipt = 'DQM-' + date.replace(/-/g, '') + '-' + cap.id.slice(-6);
  const done = { ...record, status: 'completed', key, email: payer.email, payerName: payer.name, captureId: cap.id, receipt, amount: cap.amount, paidAt: now.toISOString(), emailSent: false };
  await store.set(id, done);

  // Emails: buyer first, then a short notice to the owner. Failures do not hide the key.
  if (payer.email) {
    try {
      await sendMail({ to: payer.email, ...licenceEmail({ name, key, date, receipt, captureId: cap.id }) });
      done.emailSent = true;
      await store.set(id, done);
    } catch (e) { console.error('buyer email failed', id, e.message); }
  }
  if (process.env.OWNER_EMAIL) {
    try {
      await sendMail({ to: process.env.OWNER_EMAIL, subject: `New sale: DeepQ Manuscript (${receipt})`,
        text: `Licence sold to ${name} <${payer.email}>\nPayPal transaction: ${cap.id}\nReceipt: ${receipt}\nBuyer email sent: ${done.emailSent ? 'yes' : 'NO - please send the key manually'}\n\nKey:\n${key}\n` });
    } catch (e) { console.error('owner email failed', id, e.message); }
  }
  return Response.json({ key, email: payer.email, emailSent: done.emailSent });
};
export const config = { path: '/api/capture-order' };
