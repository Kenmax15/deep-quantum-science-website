"""Article: how DeepQ Manuscript is designed (figures and algorithms, no source code). Text and figures: CC BY 4.0."""

POST = dict(
 slug='how-deepq-manuscript-works', date='2026-11-04', tag='Software · Open design',
 title='How to build a Word \u21c4 LaTeX converter: the design of DeepQ Manuscript',
 de='Wie man einen Word-\u21c4-LaTeX-Konverter baut',
 summary='The architecture and the algorithms behind DeepQ Manuscript, explained step by step with figures and pseudocode. Free to read, reuse and build upon.',
 img='dq-pipeline.webp',
 watch_img='../assets/manuscript-app.webp',
 video=('../manuscript.html', 'DeepQ Manuscript: free trial, 5 conversions each way', 'Windows 10/11 · runs locally'),
 footer='<div class="note"><b>Licence.</b> The text and figures of this article are released under the <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">Creative Commons Attribution 4.0</a> licence: you may copy, adapt and reuse them, including commercially, as long as you credit Deep Quantum Science. The conversion relies on the open-source <a href="https://pandoc.org" target="_blank" rel="noopener">Pandoc</a> project, whose authors we thank.</div>',
 body="""
<p>Scientists write in two worlds. Many collaborators, journals and funding agencies expect Word; most physicists and mathematicians write in LaTeX. Moving a manuscript between the two by hand means retyping equations, renumbering references and rebuilding the bibliography. DeepQ Manuscript automates this, in both directions. In this article we describe how it is built, so that anyone can understand, reproduce or improve the approach. We show the architecture and the algorithms; we do not publish source code.</p>

<h2>1. Why naive conversion fails</h2>
<p>A document is more than its text. The hard parts are the <i>semantics</i> that the two formats store very differently:</p>
<table>
<tr><th>Element</th><th>LaTeX</th><th>Word</th></tr>
<tr><td>Equations</td><td>TeX source, user macros (\\newcommand)</td><td>Office Math (OMML) objects</td></tr>
<tr><td>Numbering</td><td>computed at compile time from \\label</td><td>fields, bookmarks, or plain typed numbers</td></tr>
<tr><td>References</td><td>\\ref, \\eqref, \\cite</td><td>REF and citation fields, or plain text</td></tr>
<tr><td>Bibliography</td><td>BibTeX database</td><td>source records in a hidden XML part</td></tr>
<tr><td>Project</td><td>many files (\\input, figures)</td><td>one container (DOCX = ZIP of XML)</td></tr>
</table>
<p>A good converter must therefore understand the document, not just copy text. Our design rests on four principles:</p>
<ol>
<li><b>Local first.</b> Manuscripts are confidential before publication. Everything runs on the user's computer; no cloud.</li>
<li><b>Parse, never execute.</b> A LaTeX file is a program. We read it as data and never run it during conversion.</li>
<li><b>One neutral representation.</b> Both directions go through the same document tree, so every improvement helps both ways.</li>
<li><b>Honest output.</b> When something cannot be converted safely, keep it visible and report it, rather than silently dropping it.</li>
</ol>

<h2>2. The pipeline</h2>
<figure><img src="img/dq-pipeline.webp" alt="Pipeline: input, safety gate, pre-processing, document tree, semantic passes, writer, post-processing, check and report" loading="lazy"><figcaption>Figure 1. Every conversion follows the same eight stages.</figcaption></figure>
<p>The central object is a <b>document tree</b> (an abstract syntax tree, AST): headings, paragraphs, equations, figures, tables, citations and links as typed nodes. We use the open-source universal document converter Pandoc to read a source into this tree and to write the tree into the target format. Our own work lives around it: preparing the input so that nothing is lost on the way in, enriching the tree with semantics, and repairing the output so that it behaves like a document written by hand.</p>
<p class="algo-title">Algorithm 1 · Conversion</p>
<pre class="algo"><b>input</b>  source file S, options O
<b>output</b> converted document T, report R

check S with the safety gate                            <i># Algorithm 2</i>
<b>if</b> S is a Word file:
    plant markers for captions, bookmarks, fields   <i># Algorithm 6</i>
<b>else</b>:                                               <i># LaTeX file or project</i>
    flatten the project into one source              <i># Algorithm 3</i>
    collect user math macros
    build the cross-reference plan                   <i># Algorithm 4</i>
tree ← parse(S)                                      <i># sandboxed, no execution</i>
apply semantic passes to tree: math, references, bibliography, figures
T ← write(tree)
repair T in its native format                        <i># Algorithms 5 and 7</i>
R ← quality checks (+ optional PDF build)
<b>return</b> T, R</pre>

<h2>3. The safety gate</h2>
<p>Word files and LaTeX projects arrive as ZIP archives, and ZIP archives can be hostile: a tiny file that expands to gigabytes, or entries that try to write outside the working folder.</p>
<p class="algo-title">Algorithm 2 · Safe archive</p>
<pre class="algo"><b>reject</b> if file size &gt; 30 MB
<b>for each</b> entry e in the archive:
    <b>reject</b> if total expanded size &gt; 100 MB or number of entries &gt; 1000
    <b>reject</b> if path(e) is absolute, contains "..", a drive letter or a backslash
    <b>reject</b> if e is a symbolic link
<b>extract</b> into a fresh private working folder</pre>
<p>Parsing then runs in a sandbox mode that forbids reading or writing files the parser was not explicitly given, with a time limit. When a PDF is requested, the LaTeX compiler runs with shell escape disabled.</p>

<h2>4. LaTeX to Word</h2>
<p><b>Flattening.</b> Real projects split the text into chapters with \\input and \\include. We merge them into one source, but only inside the project folder, with a size budget and protection against files that include each other in a loop. Commands that could read or write files, or run programs, are refused.</p>
<p class="algo-title">Algorithm 3 · Flatten a project</p>
<pre class="algo">flatten(file f, visited V, budget B):
    <b>if</b> f ∈ V or f is outside the project root: <b>stop</b> (cycle or escape)
    <b>if</b> |V| &gt; 30: <b>stop</b> (nesting too deep)
    text ← read(f); B ← B − size(text); <b>if</b> B &lt; 0: <b>stop</b>
    remove comments
    <b>reject</b> primitives that touch files or run commands
        (\\write18, \\openout, \\read, \\directlua, \\catcode, ...)
    <b>for each</b> \\input{g} or \\include{g} in text:
        replace it by flatten(g, V ∪ {f}, B)
    <b>check</b> that every \\includegraphics path stays inside the project
    <b>return</b> text</pre>
<p><b>Cross-references.</b> LaTeX numbers equations, figures and sections only when it compiles. Word has no compiler, so we compute the numbers ourselves, in two passes, for a chosen numbering scope (continuous, per chapter, per section).</p>
<figure><img src="img/dq-crossref.webp" alt="Two-pass cross-referencing: assign numbers, then replace references" loading="lazy"><figcaption>Figure 2. Pass 1 builds a table from labels to numbers; pass 2 rewrites every reference as the number plus a clickable link.</figcaption></figure>
<p class="algo-title">Algorithm 4 · Cross-references</p>
<pre class="algo"><i># pass 1</i>
counters ← 0 for sections, equations, figures, tables
<b>walk</b> the source in reading order:
    on a heading at depth d: increment its counter, reset deeper ones
                             (and the equation counter if the scope says so)
    on a numbered equation, figure or table: increment its counter
    on \\label{k}: table[k] ← (kind, current number, anchor)
<i># pass 2</i>
<b>for each</b> \\ref{k}, \\eqref{k}, \\autoref{k}:
    <b>if</b> k ∈ table: replace by its number (in parentheses for \\eqref) + link
    <b>else</b>: write "??" and list k in the report</pre>
<p><b>Mathematics.</b> Each equation is converted to Office Math. Before that, user macros are expanded (with a depth limit, so a recursive macro cannot hang the program) and unusual environments are mapped to standard ones. If an equation still cannot be converted, it is not dropped: it stays in the Word file as clearly marked LaTeX text, and a file EQUATIONS_TO_REVIEW lists each one with the reason. This "graceful degradation" is what makes the tool trustworthy on real manuscripts.</p>
<p><b>Numbered equations in Word.</b> Word has no built-in equivalent of a centred equation with its number on the right margin. We build it from an invisible three-column table whose width is computed from the page margins and columns of the current section.</p>
<figure><img src="img/dq-equation-table.webp" alt="A numbered equation laid out as a borderless three-column table" loading="lazy"><figcaption>Figure 3. Spacer, centred equation, number: the classic layout of a numbered display equation, rebuilt in Word.</figcaption></figure>
<p class="algo-title">Algorithm 5 · Number display equations in Word</p>
<pre class="algo"><b>for each</b> display equation E in the Word XML:
    W ← page width − margins, divided by the number of text columns
    n ← its number from the cross-reference table (or the next number)
    replace E by a borderless table with column widths
        (c, W − 2c, c), c ≈ W/12:  [ empty | E centred | "(n)" ]
    no borders, no cell margins, row may not split across pages</pre>

<h2>5. Word to LaTeX</h2>
<p>The difficulty in this direction is that the parser keeps the visible text but forgets much of the meaning: which paragraph is a caption, which bookmark a reference points to, which citation field belongs to which source. We solve this with <b>markers</b>.</p>
<p class="algo-title">Algorithm 6 · Recover Word semantics with markers</p>
<pre class="algo">P ← a random prefix (so markers cannot collide with real text)
<b>for each</b> caption, bookmark, REF field, citation field in the Word XML:
    insert an invisible text marker P+id before it
    record id → {kind, label, field instruction, source key}
tree ← parse(modified Word file)
<b>for each</b> marker found in the tree:
    look up its record and rewrite the node:
        caption   → figure or table caption + \\label
        bookmark  → \\label on the heading or equation
        REF field → \\ref or \\eqref
        citation  → \\cite{key}
remove all markers; report any that could not be resolved
bibliography ← Word source records converted to a BibTeX file</pre>
<p>Word's own bibliography list is removed when its source records are available, because those records are the authoritative data; otherwise the list would appear twice.</p>

<h2>6. The round trip</h2>
<p>A frequent workflow: the author writes in LaTeX, a co-author comments in Word, and the text comes back to LaTeX. Some LaTeX information has no place in Word (label names, BibTeX entries, the numbering scope). We store it in a small hidden manifest inside the Word file (a custom XML part, which Word preserves when the document is edited). When the file is converted back, the manifest restores labels and bibliography.</p>
<figure><img src="img/dq-roundtrip.webp" alt="Round trip LaTeX to Word to LaTeX with a hidden manifest" loading="lazy"><figcaption>Figure 4. The hidden manifest carries what Word cannot represent.</figcaption></figure>

<h2>7. Figures and the optional PDF</h2>
<ul>
<li>Single-page PDF figures, common in LaTeX, are rendered as images at up to 300 dpi for Word.</li>
<li>In the other direction, images can be exported as PNG, JPEG or PDF; PDF output embeds the pixels losslessly (it does not invent vector graphics, and the report says so).</li>
<li>On request, the exported LaTeX project is compiled to PDF (several compiler passes plus BibTeX). The compiler log is translated into readable diagnostics: missing packages, undefined references, overfull lines.</li>
</ul>
<p class="algo-title">Algorithm 7 · Quality report</p>
<pre class="algo">R.counts      ← equations, figures, tables, citations in source and result
R.math        ← normalised, coloured, numbered, failed equations (with reasons)
R.references  ← resolved / unresolved labels
R.pdf         ← compiler passes and parsed diagnostics (if requested)
R.warnings    ← everything that needs a human look, without duplicates
write R as CHECK_REPORT.txt and report.json next to the result</pre>
<p>The report explicitly states what the checks do <i>not</i> guarantee: they detect structural problems and compiler messages, but they are not a measure of visual or mathematical fidelity. A careful human review remains part of the workflow.</p>

<h2>8. The desktop application</h2>
<figure><img src="img/dq-architecture.webp" alt="Desktop window, local service and conversion engine" loading="lazy"><figcaption>Figure 5. A native window displays a local web interface; a local service runs the engine.</figcaption></figure>
<ul>
<li><b>Interface.</b> A small native launcher opens a window with an embedded web view. The interface is ordinary HTML, which makes it easy to design and translate.</li>
<li><b>Local service.</b> The engine runs behind a service that only listens on the computer itself (127.0.0.1) and requires a secret token created for each session, so other programs or websites cannot use it.</li>
<li><b>Self-contained.</b> The installer ships its own language runtime and converter, so users install nothing else. Every third-party component is downloaded once and verified against a known checksum before it is packaged.</li>
<li><b>Licensing without servers.</b> A licence key is a small signed statement. The application contains only the public key and checks the signature offline; the private key never leaves the issuer. The free trial is a local counter of 5 conversions per direction.</li>
</ul>

<h2>9. Limits and lessons</h2>
<ul>
<li>Legacy equation objects (old Equation Editor, MathType OLE) are not editable math and are reported rather than converted.</li>
<li>Tracked changes are accepted during conversion; page references are not supported.</li>
<li>New installers are flagged by Windows SmartScreen until they build a reputation or are code-signed: distribution is part of engineering.</li>
<li>The most valuable feature turned out to be the report. Users forgive a converter that tells them exactly what to check; they do not forgive one that silently changes their science.</li>
</ul>
<p>We hope this blueprint helps others build better tools for scientists. If you build on it, we would love to hear about it.</p>
""")
