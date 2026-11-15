"""Builds the legal pages (privacy policy, terms, legal notice) and the 404 page
in English and German, with the site's look, a language switch and a footer.

    python3 tools/build_legal.py && python3 tools/site_polish.py

Edit the texts below, then run both commands. Dates: UPDATED.
"""
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent / 'site'
UPDATED = ('14 November 2026', '14. November 2026')
OWNER = 'Dr. Maseim Bassis Kenmoe, Deep Quantum Science Consulting, Regensburg'
MAIL = '<a href="mailto:deepqscience@gmail.com">deepqscience@gmail.com</a>'


def bi(en, de):
    return f'<span class="en">{en}</span><span class="de">{de}</span>'


def block(en, de):
    """Paragraph-level bilingual content (block elements inside)."""
    return f'<div class="en">{en}</div><div class="de">{de}</div>'


CSS = """
@font-face{font-family:"Alegreya";src:url("/assets/fonts/alegreya.woff2") format("woff2");font-weight:500 600;font-style:normal;font-display:swap}
@font-face{font-family:"IBM Plex Sans";src:url("/assets/fonts/plex-sans.woff2") format("woff2");font-weight:400 600;font-style:normal;font-display:swap}
@font-face{font-family:"IBM Plex Mono";src:url("/assets/fonts/plex-mono-500.woff2") format("woff2");font-weight:500;font-style:normal;font-display:swap}
:root{color-scheme:dark;--navy:#0e082c;--panel:#16103f;--rule:#2a2360;--text:#ecf5f3;--muted:#b3afd6;--mint:#92ffd8;--p:#d4d8ea}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--navy:#f8f9fc;--panel:#ffffff;--rule:#d8dbeb;--text:#15113a;--muted:#55536f;--mint:#0a7462;--p:#34375a;color-scheme:light}}
:root[data-theme="light"]{--navy:#f8f9fc;--panel:#ffffff;--rule:#d8dbeb;--text:#15113a;--muted:#55536f;--mint:#0a7462;--p:#34375a;color-scheme:light}
:root:not([data-lang="de"]) .de{display:none!important}
:root[data-lang="de"] .en{display:none!important}
*{box-sizing:border-box}
body{margin:0;background:var(--navy);color:var(--text);font:400 16px/1.7 "IBM Plex Sans","Segoe UI",system-ui,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:40px max(20px,env(safe-area-inset-left,0px)) 64px}
a{color:var(--mint)}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px}
.back{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:var(--muted);font:500 13px/1 "IBM Plex Mono",monospace;letter-spacing:.08em}
.back img{width:28px;height:auto}
.lang{display:inline-flex;border:1px solid var(--rule);border-radius:999px;padding:3px}
.lang button{border:0;background:transparent;color:var(--muted);font:500 12px/1 "IBM Plex Mono",monospace;padding:8px 11px;border-radius:999px;cursor:pointer;min-width:44px;min-height:32px}
.lang button[aria-pressed="true"]{background:var(--panel);color:var(--text)}
h1{font:500 clamp(32px,5vw,50px)/1.12 "Alegreya",Georgia,serif;margin:36px 0 24px}
h2{font:600 21px/1.3 "Alegreya",Georgia,serif;margin:34px 0 8px}
p,li{color:var(--p)}
.box{padding:14px 16px;border:1px solid var(--rule);border-radius:10px}
.note{margin-top:44px;padding-top:18px;border-top:1px solid var(--rule);font-size:14px;color:var(--muted)}
footer{border-top:1px solid var(--rule);margin-top:20px}
footer .wrap{padding-top:22px;padding-bottom:28px;display:flex;flex-wrap:wrap;gap:12px 22px;font-size:14px;color:var(--muted)}
footer .legal{display:flex;flex-wrap:wrap;gap:8px 18px}
footer a{color:var(--muted);text-decoration:underline;text-underline-offset:3px}
footer a:hover{color:var(--text)}
:focus-visible{outline:2px solid var(--mint);outline-offset:3px;border-radius:4px}
.big{font:500 clamp(80px,16vw,150px)/1 "Alegreya",Georgia,serif;color:var(--mint);margin:30px 0 0}
.btn{display:inline-flex;align-items:center;min-height:46px;padding:0 22px;border-radius:999px;font-weight:600;text-decoration:none;border:1px solid var(--rule);color:var(--text);margin:6px 10px 0 0}
.btn.primary{background:var(--text);color:var(--navy);border-color:var(--text)}
"""

JS = """<script>
(function(){var r=document.documentElement;function s(l){r.dataset.lang=l;r.lang=l;document.querySelectorAll('.lang button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.lang===l))});try{localStorage.setItem('dqs-lang',l)}catch(e){}}
var v=null;try{v=localStorage.getItem('dqs-lang')}catch(e){}s(v==='de'?'de':'en');
document.querySelectorAll('.lang button').forEach(function(b){b.addEventListener('click',function(){s(b.dataset.lang)})});
var y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();})();
</script>"""


def page(slug, title, desc, body, robots=None):
    head_robots = f'\n<meta name="robots" content="{robots}">' if robots else ''
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Deep Quantum Science</title>
<meta name="description" content="{desc}">{head_robots}
<script>try{{var t=localStorage.getItem("dqs-theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t;var l=localStorage.getItem("dqs-lang");if(l==="de")document.documentElement.dataset.lang="de"}}catch(e){{}}</script>
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="top">
  <a class="back" href="/"><img src="/assets/logo-nav.webp" alt="" width="28" height="30">DEEP QUANTUM SCIENCE</a>
  <div class="lang" role="group" aria-label="Language / Sprache"><button type="button" data-lang="en" aria-pressed="true">EN</button><button type="button" data-lang="de" aria-pressed="false">DE</button></div>
</div>
<main>
{body}
</main>
</div>
<footer><div class="wrap">
  <span>© <span id="year">2026</span> Deep Quantum Science Consulting · Regensburg</span>
  <div class="legal"><a href="/">{bi('Home', 'Startseite')}</a><a href="/impressum">{bi('Legal notice', 'Impressum')}</a><a href="/terms">{bi('Terms', 'AGB')}</a><a href="/datenschutz">{bi('Privacy', 'Datenschutz')}</a></div>
</div></footer>
{JS}
</body>
</html>
"""


# ------------------------------------------------------------------ privacy
PRIVACY = f"""
<h1>{bi('Privacy policy', 'Datenschutzerklärung')}</h1>
{block(f'''
<h2>1. Who is responsible</h2>
<p>{OWNER}, Germany. Email: {MAIL}. We have not appointed a data protection officer, as we are not required to.</p>
<h2>2. Hosting and server log files</h2>
<p>This website runs on Cloudflare Pages (Cloudflare, Inc., 101 Townsend St, San Francisco, CA 94107, USA). When you visit the site, Cloudflare processes technically necessary data: IP address, date and time, the page requested, referrer and browser type. This is needed to deliver the site securely and to protect it against attacks (legal basis: Art. 6(1)(f) GDPR, our legitimate interest in a secure, stable website). Cloudflare deletes these logs after a short period under its own retention rules. Cloudflare participates in the EU-U.S. Data Privacy Framework; transfers to the USA rely on the European Commission's adequacy decision (Art. 45 GDPR). Cloudflare also hides our email address from spam robots on the page. More: <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener">Cloudflare privacy policy</a>.</p>
<p>All connections are encrypted (HTTPS/TLS).</p>
<h2>3. Cookies, local storage and your consent</h2>
<p>This website sets <b>no cookies</b>. In your browser's local storage it keeps only three small settings, which never leave your device: your language (EN/DE), your light/dark choice, and your answer to the consent question. These are strictly necessary for the functions you choose (§ 25(2) no. 2 TDDDG) and need no consent. You can delete them at any time in your browser settings.</p>
<h2>4. Audience measurement (only with your consent)</h2>
<p>If you click “Accept statistics”, we count visits with <b>Cloudflare Web Analytics</b>. It sets no cookies, does not create a profile of you and does not follow you across websites. When the page loads, your browser sends Cloudflare anonymous technical data (page address, referrer, browser type, screen size, loading times); your IP address is used only to deliver the request and is not stored for analytics. We see only aggregated figures (for example, how many people visited a page). Legal basis: your consent, Art. 6(1)(a) GDPR and § 25(1) TDDDG. If you choose “Only necessary”, nothing is loaded. You can change your choice at any time with <a href="#" onclick="window.dqsConsent&&dqsConsent.open();return false">Cookie settings</a> (also at the bottom of every page); withdrawing consent does not affect the lawfulness of earlier processing.</p>
<h2>5. Contact form and email</h2>
<p>If you use the contact form, we process your name, email address, optional organisation and your message to answer your request (Art. 6(1)(b) GDPR for enquiries about our services, otherwise Art. 6(1)(f) GDPR). The form sends your message by email to us through the email service Resend (Resend, Inc., USA; servers in the EU, Ireland), which acts as our processor; Resend is certified under the EU-U.S. Data Privacy Framework. To block spam, a hidden field and the time spent on the form are checked, and the number of messages per visitor is limited; for this a one-way hash of your IP address is kept for one hour and then deleted automatically. We do not store your message on the website; we keep the email only as long as needed to handle your request, unless statutory retention periods apply.</p>
<p>If you email us directly, we process your details in the same way.</p>
<h2>6. Links to social networks</h2>
<p>The site contains plain links to LinkedIn, YouTube and Facebook. No plugins are embedded; data is transferred to the provider only when you click a link, and then the provider's own privacy policy applies.</p>
<h2>7. Software download</h2>
<p>The installer of DeepQ Manuscript is provided via GitHub (GitHub, Inc., USA). When you click the download button, your browser connects directly to GitHub, which processes your IP address and technical data under its own privacy statement. GitHub participates in the EU-U.S. Data Privacy Framework.</p>
<h2>8. Buying a licence online</h2>
<p><b>PayPal.</b> Payments are processed by PayPal (Europe) S.à r.l. et Cie, S.C.A., 22-24 Boulevard Royal, L-2449 Luxembourg. The PayPal button is loaded only after you click “Continue to payment”; from then on PayPal processes your data, may set cookies and may perform a credit check for some payment methods, under its own privacy statement. We receive your name, email address and the transaction details. Legal basis: Art. 6(1)(b) GDPR.</p>
<p><b>Licence and receipt by email.</b> We send your licence key and receipt through Resend (see section 5). Legal basis: Art. 6(1)(b) GDPR.</p>
<p><b>Order records.</b> For each order we store the name on the licence, your email address, the PayPal transaction number, the licence key and the time of your consent with our host Cloudflare. We keep these records as long as tax and commercial law requires (in Germany up to 10 years). Legal basis: Art. 6(1)(b) and (c) GDPR.</p>
<h2>9. Your rights</h2>
<p>You have the right of access, rectification, erasure, restriction of processing, data portability and objection (Art. 15–21 GDPR), and the right to withdraw consent at any time (Art. 7(3) GDPR). You may lodge a complaint with a supervisory authority, for example the Bavarian State Office for Data Protection Supervision (BayLDA), Promenade 18, 91522 Ansbach.</p>
<p class="note">Last updated: {UPDATED[0]}</p>
''', f'''
<h2>1. Verantwortlicher</h2>
<p>{OWNER}, Deutschland. E-Mail: {MAIL}. Ein Datenschutzbeauftragter ist nicht bestellt, da keine Pflicht dazu besteht.</p>
<h2>2. Hosting und Server-Logdateien</h2>
<p>Diese Website wird bei Cloudflare Pages betrieben (Cloudflare, Inc., 101 Townsend St, San Francisco, CA 94107, USA). Beim Aufruf verarbeitet Cloudflare technisch notwendige Daten: IP-Adresse, Datum und Uhrzeit, aufgerufene Seite, Referrer und Browsertyp. Das ist erforderlich, um die Website sicher auszuliefern und vor Angriffen zu schützen (Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO, unser berechtigtes Interesse an einer sicheren und stabilen Website). Cloudflare löscht diese Protokolle nach kurzer Zeit gemäß eigenen Fristen. Cloudflare nimmt am EU-U.S. Data Privacy Framework teil; Übermittlungen in die USA beruhen auf dem Angemessenheitsbeschluss der EU-Kommission (Art. 45 DSGVO). Cloudflare verbirgt außerdem unsere E-Mail-Adresse auf der Seite vor Spam-Robotern. Mehr: <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener">Datenschutzerklärung von Cloudflare</a>.</p>
<p>Alle Verbindungen sind verschlüsselt (HTTPS/TLS).</p>
<h2>3. Cookies, lokaler Speicher und Ihre Einwilligung</h2>
<p>Diese Website setzt <b>keine Cookies</b>. Im lokalen Speicher Ihres Browsers werden nur drei kleine Einstellungen abgelegt, die Ihr Gerät nie verlassen: Ihre Sprache (EN/DE), Ihre Wahl zwischen hellem und dunklem Design und Ihre Antwort auf die Einwilligungsfrage. Sie sind für die von Ihnen gewählten Funktionen unbedingt erforderlich (§ 25 Abs. 2 Nr. 2 TDDDG) und bedürfen keiner Einwilligung. Sie können sie jederzeit in den Browser-Einstellungen löschen.</p>
<h2>4. Reichweitenmessung (nur mit Ihrer Einwilligung)</h2>
<p>Wenn Sie auf „Statistik erlauben“ klicken, zählen wir Besuche mit <b>Cloudflare Web Analytics</b>. Dabei werden keine Cookies gesetzt, kein Profil erstellt und Sie werden nicht über Websites hinweg verfolgt. Beim Laden der Seite übermittelt Ihr Browser anonyme technische Daten an Cloudflare (Seitenadresse, Referrer, Browsertyp, Bildschirmgröße, Ladezeiten); Ihre IP-Adresse wird nur zur Auslieferung verwendet und nicht für die Statistik gespeichert. Wir sehen nur zusammengefasste Zahlen (z. B. wie viele Personen eine Seite besucht haben). Rechtsgrundlage: Ihre Einwilligung, Art. 6 Abs. 1 lit. a DSGVO und § 25 Abs. 1 TDDDG. Wählen Sie „Nur notwendige“, wird nichts geladen. Sie können Ihre Wahl jederzeit über <a href="#" onclick="window.dqsConsent&&dqsConsent.open();return false">Cookie-Einstellungen</a> ändern (auch unten auf jeder Seite); der Widerruf berührt nicht die Rechtmäßigkeit der bis dahin erfolgten Verarbeitung.</p>
<h2>5. Kontaktformular und E-Mail</h2>
<p>Wenn Sie das Kontaktformular nutzen, verarbeiten wir Ihren Namen, Ihre E-Mail-Adresse, die optionale Organisation und Ihre Nachricht, um Ihre Anfrage zu beantworten (Art. 6 Abs. 1 lit. b DSGVO bei Anfragen zu unseren Leistungen, sonst Art. 6 Abs. 1 lit. f DSGVO). Das Formular sendet Ihre Nachricht per E-Mail über den Dienst Resend (Resend, Inc., USA; Server in der EU, Irland) an uns; Resend ist unser Auftragsverarbeiter und nach dem EU-U.S. Data Privacy Framework zertifiziert. Zum Schutz vor Spam werden ein verstecktes Feld und die Verweildauer im Formular geprüft und die Zahl der Nachrichten pro Besucher begrenzt; dazu wird ein nicht umkehrbarer Hashwert Ihrer IP-Adresse eine Stunde lang gespeichert und dann automatisch gelöscht. Ihre Nachricht wird nicht auf der Website gespeichert; die E-Mail bewahren wir nur so lange auf, wie es für die Bearbeitung nötig ist, sofern keine gesetzlichen Aufbewahrungspflichten bestehen.</p>
<p>Schreiben Sie uns direkt eine E-Mail, verarbeiten wir Ihre Angaben auf die gleiche Weise.</p>
<h2>6. Links zu sozialen Netzwerken</h2>
<p>Die Website enthält einfache Links zu LinkedIn, YouTube und Facebook. Es sind keine Plugins eingebunden; Daten gehen erst an den Anbieter, wenn Sie einen Link anklicken, und dann gilt dessen Datenschutzerklärung.</p>
<h2>7. Software-Download</h2>
<p>Das Installationsprogramm von DeepQ Manuscript wird über GitHub bereitgestellt (GitHub, Inc., USA). Wenn Sie auf den Download-Button klicken, verbindet sich Ihr Browser direkt mit GitHub, das Ihre IP-Adresse und technische Daten gemäß eigener Datenschutzerklärung verarbeitet. GitHub nimmt am EU-U.S. Data Privacy Framework teil.</p>
<h2>8. Online-Kauf einer Lizenz</h2>
<p><b>PayPal.</b> Zahlungen wickelt PayPal (Europe) S.à r.l. et Cie, S.C.A., 22-24 Boulevard Royal, L-2449 Luxemburg ab. Der PayPal-Button wird erst geladen, wenn Sie auf „Weiter zur Zahlung“ klicken; ab dann verarbeitet PayPal Ihre Daten, setzt ggf. Cookies und führt bei manchen Zahlarten eine Bonitätsprüfung durch, gemäß eigener Datenschutzerklärung. Wir erhalten Ihren Namen, Ihre E-Mail-Adresse und die Transaktionsdaten. Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO.</p>
<p><b>Lizenz und Beleg per E-Mail.</b> Lizenzschlüssel und Beleg senden wir über Resend (siehe Abschnitt 5). Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO.</p>
<p><b>Bestelldaten.</b> Zu jeder Bestellung speichern wir den Namen auf der Lizenz, Ihre E-Mail-Adresse, die PayPal-Transaktionsnummer, den Lizenzschlüssel und den Zeitpunkt Ihrer Zustimmung bei unserem Hoster Cloudflare, so lange es das Steuer- und Handelsrecht verlangt (in Deutschland bis zu 10 Jahre). Rechtsgrundlage: Art. 6 Abs. 1 lit. b und c DSGVO.</p>
<h2>9. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15–21 DSGVO) sowie das Recht, eine Einwilligung jederzeit zu widerrufen (Art. 7 Abs. 3 DSGVO). Sie können sich bei einer Aufsichtsbehörde beschweren, z. B. beim Bayerischen Landesamt für Datenschutzaufsicht (BayLDA), Promenade 18, 91522 Ansbach.</p>
<p class="note">Stand: {UPDATED[1]}</p>
''')}
"""

# --------------------------------------------------------------- legal notice
IMPRESSUM = f"""
<h1>{bi('Legal notice', 'Impressum')}</h1>
{block(f'''
<h2>Information pursuant to § 5 DDG</h2>
<p>Dr. Maseim Bassis Kenmoe<br>Deep Quantum Science Consulting<br>Regensburg, Germany</p>
<h2>Contact</h2>
<p>Email: {MAIL}<br>Contact form: <a href="/#kontakt">deep-quantum-science.com/#kontakt</a></p>
<h2>VAT</h2>
<p>Small business under § 19 UStG: no VAT is charged.</p>
<h2>Responsible for content (§ 18(2) MStV)</h2>
<p>Dr. Maseim Bassis Kenmoe (contact as above).</p>
<h2>Consumer dispute resolution</h2>
<p>We are neither obliged nor willing to take part in dispute resolution proceedings before a consumer arbitration board.</p>
<h2>Links to other websites</h2>
<p>This website links to external websites (for example LinkedIn, YouTube and Facebook). We have no influence over their content; the respective provider is responsible for it.</p>
''', f'''
<h2>Angaben gemäß § 5 DDG</h2>
<p>Dr. Maseim Bassis Kenmoe<br>Deep Quantum Science Consulting<br>Regensburg, Deutschland</p>
<h2>Kontakt</h2>
<p>E-Mail: {MAIL}<br>Kontaktformular: <a href="/#kontakt">deep-quantum-science.com/#kontakt</a></p>
<h2>Umsatzsteuer</h2>
<p>Kleinunternehmer gemäß § 19 UStG: Es wird keine Umsatzsteuer berechnet.</p>
<h2>Verantwortlich für den Inhalt (§ 18 Abs. 2 MStV)</h2>
<p>Dr. Maseim Bassis Kenmoe (Kontakt wie oben).</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Links auf andere Websites</h2>
<p>Diese Website verlinkt auf externe Websites (z. B. LinkedIn, YouTube und Facebook). Auf deren Inhalte haben wir keinen Einfluss; verantwortlich ist der jeweilige Anbieter.</p>
''')}
"""

# ---------------------------------------------------------------------- terms
WITHDRAW_STATEMENT = ('“I expressly agree that you begin performing the contract before the end of the withdrawal period. I know that I lose my right of withdrawal once performance has begun.”',
                      '„Ich stimme ausdrücklich zu, dass Sie vor Ablauf der Widerrufsfrist mit der Ausführung des Vertrags beginnen. Mir ist bekannt, dass ich mit Beginn der Ausführung mein Widerrufsrecht verliere.“')
TERMS = f"""
<h1>{bi('Terms and conditions', 'Allgemeine Geschäftsbedingungen')}</h1>
{block(f'''
<p>Provider: {OWNER}, Germany, email {MAIL} (“we”). Part A applies to everyone who uses this website; Part B applies to the purchase of DeepQ Manuscript licences. Consulting projects are governed by the individual offer and contract.</p>
<h2>Part A · Use of the website</h2>
<p><b>A1. Content.</b> We prepare the content of this website, including the blog, with care, but it is provided for general information only and is not professional advice for your particular case. We do not guarantee that it is complete, correct or up to date.</p>
<p><b>A2. Copyright.</b> Texts, figures, logos and software on this site are protected by copyright. You may read, print and share links to them for personal and non-commercial purposes. Any other use, in particular copying or republishing content in whole or in part, needs our prior written permission, unless a page states a different licence.</p>
<p><b>A3. Links.</b> We are not responsible for the content of external websites we link to.</p>
<p><b>A4. Contact form.</b> Please do not send confidential information or data about third parties through the contact form. Misuse, such as spam or automated requests, is not permitted.</p>
<p><b>A5. Availability and liability.</b> We try to keep the website available but cannot guarantee uninterrupted operation. Our liability follows section B6.</p>
<h2>Part B · Terms of sale for DeepQ Manuscript</h2>
<p><b>B1. Product.</b> DeepQ Manuscript is Windows software that converts Word documents into LaTeX projects and LaTeX into Word documents. A free trial with 5 conversions per direction can be downloaded from our website. The licence key unlocks unlimited conversions.</p>
<p><b>B2. Conclusion of contract.</b> The presentation of the software on our website is not a binding offer. <i>Online:</i> you enter the name for the licence, accept these terms and click the PayPal payment button. By confirming the payment at PayPal you place a binding order; the contract is concluded when the payment is completed, and we confirm it by showing the licence key and sending it by email. <i>By email:</i> the contract is concluded when we accept your order by sending a payment request and invoice. The contract language is English or German. We store the contract details; you receive them by email.</p>
<p><b>B3. Price and payment.</b> A licence costs €29.99 (one-time). This is the final price. As a small business under § 19 UStG we do not charge VAT. Payment via PayPal, or by bank transfer for orders by email.</p>
<p><b>B4. Delivery.</b> For online purchases your licence key is shown immediately after payment and sent by email with your receipt. For orders by email we send the key after receipt of payment, normally within two working days. The installer is a download; there is no physical delivery.</p>
<p><b>B5. Licence.</b> You receive a non-exclusive, non-transferable right of unlimited duration to use the software for one user. You may not resell, rent out or pass on the licence key, or decompile or modify the software except where the law expressly permits it.</p>
<p><b>B6. Warranty and liability.</b> The statutory warranty rights apply. We are liable without limitation for intent and gross negligence and for injury to life, body or health. For slight negligence we are liable only for breach of essential contractual obligations, limited to the typical, foreseeable damage. Liability under the Product Liability Act remains unaffected. Please keep backups and review every converted document.</p>
<p><b>B7. Final provisions.</b> German law applies. If you are a consumer, this choice of law does not deprive you of the protection of the mandatory provisions of the country where you live. We are neither obliged nor willing to take part in dispute resolution proceedings before a consumer arbitration board.</p>
<h2 id="withdrawal">Withdrawal information</h2>
<p><b>Right of withdrawal.</b> If you are a consumer, you have the right to withdraw from this contract within 14 days without giving any reason. The withdrawal period is 14 days from the day the contract is concluded. To exercise it, inform us ({OWNER}, Germany, email {MAIL}) of your decision by a clear statement, for example an email. You may use the model form below, but it is not obligatory. It is sufficient to send your notice before the period expires.</p>
<p><b>Effects of withdrawal.</b> If you withdraw, we refund all payments received from you without undue delay and at the latest within 14 days of receiving your notice, using the same means of payment, unless expressly agreed otherwise. You will not be charged any fees for this refund.</p>
<p><b>Early expiry.</b> For digital content not supplied on a physical medium, your right of withdrawal expires once we have begun performing the contract (by sending the licence key), provided that you have expressly agreed that we begin before the end of the withdrawal period and have confirmed that you know you lose your right of withdrawal once performance begins. For online purchases you give this consent by ticking the box before payment. For orders by email, include this statement if you want your key immediately:</p>
<p class="box">{WITHDRAW_STATEMENT[0]}</p>
<p><b>Model withdrawal form</b> (complete and return it only if you wish to withdraw):<br>
To: {OWNER}, Germany, deepqscience@gmail.com<br>
I/We hereby give notice that I/we withdraw from my/our contract for the supply of the following digital content: DeepQ Manuscript licence<br>
Ordered on: ________ · Name of consumer(s): ________ · Address of consumer(s): ________<br>
Signature (only if this form is sent on paper): ________ · Date: ________</p>
<p class="note">Last updated: {UPDATED[0]}</p>
''', f'''
<p>Anbieter: {OWNER}, Deutschland, E-Mail {MAIL} („wir“). Teil A gilt für alle, die diese Website nutzen; Teil B gilt für den Kauf von Lizenzen für DeepQ Manuscript. Für Beratungsprojekte gelten das jeweilige Angebot und der jeweilige Vertrag.</p>
<h2>Teil A · Nutzung der Website</h2>
<p><b>A1. Inhalte.</b> Wir erstellen die Inhalte dieser Website, einschließlich des Blogs, mit Sorgfalt. Sie dienen jedoch nur der allgemeinen Information und sind keine fachliche Beratung für Ihren Einzelfall. Für Vollständigkeit, Richtigkeit und Aktualität übernehmen wir keine Gewähr.</p>
<p><b>A2. Urheberrecht.</b> Texte, Abbildungen, Logos und Software auf dieser Website sind urheberrechtlich geschützt. Sie dürfen sie für private und nichtkommerzielle Zwecke lesen, ausdrucken und verlinken. Jede andere Nutzung, insbesondere das ganze oder teilweise Kopieren oder Veröffentlichen, bedarf unserer vorherigen schriftlichen Zustimmung, sofern auf einer Seite keine andere Lizenz angegeben ist.</p>
<p><b>A3. Links.</b> Für die Inhalte verlinkter externer Websites sind wir nicht verantwortlich.</p>
<p><b>A4. Kontaktformular.</b> Bitte senden Sie über das Kontaktformular keine vertraulichen Informationen und keine Daten Dritter. Missbrauch, etwa Spam oder automatisierte Anfragen, ist nicht gestattet.</p>
<p><b>A5. Verfügbarkeit und Haftung.</b> Wir bemühen uns um eine ständige Erreichbarkeit der Website, können einen unterbrechungsfreien Betrieb aber nicht garantieren. Unsere Haftung richtet sich nach Ziffer B6.</p>
<h2>Teil B · Verkaufsbedingungen für DeepQ Manuscript</h2>
<p><b>B1. Produkt.</b> DeepQ Manuscript ist eine Windows-Software, die Word-Dokumente in LaTeX-Projekte und LaTeX in Word-Dokumente umwandelt. Eine kostenlose Testversion mit 5 Umwandlungen pro Richtung steht auf unserer Website zum Download bereit. Der Lizenzschlüssel schaltet unbegrenzte Umwandlungen frei.</p>
<p><b>B2. Vertragsschluss.</b> Die Darstellung der Software auf unserer Website ist kein verbindliches Angebot. <i>Online:</i> Sie geben den Namen für die Lizenz ein, akzeptieren diese AGB und klicken auf den PayPal-Button. Mit der Bestätigung der Zahlung bei PayPal geben Sie eine verbindliche Bestellung ab; der Vertrag kommt mit Abschluss der Zahlung zustande, und wir bestätigen ihn durch Anzeige des Lizenzschlüssels und Versand per E-Mail. <i>Per E-Mail:</i> Der Vertrag kommt zustande, wenn wir Ihre Bestellung durch Zusendung einer Zahlungsaufforderung und Rechnung annehmen. Vertragssprache ist Deutsch oder Englisch. Wir speichern den Vertragstext; Sie erhalten die Vertragsdaten per E-Mail.</p>
<p><b>B3. Preis und Zahlung.</b> Eine Lizenz kostet 29,99 € (einmalig). Dies ist der Endpreis. Als Kleinunternehmer gemäß § 19 UStG berechnen wir keine Umsatzsteuer. Zahlung über PayPal oder, bei Bestellung per E-Mail, per Überweisung.</p>
<p><b>B4. Lieferung.</b> Beim Online-Kauf wird Ihr Lizenzschlüssel unmittelbar nach der Zahlung angezeigt und mit dem Beleg per E-Mail gesendet. Bei Bestellung per E-Mail senden wir den Schlüssel nach Zahlungseingang, in der Regel innerhalb von zwei Werktagen. Das Installationsprogramm ist ein Download; ein physischer Versand erfolgt nicht.</p>
<p><b>B5. Lizenz.</b> Sie erhalten ein einfaches, nicht übertragbares, zeitlich unbegrenztes Recht zur Nutzung der Software durch eine Person. Sie dürfen den Lizenzschlüssel nicht weiterverkaufen, vermieten oder weitergeben und die Software nicht dekompilieren oder verändern, soweit das Gesetz dies nicht ausdrücklich erlaubt.</p>
<p><b>B6. Gewährleistung und Haftung.</b> Es gelten die gesetzlichen Gewährleistungsrechte. Wir haften unbeschränkt bei Vorsatz und grober Fahrlässigkeit sowie bei Verletzung von Leben, Körper oder Gesundheit. Bei leichter Fahrlässigkeit haften wir nur bei Verletzung wesentlicher Vertragspflichten, begrenzt auf den vertragstypischen, vorhersehbaren Schaden. Die Haftung nach dem Produkthaftungsgesetz bleibt unberührt. Bitte sichern Sie Ihre Dokumente und prüfen Sie jedes umgewandelte Dokument.</p>
<p><b>B7. Schlussbestimmungen.</b> Es gilt deutsches Recht. Sind Sie Verbraucher, entzieht Ihnen diese Rechtswahl nicht den Schutz der zwingenden Vorschriften des Staates, in dem Sie Ihren gewöhnlichen Aufenthalt haben. Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2 id="widerruf">Widerrufsbelehrung</h2>
<p><b>Widerrufsrecht.</b> Wenn Sie Verbraucher sind, haben Sie das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen. Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag des Vertragsschlusses. Um Ihr Widerrufsrecht auszuüben, müssen Sie uns ({OWNER}, Deutschland, E-Mail {MAIL}) mittels einer eindeutigen Erklärung (z. B. per E-Mail) über Ihren Entschluss informieren. Sie können dafür das unten stehende Muster-Widerrufsformular verwenden, das jedoch nicht vorgeschrieben ist. Zur Wahrung der Frist reicht es aus, dass Sie die Mitteilung vor Ablauf der Frist absenden.</p>
<p><b>Folgen des Widerrufs.</b> Wenn Sie widerrufen, erstatten wir Ihnen alle Zahlungen, die wir von Ihnen erhalten haben, unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag, an dem die Mitteilung über Ihren Widerruf bei uns eingegangen ist. Für die Rückzahlung verwenden wir dasselbe Zahlungsmittel, das Sie bei der ursprünglichen Transaktion eingesetzt haben, es sei denn, mit Ihnen wurde ausdrücklich etwas anderes vereinbart; Ihnen werden keine Entgelte berechnet.</p>
<p><b>Vorzeitiges Erlöschen.</b> Bei digitalen Inhalten, die nicht auf einem körperlichen Datenträger geliefert werden, erlischt Ihr Widerrufsrecht, sobald wir mit der Ausführung des Vertrags begonnen haben (Versand des Lizenzschlüssels), nachdem Sie ausdrücklich zugestimmt haben, dass wir vor Ablauf der Widerrufsfrist beginnen, und Ihre Kenntnis davon bestätigt haben, dass Sie dadurch Ihr Widerrufsrecht verlieren. Beim Online-Kauf erteilen Sie diese Zustimmung durch das Häkchen vor der Zahlung. Bei Bestellung per E-Mail fügen Sie bitte folgende Erklärung ein, wenn Sie den Schlüssel sofort erhalten möchten:</p>
<p class="box">{WITHDRAW_STATEMENT[1]}</p>
<p><b>Muster-Widerrufsformular</b> (füllen Sie es nur aus und senden Sie es zurück, wenn Sie den Vertrag widerrufen wollen):<br>
An: {OWNER}, Deutschland, deepqscience@gmail.com<br>
Hiermit widerrufe(n) ich/wir den von mir/uns abgeschlossenen Vertrag über die Bereitstellung der folgenden digitalen Inhalte: Lizenz DeepQ Manuscript<br>
Bestellt am: ________ · Name des/der Verbraucher(s): ________ · Anschrift des/der Verbraucher(s): ________<br>
Unterschrift (nur bei Mitteilung auf Papier): ________ · Datum: ________</p>
<p class="note">Stand: {UPDATED[1]}</p>
''')}
"""

NOTFOUND = f"""
<p class="big">404</p>
<h1 style="margin-top:8px">{bi('This page does not exist.', 'Diese Seite gibt es nicht.')}</h1>
<p>{bi('The link may be out of date, or the address may contain a typo.', 'Der Link ist vielleicht veraltet, oder die Adresse enthält einen Tippfehler.')}</p>
<p>
  <a class="btn primary" href="/">{bi('Go to the homepage', 'Zur Startseite')}</a>
  <a class="btn" href="/blog/">Blog</a>
  <a class="btn" href="/manuscript">DeepQ Manuscript</a>
  <a class="btn" href="/#kontakt">{bi('Contact', 'Kontakt')}</a>
</p>
"""

if __name__ == '__main__':
    (SITE / 'datenschutz.html').write_text(page('datenschutz', 'Privacy policy',
        'How Deep Quantum Science handles personal data: hosting, consent, contact form, audience measurement and licence purchases.', PRIVACY), encoding='utf-8')
    (SITE / 'impressum.html').write_text(page('impressum', 'Legal notice',
        'Legal notice (Impressum) of Deep Quantum Science Consulting, Dr. Maseim Bassis Kenmoe, Regensburg.', IMPRESSUM), encoding='utf-8')
    (SITE / 'terms.html').write_text(page('terms', 'Terms and conditions',
        'Terms of use of the website and terms of sale for DeepQ Manuscript licences, with withdrawal information.', TERMS), encoding='utf-8')
    (SITE / '404.html').write_text(page('404', 'Page not found',
        'This page does not exist on deep-quantum-science.com.', NOTFOUND, robots='noindex'), encoding='utf-8')
    print('legal pages and 404 written')
