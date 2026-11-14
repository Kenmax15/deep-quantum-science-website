"""Crawls the site and reports broken links, missing anchors, images without
alt text and pages without title/description.

    npx wrangler pages dev site --port 8788      # in another terminal
    python3 tools/check_links.py [http://127.0.0.1:8788] [--external]
"""
import re, sys, urllib.request, urllib.parse, html, ssl
from collections import defaultdict

START = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://127.0.0.1:8788')
EXTERNAL = '--external' in sys.argv
UA = {'User-Agent': 'Mozilla/5.0 (DQS link check)'}
# Sites that refuse robots (LinkedIn answers 999, Facebook 400) are reported as "unverifiable", not broken
UNVERIFIABLE = ('linkedin.com', 'facebook.com')


def fetch(url, method='GET'):
    req = urllib.request.Request(url, headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
            return r.status, r.geturl(), (r.read().decode('utf-8', 'replace') if method == 'GET' else '')
    except urllib.error.HTTPError as e:
        return e.code, url, ''
    except Exception as e:
        return 0, url, str(e)


def main():
    host = urllib.parse.urlparse(START).netloc
    todo, seen, pages = [START + '/'], set(), {}
    links = defaultdict(set)          # target -> pages linking to it
    problems = []
    while todo:
        u = todo.pop()
        if u in seen:
            continue
        seen.add(u)
        st, final, body = fetch(u)
        if st != 200:
            continue
        pages[u] = body
        if '<html' not in body[:500].lower():
            continue
        title = re.search(r'<title>(.*?)</title>', body, re.S)
        if not title or not title.group(1).strip():
            problems.append(('no title', u, ''))
        if '<meta name="description"' not in body and 'noindex' not in body:
            problems.append(('no description', u, ''))
        for m in re.finditer(r'<img\b[^>]*>', body):
            if not re.search(r'\balt="', m.group(0)):
                problems.append(('img without alt', u, m.group(0)[:80]))
        for m in re.finditer(r'(?:href|src)="([^"]+)"', body):
            t = html.unescape(m.group(1))
            if t.startswith(('mailto:', 'tel:', 'javascript:', 'data:')) or t == '#':
                continue
            absu = urllib.parse.urljoin(u, t)
            links[absu].add(u)
            p = urllib.parse.urlparse(absu)
            if p.netloc == host and p.path.split('.')[-1] not in ('webp', 'png', 'jpg', 'jpeg', 'svg', 'ico', 'css', 'js', 'woff2', 'xml', 'txt', 'exe', 'webmanifest'):
                todo.append(absu.split('#')[0])
    broken, unverifiable = [], []
    for target, srcs in sorted(links.items()):
        p = urllib.parse.urlparse(target)
        base = target.split('#')[0]
        if p.netloc == host:
            st, final, body = (200, base, pages[base]) if base in pages else fetch(base)
            if st not in (200, 308, 301):
                broken.append((st, target, sorted(srcs)[0]))
            elif p.fragment and base in pages and not re.search(r'id="' + re.escape(p.fragment) + '"', pages[base]):
                broken.append(('missing #' + p.fragment, target, sorted(srcs)[0]))
        elif EXTERNAL and p.scheme in ('http', 'https'):
            if any(d in p.netloc for d in UNVERIFIABLE):
                unverifiable.append(target)
                continue
            if p.netloc.endswith('doi.org'):   # publishers block robots: ask the DOI registry instead
                import json
                st0, _, body = fetch('https://doi.org/api/handles/' + p.path.lstrip('/'))
                ok = st0 == 200 and json.loads(body or '{}').get('responseCode') == 1
                if not ok:
                    broken.append(('unknown DOI', target, sorted(srcs)[0]))
                continue
            st, _, _ = fetch(target, 'HEAD')
            if st in (0, 403, 405, 404, 400) :
                st, _, _ = fetch(target)
            if not (200 <= st < 400):
                broken.append((st, target, sorted(srcs)[0]))
    print(f'{len(pages)} pages crawled, {len(links)} distinct links')
    for p in problems:
        print('PROBLEM', *p)
    for b in broken:
        print('BROKEN ', *b)
    for u in unverifiable:
        print('UNVERIFIABLE (blocks robots, check by hand):', u)
    if not problems and not broken:
        print('No broken links, every page has a title and description, every image has alt text.')


if __name__ == '__main__':
    main()
