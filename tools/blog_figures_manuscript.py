"""Diagrams for the blog article on how DeepQ Manuscript is built."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image
import io, sys
BG = '#0b0724'; PANEL = '#1b1545'; MINT = '#92ffd8'; TXT = '#f3f1ff'; MUTED = '#aaa6cc'; WARM = '#ffcf6b'; ROSE = '#ff7aa8'; SKY = '#8fb8ff'
plt.rcParams.update({'font.family': 'Inter', 'mathtext.fontset': 'cm', 'text.color': TXT})
OUT = sys.argv[1]

def box(ax, x, y, w, h, title, sub='', col=MINT, fs=15):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=PANEL, ec=col, lw=2))
    ax.text(x + w / 2, y + h * (0.64 if sub else 0.5), title, ha='center', va='center', fontsize=fs, color=TXT, weight='bold')
    if sub: ax.text(x + w / 2, y + h * 0.3, sub, ha='center', va='center', fontsize=fs - 4, color=MUTED, linespacing=1.3)
def arr(ax, a, b, col=MUTED, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=18, lw=2, color=col, connectionstyle=f'arc3,rad={rad}'))
def save(fig, name):
    buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=110, facecolor=BG); plt.close(fig)
    Image.open(buf).convert('RGB').save(f'{OUT}/{name}.webp', quality=88)

# 1. pipeline
fig = plt.figure(figsize=(14, 7.2), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 14); ax.set_ylim(0, 7.2); ax.axis('off')
ax.text(0.4, 6.75, 'The conversion pipeline', fontsize=22, color=MINT)
steps = [('Input', 'DOCX · TEX · ZIP', SKY), ('Safety gate', 'size, paths,\nno execution', ROSE), ('Pre-processing', 'flatten, macros,\nmarkers', WARM),
         ('Document tree', 'one neutral AST\n(Pandoc JSON)', MINT), ('Semantic passes', 'math, references,\nbibliography, figures', WARM),
         ('Writer', 'LaTeX or Word', SKY), ('Post-processing', 'Word XML / TeX\nrepairs', WARM), ('Check & report', 'diagnostics,\noptional PDF', MINT)]
xs = [0.4, 3.75, 7.1, 10.45]
for i, (t, s, c) in enumerate(steps):
    r, k = divmod(i, 4); x = xs[k] if r == 0 else xs[3 - k]; y = 4.3 if r == 0 else 1.2
    box(ax, x, y, 3.0, 1.7, t, s, c)
for k in range(3):
    arr(ax, (xs[k] + 3.05, 5.15), (xs[k + 1] - 0.05, 5.15))
    arr(ax, (xs[3 - k] - 0.05, 2.05), (xs[2 - k] + 3.05, 2.05))
arr(ax, (11.95, 4.25), (11.95, 2.95), MINT)
ax.text(7.0, 0.45, 'Everything runs locally. The source document is parsed, never executed.', ha='center', fontsize=14, color=MUTED)
save(fig, 'dq-pipeline')

# 2. desktop architecture
fig = plt.figure(figsize=(14, 5.6), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 14); ax.set_ylim(0, 5.6); ax.axis('off')
ax.text(0.4, 5.1, 'Inside the desktop application', fontsize=22, color=MINT)
box(ax, 0.4, 1.6, 3.3, 2.6, 'Desktop window', 'native launcher\n+ embedded web view\n(the user interface)', SKY)
box(ax, 5.2, 1.6, 3.6, 2.6, 'Local service', 'listens on 127.0.0.1 only\nper-session secret token\njob queue + progress', WARM)
box(ax, 10.3, 2.95, 3.3, 1.5, 'Conversion engine', 'embedded runtime', MINT)
box(ax, 10.3, 1.1, 3.3, 1.5, 'Licence store', 'offline signature check\ntrial ledger', ROSE)
arr(ax, (3.75, 2.9), (5.15, 2.9)); arr(ax, (8.85, 3.4), (10.25, 3.7)); arr(ax, (8.85, 2.4), (10.25, 1.85))
ax.text(4.45, 3.1, 'HTTP', ha='center', fontsize=12, color=MUTED)
ax.text(7.0, 0.45, 'No cloud: documents never leave the computer.', ha='center', fontsize=14, color=MUTED)
save(fig, 'dq-architecture')

# 3. numbered equation as a three-column table
fig = plt.figure(figsize=(14, 4.6), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 14); ax.set_ylim(0, 4.6); ax.axis('off')
ax.text(0.4, 4.1, 'A numbered equation in Word: an invisible three-column table', fontsize=20, color=MINT)
x0, w = 0.8, 12.4; ws = [1.6, 9.2, 1.6]; xx = x0
for i, (ww, lab) in enumerate(zip(ws, ['spacer', 'centred equation', 'number'])):
    ax.add_patch(plt.Rectangle((xx, 1.4), ww, 1.6, fill=False, ec=MUTED, lw=1.5, ls='--'))
    ax.text(xx + ww / 2, 1.05, lab, ha='center', fontsize=13, color=MUTED); xx += ww
ax.text(x0 + ws[0] + ws[1] / 2, 2.2, r'$E_n=\epsilon_n+\lambda^2\sum_m\frac{|\Delta_{nm}|^2}{\epsilon_n-\epsilon_m}$', ha='center', va='center', fontsize=26, color=TXT)
ax.text(x0 + sum(ws) - ws[2] / 2, 2.2, '(12)', ha='center', va='center', fontsize=20, color=WARM)
ax.annotate('', xy=(x0, 0.6), xytext=(x0 + sum(ws), 0.6), arrowprops=dict(arrowstyle='<->', color=SKY, lw=1.5))
ax.text(x0 + sum(ws) / 2, 0.25, 'width = text width of the page section (margins and columns taken into account)', ha='center', fontsize=12, color=SKY)
save(fig, 'dq-equation-table')

# 4. cross references: two passes
fig = plt.figure(figsize=(14, 5.4), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 14); ax.set_ylim(0, 5.4); ax.axis('off')
ax.text(0.4, 4.9, 'Cross-references in two passes', fontsize=22, color=MINT)
src = ['\\section{Model}', '\\begin{equation}\\label{eq:H} ...', '\\begin{figure}...\\label{fig:graph}', 'see Eq.~\\eqref{eq:H} and Fig.~\\ref{fig:graph}']
for i, s in enumerate(src):
    ax.text(0.5, 4.0 - i * 0.72, s, fontsize=14, color=TXT, family='monospace')
box(ax, 7.6, 2.75, 2.6, 1.6, 'Pass 1', 'walk the source,\nassign numbers', WARM)
box(ax, 10.9, 2.75, 2.7, 1.6, 'Label table', 'eq:H → (1)\nfig:graph → 1', MINT)
box(ax, 9.25, 0.5, 2.8, 1.6, 'Pass 2', 'replace each \\ref\nby number + link', SKY)
arr(ax, (6.9, 3.55), (7.55, 3.55)); arr(ax, (10.25, 3.55), (10.85, 3.55)); arr(ax, (12.2, 2.7), (11.4, 2.15)); arr(ax, (6.9, 1.6), (9.2, 1.3))
ax.text(0.5, 0.35, 'Result in Word: "see Eq. (1) and Fig. 1",\nclickable, unresolved labels shown as ??', fontsize=13, color=MUTED, linespacing=1.4)
save(fig, 'dq-crossref')

# 5. round trip
fig = plt.figure(figsize=(14, 4.6), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 14); ax.set_ylim(0, 4.6); ax.axis('off')
ax.text(0.4, 4.1, 'Round trip: LaTeX → Word → LaTeX', fontsize=22, color=MINT)
box(ax, 0.5, 1.3, 3.2, 2.0, 'LaTeX project', 'labels, BibTeX,\nnumbering scope', SKY)
box(ax, 5.4, 1.3, 3.2, 2.0, 'Word document', 'readable text\n+ hidden manifest\n(custom XML part)', WARM)
box(ax, 10.3, 1.3, 3.2, 2.0, 'LaTeX again', 'labels and\nbibliography restored', MINT)
arr(ax, (3.75, 2.3), (5.35, 2.3)); arr(ax, (8.65, 2.3), (10.25, 2.3))
ax.text(7.0, 0.55, 'Co-authors edit in Word; the hidden manifest keeps what Word cannot represent.', ha='center', fontsize=14, color=MUTED)
save(fig, 'dq-roundtrip')
print('ok')
