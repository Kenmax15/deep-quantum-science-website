// GET /api/config -> public checkout settings (the PayPal Client ID is public by design).
export default async () => {
  const clientId = process.env.PAYPAL_CLIENT_ID;
  const ready = Boolean(clientId && process.env.PAYPAL_CLIENT_SECRET && process.env.LICENSE_PRIVATE_KEY);
  return Response.json({ ready, clientId: ready ? clientId : null, sandbox: process.env.PAYPAL_ENV !== 'live' },
    { headers: { 'Cache-Control': 'no-store' } });
};
export const config = { path: '/api/config' };
