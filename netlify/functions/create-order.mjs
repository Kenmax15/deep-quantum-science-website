// POST /api/create-order {name} -> {id}
import { createOrder } from './lib/paypal.mjs';
import { orders } from './lib/store.mjs';

export default async (req) => {
  if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 });
  let body = {};
  try { body = await req.json(); } catch {}
  const name = String(body.name || '').trim().replace(/\s+/g, ' ');
  if (name.length < 2 || name.length > 200) return Response.json({ error: 'Please enter the name for your licence (2 to 200 characters).' }, { status: 400 });
  if (body.consent !== true) return Response.json({ error: 'Please accept the terms of sale first.' }, { status: 400 });
  try {
    const r = await createOrder();
    if (!r.ok || !r.data.id) {
      console.error('create-order failed', r.status, JSON.stringify(r.data).slice(0, 500));
      return Response.json({ error: 'PayPal is not available right now. Please try again in a few minutes.' }, { status: 502 });
    }
    const store = await orders();
    await store.set(r.data.id, { status: 'created', name, consentAt: new Date().toISOString(), createdAt: new Date().toISOString() });
    return Response.json({ id: r.data.id });
  } catch (e) {
    console.error('create-order error', e);
    return Response.json({ error: 'Checkout is not available right now. Please order by email instead.' }, { status: 500 });
  }
};
export const config = { path: '/api/create-order' };
