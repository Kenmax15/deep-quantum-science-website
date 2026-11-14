"""Site-wide finishing pass. Run after any page is generated or edited:

    python3 tools/build_blog.py      # if the blog changed
    python3 tools/build_legal.py     # if the legal pages changed
    python3 tools/site_polish.py

It is idempotent (running it twice changes nothing) and takes care of:
  • clean URLs (/manuscript instead of /manuscript.html, which Cloudflare redirects)
  • <head>: title fallback, meta description, canonical, Open Graph + Twitter card
    with a 1200×630 JPG, favicons + web manifest, theme colour, robots
  • the consent banner script (assets/consent.js) on every page
  • WOFF2 fonts, WebP logo, lazy-loading and explicit sizes for images
  • footer links to the legal pages
  • sitemap.xml (with last-modified dates from git) and robots.txt
"""
import html, pathlib, re, subprocess, datetime
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
BASE = 'https://deep-quantum-science.com'
SKIP = {'google25dc491646750c89.html'}
BASE_CSS = ('img{max-width:100%;height:auto}'
            '.nav .links a{position:relative}'
            '.nav .links a.active,.nav .links a[aria-current]{color:var(--text)}'
            '.nav .links a.active::after,.nav .links a[aria-current]::after{content:"";position:absolute;left:0;right:0;bottom:-6px;'
            'height:2px;border-radius:2px;background:var(--mint)}')

DESC = {   # used only when a page has no description of its own
    'index.html': 'Deep Quantum Science Consulting: AI, machine learning and deep learning consulting, data analysis and scientific simulation from Regensburg, Germany.',
}
TITLE = {
    'index.html': 'Deep Quantum Science · AI, machine learning & simulation consulting, Regensburg',
}
OG = {   # page -> social image in /assets/og/
    'index.html': 'home.jpg', 'manuscript.html': 'manuscript.jpg', 'blog/index.html': 'blog.jpg',
}


def clean_url(rel: str) -> str:
    """'blog/haldane-chain.html' -> '/blog/haldane-chain', 'blog/index.html' -> '/blog/'."""
    u = '/' + rel
    if u.endswith('index.html'):
        u = u[:-len('index.html')]
    elif u.endswith('.html'):
        u = u[:-5]
    return u


def fix_links(s: str) -> str:
    def href(m):
        q, url = m.group(1), m.group(2)
        if re.match(r'^(https?:|mailto:|tel:|#|data:|javascript:)', url) and not url.startswith(BASE):
            return m.group(0)
        path, frag = (url.split('#', 1) + [''])[:2]
        frag = '#' + frag if '#' in url else ''
        if path.endswith('.html') and not path.endswith('google25dc491646750c89.html'):
            if path.endswith('index.html'):
                path = path[:-len('index.html')] or './'
            else:
                path = path[:-5]
        return f'{q}{path}{frag}"'
    s = re.sub(r'(href=")([^"]*)"', href, s)
    # absolute URLs in JSON-LD / meta
    s = re.sub(re.escape(BASE) + r'(/[^"\s<]*?)index\.html', lambda m: BASE + m.group(1), s)
    s = re.sub(re.escape(BASE) + r'(/[^"\s<]*?)\.html', lambda m: BASE + m.group(1), s)
    return s


def set_meta(head: str, attr: str, key: str, value: str) -> str:
    tag = f'<meta {attr}="{key}" content="{html.escape(value, quote=True)}">'
    pat = re.compile(r'<meta\s+' + attr + r'="' + re.escape(key) + r'"[^>]*>\n?')
    if pat.search(head):
        return pat.sub(tag + '\n', head, count=1)
    return head.replace('</head>', tag + '\n</head>', 1)


def polish(p: pathlib.Path):
    rel = p.relative_to(SITE).as_posix()
    s = p.read_text(encoding='utf-8')
    orig = s
    s = fix_links(s)
    url = BASE + clean_url(rel)
    is_404 = rel == '404.html'
    is_post = rel.startswith('blog/') and rel != 'blog/index.html'

    head_end = s.index('</head>')
    head, body = s[:head_end + 7], s[head_end + 7:]

    # title
    if rel in TITLE:
        head = re.sub(r'<title>.*?</title>', f'<title>{html.escape(TITLE[rel])}</title>', head, count=1)
    title = html.unescape(re.search(r'<title>(.*?)</title>', head).group(1))
    m = re.search(r'<meta name="description" content="([^"]*)"', head)
    desc = html.unescape(m.group(1)) if m else DESC.get(rel, title)
    head = set_meta(head, 'name', 'description', desc)

    # robots: everything indexable except the 404 page
    head = re.sub(r'<meta name="robots"[^>]*>\n?', '', head)
    if is_404:
        head = head.replace('</head>', '<meta name="robots" content="noindex">\n</head>', 1)

    # canonical
    head = re.sub(r'<link rel="canonical"[^>]*>\n?', '', head)
    if not is_404:
        head = head.replace('</head>', f'<link rel="canonical" href="{url}">\n</head>', 1)

    # Open Graph + Twitter
    head = re.sub(r'<meta (property|name)="(og|twitter):[^"]*"[^>]*>\n?', '', head)
    old_og = re.search(r'blog/img/([\w-]+)\.webp', orig[:orig.index('</head>')])
    img = OG.get(rel)
    if not img and is_post and old_og:
        img = old_og.group(1) + '.jpg'
    if not img or not (SITE / 'assets/og' / img).exists():
        img = 'home.jpg'
    og = [('property', 'og:type', 'article' if is_post else 'website'),
          ('property', 'og:site_name', 'Deep Quantum Science'),
          ('property', 'og:title', title.replace(' · Deep Quantum Science', '')),
          ('property', 'og:description', desc),
          ('property', 'og:url', url),
          ('property', 'og:image', f'{BASE}/assets/og/{img}'),
          ('property', 'og:image:width', '1200'), ('property', 'og:image:height', '630'),
          ('property', 'og:image:alt', title.replace(' · Deep Quantum Science', '')),
          ('property', 'og:locale', 'en_US'), ('property', 'og:locale:alternate', 'de_DE'),
          ('name', 'twitter:card', 'summary_large_image')]
    if not is_404:
        for a, k, v in og:
            head = set_meta(head, a, k, v)

    # favicons, manifest, theme colour
    head = re.sub(r'<link rel="(icon|apple-touch-icon|manifest)"[^>]*>\n?', '', head)
    head = re.sub(r'<meta name="theme-color"[^>]*>\n?', '', head)
    icons = ('<link rel="icon" href="/favicon.ico" sizes="48x48">\n'
             '<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">\n'
             '<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">\n'
             '<link rel="manifest" href="/site.webmanifest">\n'
             '<meta name="theme-color" content="#0e082c">\n')
    head = head.replace('</head>', icons + '</head>', 1)

    # images keep their proportions whatever width the layout gives them
    # and the navigation shows where you are (assets/nav.js sets .active / aria-current)
    head = re.sub(r'<style id="dqs-base">.*?</style>\n?', '', head, flags=re.S)
    head = head.replace('</head>', '<style id="dqs-base">' + BASE_CSS + '</style>\n</head>', 1)

    # consent banner + audience measurement (loaded only after consent)
    head = re.sub(r'<script src="/assets/(consent|nav)\.js"[^>]*></script>\n?', '', head)
    head = head.replace('</head>', '<script src="/assets/consent.js" defer></script>\n<script src="/assets/nav.js" defer></script>\n</head>', 1)

    # fonts: WOFF2
    head = re.sub(r'(fonts/[\w-]+)\.woff"\) format\("woff"\)', r'\1.woff2") format("woff2")', head)

    s = head + body
    # images: WebP logo, sizes, lazy loading
    s = re.sub(r'<img src="((?:\.\./)?)assets/logo\.png" alt="([^"]*)"( width="(\d+)" height="(\d+)")?',
               lambda m: (f'<img src="{m.group(1)}assets/' + ('logo-nav.webp' if (m.group(4) and int(m.group(4)) < 60) or not m.group(4) else 'logo.webp')
                          + f'" alt="{m.group(2)}"' + (m.group(3) or ' width="28" height="30"')), s)
    count = [0]

    def img(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if src and not src.group(1).startswith('http'):
            f = (p.parent / src.group(1).split('?')[0]).resolve()
            if f.exists():
                w, h = Image.open(f).size
                mw, mh = re.search(r'\swidth="(\d+)"', tag), re.search(r'\sheight="(\d+)"', tag)
                keep = mw and mh and abs(int(mw.group(1)) / int(mh.group(1)) - w / h) < 0.03 * (w / h)
                if not keep:   # missing or wrong proportions: use the real size
                    tag = re.sub(r'\s(width|height)="\d+"', '', tag)
                    tag = tag.replace('<img ', f'<img width="{w}" height="{h}" ', 1)
                small = f.with_name(f.stem + '-800' + f.suffix)
                if small.exists() and 'srcset=' not in tag:
                    s800 = src.group(1).rsplit('.', 1)[0] + '-800.' + src.group(1).rsplit('.', 1)[1]
                    tag = tag.replace('<img ', f'<img srcset="{s800} 800w, {src.group(1)} {w}w" sizes="(max-width: 860px) 92vw, 560px" ', 1)
        # the first two images (logo, hero/LCP image) load immediately; the rest lazily
        tag = re.sub(r'\s(loading|decoding|fetchpriority)="[^"]*"', '', tag)
        if count[0] == 1:
            tag = tag.replace('<img ', '<img fetchpriority="high" ', 1)
        elif count[0] >= 2:
            tag = tag.replace('<img ', '<img loading="lazy" decoding="async" ', 1)
        count[0] += 1
        if not re.search(r'\balt=', tag):
            tag = tag.replace('<img ', '<img alt="" ', 1)
        return tag
    s = re.sub(r'<img\b[^>]*>', img, s)

    # footer: make sure Terms are linked next to legal notice and privacy
    s = re.sub(r'(<div class="legal">)(?:(?!</div>).)*?(</div>)',
               lambda m: m.group(1) + ''.join(
                   f'<a href="{pre}{slug}"><span class="en">{en}</span><span class="de">{de}</span></a>'
                   for slug, en, de in [('impressum', 'Legal notice', 'Impressum'), ('terms', 'Terms', 'AGB'),
                                        ('datenschutz', 'Privacy', 'Datenschutz')]
                   for pre in ['../' if rel.startswith('blog/') else '' if '/' not in rel else '/']) + m.group(2)
               if 'class="en"' in m.group(0) else m.group(0), s, flags=re.S)

    if s != orig:
        p.write_text(s, encoding='utf-8')
        return True
    return False


def lastmod(p: pathlib.Path) -> str:
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', str(p)], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.date.today().isoformat()


def sitemap(pages):
    rows = []
    for p in sorted(pages, key=lambda x: (x.relative_to(SITE).as_posix() != 'index.html', x.relative_to(SITE).as_posix())):
        rel = p.relative_to(SITE).as_posix()
        if rel == '404.html' or rel in SKIP:
            continue
        prio = '1.0' if rel == 'index.html' else '0.8' if rel in ('manuscript.html', 'blog/index.html') else \
               '0.3' if rel in ('impressum.html', 'datenschutz.html', 'terms.html') else '0.6'
        rows.append(f'<url><loc>{BASE}{clean_url(rel)}</loc><lastmod>{lastmod(p)}</lastmod><priority>{prio}</priority></url>')
    (SITE / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(rows) + '\n</urlset>\n', encoding='utf-8')
    (SITE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n', encoding='utf-8')


if __name__ == '__main__':
    pages = [p for p in SITE.rglob('*.html') if p.name not in SKIP]
    changed = [p.relative_to(SITE).as_posix() for p in pages if polish(p)]
    sitemap(pages)
    print(f'{len(pages)} pages, {len(changed)} changed:', ', '.join(changed))
