// Creates DeepQ Manuscript licence keys exactly like issue_license.py:
//   DQM1.<base64url(payload)>.<base64url(RSA PKCS#1 v1.5 SHA-256 signature)>
// The private key comes from the LICENSE_PRIVATE_KEY environment variable
// (the full contents of private_key.json). It is never sent to the browser.
import { createHash, randomBytes } from 'node:crypto';

const SHA256_PREFIX = Buffer.from('3031300d060960864801650304020105000420', 'hex');

// json.dumps(obj, sort_keys=True, separators=(',',':')) with Python's default ensure_ascii=True
export function pyJson(obj) {
  const esc = (s) => JSON.stringify(s).replace(/[\u007f-￿]/g, (c) => {
    const code = c.charCodeAt(0);
    return code === 0x7f ? c : '\\u' + code.toString(16).padStart(4, '0');
  });
  const keys = Object.keys(obj).sort();
  return '{' + keys.map((k) => esc(k) + ':' + esc(String(obj[k]))).join(',') + '}';
}

// datetime.now(timezone.utc).isoformat()
export function pyIsoNow(date = new Date()) {
  const p = (n, l = 2) => String(n).padStart(l, '0');
  return `${date.getUTCFullYear()}-${p(date.getUTCMonth() + 1)}-${p(date.getUTCDate())}T` +
    `${p(date.getUTCHours())}:${p(date.getUTCMinutes())}:${p(date.getUTCSeconds())}` +
    (date.getUTCMilliseconds() ? `.${p(date.getUTCMilliseconds(), 3)}000` : '') + '+00:00';
}

const b64url = (buf) => Buffer.from(buf).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

function modPow(base, exp, mod) {
  let result = 1n; base %= mod;
  while (exp > 0n) {
    if (exp & 1n) result = (result * base) % mod;
    base = (base * base) % mod;
    exp >>= 1n;
  }
  return result;
}

export function signPayload(payload, privateKey) {
  const n = BigInt('0x' + privateKey.n), d = BigInt('0x' + privateKey.d);
  const size = Math.ceil(n.toString(2).length / 8);
  const digest = Buffer.concat([SHA256_PREFIX, createHash('sha256').update(payload).digest()]);
  const em = Buffer.concat([Buffer.from([0x00, 0x01]), Buffer.alloc(size - digest.length - 3, 0xff), Buffer.from([0x00]), digest]);
  const sig = modPow(BigInt('0x' + em.toString('hex')), d, n).toString(16).padStart(size * 2, '0');
  return Buffer.from(sig, 'hex');
}

export function issueLicence(privateKey, customer, { licenseId, issuedAt } = {}) {
  customer = String(customer || '').trim();
  if (customer.length < 1 || customer.length > 200) throw new Error('Customer name must be 1 to 200 characters.');
  const payload = Buffer.from(pyJson({
    product: 'deepq-manuscript', edition: 'full', key_id: privateKey.key_id,
    license_id: licenseId || randomBytes(16).toString('hex'), customer,
    issued_at: issuedAt || pyIsoNow(),
  }), 'utf8');
  return 'DQM1.' + b64url(payload) + '.' + b64url(signPayload(payload, privateKey));
}

export function loadPrivateKey() {
  const raw = process.env.LICENSE_PRIVATE_KEY;
  if (!raw) throw new Error('LICENSE_PRIVATE_KEY is not configured.');
  let key;
  try { key = JSON.parse(raw); }
  catch { throw new Error('LICENSE_PRIVATE_KEY is not valid JSON (it must be the full contents of private_key.json, starting with {).'); }
  if (!key.n || !key.d || !key.key_id) throw new Error('LICENSE_PRIVATE_KEY is incomplete.');
  return key;
}
