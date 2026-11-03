// Sends emails through the Resend HTTP API.
export async function sendMail({ to, subject, text, html, replyTo }) {
  const key = process.env.RESEND_API_KEY;
  if (!key) throw new Error('RESEND_API_KEY is not configured.');
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: process.env.MAIL_FROM || 'DeepQ Manuscript <licence@deep-quantum-science.com>',
      to: Array.isArray(to) ? to : [to], subject, text, html,
      reply_to: replyTo || process.env.OWNER_EMAIL || undefined,
    }),
  });
  if (!res.ok) throw new Error('Email could not be sent (' + res.status + '): ' + (await res.text()).slice(0, 200));
  return res.json();
}

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Licence email with a simplified invoice (Kleinbetragsrechnung, § 33 UStDV).
export function licenceEmail({ name, key, date, receipt, captureId }) {
  const seller = 'Dr. Maseim Bassis Kenmoe · Deep Quantum Science Consulting · Prüfeninger Str. 121 · 93049 Regensburg · Germany';
  const text = `Thank you for buying DeepQ Manuscript.

Your licence key (licensed to: ${name}):

${key}

How to activate:
1. Open DeepQ Manuscript.
2. Click "Enter licence key".
3. Paste the complete key and click "Activate". No internet connection is needed.

Download: https://deep-quantum-science.com/manuscript.html#trial

RECEIPT ${receipt}
Date: ${date}
1 × DeepQ Manuscript licence (1 user, perpetual) — 29,99 EUR
Total paid: 29,99 EUR via PayPal (transaction ${captureId})
Gemäß § 19 UStG wird keine Umsatzsteuer berechnet. / No VAT is charged under § 19 UStG (small business).

Seller: ${seller}
Terms of sale: https://deep-quantum-science.com/terms.html

Questions? Just reply to this email.
`;
  const html = `<div style="font-family:Segoe UI,Arial,sans-serif;color:#15113a;max-width:600px;line-height:1.55">
<h2 style="margin:0 0 12px">Thank you for buying DeepQ Manuscript</h2>
<p>Your licence key, licensed to <b>${esc(name)}</b>:</p>
<pre style="white-space:pre-wrap;word-break:break-all;background:#f1f4fa;border:1px solid #d8dbeb;border-radius:8px;padding:12px;font-size:12px">${esc(key)}</pre>
<p><b>How to activate:</b> open DeepQ Manuscript, click <i>Enter licence key</i>, paste the complete key and click <i>Activate</i>. No internet connection is needed.</p>
<p><a href="https://deep-quantum-science.com/manuscript.html#trial">Download DeepQ Manuscript</a></p>
<hr style="border:0;border-top:1px solid #d8dbeb;margin:20px 0">
<p style="font-size:13px"><b>Receipt ${esc(receipt)}</b> · ${esc(date)}<br>
1 × DeepQ Manuscript licence (1 user, perpetual) — 29,99 EUR<br>
Total paid: 29,99 EUR via PayPal (transaction ${esc(captureId)})<br>
Gemäß § 19 UStG wird keine Umsatzsteuer berechnet. / No VAT is charged under § 19 UStG (small business).</p>
<p style="font-size:12px;color:#585676">Seller: ${esc(seller)}<br><a href="https://deep-quantum-science.com/terms.html">Terms of sale</a> · Questions? Just reply to this email.</p></div>`;
  return { subject: 'Your DeepQ Manuscript licence key', text, html };
}
