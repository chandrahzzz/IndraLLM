
---

# PART B — Detailed build specification

The handoff prompt above (Part A) is authoritative for rules and task scope. Part B gives the detail
needed to execute the task without re-deriving anything. Where Part B gives a formatting value from
memory, it is marked **[verify]**: confirm it against the current official ACL/ARR guidelines before using
it.

## B1. ACL-family formatting specification (to verify against the current official guidelines)

### B1.1 Page and layout

| Property | Value | Note |
|---|---|---|
| Paper size | A4 (21.0 × 29.7 cm) | [verify]; ACL requires A4, not US Letter |
| Margins | 2.5 cm top, bottom, left and right | [verify] |
| Columns | Two, each 7.7 cm wide, with a 0.6 cm gap | [verify]; total text width 16.0 cm |
| Title block | Spans both columns at the top of page 1 | Title, then author block (camera-ready only), then abstract in the left column |
| Page numbers | Not required in the review PDF if the style file adds them; follow the current guideline | [verify] |
| Line numbers | The review version of the LaTeX style prints line numbers in the margins | [verify]; reproduce in Word with line numbering (w:lnNumType) restarting each page, if required |
| Content limit | Long paper: 8 pages; short paper: 4 pages | [verify]; references, Limitations, Ethics and appendices do not count |
| Camera-ready | Usually one extra page | [verify] |

### B1.2 Typography

| Element | Font / size / style | Note |
|---|---|---|
| Body text | Times New Roman 11 pt, single spacing, justified | [verify] |
| Title | 15 pt bold, centred | [verify] |
| Author block | 12 pt, centred; omitted in review version | [verify] |
| "Abstract" heading | 12 pt bold, centred | [verify] |
| Abstract text | 10 pt, indented about 0.6 cm on both sides | [verify] |
| Section headings | 12 pt bold, numbered "1 Introduction" | [verify] |
| Subsection headings | 11 pt bold, numbered "1.1 …" | [verify] |
| Captions | 10 pt; "Table 1:" and "Figure 1:" prefixes; table captions are usually placed **below** tables in ACL style | [verify] the placement in the current template |
| Footnotes | 9 pt | [verify] |
| References | 10 pt, author–year (natbib/ACL style), hanging indent, alphabetical | [verify] |
| Code and identifiers | Monospace (Courier New), 9–10 pt | e.g. `qwen/qwen3.8-27b` |
| Condition names | Small caps (lowercase text with the small-caps property) | Project convention |
| Indic scripts | Nirmala UI fallback for Devanagari, Bengali, Tamil, Telugu and Kannada | Check glyph rendering in the PDF |

### B1.3 Required and optional sections (ARR)

1. Title; anonymous author block (review) or real author block (camera-ready).
2. Abstract (single paragraph; keep at about 200 words or less if the venue asks — [verify]).
3. Body: introduction through conclusion, within the page limit.
4. **Limitations**: mandatory, unnumbered, after the conclusion and before the references; does not count
   toward the page limit [verify].
5. **Ethics Statement / Broader Impact**: optional, after Limitations [verify].
6. Acknowledgements: camera-ready only.
7. References.
8. Appendices, lettered A, B, C, …, after the references.

### B1.4 Anonymity rules (review version)

* No author names, affiliations or emails.
* No links to the author's GitHub (`chandrahzzz/IndraLLM`). Write "Code and data will be released upon
  publication" or use an anonymised repository link if the venue allows.
* No acknowledgements, so no reviewer names.
* Self-citation in the third person only. The paper does not currently cite the author's own prior work.
* Remove identifying file metadata: set the DOCX core properties author and last-modified-by to empty or
  "Anonymous", and check the PDF metadata.

### B1.5 Implementing ACL style in Word with python-docx (recipe)

```python
import docx
from docx.shared import Cm, Pt
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

d = docx.Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, side, Cm(2.5))

def set_columns(section, num, space_cm=0.6):
    sectPr = section._sectPr
    cols = sectPr.find(qn("w:cols")) or OxmlElement("w:cols")
    cols.set(qn("w:num"), str(num))
    cols.set(qn("w:space"), str(int(space_cm * 567)))   # twips (1 cm = 567 twips)
    if cols.getparent() is None:
        sectPr.append(cols)

# Title block in a one-column section, then a continuous break into two columns
set_columns(sec, 1)
# ... add title, (author), abstract ...
new = d.add_section(WD_SECTION.CONTINUOUS)
set_columns(new, 2)

# Base style
st = d.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.element.rPr.rFonts.set(qn("w:cs"), "Nirmala UI")       # complex-script fallback for Indic text
st.paragraph_format.space_after = Pt(0)

# Line numbering for the review version (if required)
ln = OxmlElement("w:lnNumType")
ln.set(qn("w:countBy"), "1"); ln.set(qn("w:restart"), "newPage")
new._sectPr.append(ln)
```

* **Full-width figures and tables.** Either insert a continuous section break with one column before the
  float and another back to two columns after it (the IEEE source uses this pattern), or place the float
  at the top of a page in a one-column section. Keep floats near their first reference.
* **Captions.** Use a caption paragraph style (10 pt) and turn on `keep_with_next` so the caption and its
  table never split. A previous build lost header rows when tables were filled without a header row, so
  always write headers explicitly.
* **Small caps.** `run.font.small_caps = True` with lowercase text. `docx_helpers.add_runs` already does
  this for the condition names EN-ORIG, EN-MATCH, CS-LAT, ROMAN, NATIVE and MIXED.
* **Hanging-indent references.** `paragraph_format.left_indent = Cm(0.5)`,
  `first_line_indent = Cm(-0.5)`.
* **Headings.** Create numbered heading styles manually ("1 Introduction"); do not rely on Word's
  automatic numbering, which renders inconsistently.
* **Figures.** `d.add_picture(path, width=Cm(7.7))` for one column; `Cm(16.0)` for full width.

### B1.6 Exporting to PDF with Word (Windows)

```powershell
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
try {
  $doc = $w.Documents.Open("<abs path>.docx", $false, $true)
  $doc.ExportAsFixedFormat("<abs path>.pdf", 17)
  $doc.Close([ref]0)
} finally { $w.Quit(); [System.Runtime.Interopservices.Marshal]::ReleaseComObject($w) | Out-Null }
```

* This may need the sandbox disabled, and it needs the author's permission because it starts Word.
* **Known failure:** `CO_E_SERVER_EXEC_FAILURE` (0x80080005). It occurred when the author had Word open
  with a Product Activation prompt (PID 67028) and after an earlier automation instance was left running.
  * Ask the author to close Word, or to export manually (File → Save As → PDF).
  * Do not kill the author's Word process yourself.
* After export, render every page:

```python
import pymupdf
doc = pymupdf.open(pdf)
for i, p in enumerate(doc):
    p.get_pixmap(dpi=100).save(f"page_{i+1:02d}.png")
```

Then read every page image.

## B2. Citation conversion: IEEE numeric to ACL author–year

All 27 references exist. [1]–[22] are from the original manuscript; [23]–[27] were verified on ACL
Anthology or arXiv on 2026-10-10. Full bibliographic entries are in the original DOCX (paragraphs after
"REFERENCES") and in `build_paper.py` `NEW_REFS`.

| IEEE # | ACL in-text form | Work |
|---|---|---|
| [1] | Ahuja et al. (2023) | MEGA: Multilingual evaluation of generative AI (EMNLP 2023) |
| [2] | Kakwani et al. (2020) | IndicNLPSuite (Findings of EMNLP 2020) |
| [3] | Doddapaneni et al. (2023) | Towards leaving no Indic language behind / IndicXTREME (ACL 2023) |
| [4] | Khanuja et al. (2020) | GLUECoS (ACL 2020) |
| [5] | Ahia et al. (2023) | Do all languages cost the same? Tokenization in the era of commercial language models (EMNLP 2023) |
| [6] | Petrov et al. (2023) | Language model tokenizers introduce unfairness between languages (NeurIPS 2023) |
| [7] | Rust et al. (2021) | How good is your tokenizer? (ACL 2021) |
| [8] | Zhang et al. (2023) | Multilingual large language models are not (yet) code-switchers (EMNLP 2023) |
| [9] | Yong et al. (2023) | Prompting multilingual LLMs to generate code-mixed texts (CALCS workshop 2023) |
| [10] | Sennrich et al. (2016) | Neural machine translation of rare words with subword units (ACL 2016) |
| [11] | Lin et al. (2022) | TruthfulQA (ACL 2022) |
| [12] | Min et al. (2023) | FActScore (EMNLP 2023) |
| [13] | Zheng et al. (2023) | Judging LLM-as-a-judge with MT-Bench and Chatbot Arena (NeurIPS 2023 D&B) |
| [14] | Bari et al. (2024) | ALLaM (arXiv:2407.15390) |
| [15] | McNemar (1947) | Note on the sampling error of the difference between correlated proportions (Psychometrika) |
| [16] | Holm (1979) | A simple sequentially rejective multiple test procedure (Scand. J. Statistics) |
| [17] | Wilson (1927) | Probable inference, the law of succession, and statistical inference (JASA) |
| [18] | Liang and Zeger (1986) | Longitudinal data analysis using generalized linear models (Biometrika) |
| [19] | Cameron et al. (2008) | Bootstrap-based improvements for inference with clustered errors (REStat) |
| [20] | Mancl and DeRouen (2001) | A covariance estimator for GEE with improved small-sample properties (Biometrics) |
| [21] | Kish (1965) | Survey Sampling (Wiley) |
| [22] | Rogan and Gladen (1978) | Estimating prevalence from the results of a screening test (Am. J. Epidemiology) |
| [23] | Husain et al. (2024) | RomanSetu (ACL 2024) |
| [24] | Wang et al. (2024) | Large language models are not fair evaluators (ACL 2024) |
| [25] | Dubois et al. (2024) | Length-controlled AlpacaEval (arXiv:2404.04475) |
| [26] | Watts et al. (2024) | PARIKSHA (EMNLP 2024, pp. 7900–7932) |
| [27] | Fu and Liu (2025) | How reliable is multilingual LLM-as-a-judge? (Findings of EMNLP 2025, pp. 11040–11053) |

**Conversion rules:**
* "[5], [6]" becomes "(Ahia et al., 2023; Petrov et al., 2023)".
* When a citation is the subject of a sentence, use the textual form: "Ahia et al. (2023) show …".
* Sort the reference list alphabetically by first author.
* Write a regex check that no "[n]" numeric citation remains in the body text. Table cells may contain
  bracketed intervals such as "[40, 80]"; exclude those from the check.

## B3. ACL 8-page content plan (section → source text → budget)

Text keys refer to `TEXT[...]` in `build_paper.py`. Word budgets are targets for about 8 pages with
2 full-width figures, 1 one-column figure and 4 tables in the body. Adjust after rendering.

| ACL section | Source text keys | Target words | Floats |
|---|---|---|---|
| Title, Abstract | `title`, `abstract` | ≤ 200 (abstract) | — |
| 1 Introduction | 7 (farmer example; original text), 8, `9`, `13` (RQs), `14` (contributions), `15` (findings) | 750 | Table 1 (prompts, full width or one column) |
| 2 Related Work | `18`, `19`, `20` + code-switching paragraph (original ¶17) | 300 | — |
| 3 Benchmark and Design | 27 (original), `28`, `30`, 31 (original), `34` (gold, shortened) | 600 | — |
| 4 Experimental Setup | `36`, `37`, `38`, `39`, `40` (shortened: keep units explanation, tests, multiplicity, planning status) | 600 | Figure 1 (design, full width) |
| 5 Results at 128 Tokens | `43`, `53`, `55`, `57`, `59` (condensed), `65` | 650 | Table 2 (accuracy, full width), Figure 2 (one column, panel a only or compact) |
| 6 Output Budget | `75`, `76`, `77` | 650 | Table 3 (budgets × judges, full width), Figure 5 (one column, panel b) |
| 7 Judge Dependence | `79`, short version of `80` | 450 | Table 4 (agreement) |
| 8 Discussion and Conclusion | `83`, `84` | 300 | — |
| Limitations (unnumbered) | `87` | 300 (not counted) | — |
| Ethics Statement | `89` | 120 (not counted) | — |
| References | 27 entries | — | — |
| Appendix A Benchmark | `94`, A.2 text, gold notes | — | Table 7 (topics + provisions) |
| Appendix B Additional results | `appB`, all pairwise, GEE, per-language, ALLaM (`66`) | — | Tables 8, 9; Figures 3, 4 |
| Appendix C Tokenization | `69` | — | Figure 5 panels a, c |
| Appendix D Judge details | tipping points (`80`, Table 5), claims (Table 6), rubric (`110`) | — | Tables 5, 6 |
| Appendix E Audit | truncation, complete answers, Holm-18 (from `numbers_audit.json`) | — | new tables |
| Appendix F Design calculation | `112` | — | — |
| Appendix G Reproducibility | `114`, `91` (anonymised) | — | — |

**Shortening guidance:**
* Keep every qualification. Section 6 of Part A lists the required wording.
* Remove repeated numbers: each number appears once in prose, or once in a table and is referenced.
* Keep these in the body:
  * the three-budget table;
  * the judge-agreement table;
  * the statement that no human evaluation was performed;
  * the 64% MIXED capped-at-1,024 caveat;
  * Holm-18 for the English result;
  * the word-identical (hi, bn, ta) sensitivity result;
  * the judge-configuration discovery.
* Figure 5 may be split: panel (b) (accuracy across budgets) in the body; panels (a) and (c) in the
  appendix. Regenerate with `make_figures.py` changes if split. Keep fonts at least about 7 pt.

## B4. ACL figure and table sizing

| Float | Current file | ACL placement | Width |
|---|---|---|---|
| Figure 1 (design) | `fig1.png` (6.6 × 3.25 in at 300 dpi) | Full width, top of page 2 or 3 | 16 cm |
| Figure 2 (accuracy + heatmap) | `fig2.png` | Body: panel (a) only, one column; full figure in appendix | 7.7 cm / 16 cm |
| Figure 3 (per language) | `fig3.png` | Appendix | 7.7 cm |
| Figure 4 (GEE + per-topic) | `fig4.png` | Appendix | 16 cm |
| Figure 5 (budgets) | `fig5.png` | Body: panel (b) one column; full figure in appendix | 7.7 cm / 16 cm |
| Table 1 (prompts) | built in code | Body, one column if prompts wrap acceptably, else full width | — |
| Table 2 (accuracy) | built in code | Body, full width (10 columns) | 16 cm |
| Table 3 (budgets) | built in code | Body, full width (8 columns) | 16 cm |
| Table 4 (agreement) | built in code | Body, one column (6 columns) | 7.7 cm |

To split figures, add functions to `make_figures.py` (e.g. `fig5b_only`) with
`figsize=(3.03, 2.4)` inches (7.7 cm wide) and font size about 7 pt.

## B5. Prompt templates (exactly as used; source of truth: `research/PROMPT_VALIDATION_PROTOCOL.md`)

(The generated section at the end of this file reproduces them from the protocol file.)

## B6. Verification checklist (complete before reporting done)

| # | Check | How | Pass criterion |
|---|---|---|---|
| 1 | Page count | Render PDF | ≤ 8 content pages before Limitations |
| 2 | Paper size and margins | PDF page size; visual | A4; margins as specified |
| 3 | Two columns, widths | Visual | 7.7 cm columns, 0.6 cm gap |
| 4 | Fonts | PDF font list (`pymupdf` `page.get_fonts()`) | Times New Roman body; Indic fonts embedded |
| 5 | Indic glyphs | Visual, Table 1 and §3 | Devanagari, Telugu and Kannada words render (no boxes) |
| 6 | Small caps | Visual | Condition names in small caps |
| 7 | Tables | Visual | Every table has a header row; no clipped cells; captions attached |
| 8 | Figures | Visual | Readable labels (at least about 7 pt); correct figure numbers |
| 9 | Citations | Regex over text | No IEEE numeric citations remain; every author–year key appears in the reference list |
| 10 | Section order | Visual | Body → Limitations → Ethics → References → Appendices |
| 11 | Anonymity | Text search + file metadata | No author name, email, GitHub link or reviewer names in the review version |
| 12 | Numbers | `independent_check.py` | 118/118 pass |
| 13 | Forbidden phrasing | Regex over built text (Part A §6 list) | No unqualified hits |
| 14 | Consistency | Compare body numbers with `numbers_*.json` | All match |
| 15 | No IEEE remnants | Text search | No "Index Terms", roman section numerals or IEEE author block |

## B7. Pitfalls met in the previous session (avoid repeating them)

1. **Heredoc and escape handling in Git Bash.** Python code passed through `python - <<'EOF'` turned `\\n`
   inside strings into real newlines when written to files, which broke string literals. Use the Edit tool
   for code containing `\n`, or write scripts to files with the Write tool.
2. **Silent string replacements.** `str.replace` with no match fails silently. `build_paper.py` asserts that
   required phrases are present after replacement. Keep that pattern.
3. **Table header loss.** `fill_table(table, rows)` without `header=` overwrote header rows. Always pass
   headers.
4. **Word COM.** Covered in B1.6.
5. **Groq rate limits.** 32,000 output tokens per minute for qwen3.8-27b. Use at most 3 workers with
   backoff. Not relevant unless the author approves new runs.
6. **Hosted greedy decoding is not fully deterministic.** Re-running generation will not exactly reproduce
   outputs. The analysis is reproducible from the saved outputs.
7. **The generated markdown and the DOCX must stay in sync.** Regenerate the guide and report after any
   text change: `dump_report_parts.py`, then `make_guide.py`.

## B8. Draft answers for the ACL Responsible NLP checklist (to adapt; verify current questions)

Answer truthfully; these drafts reflect what was actually done.

* **A. Limitations and risks.** Limitations section present (unnumbered, after the conclusion). Risks: the
  benchmark contains legal and policy facts that become outdated (one already has); it is not legal
  advice. Over- or under-stated gaps could mislead deployment decisions; the paper reports dependence on
  budget and judge.
* **B. Artifacts:**
  * Used: the Qwen3.8-27B (Apache-2.0) and gpt-oss-120b models via the Groq API, and ALLaM-2-7B via the
    Groq API.
  * Created: the benchmark prompts and judgements (to be released).
  * Licence for the released data: to be decided by the author.
  * No personal data.
  * The topic content is public-policy facts.
* **C. Computational experiments:**
  * hosted API inference only; no training;
  * decoding: greedy (temperature 0, top-p 1); budgets 128, 512 and 1,024 tokens;
  * cost of the revision runs: $1.10 + $1.23 at list prices;
  * single run, with the determinism caveat (prefix-consistency figures);
  * statistics: exact tests, permutation, bootstrap, Holm; code released.
* **D. Human subjects / annotators:**
  * No human annotation of model outputs was performed.
  * Fluent speakers (the author, a teammate and two friends) reviewed prompt templates informally as
    volunteers. No payment and no personal data are documented. **Ask the author** to confirm payment
    status and consent to be named before filling this in.
  * No IRB review is documented.
* **E. AI assistants.** ARR asks authors to disclose use of AI assistants. An AI coding assistant (Claude)
  was used for code auditing, analysis scripts, experiment scripts and drafting and revising manuscript
  text. **Ask the author** how they want to disclose this, and follow the venue's current AI policy. Do
  not omit it.

## B9. Final message template to the author (fill in only verified facts)

```
Built: paper_v2/acl/IndraLLM_ACL_review.docx (+ .pdf) [and camera-ready version].
Format: <venue + guideline version/date checked>; A4, two columns, Times 11 pt, <N> content pages.
Checks passed: <list from B6 with evidence>; checks failed or not done: <list>.
Changes vs build_paper.py text: see paper_v2/acl/CHANGELOG_ACL.md (<k> shortenings, <m> moves to appendix).
Still open: human annotation; venue choice/dates; optional uncapped run (needs approval).
```

---

# PART C — Generated reference material

Part C is generated from the repository files (prompt protocol, gold ledger and result JSON) by
`paper_v2/scripts/make_handoff_full.py`. Do not edit it by hand; regenerate it.

