// Cloudflare Pages: copy the project's variables and secrets into process.env (read by the shared
// checkout code in netlify/functions/lib) and use the KV namespace bound as ORDERS for order records.
import { useKV } from '../../netlify/functions/lib/store.mjs';
export function wrap(handler) {
  return async (ctx) => {
    for (const [k, v] of Object.entries(ctx.env)) if (typeof v === 'string') process.env[k] = v;
    if (!ctx.env.ORDERS) return Response.json({ error: 'Checkout is not available right now. Please order by email instead.' }, { status: 503 });
    useKV(ctx.env.ORDERS);
    return handler(ctx.request);
  };
}
