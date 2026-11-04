"""Build the static blog (site/blog/) from the posts below.

Run:  python3 tools/build_blog.py
It reuses the design of the site (CSS taken from site/manuscript.html), so the blog always matches the main pages.
To add an article: append a dict to POSTS (newest last), add images to site/blog/img/, run the script, commit.
"""
import html, json, re, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'; BLOG = SITE / 'blog'
BASE = 'https://deep-quantum-science.com'

src = (SITE / 'manuscript.html').read_text(encoding='utf-8')
styles = re.findall(r'<style>(.*?)</style>', src, flags=re.S)
BASE_CSS = '\n'.join(styles[:3]).replace('url("assets/', 'url("../assets/')

BLOG_CSS = """
.b-hero{border-bottom:1px solid var(--rule)}
.b-hero .wrap{padding-block:clamp(48px,7vw,88px) clamp(32px,5vw,56px)}
.b-hero h1{font-size:var(--step-4);margin-top:14px;max-width:20ch}
.b-hero .lead{margin-top:18px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;padding-block:clamp(36px,5vw,64px)}
.card{display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--rule);border-radius:14px;overflow:hidden;text-decoration:none;color:inherit;transition:border-color .2s,transform .2s}
.card:hover{border-color:var(--mint);transform:translateY(-2px)}
.card img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;border-bottom:1px solid var(--rule)}
.card .c-body{padding:20px 22px 22px;display:grid;gap:10px}
.card h2{font-size:var(--step-2)}
.card p{margin:0;color:var(--muted)}
.meta{font:500 var(--step--1)/1.4 var(--mono);letter-spacing:.06em;color:var(--muted)}
.meta .tag{color:var(--mint);text-transform:uppercase;letter-spacing:.14em}
.article{max-width:72ch;margin:0 auto;padding-block:clamp(36px,6vw,72px)}
.article h1{font-size:var(--step-3);margin:12px 0 16px}
.article h2{font-size:var(--step-2);margin:44px 0 12px}
.article p,.article li{color:var(--text-2,var(--text))}
.article p{margin:0 0 16px}
.article ul,.article ol{padding-left:22px;margin:0 0 18px}
.article li{margin-bottom:6px}
.article figure{margin:28px 0}
.article figure img{display:block;width:100%;border-radius:12px;border:1px solid var(--rule)}
.article figcaption{font-size:var(--step--1);color:var(--muted);margin-top:8px}
.article .eq{font:400 1.08em/1.5 var(--mono);background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 18px;overflow-x:auto;margin:18px 0;white-space:nowrap}
.article a{color:var(--mint)}
.article .note{border-left:3px solid var(--mint);background:var(--panel);padding:14px 18px;border-radius:0 10px 10px 0;margin:22px 0}
.watch{display:flex;gap:18px;align-items:center;background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:16px;margin:28px 0;text-decoration:none;color:inherit}
.watch:hover{border-color:var(--mint)}
.watch img{width:180px;aspect-ratio:16/9;object-fit:cover;border-radius:8px;flex:none}
.watch b{display:block;font:500 var(--step-1)/1.3 var(--display)}
.watch span{color:var(--muted);font-size:var(--step--1)}
@media(max-width:520px){.watch{flex-direction:column;align-items:stretch}.watch img{width:100%}}
.lang-note{font-size:var(--step--1);color:var(--muted);margin-top:10px}
.back{display:inline-block;margin-top:36px}
.article pre.algo{font:400 .92em/1.6 var(--mono);background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:16px 20px;overflow-x:auto;margin:18px 0;white-space:pre}
.article pre.algo b{color:var(--mint);font-weight:500}
.article pre.algo i{color:var(--muted);font-style:normal}
.article .algo-title{font:500 var(--step--1)/1.3 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--mint);margin:26px 0 -8px}
.article table{border-collapse:collapse;width:100%;margin:18px 0;font-size:var(--step--1)}
.article th,.article td{border-bottom:1px solid var(--rule);padding:8px 10px;text-align:left;vertical-align:top}
.article th{color:var(--mint);font-weight:500}
"""

POSTS = [
 dict(slug='quantum-spins-are-binary-numbers', date='2026-11-03', tag='Research',
  title='Quantum spins are just binary numbers',
  de='Quantenspins sind Binärzahlen',
  summary='Read a chain of spins as a binary number, and spin operators become simple jumps between integers: the idea behind our Dirac representation.',
  img='spins-hero.webp',
  video=('https://youtu.be/Fhv4cZ8gtw0', 'Watch: Quantum spins are just binary numbers (60 s)', 'YouTube · Research in 60 seconds'),
  body="""
<p>Spin systems are everywhere in physics: magnets, qubits, cold atoms in optical lattices. Their standard description uses tensor products of small matrices, one per site. That is exact, but it quickly becomes hard to read and to compute with. In our paper in <i>Physica B</i> we start from a much simpler picture.</p>
<h2>Spins are bits</h2>
<p>Write spin up as <b>0</b> and spin down as <b>1</b>. A row of K spins is then a string of K bits, and therefore an ordinary integer n between 0 and 2<sup>K</sup>−1. For three spins, ↑↓↑ is 010, which is the number 2.</p>
<figure><img src="img/spins-pattern.webp" alt="Counting from 0 to 15: each spin site follows a regular square-wave pattern" loading="lazy"><figcaption>Counting through all configurations: every site follows a regular pattern, not a random one.</figcaption></figure>
<p>If you count from 0 upwards, each site flips with a perfectly regular rhythm: the last site every step, the one before every two steps, and so on. Site j has a weight q<sub>j</sub> = 2<sup>K−j</sup>.</p>
<h2>Flipping a spin is a jump</h2>
<p>Turning spin j from up to down adds q<sub>j</sub> to the number. So the lowering operator is nothing but a jump on the number line:</p>
<div class="eq">S<sub>j</sub><sup>−</sup> = Σ<sub>n</sub> s<sub>n</sub><sup>(j)</sup> |n + q<sub>j</sub>⟩⟨n| ,&nbsp;&nbsp;&nbsp; S<sub>j</sub><sup>+</sup> = Σ<sub>n</sub> s<sub>n</sub><sup>(j)</sup> |n⟩⟨n + q<sub>j</sub>|</div>
<p>The coefficient s<sub>n</sub><sup>(j)</sup> is a gatekeeper: it equals 1 when spin j is up in configuration n and 0 otherwise, so a spin that is already down cannot be lowered further. The z component is diagonal: it simply reads a digit of n.</p>
<p>The key result of the paper is that these digits have a <b>closed formula</b> made of unit-step functions, so one never needs to convert n to binary by hand:</p>
<div class="eq">s<sub>n</sub><sup>(j)</sup> = Σ<sub>m</sub> [ u(n − 2m q<sub>j</sub>) − u(n − (2m+1) q<sub>j</sub>) ]</div>
<h2>Why this is useful</h2>
<ul>
<li><b>No Jordan–Wigner strings.</b> Operators on different sites commute and stay local.</li>
<li><b>Any dimension, any lattice.</b> Geometry only enters through which pairs of sites interact.</li>
<li><b>Exact algebra.</b> [S<sup>+</sup>, S<sup>−</sup>] = 2S<sup>z</sup> holds exactly. We checked numerically that the operators coincide with the usual tensor products.</li>
<li><b>Spin chains become hopping problems.</b> The Heisenberg (XXZ) chain turns into a single particle hopping on a graph of configurations.</li>
</ul>
<figure><img src="img/spins-graph.webp" alt="Configuration graph: each node is a spin configuration, each link a spin exchange" loading="lazy"><figcaption>The Heisenberg chain as a particle hopping on a graph of configurations.</figcaption></figure>
<p>The paper also treats spin-1, where each site carries three states instead of two. The same ideas power the next two articles on perturbation theory.</p>
"""),
 dict(slug='perturbation-theory-explained', date='2026-11-03', tag='Research explained',
  title='Perturbation theory explained like you’re 10',
  de='Störungstheorie, kindgerecht erklärt',
  summary='Tiny magnets on a bumpy road: how physicists estimate energies when the exact problem is too hard, step by step and with real numbers.',
  img='pt-hero.webp',
  video=('https://youtu.be/fzENbadiQsU', 'Watch: Tiny magnets on a bumpy road (3:52)', 'YouTube · Research explained'),
  body="""
<p>Most quantum problems cannot be solved exactly. Perturbation theory is the art of starting from an easy problem and adding small corrections, one at a time. Here is the idea, using the disordered spin chain from our paper.</p>
<h2>The easy world: nobody moves</h2>
<p>Take a row of six tiny magnets, each sitting on a random magnetic field (a "bump" in the road), with neighbours that feel each other. If the magnets cannot swap places, every arrangement has one fixed energy: a step on a ladder. With two magnets pointing down there are 15 arrangements, and we can compute every step exactly.</p>
<figure><img src="img/pt-ladder.webp" alt="Frozen arrangements and their energy ladder" loading="lazy"><figcaption>The unperturbed problem: each frozen arrangement is a step on an energy ladder.</figcaption></figure>
<h2>Small hops</h2>
<p>Now neighbouring up and down magnets may swap, with a small strength J. Draw each arrangement as a dot and each possible swap as a link: from any dot you can only hop to a few neighbouring dots. Because J is small, the system mostly stays home and only peeks next door.</p>
<h2>The recipe</h2>
<ol>
<li><b>Step 0</b> is the height of your own ladder step.</li>
<li><b>Step 1 is zero.</b> After a single hop you are somewhere else, and only trips that come back home change the energy.</li>
<li><b>Step 2: go and come back.</b> Each neighbour m gives a push |V<sub>nm</sub>|² / (E<sub>n</sub> − E<sub>m</sub>). Far-away energies barely matter; close energies matter a lot. Levels repel each other.</li>
</ol>
<figure><img src="img/pt-step2.webp" alt="Second-order correction: hop to a neighbour and back" loading="lazy"><figcaption>Second order: hop and come back. Here all neighbours sit higher and push the level down.</figcaption></figure>
<h2>A chessboard trick</h2>
<p>Colour the arrangements like a chessboard. Every hop changes the colour (the graph is bipartite), so after an odd number of hops you can never be home. Steps 1 and 3 vanish exactly, and two simple terms already give the energy with an error of order J<sup>4</sup>.</p>
<h2>Does it work?</h2>
<p>We compared the two-term recipe with exact diagonalisation. The largest error over all 15 levels is 0.0005 at J = 0.2 and 0.0068 at J = 0.4: doubling J multiplies the error by about 16, exactly the J<sup>4</sup> we predicted. For large J the recipe breaks down, as expected for a small-J theory.</p>
<figure><img src="img/pt-test.webp" alt="Exact energies versus perturbation theory as a function of J" loading="lazy"><figcaption>Exact energies (green) and the two-term recipe (yellow, dashed), with the error growing as J<sup>4</sup>.</figcaption></figure>
<div class="note">Why it matters: the same hop-and-return picture explains when strong disorder traps a quantum system near its starting point, the physics of many-body localisation.</div>
"""),
 dict(slug='perturbation-theory-matrix-machine', date='2026-11-04', tag='Research explained',
  title='One machine, all the energies: perturbation theory with matrices',
  de='Eine Maschine für alle Energien',
  summary='A compact matrix recursion gives every eigenvalue and eigenstate at once, to any order. We run it, and show exactly when and why it breaks.',
  img='mm-hero.webp',
  video=('https://youtu.be/Aia_6b0e7Uc', 'Watch: One machine, all the energies (3:13)', 'YouTube · Research explained'),
  body="""
<p>The previous article built the energy by hand, order by order. The appendix of our paper turns the whole procedure into a machine that only uses matrix operations, and that gives every state at once.</p>
<h2>The problem as a table of numbers</h2>
<p>We write the Hamiltonian as H = Λ + λΔ: a diagonal, easy part Λ with entries ε<sub>n</sub>, and a small off-diagonal push Δ of size λ.</p>
<figure><img src="img/mm-table.webp" alt="Heatmaps of the diagonal part, the off-diagonal part and the full Hamiltonian" loading="lazy"><figcaption>An easy diagonal part plus a small off-diagonal push.</figcaption></figure>
<h2>Store every correction in a matrix</h2>
<p>Energies and states are expanded as series in λ. Each correction to state n is a mix of the simple states, |ψ<sub>n</sub><sup>(k)</sup>⟩ = Σ<sub>j</sub> A<sub>j,n</sub><sup>(k)</sup> |j⟩. Stacking these numbers gives one matrix A<sup>(k)</sup> per order, with one column per state. Two rules fix everything: A<sup>(0)</sup> is the identity, and corrections never point back along the original state, so the diagonal of A<sup>(k)</sup> is empty. The energy corrections are then read off a diagonal:</p>
<div class="eq">E<sub>n</sub><sup>(k)</sup> = ( Δ A<sup>(k−1)</sup> )<sub>n,n</sub></div>
<h2>The machine</h2>
<p>With the gap table θ<sub>j,n</sub> = 1/(ε<sub>j</sub> − ε<sub>n</sub>) (zero on the diagonal), the next correction follows from the previous ones:</p>
<div class="eq">A<sup>(k)</sup> = θ ∘ ( Σ<sub>q=1..k</sub> A<sup>(k−q)</sup> D(Δ A<sup>(q−1)</sup>) − Δ A<sup>(k−1)</sup> )</div>
<p>Here ∘ is the cell-by-cell (Hadamard) product and D keeps only the diagonal. In words: take the previous correction, mix it with Δ using ordinary matrix products, multiply cell by cell by the gap table, and repeat.</p>
<figure><img src="img/mm-machine.webp" alt="Animated recursion: previous correction, mixing, Hadamard product with the gap table" loading="lazy"><figcaption>Three simple operations per order, for all states at once.</figcaption></figure>
<h2>Turning the crank</h2>
<p>On our six-site chain with λ = 0.2, the error drops by orders of magnitude with each even order and reaches about 10<sup>−13</sup> after 30 orders; odd orders change nothing, as expected from the bipartite structure.</p>
<h2>When the machine breaks</h2>
<p>Push harder, λ = 0.6, and the error first decreases, then explodes. The reason is a near-resonance: two levels only 0.033 apart give a huge entry in θ, which is amplified at every order. Perturbation theory is a theory for small pushes, and the closest gaps set its range.</p>
<figure><img src="img/mm-break.webp" alt="Error versus order for a small and a larger perturbation" loading="lazy"><figcaption>Converging for λ = 0.2, diverging for λ = 0.6 because of a near-resonance.</figcaption></figure>
"""),
 dict(slug='many-body-localization', date='2026-11-04', tag='Physics explained',
  title='Can a quantum system remember its past? Many-body localisation',
  de='Kann sich ein Quantensystem erinnern?',
  summary='Most systems forget where they started. With strong disorder, interacting quantum spins can refuse to. Three fingerprints, computed exactly.',
  img='mbl-hero.webp',
  video=('https://youtu.be/h4KV_LYPWY8', 'Watch: Can a quantum system remember its past? (3:45)', 'YouTube · Research explained'),
  body="""
<p>Drop ink in water and wait: it spreads everywhere, and soon you cannot tell where the drop was. Physicists call this thermalisation, and almost every system does it. Many-body localisation (MBL) is a striking exception: with enough disorder, a system of interacting quantum particles can keep a memory of its initial state.</p>
<h2>The memory experiment</h2>
<p>We take a chain of 12 spins with neighbour interactions and a random magnetic field of strength up to W on each site, start from the pattern up, down, up, down, and let it evolve. All results below come from exact diagonalisation, averaged over 40 disorder realisations.</p>
<figure><img src="img/mbl-memory.webp" alt="Memory of the initial pattern over time for weak and strong disorder" loading="lazy"><figcaption>Weak disorder (W = 0.5): the pattern melts away. Strong disorder (W = 6): about two thirds of it survives.</figcaption></figure>
<h2>Why it gets stuck</h2>
<p>Follow a single flipped spin. With small bumps it spreads like a wave; with big bumps it stays near its starting point. In the perturbative picture of our paper, the hopping strength between two configurations is inversely proportional to the difference of their local fields: with large random fields, almost every hop is a step too high.</p>
<h2>Three fingerprints</h2>
<ol>
<li><b>Concentrated eigenstates.</b> The inverse participation ratio IPR = Σ<sub>m</sub> |⟨m|ψ⟩|<sup>4</sup> measures how concentrated a state is. It grows steadily with W.</li>
<li><b>Random energy levels.</b> In the thermal phase levels repel each other; in the localised phase they fall at random. The mean level-spacing ratio ⟨r⟩ slides from about 0.53 (Wigner–Dyson) to about 0.39 (Poisson) as W grows.</li>
<li><b>Slow entanglement.</b> Entanglement between the two halves of the chain saturates quickly for weak disorder, but grows only very slowly, roughly like the logarithm of time, for strong disorder.</li>
</ol>
<figure><img src="img/mbl-levels.webp" alt="Level statistics: ratio r versus disorder for 8, 10 and 12 spins" loading="lazy"><figcaption>The level-spacing ratio for chains of 8, 10 and 12 spins.</figcaption></figure>
<figure><img src="img/mbl-ent.webp" alt="Half-chain entanglement versus time for weak and strong disorder" loading="lazy"><figcaption>Fast versus very slow growth of entanglement.</figcaption></figure>
<h2>Why it matters</h2>
<p>An MBL system never heats up and never forgets, which makes it interesting for protecting quantum information and a test bed for quantum simulators with cold atoms and qubits. It is also still an open question: whether MBL survives in very large systems is actively debated, and small chains like ours shift the apparent transition point. Our Dirac representation turns these chains into hopping problems on a graph, a useful new angle on the puzzle.</p>
"""),
]

import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from blog_post_manuscript import POST as _MANUSCRIPT
POSTS.append(_MANUSCRIPT)

PAPER_NOTE = '<div class="note">Paper: <a href="https://doi.org/10.1016/j.physb.2026.419578" target="_blank" rel="noopener">Dirac representation for lattice spin operators: Spin-1/2 and spin-1 cases</a>, <i>Physica B: Condensed Matter</i> (2026).</div>'

NAV = """<nav class="nav" aria-label="Main navigation">
  <div class="wrap">
    <a class="brand" href="../index.html" aria-label="Deep Quantum Science">
      <img src="../assets/logo.png" alt="" width="34" height="37">
      <span>Deep Quantum Science<small>Consulting · Regensburg</small></span>
    </a>
    <div class="links">
      <a href="../index.html#leistungen"><span class="de">Leistungen</span><span class="en">Services</span></a>
      <a href="../manuscript.html"><span class="de">Software</span><span class="en">Software</span></a>
      <a href="../index.html#publikationen"><span class="de">Publikationen</span><span class="en">Publications</span></a>
      <a href="index.html">Blog</a>
    </div>
    <div class="nav-actions">
      <button type="button" class="theme-btn" id="theme-toggle" aria-label="Switch light/dark mode" title="Light / dark mode">
        <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>
        <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <div class="lang" role="group" aria-label="Language / Sprache">
        <button type="button" id="lang-en" data-lang="en" aria-pressed="true">EN</button>
        <button type="button" id="lang-de" data-lang="de" aria-pressed="false">DE</button>
      </div>
      <a class="btn btn-primary" href="../index.html#kontakt"><span class="de">Erstgespräch</span><span class="en">Free consultation</span></a>
    </div>
  </div>
</nav>"""

FOOTER = """<footer>
  <div class="wrap">
    <span>© <span id="year">2026</span> Deep Quantum Science Consulting · Regensburg</span>
    <span class="motto">The future is you!</span><div class="legal"><a href="../impressum.html"><span class="en">Legal notice</span><span class="de">Impressum</span></a><a href="../datenschutz.html"><span class="en">Privacy</span><span class="de">Datenschutz</span></a></div>
    <div class="social">
      <a href="https://www.linkedin.com/in/maseim-bassis-kenmoe-22077" target="_blank" rel="noopener">LinkedIn</a>
      <a href="https://www.youtube.com/@DeepQuantumScience" target="_blank" rel="noopener">YouTube</a>
      <a href="https://www.facebook.com/profile.php?id=61573518324805" target="_blank" rel="noopener">Facebook</a>
    </div>
  </div>
</footer>
<script>
(function(){
  const root=document.documentElement;
  function setLang(l){root.dataset.lang=l;root.lang=l;document.querySelectorAll('.lang button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lang===l)));try{localStorage.setItem('dqs-lang',l)}catch(e){}}
  let saved=null;try{saved=localStorage.getItem('dqs-lang')}catch(e){}
  setLang(saved==='de'?'de':'en');
  document.querySelectorAll('.lang button').forEach(b=>b.addEventListener('click',()=>setLang(b.dataset.lang)));
  document.getElementById('year').textContent=new Date().getFullYear();
  const mqLight=matchMedia('(prefers-color-scheme: light)');
  let savedTheme=null;try{savedTheme=localStorage.getItem('dqs-theme')}catch(e){}
  if(savedTheme==='light'||savedTheme==='dark')root.dataset.theme=savedTheme;
  const effTheme=()=>root.dataset.theme==='light'||root.dataset.theme==='dark'?root.dataset.theme:(mqLight.matches?'light':'dark');
  function syncTheme(){root.dataset.eff=effTheme()}
  syncTheme();
  mqLight.addEventListener?mqLight.addEventListener('change',syncTheme):mqLight.addListener(syncTheme);
  new MutationObserver(syncTheme).observe(root,{attributes:true,attributeFilter:['data-theme']});
  document.getElementById('theme-toggle').addEventListener('click',()=>{const next=effTheme()==='light'?'dark':'light';root.dataset.theme=next;try{localStorage.setItem('dqs-theme',next)}catch(e){}syncTheme()});
})();
</script>"""

def fmt_date(d):
    return datetime.date.fromisoformat(d).strftime('%-d %B %Y')

def page(title, desc, path, body, og_img, extra_head=''):
    url = f'{BASE}/blog/{path}'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Deep Quantum Science blog" href="{BASE}/blog/feed.xml">
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/blog/img/{og_img}">
<link rel="canonical" href="{url}">
{extra_head}<style>{BASE_CSS}
{BLOG_CSS}</style>
</head>
<body>
{NAV}
{body}
{FOOTER}
</body>
</html>
"""

def build():
    posts = sorted(POSTS, key=lambda p: p['date'], reverse=True)
    for p in posts:
        vurl, vtitle, vsub = p['video']
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'], 'description': p['summary'],
                         'datePublished': p['date'], 'image': f"{BASE}/blog/img/{p['img']}", 'author': {'@type': 'Organization', 'name': 'Deep Quantum Science'},
                         'publisher': {'@type': 'Organization', 'name': 'Deep Quantum Science', 'logo': f'{BASE}/assets/logo.png'},
                         'mainEntityOfPage': f"{BASE}/blog/{p['slug']}.html"}, ensure_ascii=False)
        body = f"""<main id="top">
<article class="wrap"><div class="article">
  <p class="meta"><span class="tag">{p['tag']}</span> · <time datetime="{p['date']}">{fmt_date(p['date'])}</time> · Deep Quantum Science</p>
  <h1>{html.escape(p['title'])}</h1>
  <p class="lead">{html.escape(p['summary'])}</p>
  <p class="lang-note de">Dieser Artikel ist auf Englisch verfügbar.</p>
  <a class="watch" href="{vurl}"{'' if vurl.startswith('..') else ' target="_blank" rel="noopener"'}><img src="{p.get('watch_img', 'img/' + p['img'])}" alt=""><div><b>{html.escape(vtitle)}</b><span>{html.escape(vsub)}{'' if vurl.startswith('..') else ' ↗'}</span></div></a>
  {p['body']}
  {p.get('footer', PAPER_NOTE)}
  <a class="btn btn-ghost back" href="index.html"><span class="en">← All articles</span><span class="de">← Alle Artikel</span></a>
</div></article>
</main>"""
        (BLOG / f"{p['slug']}.html").write_text(page(f"{p['title']} · Deep Quantum Science", p['summary'], f"{p['slug']}.html", body, p['img'],
                                                     f'<script type="application/ld+json">{ld}</script>\n'), encoding='utf-8')
    cards = '\n'.join(f"""  <a class="card" href="{p['slug']}.html"><img src="img/{p['img']}" alt="" loading="lazy"><div class="c-body">
    <p class="meta"><span class="tag">{p['tag']}</span> · <time datetime="{p['date']}">{fmt_date(p['date'])}</time></p>
    <h2><span class="en">{html.escape(p['title'])}</span><span class="de">{html.escape(p['de'])}</span></h2>
    <p>{html.escape(p['summary'])}</p></div></a>""" for p in posts)
    body = f"""<header class="b-hero" id="top"><div class="wrap">
  <p class="label">Blog</p>
  <h1><span class="en">Quantum physics, AI and research, explained.</span><span class="de">Quantenphysik, KI und Forschung, verständlich erklärt.</span></h1>
  <p class="lead"><span class="en">Articles from Deep Quantum Science: our research made accessible, with real simulations behind every figure.</span><span class="de">Artikel von Deep Quantum Science: unsere Forschung verständlich aufbereitet, mit echten Simulationen hinter jeder Abbildung. Die Artikel sind auf Englisch.</span></p>
</div></header>
<main><div class="wrap"><div class="cards">
{cards}
</div></div></main>"""
    (BLOG / 'index.html').write_text(page('Blog · Deep Quantum Science', 'Articles on quantum physics, AI and our research, explained with real simulations.', 'index.html', body, posts[0]['img']).replace(f'<link rel="canonical" href="{BASE}/blog/index.html">', f'<link rel="canonical" href="{BASE}/blog/">'), encoding='utf-8')
    items = '\n'.join(f"""<item><title>{html.escape(p['title'])}</title><link>{BASE}/blog/{p['slug']}.html</link><guid>{BASE}/blog/{p['slug']}.html</guid><pubDate>{datetime.datetime.fromisoformat(p['date']).strftime('%a, %d %b %Y 08:00:00 +0100')}</pubDate><description>{html.escape(p['summary'])}</description></item>""" for p in posts)
    (BLOG / 'feed.xml').write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Deep Quantum Science blog</title><link>{BASE}/blog/</link><description>Quantum physics, AI and research, explained.</description><language>en</language>
{items}
</channel></rss>
""", encoding='utf-8')
    urls = ['/', '/manuscript.html', '/blog/'] + [f"/blog/{p['slug']}.html" for p in posts]
    (SITE / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      '\n'.join(f'<url><loc>{BASE}{u}</loc></url>' for u in urls) + '\n</urlset>\n', encoding='utf-8')
    print('built', len(posts), 'posts')

if __name__ == '__main__':
    build()
