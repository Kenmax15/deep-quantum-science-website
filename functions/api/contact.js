// POST /api/contact — contact form of the homepage (Cloudflare Pages Function).
//
// Server-side checks (the browser checks are only a convenience):
//   • required fields, lengths, email syntax, consent to the privacy policy
//   • anti-spam: hidden honeypot field, minimum time on the page, link limit,
//     (a form older than 24 h gets a real "stale" answer so a person can resend;
//     only the honeypot and the too-fast case answer a silent "ok"),
//     and at most 5 messages per hour per visitor (IP address stored only as a
//     salted SHA-256 hash, for one hour, in the KV namespace bound as ORDERS)
// The message is emailed to OWNER_EMAIL through Resend (RESEND_API_KEY); the
// visitor's address is set as reply-to. No message is stored on the server.

const TOPICS = { project: 'Project', talk: 'Talk or teaching', other: 'Other' };
const MAX = { name: 100, email: 254, org: 120, message: 5000 };
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]+@[^\s@<>()[\]\\,;:"]+\.[^\s@<>()[\]\\,;:"]{2,}$/;
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

async function sha256(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export async function onRequestPost({ request, env }) {
  let data;
  try {
    const type = request.headers.get('Content-Type') || '';
    data = type.includes('application/json') ? await request.json() : Object.fromEntries(await request.formData());
  } catch {
    return json({ ok: false, error: 'bad_request' }, 400);
  }
  const f = {
    name: String(data.name || '').trim(),
    email: String(data.email || '').trim(),
    org: String(data.org || '').trim(),
    message: String(data.message || '').trim(),
    consent: data.consent === true || data.consent === 'on' || data.consent === 'true',
    website: String(data.website || ''),          // honeypot: humans never see it
    t: Number(data.t || 0),                      // when the form was shown (ms)
    lang: data.lang === 'de' ? 'de' : 'en',
    topic: TOPICS[data.topic] ? data.topic : 'project',
  };

  // Spam traps: answer "ok" so bots learn nothing, but send nothing.
  const age = Date.now() - f.t;
  if (f.website || !f.t || age < 3000) return json({ ok: true });
  // A form left open for more than a day: tell the visitor, the browser refreshes the timestamp.
  if (age > 24 * 3600 * 1000) return json({ ok: false, error: 'stale' }, 409);
  if ((f.message.match(/https?:\/\//gi) || []).length > 3) return json({ ok: false, error: 'too_many_links' }, 422);

  const errors = {};
  if (f.name.length < 2 || f.name.length > MAX.name) errors.name = 'invalid';
  if (!EMAIL_RE.test(f.email) || f.email.length > MAX.email) errors.email = 'invalid';
  if (f.org.length > MAX.org) errors.org = 'invalid';
  if (f.message.length < 10 || f.message.length > MAX.message) errors.message = 'invalid';
  if (!f.consent) errors.consent = 'required';
  if (Object.keys(errors).length) return json({ ok: false, error: 'validation', fields: errors }, 422);

  // Rate limit: 5 messages per hour per visitor.
  if (env.ORDERS) {
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    const hour = new Date().toISOString().slice(0, 13);
    const key = 'rl:contact:' + (await sha256((env.RATE_SALT || 'dqs') + ip + hour));
    const n = Number((await env.ORDERS.get(key)) || 0);
    if (n >= 5) return json({ ok: false, error: 'rate_limited' }, 429);
    await env.ORDERS.put(key, String(n + 1), { expirationTtl: 3600 });
  }

  if (!env.RESEND_API_KEY || !env.OWNER_EMAIL) return json({ ok: false, error: 'unavailable' }, 503);
  const subject = `Website enquiry [${TOPICS[f.topic]}] from ${f.name}${f.org ? ' (' + f.org + ')' : ''}`;
  const text = `Topic: ${TOPICS[f.topic]}\nName: ${f.name}\nEmail: ${f.email}\nOrganisation: ${f.org || '-'}\nLanguage: ${f.lang}\n` +
    `Consent to privacy policy: yes (${new Date().toISOString()})\n\n${f.message}\n`;
  const html = `<div style="font-family:Segoe UI,Arial,sans-serif;line-height:1.55;color:#15113a">
<p><b>Topic:</b> ${TOPICS[f.topic]}<br><b>Name:</b> ${esc(f.name)}<br><b>Email:</b> ${esc(f.email)}<br><b>Organisation:</b> ${esc(f.org || '-')}<br>
<b>Language:</b> ${f.lang} · consent to privacy policy given</p>
<pre style="white-space:pre-wrap;font:15px/1.55 Segoe UI,Arial,sans-serif">${esc(f.message)}</pre></div>`;
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + env.RESEND_API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: env.CONTACT_FROM || 'Deep Quantum Science Website <licence@deep-quantum-science.com>',
      to: [env.OWNER_EMAIL], reply_to: f.email, subject, text, html,
    }),
  });
  if (!res.ok) return json({ ok: false, error: 'send_failed' }, 502);
  return json({ ok: true });
}

export async function onRequest() {
  return json({ ok: false, error: 'method_not_allowed' }, 405);
}
