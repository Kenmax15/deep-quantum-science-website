// Order records live in Cloudflare KV (binding ORDERS) on Cloudflare Pages, or in Netlify Blobs
// (store "orders") on Netlify. Tests can inject a memory store.
let injected = null;
export function useKV(kv) {
  injected = { get: (k) => kv.get(k, { type: 'json' }), set: (k, v) => kv.put(k, JSON.stringify(v)) };
  return injected;
}
export function useMemoryStore(map = new Map()) {
  injected = {
    get: async (k) => (map.has(k) ? JSON.parse(map.get(k)) : null),
    set: async (k, v) => { map.set(k, JSON.stringify(v)); },
    map,
  };
  return injected;
}
export async function orders() {
  if (injected) return injected;
  const pkg = '@netlify/blobs'; // not bundled on Cloudflare (non-literal import)
  const { getStore } = await import(pkg);
  const s = getStore({ name: 'orders', consistency: 'strong' });
  return { get: (k) => s.get(k, { type: 'json' }), set: (k, v) => s.setJSON(k, v) };
}
