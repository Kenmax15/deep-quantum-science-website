// Order records live in Netlify Blobs (store "orders"). Tests can inject a memory store.
let injected = null;
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
  const { getStore } = await import('@netlify/blobs');
  const s = getStore({ name: 'orders', consistency: 'strong' });
  return { get: (k) => s.get(k, { type: 'json' }), set: (k, v) => s.setJSON(k, v) };
}
