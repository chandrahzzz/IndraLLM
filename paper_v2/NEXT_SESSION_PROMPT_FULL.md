# PART A — Handoff: build the IndraLLM paper as a two-column, top-tier-conference Word document

You are continuing a research project. A previous session audited the paper, ran new experiments, fixed
the analysis and produced a revised manuscript. Your job is to turn that work into a **submission-ready,
two-column Word document (.docx) in the format of a top-tier NLP conference**, then render and check it.

Before writing anything, read the files listed in Section 2. This prompt summarises them, but they are the
source of truth. Every number in the paper must come from the result files, never from memory or from this
prompt.

---

## 0. Ground rules (the author's standing requirements)

1. **No fabrication of any kind.** That covers numbers, citations, experiments, reviewer counts, human
   annotations and validation results. If something was not done, say so.
2. **Every number comes from the JSON result files** in `paper_v2/output/`, read by a script. Do not type
   numbers by hand. The existing build scripts already do this; reuse them.
3. **Do not overclaim.** Section 6 lists the claims that are forbidden and the wording to use instead.
4. **No new API spending without explicit permission.**
   * The author's Groq budget target is $5 and the ceiling $10.
   * Estimated cumulative spend is already about $4.4.
   * Nothing in this task requires an API call.
5. **No `git push`.** Work on branch `paper-v2-revision`, commit locally, and end commit messages with the
   attribution line the environment gives you.
6. **Preserve originals.** Never modify `paper_v2/source/`, `results/EXP-002/` or
   `results/EXP-003-matched-en/`.
7. **Ask before outward-facing or hard-to-reverse actions**, such as killing processes the author did not
   start or closing their Word windows.
8. **Confirm a fact before stating it.** Do not claim a file was generated, a page count reached or a check
   passed unless you have done it.

---

## 1. Project in one paragraph

IndraLLM measures how the **representation** of a fixed factual question affects an LLM's judge-assessed
accuracy. The question is held fixed while its representation changes:
* English (EN-ORIG, original template; EN-MATCH, template matched to the other conditions);
* native Indic script (NATIVE);
* Romanized Indic (ROMAN);
* Latin-script code-switching (CS-LAT);
* mixed-script code-switching (MIXED: the same words as CS-LAT, but the Indic words in Brahmic script).

There are 100 propositions: 20 Indian public-policy topics × 5 languages (Hindi, Bengali, Tamil, Telugu,
Kannada). The model is `qwen/qwen3.8-27b` on Groq, under greedy decoding.

The original paper claimed that mixed script hurts accuracy. The audit showed that claim was an artefact of
a 128-token output cap and of judge configuration. The paper is now a **methodological** paper:

> *Evaluating multilingual LLMs across representation conditions is sensitive to output-token budgets and
> evaluator choice; observed differences should not automatically be interpreted as representation
> effects.*

---

## 2. Read these first (in this order)

| File | What it is |
|---|---|
| `paper_v2/FULL_REVISION_REPORT.md` (≈1,670 lines) | Complete record of everything done: procedures, results, change log, verdict. Section 20 is the post-review audit. Part G holds all generated tables and the final manuscript text |
| `paper_v2/MANUSCRIPT_BUILD_GUIDE.md` (v2, ≈770 lines) | Conventions, supported claims, forbidden claims, page plan, and all tables and text (generated) |
| `paper_v2/scripts/build_paper.py` | **Final manuscript text** (dictionary `TEXT`, partly inheriting from `build_revised_docx.py`) and the DOCX builder for the IEEE layout |
| `paper_v2/scripts/build_revised_docx.py` | Base text, `PROVISION` table, number-formatting helpers (`fp`, `sgn`, `neg`) |
| `paper_v2/scripts/docx_helpers.py` | python-docx helpers (runs with markup, small caps for condition names, tables, captions) |
| `paper_v2/output/numbers_original.json`, `numbers_jqwen.json`, `numbers_exp004.json`, `numbers_budgets.json`, `numbers_audit.json` | All numbers |
| `paper_v2/output/independent_check.md` | 118/118 numbers independently re-derived and passing |
| `paper_v2/output/fig1.png` … `fig5.png` | Final figures (300 dpi) |
| `research/gold_verification_ledger.csv` | Gold-answer ledger (author-confirmed 2026-10-10) |
| `research/PROMPT_VALIDATION_PROTOCOL.md` | Prompt templates, lexical findings, fluent-speaker review record |
| `research/HUMAN_EVAL_PROTOCOL.md` | Judge-validation protocol (not executed) |
| `paper_v2/revised/IndraLLM_IEEE_REVISED.docx` | Current build: IEEE two-column layout, not yet rendered or checked |

Repository: `C:\Users\Chandrahas Reddy\MYallPROJECTS\IndraLLM` (Windows; Git Bash and PowerShell
available). Branch `paper-v2-revision`. Commits, oldest first:

| Commit | Content |
|---|---|
| `908ed5b` | Tagged `freeze-512-2026-10-10` |
| `3a8ba0d` | EXP-005 + final build + report |
| `842f5ae` | Post-review audit |
| `8bf83ed` | Sensitivity framing |

---

## 3. What happened (chronological)

1. **Original manuscript.** `paper_v2/source/IndraLLM_IEEE_FINAL.pdf` (10 pages, IEEE) and its DOCX
   source, preserved unchanged.
2. **Audit of code and data.** The problems found:
   * **Judge configuration mismatch.** EXP-002 (EN-ORIG + 4 Indic conditions) was graded by the judge at
     temperature 0.3 with the answering system prompt, because it reused the generation client
     (`config.yaml`). EXP-003 (EN-MATCH) was graded at temperature 0 with "You are an expert factuality
     evaluator." The paper falsely said judging was identical.
   * **Truncation.** 598/600 responses hit the 128-token cap, and 82–95% end mid-sentence in every
     condition.
   * **Wrong tokenizer.** The analysis used Qwen2.5-7B. The public `Qwen/Qwen3.8-27B` tokenizer
     reproduces the API's prompt-token counts exactly (constant 48-token offset on all 1,600 prompts), so
     that is the correct one.
   * **CS-LAT ≠ MIXED wording in Telugu and Kannada.** Telugu `enti` vs `ఏమిటి`; Kannada `yenu` vs
     `ಯಾವುದು`. Hindi ROMAN uses `tareekh` while NATIVE uses `तिथि`. Only hi, bn and ta are
     word-identical.
   * **Missing script.** The reproducibility script cited in the paper (`paper_v2/scripts/make_all.py`) did
     not exist. It has now been written.
   * **Spend understated.** The ledger used a placeholder $0.08/M price. The real Qwen price is
     $0.80 in / $4.00 out per M tokens; the earlier runs cost about $2.1, not $0.21.
   * **Unbacked figures.** The κ = 0.719 and "300-item human validation" figures have no raw annotation
     files and must not be used.
   * **Reproduced exactly:** all other original-PDF numbers.
   * **Not reproducible:** the language-dependence p (0.15), the numeral check (60%) and the "mostly
     Brahmic" shares.
3. **EXP-004 ($1.10).**
   * Re-answered EN-MATCH, CS-LAT and MIXED (300 prompts) with max_tokens = 512, everything else identical.
   * Re-graded all 600 original outputs and the 300 new ones with two judges:
     * **J-QWEN:** qwen3.8-27b, T = 0, evaluator prompt. This is the harmonised, primary label set.
     * **J-OSS:** `openai/gpt-oss-120b`, T = 0, low reasoning effort. Cross-family judge.
4. **EXP-005 ($1.23).** Same 300 prompts with max_tokens = 1,024, graded by both judges. 0 parse
   failures, 0 persistent failures.
5. **Gold answers.** The author and volunteer friends checked them. Ledger results: all 20 consistent with
   their governing provision; 1 dated (Rythu Bandhu → Rythu Bharosa); 3 narrow (GST, MTP Act, Environment
   Clearance). Excluding those 3 changes no conclusion.
6. **Fluent-speaker template review.** Yes/no check of templates only, not outputs. Reviewers:
   * Telugu: Chandrahas Reddy (author) and Akshith Chawla (teammate);
   * Hindi and Kannada: Akshith Chawla;
   * Tamil: Kapilan;
   * Bengali: Shamik Mukherjee.

   Thank them by name **only** in the camera-ready Acknowledgements, never in the anonymous submission.
7. **Post-review audit.**
   * Truncation at 1,024 tokens: still 5 / 39 / 64 capped (EN-MATCH / CS-LAT / MIXED).
   * Complete-answers sensitivity analysis.
   * Holm correction within each budget–judge cell and across all 18 follow-up tests.
   * Equivalence wording removed.
   * Independent re-derivation of 118 numbers: all pass.
8. **Framing.** Because MIXED is still 64% capped at 1,024 tokens, the budget result is a *sensitivity
   finding*, not a clean estimate of the script effect.
9. **PDF rendering not done.** Word COM export (`Word.Application` via PowerShell) worked once, then failed
   with `CO_E_SERVER_EXEC_FAILURE` (0x80080005). The author has a Word window open (PID 67028, showing a
   Product Activation prompt), which is probably the cause. A leftover automation instance was stopped. The
   author declined a further automated retry. **Ask the author** to either close Word so you can retry, or
   export the PDF themselves (File → Save As → PDF).

---

## 4. Key results (verify each against the JSON before use)

### 4.1 128 tokens, all six conditions (J-QWEN primary; stored and J-OSS for comparison)

| Condition | J-QWEN % | Stored % | J-OSS % |
|---|---|---|---|
| EN-ORIG | 70 | 64 | 40 |
| EN-MATCH | 60 | 60 | 37 |
| CS-LAT | 49 | 43 | 25 |
| ROMAN | 37 | 33 | 24 |
| NATIVE | 32 | 28 | 21 |
| MIXED | 26 | 24 | 17 |

J-QWEN primary contrasts (exact McNemar; topic = exact sign-flip over 20 topics):

| Contrast | Δ | p | Topic p |
|---|---|---|---|
| CS-LAT vs EN-MATCH | −11 | 0.13 | 0.42 |
| ROMAN vs EN-MATCH | −23 | 0.001 | 0.087 |
| NATIVE vs EN-MATCH | −28 | < 0.001 | 0.031 |
| MIXED vs EN-MATCH | −34 | < 0.001 | 0.030 |
| MIXED vs CS-LAT | −23 | < 0.001 | 0.004 (Holm 0.018) |

Clustering: ICC 0.27, design effect 7.5, effective n 67 of 500.

### 4.2 Three budgets × two judges (EN-MATCH / CS-LAT / MIXED)

| Judge | 128 | 512 | 1,024 |
|---|---|---|---|
| J-QWEN | 60 / 49 / 26 | 80 / 59 / 63 | 85 / 61 / 58 |
| J-OSS | 37 / 25 / 17 | 58 / 54 / 48 | 63 / 56 / 51 |

**MIXED − CS-LAT:**
* J-QWEN: −23 (p < 0.001) → +4 (p 0.57, CI [−8, 15]) → −3 (p 0.70, CI [−14, 8]).
* J-OSS: −8 → −6 → −5, never significant.
* "Not detected" with intervals that exclude the 128-token gap. **Not equivalence.**

**English − CS-LAT:**
* J-QWEN: −11 → −21 → −24 (at 1,024: topic p 0.018, Holm-3 0.036, Holm-18 0.29).
* J-OSS: −12 → −4 → −7, never significant.
* Conclusion: judge-dependent, and the 1,024-token run is exploratory.

**Responses that hit the cap** (EN-MATCH / CS-LAT / MIXED): 100/99/100 at 128, 42/85/95 at 512,
5/39/64 at 1,024.

**Judge agreement** (J-QWEN vs J-OSS):

| Budget | Agreement | κ |
|---|---|---|
| 128 | 74.7% | 0.47 |
| 512 | 80.0% | 0.59 |
| 1,024 | 81.3% | 0.61 |

Disagreement is lopsided: J-QWEN accepts 30–36% of the answers J-OSS rejects, and J-OSS accepts 6–11% of
the answers J-QWEN rejects. **No human labels exist; do not call either judge more accurate.**

**Complete answers only** (exploratory), at 1,024 tokens:
* MIXED vs CS-LAT on 29 pairs: J-QWEN 55 vs 48 (p 0.75); J-OSS 52 vs 55 (p 1.0).
* EN-MATCH vs CS-LAT on 57 pairs: J-QWEN p 0.013; J-OSS p 0.55.

### 4.3 Other results

* **Tokenizer** (Qwen3.8), prompt characters per token: NATIVE 2.43, MIXED 3.70, EN-MATCH 4.65, CS-LAT
  4.11.
* **Mediation:** null and exploratory (b p = 0.08, wrong sign).
* **ALLaM-2-7B:** near floor (2–10%); uninformative.
* **Determinism:** hosted greedy decoding is not fully deterministic. 84–85% of 512-token outputs start with
  the 128-token text, and 78–91% of 1,024-token outputs start with the 512-token text.

---

## 5. Methods to describe (already written in `build_paper.py` TEXT)

* **Statistics:**
  * exact McNemar at the proposition level;
  * Holm correction within five pre-specified primary contrasts;
  * exact sign-flip permutation over all 2^20 topic sign patterns;
  * topic bootstrap (10,000 resamples);
  * GEE at three clustering levels (appendix only; anti-conservative with 20 clusters);
  * Wilson intervals; ANOVA ICC.
* **Follow-up:** the same three contrasts at each budget, fixed before grading. The 1,024 run was added
  after the 512 results were seen, so it is exploratory. Holm-3 and Holm-18 are reported.
* **Judge rubric:** prompt and settings for all three label sets, in Appendix C text.

---

## 6. Wording rules (forbidden → use instead)

| Forbidden | Use instead |
|---|---|
| Mixed or native script harms recall or reasoning | The 128-token gap is sensitive to the output budget |
| Conditions are equivalent; "removes"/"eliminates" the gap | No gap detected; intervals exclude the 128-token gap; no equivalence test was pre-specified |
| English is superior | The English comparison depends on the judge and the budget |
| "Factual recall" as the measured quantity | Judge-assessed accuracy |
| Either judge is accurate or validated | Judge sensitivity; no human evaluation was performed |
| 1,024 tokens is unconstrained | The budget remains a possible confound (64% of MIXED still capped) |
| Prompts validated for semantic equivalence | Fluent speakers reviewed the templates and judged them natural and correct (yes/no check of templates only) |
| κ = 0.719, naturalness 4.74, "300-item human validation" | Do not mention |
| Causal mechanisms; generalisation beyond one model | Scope: one informative model, 20 topics, five languages |

---

## 7. YOUR TASK: build the two-column conference-format Word document

### 7.1 Target format

The target venue is an ACL-family conference: ACL, EMNLP or NAACL, via ACL Rolling Review (ARR).
**First, fetch and read the current official requirements**, because they change between cycles:
* the ARR call for papers and the ACL formatting guidelines;
* the `acl-org/acl-style-files` repository;
* any official Word template, if one exists.

If there is no current official Word template, reproduce the ACL style faithfully in Word. Known ACL
conventions (**verify each against the current guidelines**):

* **Page:** A4; all margins 2.5 cm; two columns, each 7.7 cm wide with a 0.6 cm gap.
* **Fonts:** Times New Roman (or Times) 11 pt for body text. Title 15 pt bold, centred. Abstract 10 pt,
  indented, with a bold centred "Abstract" heading.
* **Headings:** section headings 12 pt bold and numbered (1, 1.1); captions 10 pt; references in ACL
  natbib author–year style (e.g. "Ahia et al. (2023)"), not IEEE numeric.
* **Length:** long paper 8 pages of content, plus unlimited references and appendices. A mandatory
  **Limitations** section goes after the conclusion and before the references; it does not count toward
  the limit. An optional Ethics statement may follow it.
* **Review version:** anonymous. Remove the author name, email and identifying repository links (write
  "code and data will be released"). Add line numbers if the guidelines require them. No acknowledgements.
* **Order:** references come before appendices, and appendices start on a new page.
* **Responsible NLP checklist:** answered in the submission form, not in the paper. Prepare draft answers in
  a separate Markdown file.
* **Two documents** if feasible: `IndraLLM_ACL_review.docx` (anonymous) and `IndraLLM_ACL_camera.docx`
  (with author block and an Acknowledgements section thanking the five reviewers by name).

### 7.2 Recommended approach

Write a new script, `paper_v2/scripts/build_acl_docx.py`, that builds the document **from a blank
python-docx Document with explicitly defined styles**: page setup, two-column sections, fonts and heading
styles. Do not edit the IEEE source. Requirements:

* **Text:** import from `build_paper.py` (`TEXT`, `NEW_REFS`) and `build_revised_docx.py` (`PROVISION`,
  `fp`, `sgn`, `neg`).
* **Numbers:** read only from the JSON files. Reuse table-building logic from `build_paper.py`, which
  already builds every table from JSON.
* **Section numbering:** convert IEEE roman numerals (I, II, …) to ACL arabic (1, 1.1, …).
* **Citations:** convert IEEE numeric citations [1]–[27] to author–year. The full reference list is
  references [1]–[22] in the original DOCX (`paper_v2/source/IndraLLM_IEEE_FINAL.docx`, the paragraphs
  after "REFERENCES"), plus [23]–[27] in `build_paper.py` `NEW_REFS`, all verified to exist. Build a
  mapping and check every in-text citation.
* **Full-width elements:** one-column section breaks around full-width floats (as the IEEE source does), or
  floating tables or figures that span both columns.
* **Condition names:** small caps, via `docx_helpers.add_runs`. Indic text needs a font with Devanagari,
  Telugu and Kannada glyphs (Nirmala UI on Windows).
* **Figures:** Figs. 1–5 from `paper_v2/output/`. One-column width is 7.7 cm and full width 16 cm.
  Regenerate them with `make_figures.py` and `make_fig1.py` at ACL-appropriate sizes if fonts become
  unreadable; keep fonts at least about 7 pt after scaling.

### 7.3 Fitting 8 pages: content plan

The current text is about 8,200 words with 5 figures and 9 tables, which is too long for 8 ACL pages.

**Main body** (8 pages):
1. Introduction (motivation, design, RQs, contributions).
2. Related work: condensed.
3. Benchmark and design (conditions; matched English; judge-configuration issue; gold answers; template
   review).
4. Setup (model and tokenizer identity, prompting and budgets, judges, statistics).
5. Results at 128 tokens (Table II, Fig. 2).
6. Output budget (Table III, Fig. 5): the core result.
7. Judge dependence (Table IV): a core result.
8. Discussion and conclusion.

**After the body:** Limitations (mandatory); Ethics; references.

**Appendices:**
* tokenization and mediation (§VI-A);
* clustering detail and GEE (Table IX, Fig. 4);
* per-language results (Fig. 3), ALLaM;
* tipping points (Table V);
* claims table (Table VI);
* topics and provisions (Table VII);
* all pairwise contrasts (Table VIII);
* complete-answers and multiplicity tables (`numbers_audit.json`);
* rubric and settings (Appendix C);
* power (Appendix D);
* reproducibility (Appendix E).

**Shortening.** You may condense or merge prose to fit, provided:
* every claim keeps its qualification (Section 6);
* numbers still come from JSON;
* nothing is added that is not supported.

Keep the abstract at or under about 200 words if the venue asks. Record every shortening in a change log.

### 7.4 Rendering and checking (mandatory, and the current hard blocker)

1. **Export to PDF with Word.** Ask the author first: they may need to close their open Word window, or they
   can export manually. If automation works, use `Documents.Open(path, False, True)` then
   `ExportAsFixedFormat(pdf, 17)`. Always call `Quit()` and release the COM object; leftover WINWORD
   instances block later exports.
2. **Render every page** with PyMuPDF (`pip install pymupdf` is done; `import pymupdf`) at about 100 dpi and
   **look at each page**.
3. **Check:**
   * page count: 8 content pages before Limitations;
   * column widths and margins;
   * table headers present (a previous build lost header rows when tables were filled without a header);
   * no clipped table cells;
   * figures readable;
   * captions attached to their tables (use "keep with next");
   * Devanagari, Telugu and Kannada glyphs render;
   * small caps;
   * reference style consistent;
   * no IEEE remnants (roman numerals, "Index Terms", the IEEE author block);
   * anonymity.
4. **Run `python paper_v2/scripts/independent_check.py`** and confirm 118/118 still pass.
5. **Scan the final text for forbidden phrases** (Section 6), the way `build_paper.py` does with
   assertions.
6. **Iterate** until all checks pass, then commit.

### 7.5 Deliverables

* `paper_v2/acl/IndraLLM_ACL_review.docx` and its PDF (anonymous).
* `paper_v2/acl/IndraLLM_ACL_camera.docx` and its PDF (optional).
* `paper_v2/scripts/build_acl_docx.py` (reproducible build).
* `paper_v2/acl/FORMAT_CHECKLIST.md`: each venue requirement, how it is met, and evidence (page renders).
* `paper_v2/acl/CHANGELOG_ACL.md`: what was shortened, moved or merged relative to `build_paper.py`.
* `paper_v2/acl/responsible_nlp_checklist_draft.md`.
* A short final message to the author covering: what was built, the page count, which checks passed, and
  what remains.

---

## 8. Still open (be honest about these in the paper and to the author)

* **Human annotation of the judges: not done.**
  * A 210-item blinded sample and protocol exist in `results/EXP-004-budget-rejudge/human_eval/` and
    `research/HUMAN_EVAL_PROTOCOL.md`.
  * If it remains undone, the paper must keep stating that no human evaluation was performed, which it
    already does in the abstract, setup, judge section and limitations.
  * This is the most likely rejection reason. Other likely reasons: a single model, 20 topics, residual
    truncation at 1,024 tokens, and novelty relative to tokenization-premium and multilingual-judge work
    (references [5], [6], [26], [27]).
* **Optional:** an uncapped run, or one with a fixed answer language, for EN-MATCH/CS-LAT/MIXED. Estimated
  $1.5–3. Do not run it without the author's explicit approval.
* **Venue choice.**
  * Fit: an ARR short paper or Findings, evaluation workshops (GEM, Eval4NLP), or multilingual and
    code-switching venues (MRL, CALCS).
  * Check current scope and dates. Do not assume a workshop is easier.
  * If the author picks a non-ACL venue, use that venue's official template instead and follow the same
    process.

## 9. Useful commands

```bash
# regenerate all numbers and figures (no API calls)
python paper_v2/scripts/make_all.py
python paper_v2/scripts/make_all.py --labels jqwen
python paper_v2/scripts/analyze_exp004.py
python paper_v2/scripts/analyze_budgets.py
python paper_v2/scripts/audit_budget_truncation.py
python paper_v2/scripts/make_figures.py
python paper_v2/scripts/make_fig1.py
python paper_v2/scripts/independent_check.py      # expect 118 checks, 0 failed
python paper_v2/scripts/build_paper.py            # current IEEE build (reference)
python paper_v2/scripts/dump_report_parts.py && python paper_v2/scripts/make_guide.py
```

Set `PYTHONIOENCODING=utf-8` on Windows. Python 3.11 is installed with numpy, pandas, scipy, statsmodels,
scikit-learn, tokenizers, matplotlib, python-docx, pymupdf and pywin32.



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



## C1. Prompt templates, findings and fluent-speaker review record (from research/PROMPT_VALIDATION_PROTOCOL.md)


### 0. Fluent-speaker review record

As reported by the author (Chandrahas Reddy), 2026-10-10:

| Language | Reviewer(s) | Outcome |
|---|---|---|
| Telugu | Chandrahas Reddy (author; speaks Telugu, English); Akshith Chawla (teammate) | Proper |
| Hindi | Akshith Chawla (teammate; speaks Hindi, Telugu, Kannada) | Proper |
| Kannada | Akshith Chawla | Proper |
| Tamil | Kapilan (friend of the author) | Proper |
| Bengali | Shamik Mukherjee (friend of the author) | Proper |

Scope and form: reviewers checked the **prompt templates** (the questions sent to the
model) as used in the evaluated prompts and reported them proper. They did **not** review
the model's outputs, and the review does not validate the LLM judges or establish full
semantic equivalence across conditions. The review was a yes/no judgement; no per-item 1–5 ratings,
written corrections or agreement statistic were recorded. Report it in the paper as
an informal fluent-speaker check, not as a measured naturalness score.

What the review does not change: the CS-LAT and MIXED templates in Telugu and Kannada
use different question words (Section 2, item 1), and Hindi ROMAN uses *tareekh* where
Hindi NATIVE uses *tithi* (item 2). These are facts about the strings, not quality
problems; the reviewers' judgement is that each template is proper in its own right.
The paper still reports the CS-LAT–MIXED contrast on the 60 word-identical
propositions (hi, bn, ta) as a sensitivity analysis.

To strengthen this record (optional): a one-line note per language of what was
checked (naturalness, spelling, transliteration, script rendering).

All 400 Indic prompts are produced by one template per language and condition
(`src/indrallm/collection/build_decontaminated_benchmark_v1_1.py`,
`generate_prompts_for_fact`), with the topic string `{X}` inserted verbatim in
Latin script. Validating the 20 templates below therefore covers the frames of
all 400 prompts; the inserted topic strings are identical across languages.

### 1. Inventory of templates (exactly as used)

| Lang | NATIVE | ROMAN | CS-LAT | MIXED |
|---|---|---|---|---|
| hi | `{X} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?` | `{X} ke sambandh mein mukhya niyam, tareekh ya mapdand kya hai?` | `{X} ke regarding main rule, date ya parameter kya hai?` | `{X} के regarding main rule, date या parameter क्या है?` |
| bn | `{X} সম্পর্কিত মূল নিয়ম, তারিখ বা মাপদণ্ড কী?` | `{X} somporkito mool niyam, tarikh ba mapdando ki?` | `{X} er regarding main rule, date ba parameter ki?` | `{X} এর regarding main rule, date বা parameter কী?` |
| ta | `{X} தொடர்பான முக்கிய விதி, தேதி அல்லது அளவுரு என்ன?` | `{X} thodarbana mukkiya vidhi, thethi allathu alavuru enna?` | `{X} pathi main rule, date illa parameter enna?` | `{X} பத்தி main rule, date இல்ல parameter என்ன?` |
| te | `{X} కు సంబంధించిన ప్రధాన నిబంధన, తేదీ లేదా పారామితి ఏమిటి?` | `{X} ku sambandhinchina pradhaana nibandhana, thedhee leda paramiti emiti?` | `{X} gurinchi main rule, date leda parameter enti?` | `{X} గురించి main rule, date లేదా parameter ఏమిటి?` |
| kn | `{X} ಗೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಮುಖ ನಿಯಮ, ದಿನಾಂಕ ಅಥವಾ ನಿಯತಾಂಕ ಯಾವುದು?` | `{X} ge sambandhisida pramukha niyama, dinaanka athava niyataamka yaavudu?` | `{X} bagge main rule, date athava parameter yenu?` | `{X} ಬಗ್ಗೆ main rule, date ಅಥವಾ parameter ಯಾವುದು?` |

English: EN-MATCH `What is the main rule, date or parameter regarding {X}?`;
EN-ORIG uses two other templates (TF-11 "key structural or operational difference
between {X}", TF-12 "Under Indian statutory regulations, what specific prerequisite
condition or timeline applies to {X}?").

### 2. Findings from inspecting the strings (no speaker judgement involved)

1. **CS-LAT and MIXED are not word-identical in Telugu and Kannada.**
   - te: CS-LAT ends in `enti` (colloquial "what"), MIXED in `ఏమిటి` (*emiti*, formal "what").
   - kn: CS-LAT ends in `yenu` ("what"), MIXED in `ಯಾವುದು` (*yāvudu*, "which").
   In Hindi, Bengali and Tamil the two prompts are word-for-word transliterations.
   The manuscript's statement that the two conditions "contain the same words"
   holds for 60 of the 100 propositions. On those 60, the CS-LAT → MIXED drop is
   45.0% → 21.7% (exact McNemar p = 0.004; topic-level sign-flip p = 0.020); on the
   40 te/kn propositions it is 40.0% → 27.5% (p = 0.33).
2. **Hindi ROMAN is not a transliteration of Hindi NATIVE**: `tareekh` (तारीख) vs
   `तिथि` (*tithi*) for "date". Other languages' ROMAN/NATIVE pairs match word for word.
3. **The CS-LAT frame differs in structure across languages.** Hindi and Bengali use
   the English word *regarding* as a postposition after a genitive (`ke regarding`,
   `er regarding`), which is unusual; Tamil, Telugu and Kannada use a native
   postposition (`pathi`, `gurinchi`, `bagge`). The amount of English in CS-LAT
   therefore differs by language. Naturalness of `ke regarding` / `er regarding`
   has not been assessed.
4. **One template for all topics.** "Main rule, date or parameter regarding X" does
   not ask for the comparison that the ten TF-11 gold answers encode (e.g. "PMFBY vs
   WBCIS"), and for three TF-12 topics (GST, MTP Act, Environment Clearance) it
   admits correct answers other than the gold (see `gold_verification_ledger.csv`).
   This affects all conditions equally in wording, but it makes the judge's task
   harder and the gold narrower than the question.
5. **Scheme names stay in Latin script in every condition**, so NATIVE contains one
   Latin–Brahmic boundary; this is intended and documented.


## C2. Gold-answer ledger (from research/gold_verification_ledger.csv)

| Topic | Gold answer | Provision | Factual status | Completeness | Currency / notes |
|---|---|---|---|---|---|
| PMFBY vs WBCIS | PMFBY is crop yield-based; WBCIS is weather index-based. | PMFBY & RWBCIS Operational Guidelines (Ministry of Agriculture & Farmers Welfare) | consistent | adequate | WBCIS now operated as Restructured WBCIS (RWBCIS) |
| NEFT vs RTGS | NEFT has no minimum limit and settles in batches; RTGS has ₹2 Lakh minimum and settles real-time. | RBI NEFT and RTGS system directions / FAQs | consistent | adequate | Both systems 24x7 since Dec 2019 (NEFT) and Dec 2020 (RTGS); limits unchanged |
| Covaxin vs Covishield | Covaxin is inactivated virus; Covishield is chimpanzee adenovirus vector. | CDSCO emergency-use approvals (Jan 2021); manufacturer product information | consistent | adequate | Evidence snippet calls this a 'statutory analysis' (template artifact) |
| Kharif vs Rabi Rice | Kharif is monsoon rainfed; Rabi is winter irrigated. | ICAR / agronomy references on rice seasons | consistent_simplified | adequate | Kharif rice is also widely irrigated; gold is a simplification |
| ISRO PSLV vs GSLV Mk III | PSLV carries 1,750 kg to SSO; GSLV Mk III carries 4,000 kg to GTO using cryogenic stage. | ISRO launcher pages (PSLV; LVM3) | consistent | adequate | GSLV Mk III renamed LVM3; Published GTO figures vary slightly (about 4000-4200 kg) |
| Lok Sabha vs Rajya Sabha Money Bill | Rajya Sabha cannot reject or amend Money Bills and has only 14 days to return. | Constitution of India, Arts. 109-110 | consistent | adequate | Rajya Sabha may recommend amendments that Lok Sabha can accept or reject |
| National Park vs Wildlife Sanctuary | No private rights or grazing permitted in National Parks; limited rights allowed in Sanctuaries. | Wild Life (Protection) Act 1972, ss. 24, 33, 35 | consistent | adequate |  |
| Classical Tamil vs Sanskrit Grammar | Tolkappiyam for Tamil; Ashtadhyayi (Panini) for Sanskrit. | Standard philological references (Central Institute of Classical Tamil) | consistent | ill_posed_for_template | Not a policy fact; 'main rule, date or parameter' does not naturally elicit the grammar names |
| PM-KISAN vs Rythu Bandhu | PM-KISAN is flat per family; Rythu Bandhu is per acre acreage-linked. | PM-KISAN operational guidelines; Telangana Rythu Bandhu G.O.s | consistent_historical | adequate | OUTDATED: Telangana replaced Rythu Bandhu with Rythu Bharosa (2024-25); gold should be dated |
| Supreme Court vs High Court Writ Jurisdiction | Article 226 has wider jurisdiction covering fundamental and other statutory legal rights. | Constitution of India, Arts. 32 and 226 | consistent | adequate |  |
| Patents Act Compulsory License | After expiration of 3 years from patent grant date. | Patents Act 1970, s. 84(1) | consistent | narrow | Generic question also admits the s.84 grounds (reasonable requirements, affordability, working in India) |
| RTI Third Party Information | Within 5 days from receipt of request. | Right to Information Act 2005, s. 11(1) | consistent | narrow | Evidence snippet's 'trade secrets' wording is imprecise: s.11 covers information relating to or supplied by a third party and treated as confidential |
| GST Registration Exemption | Turnover does not exceed ₹40 Lakh (for goods). | CGST Act 2017, s. 22; Notification 10/2019-Central Tax | consistent | AMBIGUOUS | ₹20 lakh (services / general) and ₹10-20 lakh (special-category States) are also correct answers to the generic question |
| Companies Act CSR Mandate | Net worth ≥ ₹500 Cr, Turnover ≥ ₹1000 Cr, or Net Profit ≥ ₹5 Cr. | Companies Act 2013, s. 135(1) | consistent | adequate |  |
| Arbitration Act Time Limit | 12 months (extendable by 6 months). | Arbitration and Conciliation Act 1996, s. 29A (as amended 2019) | consistent | adequate | 12 months runs from completion of pleadings (post-2019); further extension only by court |
| IBC Section 7 Default Threshold | Minimum default of ₹1 Crore. | Insolvency and Bankruptcy Code 2016, s. 4 (threshold raised from ₹1 lakh to ₹1 crore, March 2020) | consistent | adequate | Model answers the pre-2020 ₹1 lakh threshold: a genuine model error |
| Environment Clearance Public Hearing | Exempted inside notified industrial estates or defense projects. | EIA Notification 2006 (S.O. 1533(E)), para. 7(i) Stage III | partially_consistent | INCOMPLETE_AND_ILL_POSED | Gold lists 2 of the notification's public-consultation exemptions (others include B2 projects, building/construction, certain road expansions, irrigation modernisation); the 'main rule' is that a hearing is required; 0/30 correct in every condition |
| Medical Termination of Pregnancy Act | Opinion of two registered medical practitioners. | MTP Act 1971 s. 3(2) as amended 2021; MTP Rules r. 3B | consistent | AMBIGUOUS | Two RMPs applies only to 20-24 weeks; 'one RMP up to 20 weeks' and '24-week limit' are equally correct answers to the generic question (EN-ORIG 5/5 vs EN-MATCH 0/5) |
| SEBI Insider Trading Pre-Clearance | Pre-clearance required from compliance officer. | SEBI (Prohibition of Insider Trading) Regulations 2015, Sch. B | consistent | adequate |  |
| Citizenship Amendment Act Cut-off | On or before 31 December 2014. | Citizenship (Amendment) Act 2019, s. 2 | consistent | adequate |  |

Author verification record (all rows): confirmed by author 2026-10-10 (ledger reviewed; law/policy as of Oct 2026).



## C3. File inventory (tracked files produced or used in the revision)

| File | Size (KB) |
|---|---|
| `paper_v2/FULL_REVISION_REPORT.md` | 133.3 |
| `paper_v2/MANUSCRIPT_BUILD_GUIDE.md` | 75.3 |
| `paper_v2/NEXT_SESSION_PROMPT.md` | 21.8 |
| `paper_v2/guide_header.md` | 6.9 |
| `paper_v2/output/fig1.png` | 230.1 |
| `paper_v2/output/fig2.png` | 224.6 |
| `paper_v2/output/fig3.png` | 96.0 |
| `paper_v2/output/fig4.png` | 103.0 |
| `paper_v2/output/fig5.png` | 206.9 |
| `paper_v2/output/independent_check.md` | 8.9 |
| `paper_v2/output/numbers_audit.json` | 15.5 |
| `paper_v2/output/numbers_budgets.json` | 36.1 |
| `paper_v2/output/numbers_exp004.json` | 19.3 |
| `paper_v2/output/numbers_jqwen.json` | 23.8 |
| `paper_v2/output/numbers_original.json` | 23.7 |
| `paper_v2/output/report_generated.md` | 68.2 |
| `paper_v2/revised/IndraLLM_IEEE_REVISED.docx` | 2871.5 |
| `paper_v2/revised/IndraLLM_IEEE_REVISED.pdf` | 1345.7 |
| `paper_v2/scripts/analyze_budgets.py` | 10.8 |
| `paper_v2/scripts/analyze_exp004.py` | 8.9 |
| `paper_v2/scripts/audit_budget_truncation.py` | 6.3 |
| `paper_v2/scripts/build_paper.py` | 38.0 |
| `paper_v2/scripts/build_revised_docx.py` | 58.3 |
| `paper_v2/scripts/docx_helpers.py` | 4.2 |
| `paper_v2/scripts/dump_report_parts.py` | 15.6 |
| `paper_v2/scripts/dump_tables_md.py` | 5.8 |
| `paper_v2/scripts/independent_check.py` | 6.0 |
| `paper_v2/scripts/make_all.py` | 16.4 |
| `paper_v2/scripts/make_fig1.py` | 3.3 |
| `paper_v2/scripts/make_figures.py` | 8.2 |
| `paper_v2/scripts/make_guide.py` | 0.5 |
| `paper_v2/scripts/stats_lib.py` | 4.8 |
| `paper_v2/source/IndraLLM_IEEE_FINAL.docx` | 2840.3 |
| `paper_v2/source/IndraLLM_IEEE_FINAL.pdf` | 1279.7 |
| `research/HUMAN_EVAL_PROTOCOL.md` | 6.1 |
| `research/PROMPT_VALIDATION_PROTOCOL.md` | 8.4 |
| `research/gold_verification_ledger.csv` | 8.0 |
| `results/EXP-004-budget-rejudge/gen512_predictions.jsonl` | 902.7 |
| `results/EXP-004-budget-rejudge/human_eval/items_blinded.csv` | 102.0 |
| `results/EXP-004-budget-rejudge/human_eval/items_blinded_512.csv` | 122.0 |
| `results/EXP-004-budget-rejudge/human_eval/key.csv` | 24.1 |
| `results/EXP-004-budget-rejudge/human_eval/key_512.csv` | 6.1 |
| `results/EXP-004-budget-rejudge/human_eval/reviewers.csv` | 0.1 |
| `results/EXP-004-budget-rejudge/judgements.jsonl` | 893.1 |
| `results/EXP-004-budget-rejudge/spend_log.jsonl` | 157.1 |
| `results/EXP-005-budget1024/gen1024_predictions.jsonl` | 1224.1 |
| `results/EXP-005-budget1024/judgements.jsonl` | 299.6 |
| `results/EXP-005-budget1024/spend_log.jsonl` | 67.2 |
| `scripts/build_human_eval_sample.py` | 5.8 |
| `scripts/run_exp004_budget_rejudge.py` | 9.6 |
| `scripts/run_exp005_budget1024.py` | 9.3 |


## C4. All results tables and the final manuscript text (from report_generated.md)

## G1. Three-budget results (EXP-004 + EXP-005), both judges

### G1.1 Accuracy (%, n = 100 per cell) with Wilson 95% CI

| Judge | Budget | EN-MATCH | CS-LAT | MIXED |
| --- | --- | --- | --- | --- |
| J-QWEN | 128 | 60 [50.2, 69.1] | 49 [39.4, 58.7] | 26 [18.4, 35.4] |
| J-QWEN | 512 | 80 [71.1, 86.7] | 59 [49.2, 68.1] | 63 [53.2, 71.8] |
| J-QWEN | 1024 | 85 [76.7, 90.7] | 61 [51.2, 70.0] | 58 [48.2, 67.2] |
| J-OSS | 128 | 37 [28.2, 46.8] | 25 [17.5, 34.3] | 17 [10.9, 25.5] |
| J-OSS | 512 | 58 [48.2, 67.2] | 54 [44.3, 63.4] | 48 [38.5, 57.7] |
| J-OSS | 1024 | 63 [53.2, 71.8] | 56 [46.2, 65.3] | 51 [41.3, 60.6] |

### G1.2 Paired contrasts at each budget (comparison vs reference)

b = reference correct & comparison wrong; c = the reverse. Topic p = exact sign-flip over 2^20 patterns; topic CI = percentile bootstrap over 20 topics (10,000 resamples).

| Judge | Budget | Contrast | Ref % | Cmp % | Δ (pp) | b | c | Exact p | Topic p | Topic 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128 | CS-LAT vs EN-MATCH | 60 | 49 | −11 | 27 | 16 | 0.13 | 0.42 | [-34, 13] |
| J-QWEN | 128 | MIXED vs CS-LAT | 49 | 26 | −23 | 30 | 7 | <0.001 | 0.004 | [-35, -11] |
| J-QWEN | 128 | MIXED vs EN-MATCH | 60 | 26 | −34 | 45 | 11 | <0.001 | 0.030 | [-59, -7] |
| J-QWEN | 512 | CS-LAT vs EN-MATCH | 80 | 59 | −21 | 28 | 7 | <0.001 | 0.082 | [-41, -1] |
| J-QWEN | 512 | MIXED vs CS-LAT | 59 | 63 | +4 | 12 | 16 | 0.57 | 0.65 | [-8, 15] |
| J-QWEN | 512 | MIXED vs EN-MATCH | 80 | 63 | −17 | 24 | 7 | 0.003 | 0.13 | [-35, 3] |
| J-QWEN | 1024 | CS-LAT vs EN-MATCH | 85 | 61 | −24 | 27 | 3 | <0.001 | 0.018 | [-42, -8] |
| J-QWEN | 1024 | MIXED vs CS-LAT | 61 | 58 | −3 | 15 | 12 | 0.70 | 0.72 | [-14, 8] |
| J-QWEN | 1024 | MIXED vs EN-MATCH | 85 | 58 | −27 | 29 | 2 | <0.001 | 0.003 | [-42, -13] |
| J-OSS | 128 | CS-LAT vs EN-MATCH | 37 | 25 | −12 | 22 | 10 | 0.050 | 0.22 | [-29, 4] |
| J-OSS | 128 | MIXED vs CS-LAT | 25 | 17 | −8 | 18 | 10 | 0.18 | 0.24 | [-19, 2] |
| J-OSS | 128 | MIXED vs EN-MATCH | 37 | 17 | −20 | 29 | 9 | 0.002 | 0.067 | [-39, -2] |
| J-OSS | 512 | CS-LAT vs EN-MATCH | 58 | 54 | −4 | 16 | 12 | 0.57 | 0.76 | [-22, 15] |
| J-OSS | 512 | MIXED vs CS-LAT | 54 | 48 | −6 | 17 | 11 | 0.34 | 0.44 | [-18, 6] |
| J-OSS | 512 | MIXED vs EN-MATCH | 58 | 48 | −10 | 19 | 9 | 0.087 | 0.31 | [-26, 6] |
| J-OSS | 1024 | CS-LAT vs EN-MATCH | 63 | 56 | −7 | 15 | 8 | 0.21 | 0.52 | [-24, 10] |
| J-OSS | 1024 | MIXED vs CS-LAT | 56 | 51 | −5 | 14 | 9 | 0.40 | 0.52 | [-17, 7] |
| J-OSS | 1024 | MIXED vs EN-MATCH | 63 | 51 | −12 | 21 | 9 | 0.043 | 0.22 | [-28, 5] |

### G1.3 Within-condition change between budgets (same judge)

| Judge | Change | Condition | Acc before | Acc after | Lost (b) | Gained (c) | Exact p | Topic p | Topic 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128->512 | EN-MATCH | 60 | 80 | 0 | 20 | <0.001 | 0.12 | [5, 40] |
| J-QWEN | 128->512 | CS-LAT | 49 | 59 | 11 | 21 | 0.11 | 0.22 | [-2, 24] |
| J-QWEN | 128->512 | MIXED | 26 | 63 | 5 | 42 | <0.001 | 0.003 | [18, 57] |
| J-QWEN | 512->1024 | EN-MATCH | 80 | 85 | 0 | 5 | 0.062 | 1.00 | [0, 15] |
| J-QWEN | 512->1024 | CS-LAT | 59 | 61 | 3 | 5 | 0.73 | 0.73 | [-3, 7] |
| J-QWEN | 512->1024 | MIXED | 63 | 58 | 8 | 3 | 0.23 | 0.19 | [-11, 0] |
| J-QWEN | 128->1024 | EN-MATCH | 60 | 85 | 0 | 25 | <0.001 | 0.062 | [10, 45] |
| J-QWEN | 128->1024 | CS-LAT | 49 | 61 | 9 | 21 | 0.043 | 0.11 | [0, 25] |
| J-QWEN | 128->1024 | MIXED | 26 | 58 | 5 | 37 | <0.001 | 0.003 | [15, 50] |
| J-OSS | 128->512 | EN-MATCH | 37 | 58 | 3 | 24 | <0.001 | 0.043 | [5, 39] |
| J-OSS | 128->512 | CS-LAT | 25 | 54 | 3 | 32 | <0.001 | <0.001 | [16, 43] |
| J-OSS | 128->512 | MIXED | 17 | 48 | 3 | 34 | <0.001 | <0.001 | [19, 43] |
| J-OSS | 512->1024 | EN-MATCH | 58 | 63 | 2 | 7 | 0.18 | 0.50 | [-1, 15] |
| J-OSS | 512->1024 | CS-LAT | 54 | 56 | 2 | 4 | 0.69 | 0.69 | [-3, 7] |
| J-OSS | 512->1024 | MIXED | 48 | 51 | 6 | 9 | 0.61 | 0.59 | [-4, 10] |
| J-OSS | 128->1024 | EN-MATCH | 37 | 63 | 4 | 30 | <0.001 | 0.021 | [8, 45] |
| J-OSS | 128->1024 | CS-LAT | 25 | 56 | 2 | 33 | <0.001 | <0.001 | [18, 45] |
| J-OSS | 128->1024 | MIXED | 17 | 51 | 3 | 37 | <0.001 | <0.001 | [23, 45] |

### G1.4 Change in each gap between budgets (per-topic difference-in-differences)

| Judge | Change | Gap | Gap before | Gap after | Change | Topic 95% CI | Topic p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128->512 | CS-LAT-EN-MATCH | -11 | -21 | −10 | [-31, 9] | 0.41 |
| J-QWEN | 128->512 | MIXED-CS-LAT | -23 | 4 | +27 | [7, 45] | 0.018 |
| J-QWEN | 128->512 | MIXED-EN-MATCH | -34 | -17 | +17 | [-4, 39] | 0.18 |
| J-QWEN | 512->1024 | CS-LAT-EN-MATCH | -21 | -24 | −3 | [-16, 6] | 0.86 |
| J-QWEN | 512->1024 | MIXED-CS-LAT | 4 | -3 | −7 | [-14, 1] | 0.14 |
| J-QWEN | 512->1024 | MIXED-EN-MATCH | -17 | -27 | −10 | [-22, -1] | 0.094 |
| J-QWEN | 128->1024 | CS-LAT-EN-MATCH | -11 | -24 | −13 | [-36, 7] | 0.31 |
| J-QWEN | 128->1024 | MIXED-CS-LAT | -23 | -3 | +20 | [5, 34] | 0.023 |
| J-QWEN | 128->1024 | MIXED-EN-MATCH | -34 | -27 | +7 | [-15, 29] | 0.62 |
| J-OSS | 128->512 | CS-LAT-EN-MATCH | -12 | -4 | +8 | [-8, 23] | 0.42 |
| J-OSS | 128->512 | MIXED-CS-LAT | -8 | -6 | +2 | [-11, 16] | 0.89 |
| J-OSS | 128->512 | MIXED-EN-MATCH | -20 | -10 | +10 | [-6, 26] | 0.30 |
| J-OSS | 512->1024 | CS-LAT-EN-MATCH | -4 | -7 | −3 | [-12, 4] | 0.66 |
| J-OSS | 512->1024 | MIXED-CS-LAT | -6 | -5 | +1 | [-8, 10] | 1.00 |
| J-OSS | 512->1024 | MIXED-EN-MATCH | -10 | -12 | −2 | [-13, 7] | 0.88 |
| J-OSS | 128->1024 | CS-LAT-EN-MATCH | -12 | -7 | +5 | [-11, 20] | 0.63 |
| J-OSS | 128->1024 | MIXED-CS-LAT | -8 | -5 | +3 | [-7, 13] | 0.71 |
| J-OSS | 128->1024 | MIXED-EN-MATCH | -20 | -12 | +8 | [-9, 24] | 0.43 |

### G1.5 MIXED vs CS-LAT on the 60 word-identical propositions (hi, ta, bn)

| Judge | Budget | CS-LAT % | MIXED % | b | c | Exact p | Topic p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128 | 51.7 | 26.7 | 18 | 3 | 0.001 | 0.016 |
| J-QWEN | 512 | 61.7 | 63.3 | 7 | 8 | 1.00 | 1.00 |
| J-QWEN | 1024 | 65.0 | 60.0 | 8 | 5 | 0.58 | 0.64 |
| J-OSS | 128 | 30.0 | 16.7 | 13 | 5 | 0.096 | 0.19 |
| J-OSS | 512 | 55.0 | 48.3 | 11 | 7 | 0.48 | 0.53 |
| J-OSS | 1024 | 56.7 | 53.3 | 9 | 7 | 0.80 | 0.84 |

### G1.6 Generation descriptives by budget

| Budget | Condition | Stopped before cap (of 100) | Hit cap | Mean completion tokens | Mean chars | Mostly Brahmic % |
| --- | --- | --- | --- | --- | --- | --- |
| 128 | EN-MATCH | 0 | 100 | 128 | 529 | 0 |
| 128 | CS-LAT | 1 | 99 | 128 | 423 | 2 |
| 128 | MIXED | 0 | 100 | 128 | 303 | 88 |
| 512 | EN-MATCH | 58 | 42 | 438 | 1,771 | 0 |
| 512 | CS-LAT | 15 | 85 | 484 | 1,601 | 2 |
| 512 | MIXED | 5 | 95 | 508 | 1,122 | 96 |
| 1024 | EN-MATCH | 95 | 5 | 510 | 1,988 | 0 |
| 1024 | CS-LAT | 61 | 39 | 812 | 2,679 | 2 |
| 1024 | MIXED | 36 | 64 | 936 | 2,054 | 97 |

Prefix consistency (longer response begins with the shorter one, of 100): 512 starts with 128 — EN-MATCH 84, CS-LAT 85, MIXED 84; 1,024 starts with 512 — EN-MATCH 91, CS-LAT 78, MIXED 80.

### G2. Judge agreement (J-QWEN vs J-OSS) by budget and condition

| Budget | Condition | n | Both correct | Both wrong | Q correct / O wrong | Q wrong / O correct | Agreement | κ | κ topic 95% CI | P(Q correct | O wrong) | P(O correct | Q wrong) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 128 | EN-MATCH | 100 | 35 | 38 | 25 | 2 | 0.730 | 0.49 | [0.21, 0.77] | 0.40 | 0.05 |
| 128 | CS-LAT | 100 | 23 | 49 | 26 | 2 | 0.720 | 0.43 | [0.22, 0.65] | 0.35 | 0.04 |
| 128 | MIXED | 100 | 11 | 68 | 15 | 6 | 0.790 | 0.39 | [0.15, 0.61] | 0.18 | 0.08 |
| 128 | ALL | 300 | 69 | 155 | 66 | 10 | 0.747 | 0.47 | [0.29, 0.66] | 0.30 | 0.06 |
| 512 | EN-MATCH | 100 | 58 | 20 | 22 | 0 | 0.780 | 0.51 | [0.16, 0.86] | 0.52 | 0.00 |
| 512 | CS-LAT | 100 | 48 | 35 | 11 | 6 | 0.830 | 0.66 | [0.39, 0.84] | 0.24 | 0.15 |
| 512 | MIXED | 100 | 45 | 34 | 18 | 3 | 0.790 | 0.58 | [0.36, 0.76] | 0.35 | 0.08 |
| 512 | ALL | 300 | 151 | 89 | 51 | 9 | 0.800 | 0.59 | [0.37, 0.77] | 0.36 | 0.09 |
| 1024 | EN-MATCH | 100 | 63 | 15 | 22 | 0 | 0.780 | 0.46 | [0.00, 0.83] | 0.59 | 0.00 |
| 1024 | CS-LAT | 100 | 50 | 33 | 11 | 6 | 0.830 | 0.65 | [0.42, 0.82] | 0.25 | 0.15 |
| 1024 | MIXED | 100 | 46 | 37 | 12 | 5 | 0.830 | 0.66 | [0.41, 0.86] | 0.24 | 0.12 |
| 1024 | ALL | 300 | 159 | 85 | 45 | 11 | 0.813 | 0.61 | [0.40, 0.78] | 0.35 | 0.11 |

Agreement at 128 tokens across all six conditions (from EXP-004): 75.7% (146 both correct, 308 both wrong, 128 Q-correct/O-wrong, 18 Q-wrong/O-correct).

### G2.1 Per condition, all six conditions at 128 tokens (EXP-004)

| Condition | Stored vs J-QWEN | J-QWEN vs J-OSS | κ |
| --- | --- | --- | --- |
| EN-ORIG | 0.94 | 0.64 | 0.33 |
| EN-MATCH | 1.00 | 0.73 | 0.49 |
| CS-LAT | 0.90 | 0.72 | 0.43 |
| ROMAN | 0.94 | 0.81 | 0.56 |
| NATIVE | 0.92 | 0.85 | 0.62 |
| MIXED | 0.92 | 0.79 | 0.39 |

### G3. Does the conclusion change? (α = 0.05)

| Judge | Budget | Contrast | Δ (pp) | Exact p | Topic p | Significant (proposition) | Significant (topic) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128 | CS-LAT vs EN-MATCH | −11 | 0.13 | 0.42 | no | no |
| J-QWEN | 128 | MIXED vs CS-LAT | −23 | <0.001 | 0.004 | yes | yes |
| J-QWEN | 128 | MIXED vs EN-MATCH | −34 | <0.001 | 0.030 | yes | yes |
| J-QWEN | 512 | CS-LAT vs EN-MATCH | −21 | <0.001 | 0.082 | yes | no |
| J-QWEN | 512 | MIXED vs CS-LAT | +4 | 0.57 | 0.65 | no | no |
| J-QWEN | 512 | MIXED vs EN-MATCH | −17 | 0.003 | 0.13 | yes | no |
| J-QWEN | 1024 | CS-LAT vs EN-MATCH | −24 | <0.001 | 0.018 | yes | yes |
| J-QWEN | 1024 | MIXED vs CS-LAT | −3 | 0.70 | 0.72 | no | no |
| J-QWEN | 1024 | MIXED vs EN-MATCH | −27 | <0.001 | 0.003 | yes | yes |
| J-OSS | 128 | CS-LAT vs EN-MATCH | −12 | 0.050 | 0.22 | no | no |
| J-OSS | 128 | MIXED vs CS-LAT | −8 | 0.18 | 0.24 | no | no |
| J-OSS | 128 | MIXED vs EN-MATCH | −20 | 0.002 | 0.067 | yes | no |
| J-OSS | 512 | CS-LAT vs EN-MATCH | −4 | 0.57 | 0.76 | no | no |
| J-OSS | 512 | MIXED vs CS-LAT | −6 | 0.34 | 0.44 | no | no |
| J-OSS | 512 | MIXED vs EN-MATCH | −10 | 0.087 | 0.31 | no | no |
| J-OSS | 1024 | CS-LAT vs EN-MATCH | −7 | 0.21 | 0.52 | no | no |
| J-OSS | 1024 | MIXED vs CS-LAT | −5 | 0.40 | 0.52 | no | no |
| J-OSS | 1024 | MIXED vs EN-MATCH | −12 | 0.043 | 0.22 | yes | no |

### G4. EXP-005 cost and failures

* openai/gpt-oss-120b: 300 calls, 261,224 input tokens, 25,234 output tokens, $0.054
* qwen/qwen3.8-27b: 600 calls, 299,795 input tokens, 233,669 output tokens, $1.175
* Total EXP-005: $1.229
* Persistent failures logged: 0; parse failures: 128|J-QWEN 0, 128|J-OSS 0, 512|J-QWEN 0, 512|J-OSS 0, 1024|J-QWEN 0, 1024|J-OSS 0

### G5. 128-token results, all six conditions (harmonised J-QWEN labels)

| Condition | Acc % | Wilson CI | Topic-boot CI | Stored | J-OSS | Topics 5/5 | Topics 0/5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EN-ORIG | 70 | [60.4, 78.1] | [50, 90] | 64 | 40 | 14 | 6 |
| EN-MATCH | 60 | [50.2, 69.1] | [40, 80] | 60 | 37 | 12 | 8 |
| CS-LAT | 49 | [39.4, 58.7] | [34, 64] | 43 | 25 | 3 | 4 |
| ROMAN | 37 | [28.2, 46.8] | [24, 50] | 33 | 24 | 1 | 6 |
| NATIVE | 32 | [23.7, 41.7] | [18, 46] | 28 | 21 | 0 | 8 |
| MIXED | 26 | [18.4, 35.4] | [12, 41] | 24 | 17 | 0 | 11 |

### G5.1 All 11 pairwise contrasts (J-QWEN)

| Contrast | Δ | b | c | Exact p | Holm (primary) | Topic p | Holm topic | Topic CI | Topics differing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-LAT vs EN-MATCH | −11 | 27 | 16 | 0.13 | 0.13 | 0.42 | 0.42 | [-34, 13] | 15 |
| ROMAN vs EN-MATCH | −23 | 35 | 12 | 0.001 | 0.002 | 0.087 | 0.17 | [-46, 0] | 17 |
| NATIVE vs EN-MATCH | −28 | 36 | 8 | <0.001 | <0.001 | 0.031 | 0.12 | [-49, -6] | 15 |
| MIXED vs EN-MATCH | −34 | 45 | 11 | <0.001 | <0.001 | 0.030 | 0.12 | [-59, -7] | 15 |
| MIXED vs CS-LAT | −23 | 30 | 7 | <0.001 | <0.001 | 0.004 | 0.018 | [-35, -11] | 14 |
| EN-MATCH vs EN-ORIG | −10 | 20 | 10 | 0.099 | – | 0.69 | – | [-35, 15] | 6 |
| MIXED vs ROMAN | −11 | 19 | 8 | 0.052 | – | 0.069 | – | [-21, -1] | 11 |
| MIXED vs NATIVE | −6 | 14 | 8 | 0.29 | – | 0.46 | – | [-18, 6] | 9 |
| ROMAN vs CS-LAT | −12 | 25 | 13 | 0.073 | – | 0.057 | – | [-22, -2] | 16 |
| NATIVE vs CS-LAT | −17 | 27 | 10 | 0.008 | – | 0.033 | – | [-30, -4] | 13 |
| NATIVE vs ROMAN | −5 | 16 | 11 | 0.44 | – | 0.37 | – | [-13, 3] | 10 |

### G5.2 Same, stored labels (original PDF numbers)

| Contrast | Δ | b | c | Exact p | Holm (primary) | Topic p | Holm topic | Topic CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-LAT vs EN-MATCH | −17 | 30 | 13 | 0.014 | 0.014 | 0.19 | 0.19 | [-39, 5] |
| ROMAN vs EN-MATCH | −27 | 37 | 10 | <0.001 | <0.001 | 0.036 | 0.073 | [-48, -5] |
| NATIVE vs EN-MATCH | −32 | 39 | 7 | <0.001 | <0.001 | 0.014 | 0.072 | [-53, -10] |
| MIXED vs EN-MATCH | −36 | 47 | 11 | <0.001 | <0.001 | 0.021 | 0.072 | [-61, -10] |
| MIXED vs CS-LAT | −19 | 29 | 10 | 0.003 | 0.007 | 0.015 | 0.072 | [-32, -6] |
| EN-MATCH vs EN-ORIG | −4 | 16 | 12 | 0.57 | – | 0.84 | – | [-26, 19] |
| MIXED vs ROMAN | −9 | 20 | 11 | 0.15 | – | 0.14 | – | [-19, 1] |
| MIXED vs NATIVE | −4 | 15 | 11 | 0.56 | – | 0.64 | – | [-16, 8] |
| ROMAN vs CS-LAT | −10 | 26 | 16 | 0.16 | – | 0.15 | – | [-21, 1] |
| NATIVE vs CS-LAT | −15 | 30 | 15 | 0.036 | – | 0.10 | – | [-30, 0] |
| NATIVE vs ROMAN | −5 | 18 | 13 | 0.47 | – | 0.37 | – | [-13, 3] |

### G5.3 J-OSS primary contrasts at 128 tokens

| Contrast | Δ | b | c | Exact p | Holm | Topic p | Holm topic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CS-LAT vs EN-MATCH | −12 | 22 | 10 | 0.050 | 0.10 | 0.22 | 0.45 |
| ROMAN vs EN-MATCH | −13 | 22 | 9 | 0.029 | 0.088 | 0.15 | 0.44 |
| NATIVE vs EN-MATCH | −16 | 20 | 4 | 0.002 | 0.008 | 0.035 | 0.18 |
| MIXED vs EN-MATCH | −20 | 29 | 9 | 0.002 | 0.008 | 0.067 | 0.27 |
| MIXED vs CS-LAT | −8 | 18 | 10 | 0.18 | 0.18 | 0.24 | 0.45 |

### G5.4 GEE (J-QWEN), log-odds vs EN-MATCH or CS-LAT

| Contrast | Unit | β | Robust SE | p |
| --- | --- | --- | --- | --- |
| CS-LAT | prompt | -0.445 | 0.286 | 0.12 |
| CS-LAT | proposition | -0.445 | 0.264 | 0.091 |
| CS-LAT | topic | -0.445 | 0.493 | 0.37 |
| ROMAN | prompt | -0.938 | 0.291 | 0.001 |
| ROMAN | proposition | -0.938 | 0.273 | <0.001 |
| ROMAN | topic | -0.938 | 0.494 | 0.058 |
| NATIVE | prompt | -1.159 | 0.296 | <0.001 |
| NATIVE | proposition | -1.159 | 0.263 | <0.001 |
| NATIVE | topic | -1.159 | 0.473 | 0.014 |
| MIXED | prompt | -1.451 | 0.306 | <0.001 |
| MIXED | proposition | -1.451 | 0.310 | <0.001 |
| MIXED | topic | -1.451 | 0.606 | 0.017 |
| MIXED_vs_CS-LAT | prompt | -1.006 | 0.303 | <0.001 |
| MIXED_vs_CS-LAT | proposition | -1.006 | 0.257 | <0.001 |
| MIXED_vs_CS-LAT | topic | -1.006 | 0.293 | <0.001 |

### G5.5 Per-language accuracy (J-QWEN, %)

| Language | EN-ORIG | EN-MATCH | CS-LAT | ROMAN | NATIVE | MIXED |
| --- | --- | --- | --- | --- | --- | --- |
| Hindi | 70 | 60 | 45 | 40 | 40 | 30 |
| Bengali | 70 | 60 | 60 | 20 | 20 | 35 |
| Tamil | 70 | 60 | 50 | 35 | 35 | 15 |
| Telugu | 70 | 60 | 40 | 50 | 30 | 35 |
| Kannada | 70 | 60 | 50 | 40 | 35 | 15 |

### G5.6 Per-topic correct languages (of 5), J-QWEN, with provision and gold status

| Topic | Provision verified | Gold | EN-ORIG | EN-MATCH | CS-LAT | ROMAN | NATIVE | MIXED |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Citizenship Amendment Act Cut-off | Citizenship (Amendment) Act 2019, s. 2 | ok | 5 | 5 | 1 | 3 | 4 | 2 |
| Companies Act CSR Mandate | Companies Act 2013, s. 135(1) | ok | 5 | 5 | 3 | 2 | 0 | 0 |
| Covaxin vs Covishield | CDSCO approvals, Jan. 2021 | ok | 5 | 5 | 5 | 4 | 2 | 4 |
| GST Registration Exemption | CGST Act s. 22; Notif. 10/2019-CT | narrow | 5 | 5 | 4 | 2 | 4 | 1 |
| ISRO PSLV vs GSLV Mk III | ISRO launcher specifications | ok | 5 | 5 | 2 | 0 | 1 | 0 |
| Kharif vs Rabi Rice | ICAR crop-season references | simpl. | 5 | 5 | 5 | 4 | 4 | 4 |
| Lok Sabha vs Rajya Sabha Money Bill | Constitution, Arts. 109–110 | ok | 5 | 5 | 2 | 3 | 3 | 3 |
| National Park vs Wildlife Sanctuary | Wild Life (Protection) Act 1972, ss. 33, 35 | ok | 5 | 5 | 3 | 2 | 2 | 0 |
| Patents Act Compulsory License | Patents Act 1970, s. 84(1) | ok | 5 | 5 | 3 | 3 | 3 | 0 |
| SEBI Insider Trading Pre-Clearance | SEBI PIT Regulations 2015, Sch. B | ok | 5 | 5 | 4 | 2 | 1 | 1 |
| Arbitration Act Time Limit | Arbitration Act 1996, s. 29A | ok | 0 | 5 | 1 | 0 | 0 | 0 |
| PMFBY vs WBCIS | PMFBY/RWBCIS operational guidelines | ok | 0 | 5 | 0 | 0 | 0 | 0 |
| Classical Tamil vs Sanskrit Grammar | Philological references | ok | 5 | 0 | 3 | 1 | 0 | 3 |
| Medical Termination of Pregnancy Act | MTP Act 1971 (am. 2021), s. 3(2) | narrow | 5 | 0 | 0 | 1 | 0 | 0 |
| NEFT vs RTGS | RBI NEFT/RTGS directions | ok | 5 | 0 | 4 | 5 | 4 | 4 |
| RTI Third Party Information | RTI Act 2005, s. 11(1) | ok | 5 | 0 | 1 | 0 | 0 | 0 |
| Environment Clearance Public Hearing | EIA Notification 2006, para. 7 | narrow | 0 | 0 | 0 | 0 | 0 | 0 |
| IBC Section 7 Default Threshold | IBC 2016, s. 4 (₹1 crore from 2020) | ok | 0 | 0 | 0 | 0 | 0 | 0 |
| PM-KISAN vs Rythu Bandhu | PM-KISAN guidelines; Telangana G.O.s | dated | 0 | 0 | 3 | 2 | 1 | 0 |
| Supreme Court vs High Court Writ Jurisdiction | Constitution, Arts. 32, 226 | ok | 0 | 0 | 5 | 3 | 3 | 4 |

### G5.7 Response-side descriptors at 128 tokens (J-QWEN for errors/incompleteness)

| Condition | Script transitions | Prompt chars/tok Qwen3.8 | Prompt chars/tok Qwen2.5 (old) | Resp. chars | Mostly Brahmic % | Any Brahmic % | Ends mid-sentence | Hit 128 | Errors | Incomplete rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EN-ORIG | 0.0 | 5.83 | 5.82 | 538 | 0 | 0 | 82 | 100 | 30 | 0 |
| EN-MATCH | 0.0 | 4.65 | 4.64 | 529 | 0 | 0 | 87 | 100 | 40 | 0 |
| CS-LAT | 0.0 | 4.11 | 4.02 | 423 | 2 | 2 | 90 | 99 | 51 | 11 |
| ROMAN | 0.0 | 3.15 | 2.90 | 390 | 8 | 8 | 91 | 99 | 63 | 18 |
| NATIVE | 1.0 | 2.43 | 1.24 | 279 | 98 | 100 | 95 | 100 | 68 | 36 |
| MIXED | 5.0 | 3.70 | 2.49 | 303 | 88 | 98 | 92 | 100 | 74 | 38 |

### G5.8 Tipping points (J-QWEN)

| FPR | CS-LAT vs EN-MATCH | MIXED vs EN-MATCH | MIXED vs CS-LAT |
| --- | --- | --- | --- |
| 0.00 | 0.82 | 0.43 | 0.53 |
| 0.04 | 0.79 | 0.41 | 0.49 |
| 0.08 | 0.76 | 0.38 | 0.45 |
| 0.12 | 0.74 | 0.35 | 0.41 |
| 0.16 | 0.71 | 0.33 | 0.36 |

### G5b. Post-review audit (audit_budget_truncation.py)

### Truncation by budget (finish reasons logged at 512 and 1,024; at 128 'hit cap' = 128 completion tokens)

| Budget | Condition | Finish reasons | Hit cap | Stopped before cap | Ends mid-sentence | Hit cap & mid-sentence | Stopped but mid-sentence | Mean tokens | Max tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 128 | EN-MATCH | None: 100 | 100 | 0 | 87 | 87 | 0 | 128 | 128 |
| 128 | CS-LAT | None: 100 | 99 | 1 | 90 | 90 | 0 | 128 | 128 |
| 128 | MIXED | None: 100 | 100 | 0 | 92 | 92 | 0 | 128 | 128 |
| 512 | EN-MATCH | stop: 58, length: 42 | 42 | 58 | 42 | 42 | 0 | 438 | 512 |
| 512 | CS-LAT | length: 85, stop: 15 | 85 | 15 | 78 | 75 | 3 | 484 | 512 |
| 512 | MIXED | length: 95, stop: 5 | 95 | 5 | 88 | 88 | 0 | 508 | 512 |
| 1024 | EN-MATCH | stop: 95, length: 5 | 5 | 95 | 15 | 5 | 10 | 510 | 1024 |
| 1024 | CS-LAT | stop: 61, length: 39 | 39 | 61 | 39 | 35 | 4 | 812 | 1024 |
| 1024 | MIXED | length: 64, stop: 36 | 64 | 36 | 63 | 61 | 2 | 936 | 1024 |

### Complete-answers sensitivity (exploratory; selecting on completion can bias)

| Budget | Judge | Contrast | Pairs with both complete | Ref % | Cmp % | b | c | Exact p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 512 | J-QWEN | CS-LAT vs EN-MATCH | 15 | 80 | 33 | 7 | 0 | 0.016 |
| 512 | J-QWEN | MIXED vs CS-LAT | 3 | 0 | 67 | 0 | 2 | 0.50 |
| 512 | J-QWEN | MIXED vs EN-MATCH | 5 | 100 | 60 | 2 | 0 | 0.50 |
| 512 | J-OSS | CS-LAT vs EN-MATCH | 15 | 67 | 20 | 7 | 0 | 0.016 |
| 512 | J-OSS | MIXED vs CS-LAT | 3 | 33 | 67 | 0 | 1 | 1.00 |
| 512 | J-OSS | MIXED vs EN-MATCH | 5 | 100 | 60 | 2 | 0 | 0.50 |
| 1024 | J-QWEN | CS-LAT vs EN-MATCH | 57 | 79 | 61 | 12 | 2 | 0.013 |
| 1024 | J-QWEN | MIXED vs CS-LAT | 29 | 48 | 55 | 4 | 6 | 0.75 |
| 1024 | J-QWEN | MIXED vs EN-MATCH | 34 | 76 | 59 | 8 | 2 | 0.11 |
| 1024 | J-OSS | CS-LAT vs EN-MATCH | 57 | 65 | 60 | 7 | 4 | 0.55 |
| 1024 | J-OSS | MIXED vs CS-LAT | 29 | 55 | 52 | 3 | 2 | 1.00 |
| 1024 | J-OSS | MIXED vs EN-MATCH | 34 | 65 | 59 | 6 | 4 | 0.75 |

Unpaired accuracy among complete responses only:

| Budget | Judge | EN-MATCH (n, %) | CS-LAT (n, %) | MIXED (n, %) |
| --- | --- | --- | --- | --- |
| 512 | J-QWEN | 58, 86 | 15, 33 | 5, 60 |
| 512 | J-OSS | 58, 74 | 15, 20 | 5, 60 |
| 1024 | J-QWEN | 95, 84 | 61, 59 | 36, 58 |
| 1024 | J-OSS | 95, 66 | 61, 57 | 36, 56 |

### Multiplicity across the follow-up (18 tests = 3 budgets × 2 judges × 3 contrasts)

Holm-3 = within the three contrasts of one budget–judge cell; Holm-18 = across all 18 follow-up tests. The 1,024-token run was added after the 512-token results were seen, so its tests are exploratory.

| Judge | Budget | Contrast | Δ | Exact p | Holm-3 | Holm-18 | Topic p | Topic Holm-3 | Topic Holm-18 | Topic 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128 | CS-LAT vs EN-MATCH | −11 | 0.13 | 0.13 | 1.00 | 0.42 | 0.42 | 1.00 | [-34, 13] |
| J-QWEN | 128 | MIXED vs CS-LAT | −23 | <0.001 | <0.001 | 0.003 | 0.004 | 0.011 | 0.062 | [-35, -11] |
| J-QWEN | 128 | MIXED vs EN-MATCH | −34 | <0.001 | <0.001 | <0.001 | 0.030 | 0.061 | 0.46 | [-59, -7] |
| J-QWEN | 512 | CS-LAT vs EN-MATCH | −21 | <0.001 | 0.002 | 0.007 | 0.082 | 0.24 | 1.00 | [-41, -1] |
| J-QWEN | 512 | MIXED vs CS-LAT | +4 | 0.57 | 0.57 | 1.00 | 0.65 | 0.65 | 1.00 | [-8, 15] |
| J-QWEN | 512 | MIXED vs EN-MATCH | −17 | 0.003 | 0.007 | 0.040 | 0.13 | 0.26 | 1.00 | [-35, 3] |
| J-QWEN | 1024 | CS-LAT vs EN-MATCH | −24 | <0.001 | <0.001 | <0.001 | 0.018 | 0.036 | 0.29 | [-42, -8] |
| J-QWEN | 1024 | MIXED vs CS-LAT | −3 | 0.70 | 0.70 | 1.00 | 0.72 | 0.72 | 1.00 | [-14, 8] |
| J-QWEN | 1024 | MIXED vs EN-MATCH | −27 | <0.001 | <0.001 | <0.001 | 0.003 | 0.010 | 0.062 | [-42, -13] |
| J-OSS | 128 | CS-LAT vs EN-MATCH | −12 | 0.050 | 0.10 | 0.50 | 0.22 | 0.45 | 1.00 | [-29, 4] |
| J-OSS | 128 | MIXED vs CS-LAT | −8 | 0.18 | 0.18 | 1.00 | 0.24 | 0.45 | 1.00 | [-19, 2] |
| J-OSS | 128 | MIXED vs EN-MATCH | −20 | 0.002 | 0.005 | 0.022 | 0.067 | 0.20 | 0.94 | [-39, -2] |
| J-OSS | 512 | CS-LAT vs EN-MATCH | −4 | 0.57 | 0.69 | 1.00 | 0.76 | 0.93 | 1.00 | [-22, 15] |
| J-OSS | 512 | MIXED vs CS-LAT | −6 | 0.34 | 0.69 | 1.00 | 0.44 | 0.93 | 1.00 | [-18, 6] |
| J-OSS | 512 | MIXED vs EN-MATCH | −10 | 0.087 | 0.26 | 0.78 | 0.31 | 0.93 | 1.00 | [-26, 6] |
| J-OSS | 1024 | CS-LAT vs EN-MATCH | −7 | 0.21 | 0.42 | 1.00 | 0.52 | 1.00 | 1.00 | [-24, 10] |
| J-OSS | 1024 | MIXED vs CS-LAT | −5 | 0.40 | 0.42 | 1.00 | 0.52 | 1.00 | 1.00 | [-17, 7] |
| J-OSS | 1024 | MIXED vs EN-MATCH | −12 | 0.043 | 0.13 | 0.47 | 0.22 | 0.66 | 1.00 | [-28, 5] |

### Independent check (independent_check.py)

**118 checks, 118 passed, 0 failed.** Full table: `paper_v2/output/independent_check.md` (statsmodels exact McNemar and Wilson, scikit-learn κ, Monte Carlo sign-flip, bootstrap with a different seed).


### G6. Final manuscript text exactly as built into the DOCX (build_paper.py)

**Title**

> Representation Effects in Indic Factual Question Answering: Script, Output Budget, and Judge Dependence

**Abstract**

> Comparisons of LLM factual accuracy across languages and scripts usually change the question along with its representation. We hold 100 propositions on 20 Indian public-policy topics fixed and render each in English, native script, Romanized text, Latin-script code-switching (CS-LAT) and mixed-script code-switching (MIXED) in five Indic languages (Hindi, Bengali, Tamil, Telugu, Kannada), and ask how much the measured differences depend on two evaluation choices: the output-token budget and the judge. With Qwen3.8-27B and a 128-token cap, judge-assessed accuracy is 60% for a template-matched English prompt and 49%, 37%, 32% and 26% for CS-LAT, Romanized, native-script and MIXED prompts, and MIXED is 23 points below CS-LAT (p < 0.001; topic-level p = 0.004). Almost every response hit that cap, and Brahmic-script answers fit half as many characters into it. When the key conditions are re-answered with 512 and 1,024 tokens, no MIXED–CS-LAT gap is detected under either a self-judge (+4 and −3 points) or a judge from another model family (−6 and −5); the intervals exclude the 128-token gap, although no equivalence test was pre-specified and 64% of MIXED answers still reach the 1,024-token cap. The English–CS-LAT gap behaves differently: under the self-judge it grows to 24 points at 1,024 tokens (topic-level p = 0.018; 0.29 after correction across all follow-up tests), while under the second judge it is 4–12 points and never significant. The judges agree on 75–81% of outputs (κ = 0.47–0.61), and no human validation of either was performed. Measured representation effects are therefore sensitive to the output budget and to the evaluator, and should not be read as effects of representation without checking both. Prompts, outputs, judgements, a gold-answer ledger and code are released.

**Index Terms**

> multilingual evaluation, code-switching, script, Indic languages, output budget, LLM-as-a-judge, judge agreement, paired evaluation

**I ¶3**

> We build the comparison so that they can be. Each of 100 propositions is rendered in five paired representations (Table I). Two of them, CS-LAT and MIXED, are meant to differ only in whether the Indic words are written in Latin or Brahmic script; this holds word for word in Hindi, Bengali and Tamil, while in Telugu and Kannada the question word also differs (Section III-A). We add a second English condition after finding that the original English template was more specific than the template shared by the other four conditions (Section III-B). We then ask whether the differences we measure survive two changes to the evaluation that representation studies rarely make: a larger output budget (512 and 1,024 tokens instead of 128) and a judge from a different model family.

**I Research questions**

> **Research questions.** RQ1: at a fixed output budget and judge, does judge-assessed accuracy depend on representation when the proposition is held fixed? RQ2: does mixed-script code-switching lower accuracy relative to the same code-switched words in Latin script? RQ3: do these differences change when the output budget grows? RQ4: do they change with the judge, and how far do two judges agree? RQ5: is the script contrast associated with input tokenization length? Hallucination detectors and mitigation are outside the scope of this paper.

**I Contributions**

> **Contributions.** (1) A paired six-condition design for Indic factual QA, with a matched-English control that removes a template confound we found in our first run. (2) A controlled three-budget rerun in which the 23-point mixed-script penalty measured at 128 tokens is not detectable at 512 or 1,024 tokens under either of two judges, while the English–code-switching gap moves in the opposite direction under one judge only. (3) Judge disagreement as a result: harmonising the judge configuration shrinks the English–code-switching gap at 128 tokens from 17 to 11 points, the two judges agree on 75–81% of outputs, and whether the English advantage is significant depends on which judge is used. (4) Inference that treats the 20 topics as the unit of independent evidence, and a release of prompts, outputs, both judges' labels, a gold-answer ledger and evaluation scripts.

**I Findings in brief**

> **Findings in brief.** Evaluating multilingual LLMs across representation conditions is sensitive to the output-token budget and to the choice of evaluator, and observed differences should not automatically be interpreted as representation effects. At 128 tokens, accuracy falls from English to the Indic representations and mixed script is lowest. Almost every response hits that cap and Brahmic-script answers are about half as long in characters; with 512 or 1,024 tokens, no MIXED–CS-LAT difference is detected under either judge, though we do not claim equivalence. Because 64% of MIXED answers still reach the 1,024-token limit, this is a sensitivity finding, not a clean estimate of the effect of script. The English advantage over Latin-script code-switching is significant at the topic level only under the self-judge at 1,024 tokens, and not after correction across all follow-up tests; under the cross-family judge it is small at every budget. Neither judge has been validated against human labels, so we report this as judge sensitivity, not as evidence that either judge is right.

**II Multilingual evaluation**

> **Multilingual evaluation for Indic languages.** IndicNLPSuite and IndicXTREME provide corpora and task benchmarks for Indic languages [2], [3], and MEGA compares generative models across many languages and tasks [1]. Such benchmarks answer how well a model performs per language, but their per-language items are not the same questions. Romanized input has itself been proposed as a bridge to Indic languages for LLMs [23]; our ROMAN condition measures the same factor on fixed propositions.

**II Tokenization**

> **Tokenization.** Subword vocabularies fragment low-resource scripts into more tokens [7], [10], with measurable differences in cost and quality across languages [5], [6]. The same premium applies to generated text: an answer in a script that costs more tokens per character fits less content into a fixed output limit, which is the mechanism our budget experiment probes. Our mediation analysis asks whether the input-side quantity explains the script contrast.

**II Judges**

> **Factuality evaluation and LLM judges.** We use closed-book questions with a gold answer, closer in spirit to TruthfulQA-style checks than to long-form factual precision scoring [11], [12]. LLM graders are convenient but biased, for example towards their own outputs, answer position and length [13], [24], [25], and their agreement with humans and with each other is lower in many non-English languages, including Indic languages [26], [27]. We therefore grade with two judges from different model families and report their disagreement as a result.

**Fig. 1 caption**

> Fig. 1. Study design. Each proposition is rendered in six conditions and answered once by Qwen3.8-27B under greedy decoding with a 128-token limit; responses are graded against the gold answer by the same model (J-QWEN). The follow-up (Section VI-B) re-answers three conditions with 512 and 1,024-token limits and grades every budget with J-QWEN and with gpt-oss-120b (J-OSS). Key contrasts: EN-MATCH vs. CS-LAT (code-switching) and CS-LAT vs. MIXED (script).

**Table I caption**

> One proposition in all six conditions (Hindi). In Hindi, CS-LAT and MIXED contain the same words in the same order and differ only in the script of *ke*, *ya*, *kya hai* (also true for Bengali and Tamil; in Telugu and Kannada the question word differs, Section III-A). The topic string stays in Latin script in every condition, so NATIVE contains one Latin–Brahmic boundary per prompt.

**III-A conditions**

> Table I defines the six conditions. In NATIVE, ROMAN, CS-LAT and MIXED the question frame is one fixed template (“main rule, date or parameter regarding *X*”) with *X* the topic string; only the rendering varies. ROMAN and NATIVE render the same Indic frame in Latin and Brahmic script, except in Hindi, where ROMAN uses *tareekh* and NATIVE *tithi* for “date”. CS-LAT replaces part of the frame with English words (“main rule”, “date”, “parameter”, and in Hindi and Bengali also “regarding”), and MIXED writes the remaining Indic words of CS-LAT in native script. In Hindi, Bengali and Tamil, CS-LAT and MIXED are word-for-word transliterations of each other. In Telugu and Kannada they are not: the question word is *enti* vs. ఏమిటి (*emiti*) in Telugu and *yenu* vs. ಯಾವುದು (*yāvudu*, “which”) in Kannada. We report the CS-LAT–MIXED contrast on all 100 propositions, as planned, and on the 60 word-identical ones as a sensitivity analysis. Fluent speakers of all five languages, including the author (Telugu) and a teammate (Hindi, Telugu, Kannada), reviewed the prompt templates and judged them natural and correct. This was a yes/no check without item-level ratings; the reviewers saw the templates, not the model's outputs, and the check establishes neither full semantic equivalence nor the validity of the judges.

**III-B amendment**

> In the first run (EXP-002) the English prompts used two question templates (“key structural or operational difference between *X*” and “specific prerequisite condition or timeline applies to *X*”), while all other conditions used the single generic template. English-versus-Indic comparisons were therefore confounded with question type, a flaw we found only when auditing the raw prompt strings. We added EN-MATCH, the generic template in English (100 prompts, same gold answers), and ran it in a second run (EXP-003) with the same model and decoding settings, without modifying the earlier results. The two runs did not grade alike: EXP-002 called the judge at temperature 0.3 with the answering system prompt, EXP-003 at temperature 0 with an evaluator system prompt (Section IV). We therefore re-graded all 600 outputs with the EXP-003 configuration; all comparisons below use these harmonised labels and EN-MATCH as the English reference. EN-ORIG and EN-MATCH do not differ detectably (70% vs. 60%; exact p = 0.10, topic-level p = 0.69).

**III-C gold answers**

> **Gold answers.** Each topic has one gold answer, shared by its five language groups and all six conditions. The benchmark stores an evidence snippet and a source URL with each; the snippets are template-generated paraphrases rather than quotations, and the URLs point to agency home pages (e.g. rbi.org.in) rather than to specific documents. The author and, separately, volunteer reviewers checked the gold answers for factual correctness against public sources, and the author verified each answer against its governing provision, as in force in October 2026, for currency and for completeness relative to the question actually asked (Appendix A, Table VII; a per-topic ledger is released). The volunteer check was not logged item by item and no agreement statistic was computed, so we report it as a check rather than a measurement. All 20 answers are consistent with the provision identified. One describes a scheme that has since been replaced (Telangana's Rythu Bandhu, now Rythu Bharosa). Three are narrower than the generic question allows, so that other correct answers exist: the GST registration threshold (₹40 lakh applies to suppliers of goods, ₹20 lakh to services), the MTP Act (two practitioners are required only between 20 and 24 weeks) and the environmental-clearance public hearing (the gold lists two of several exemptions). Removing these three topics changes no conclusion (Appendix B). Gold-answer checks establish that the reference is right; they do not show that the judge grades model answers correctly, which no human has yet assessed on these outputs (Section VII). Agreement figures in older project documents (e.g. κ = 0.719) concern a different, earlier pilot whose annotation files are not in the repository; they are not used.

**IV intro**

> Fig. 1 summarizes the pipeline: 100 propositions are rendered in six conditions, answered once by the primary model under greedy decoding, graded against the gold answer, and analysed at three levels of clustering. Section VI-B adds a follow-up run with a larger output budget.

**IV Models**

> **Models.** The primary model is served by Groq under the API identifier `qwen/qwen3.8-27b`, which is recorded in every prediction row and in the response metadata of the follow-up. The provider lists it as an Alibaba Cloud model, and a public checkpoint of that name exists (Qwen/Qwen3.8-27B, 27.8B parameters, Apache-2.0). That checkpoint's tokenizer reproduces the API's prompt-token counts for all 600 prompts up to a constant chat-template offset of 48 tokens, and counts 125–128 tokens for responses the API reports as 128, so the tokenizer is established; whether the provider serves exactly those weights, and at what numerical precision, we cannot verify. We call the model Qwen3.8-27B. Older project documents call it “Qwen-2.5-27B” and the repository configuration lists `qwen/qwen3.6-27b`; neither produced the reported outputs. The second model is ALLaM-2-7B (`allam-2-7b`) [14]. All results are single-run. Greedy decoding on the hosted API was not fully deterministic: 84–85% of 512-token responses begin with exactly the 128-token response to the same prompt, and 78–91% of 1,024-token responses with the 512-token response; the rest diverge.

**IV Prompting**

> **Prompting and output budget.** Each prompt is sent with the system message “You are a helpful assistant answering questions from Indian users. Questions may mix an Indian language with English. Answer factually, accurately, and concisely.” Decoding is greedy (temperature 0, top-p 1) with at most 128 output tokens in the main runs. The model almost never stops on its own: 598 of 600 responses used all 128 tokens, and 82–95% end mid-sentence in every condition, English included. The provider's finish reason was not logged in the main runs; it was logged in both follow-up runs.

**IV Judging**

> **Judging.** A judge receives the question as the model saw it, the gold answer and the response, and returns CORRECT or HALLUCINATED with a short reason (Appendix C). Three label sets exist. *Stored*: the labels saved with the predictions; EXP-002 obtained them from Qwen3.8-27B at temperature 0.3 with the answering system prompt (a side effect of reusing the generation client), EXP-003 at temperature 0 with the system prompt “You are an expert factuality evaluator.” *J-QWEN*: all 600 outputs re-graded by Qwen3.8-27B with the EXP-003 configuration, the one the study intended; these labels are the primary analysis. *J-OSS*: the same rubric applied by gpt-oss-120b (`openai/gpt-oss-120b`, temperature 0, low reasoning effort), a judge from a different model family that did not produce the answers. J-QWEN reproduces the stored labels on all 100 EN-MATCH items (same configuration) and on 90–94% of items in the other conditions. No judge has been validated against human labels on these outputs, and we do not treat either as the more accurate one. “Accuracy” below is the share of responses a judge labels CORRECT: a judge-assessed quantity, not a direct measurement of recall.

**IV Statistics**

> **Statistics.** Observations are nested. A *prompt* is one string sent to the model. A *proposition* is a fact in one language group, rendered as six paired prompts. A *topic* (e.g. NEFT vs. RTGS) contains five propositions, one per language, with the same gold answer; across the five matched-template conditions it contributes 25 prompts. A proposition-level test asks whether the model, given these 100 facts, does better in one representation than in another. A topic-level test asks whether the difference should be expected to recur on new topics; with 20 topics it has much less power, but it matches the generalisation most readers want, so we report both. At the proposition level we use exact McNemar tests [15] with Holm correction [16] within a pre-specified family of five contrasts: each of NATIVE, ROMAN, CS-LAT and MIXED against EN-MATCH, and MIXED against CS-LAT. At the topic level we use an exact sign-flip permutation test over all 2²⁰ sign patterns of the 20 per-topic accuracy differences and a percentile bootstrap over topics (10,000 resamples, fixed seed), with Holm correction within the same family. Logistic GEE with independence working correlation and robust covariance clustered at prompt, proposition and topic level [18] is reported in Appendix B; with 20 clusters robust standard errors are anti-conservative [19], [20], so topic-level conclusions do not rest on it. Wilson intervals [17] are given for single proportions; the design effect is 1 + (*m* − 1)ρ with ρ from the one-way ANOVA estimator [21]. The follow-up (Section VI-B) has the same three contrasts at every budget, fixed in the analysis scripts before its outputs were graded: CS-LAT vs. EN-MATCH, MIXED vs. CS-LAT and MIXED vs. EN-MATCH, plus the change in each gap between budgets, each under both judges. The 512-token run was planned to test the budget confound; the 1,024-token run was added after its results were seen, so 1,024-token results are exploratory. For the follow-up we report Holm adjustment within each budget–judge cell and across all 18 follow-up tests (3 budgets × 2 judges × 3 contrasts). A non-significant difference is not evidence of equivalence; no equivalence margin was pre-specified, so we report intervals. Everything else is exploratory. All numbers are recomputed from the raw files by the scripts in Appendix E.

**V heading**

> V. RESULTS AT A 128-TOKEN BUDGET

**V-A**

> Table II and Fig. 2 give the main result under the harmonised judge. Relative to EN-MATCH (60%), accuracy is 49% for CS-LAT, 37% for ROMAN, 32% for NATIVE and 26% for MIXED, differences of 11, 23, 28 and 34 points. At the proposition level the ROMAN, NATIVE and MIXED differences are significant after Holm correction (adjusted p ≤ 0.002); the CS-LAT difference is not (p = 0.13). With the stored labels, which graded EN-MATCH and the Indic conditions under different judge settings, the CS-LAT gap was 17 points (p = 0.014): about a third of it came from the grading difference. The ordering among the three non-English-script conditions is uncertain: ROMAN vs. MIXED gives p = 0.052 and NATIVE vs. MIXED p = 0.29 (Table VIII).

**Table II caption**

> Qwen3.8-27B accuracy on the 100 paired propositions at a 128-token budget, harmonised judge (J-QWEN). Δ: difference in correct answers out of 100 relative to EN-MATCH. Exact p: two-sided exact McNemar; Holm: within the five primary contrasts (MIXED vs. CS-LAT is in the text and Table VIII). Topic p: exact sign-flip permutation test on the 20 per-topic differences, Holm-adjusted in parentheses. Stored, J-OSS: accuracy (%) under the original labels and under the cross-family judge. †EN-ORIG vs. EN-MATCH, exploratory.

**Fig. 2 caption**

> Fig. 2. (a) Accuracy (J-QWEN) with Wilson 95% intervals (n = 100 per condition; points not independent within topic). (b) Number of languages (of five) in which each topic is answered correctly, per condition. Topics sorted by EN-MATCH, then EN-ORIG.

**Fig. 3 caption**

> Fig. 3. Accuracy by language and condition (J-QWEN; n = 20 per cell).

**V-A uncertainty**

> The uncertainty is larger than the Wilson intervals imply. Topic-bootstrap intervals are wider (for EN-MATCH [40, 80] against Wilson [50.2, 69.1]) because accuracy is concentrated by topic: two topics (Environment Clearance Public Hearing, IBC Section 7) are wrong in every condition, and twelve are right for English in all five languages (Fig. 2b). The two all-wrong topics fail for different reasons. For IBC the model gives the pre-2020 default threshold of ₹1 lakh, a genuine error; for Environment Clearance the gold answer lists exemptions that the generic question does not ask for (Section III-C).

**V-B heading**

> B. Mixed vs. Latin-script code-switching

**V-B**

> Writing the code-switched prompt with its Indic words in Brahmic rather than Latin script lowers accuracy from 49% to 26%, a 23-point drop. Of 37 propositions that differ, 30 favour CS-LAT and 7 favour MIXED (exact p < 0.001, Holm p < 0.001). The drop appears in all five languages (Fig. 3); the mean of the 20 per-topic differences is 23 points (bootstrap 95% CI [11, 35]; permutation p = 0.004, Holm-adjusted 0.018; 14 of 20 topics differ), and the GEE odds ratio is 0.37 (topic-clustered 95% CI 0.21–0.65). On the 60 propositions in Hindi, Bengali and Tamil, where the two prompts are word-for-word identical, the drop is 25 points (p = 0.0015; topic-level p = 0.016). Excluding the three topics with narrow gold answers leaves it at 23.5 points (p < 0.001). Under the stored labels it was 19 points (p = 0.003; topic-level p = 0.015, Holm-adjusted 0.072). At a 128-token budget, then, the mixed-script penalty is the most consistent result in the study.

**V-B note**

> Section VI shows that this result does not survive a larger output budget. Here we note only why that check is needed: 88% of MIXED responses are written mostly in Brahmic script, against 2% of CS-LAT responses, so the prompt script also changes the script of the answer, and with it how much answer fits into 128 tokens.

**V-C**

> Observations within a topic are strongly dependent. In the five matched-template conditions the intra-topic correlation is ρ = 0.27, the design effect 7.5 and the effective sample size 67 out of 500. Fig. 4a and Table IX show what this does. For CS-LAT against EN-MATCH, the GEE p value is 0.12 at prompt level, 0.09 at proposition level and 0.37 at topic level, and the topic-level permutation test gives p = 0.42 (bootstrap 95% CI for the mean per-topic difference [−34, 13] points). For ROMAN, NATIVE and MIXED against EN-MATCH the topic-level permutation p values are 0.087, 0.031 and 0.030, and none survives Holm correction at topic level (smallest adjusted value 0.12). Only MIXED vs. CS-LAT survives Holm correction at every level (adjusted topic-level p = 0.018). At this budget the English-vs-Indic differences are consistent in direction, but at the level of topics only the larger ones approach significance, and the English–CS-LAT gap does not.

**Fig. 4 caption**

> Fig. 4. (a) GEE log-odds differences from EN-MATCH (J-QWEN) with robust 95% CIs at three clustering levels (circle: prompt; square: proposition; diamond: topic). Intervals widen at topic level, where the CS-LAT and ROMAN intervals include zero. (b) Per-topic accuracy difference, CS-LAT minus MIXED (20 topics; band: bootstrap 95% CI of the mean; line: mean).

**V-D languages**

> Accuracy by language is in Fig. 3. MIXED is below CS-LAT in all five languages; EN-MATCH is above CS-LAT in four and tied with it in Bengali. A permutation test of whether the condition profile depends on language (statistic: interaction sum of squares of the language × condition accuracy table; null: language labels permuted among the five propositions of each topic; 10,000 permutations) gives p = 0.17. With 20 observations per cell this test has little power, so we report no detectable language dependence, not that languages behave alike; Bengali and Telugu differ visibly in the ROMAN column (20% vs. 50%), and nothing here can separate chance from effect.

**V-D models**

> ALLaM-2-7B answers 10% of matched-English questions correctly and 5%, 2%, 2% and 3% in CS-LAT, ROMAN, NATIVE and MIXED (stored labels), so the representation contrast cannot be measured on it. The five-condition rank correlation with Qwen3.8-27B under the stored labels (ρ = 0.67, p = 0.22) describes a floor, not a replication. We make no claim about other model families.

**VI heading**

> VI. TOKENIZATION AND THE OUTPUT BUDGET

**VI-A heading**

> A. Input tokenization (exploratory)

**VI-A tokenization**

> Subword fragmentation is a standard explanation for weaker performance on non-Latin scripts. Our earlier analysis measured characters per token with the Qwen2.5-7B tokenizer, which does not match the served model: it disagrees with the API's prompt-token counts and would put capped 128-token responses at 120–305 tokens. With the Qwen3.8-27B tokenizer, which does match (Section IV), Brahmic text is less fragmented than that analysis implied: prompts average 2.43 characters per token in NATIVE and 3.70 in MIXED, against 4.65 in EN-MATCH and 4.11 in CS-LAT (previously 1.24 and 2.49 for NATIVE and MIXED). Within the CS-LAT–MIXED contrast, MIXED lowers characters per token (*a* = −0.41, SE 0.10), but once condition is controlled the mediator's association with correctness is not significant and has the wrong sign for a fragmentation account (*b* = −0.40, SE 0.23, p = 0.08; 95% CI −0.85 to 0.05; Sobel p = 0.11). The implied indirect effect is positive while the total effect is negative (−1.01). Because characters per token is almost determined by condition and language in this design, the test has little leverage: it is exploratory and does not rule out a tokenization effect. Across the six conditions, characters per token and accuracy are rank-correlated (ρ = 0.83), but six points that differ in language frame, script and answer length identify nothing (Fig. 5c).

**Fig. 5 caption**

> Fig. 5. (a) Mean response length for EN-MATCH, CS-LAT and MIXED at 128, 512 and 1,024 tokens; labels give the % of responses that hit the cap. (b) Accuracy of the same 300 prompts at each budget, graded by J-QWEN (solid) and J-OSS (dashed). (c) Condition-level prompt characters per token (Qwen3.8 tokenizer) against accuracy at 128 tokens (six points; descriptive only).

**VI-B heading**

> B. Response script, length and the output budget

**VI-B response side**

> The prompt script largely determines the response script: 98% of NATIVE and 88% of MIXED responses are written mostly in Brahmic script (more than half of their letters), against 8% and 2% for ROMAN and CS-LAT and none for English. Brahmic answers cost more tokens per character (2.2–2.4 characters per token in NATIVE and MIXED responses against 4.1 in English ones), and nearly all responses used the full 128 tokens, so mean response length is 529 characters in EN-MATCH but 279 in NATIVE and 303 in MIXED (Fig. 5a). Among errors, the share whose judge reason mentions an incomplete or missing answer (a keyword rule, Appendix C) is 0 of 40 in EN-MATCH, 11 of 51 in CS-LAT, 36 of 68 in NATIVE and 38 of 74 in MIXED. The rule depends on the judge's wording and does not measure truncation, but it points the same way.

**VI-B budget reruns**

> To separate script from budget we re-ran EN-MATCH, CS-LAT and MIXED (300 prompts) twice, with 512 and with 1,024-token limits, changing nothing else: same model identifier, system prompt, decoding settings and prompts. Every budget was graded by J-QWEN and by J-OSS, so each comparison across budgets uses one judge (Table III, Fig. 5b). Even 1,024 tokens is not an unconstrained condition: according to the provider's finish reasons, 5 EN-MATCH, 39 CS-LAT and 64 MIXED responses still hit the limit (15, 39 and 63 end mid-sentence). The MIXED–CS-LAT gap, −23 points at 128 tokens under J-QWEN, is +4 at 512 and −3 at 1,024 (p = 0.57 and 0.70; topic-bootstrap 95% CIs [−8, 15] and [−14, 8]); under J-OSS it is −8, −6 and −5, never significant (CIs at 512 and 1,024 [−18, 6] and [−17, 7]). These intervals exclude the 23-point gap seen at 128 tokens, but they do not establish equivalence. Between 128 and 1,024 tokens the gap narrows by 20 points under J-QWEN (CI [5, 34], permutation p = 0.023). The pattern holds on the 60 word-identical propositions (J-QWEN at 1,024 tokens: 65% vs. 60%, p = 0.58) and, as an exploratory check that may be biased by selecting on completion, on the 29 propositions where both responses finished before the 1,024-token limit (J-QWEN 48% vs. 55%, p = 0.75; J-OSS 55% vs. 52%, p = 1.0). The English–CS-LAT gap moves the other way under J-QWEN, from −11 at 128 to −21 at 512 and −24 at 1,024 tokens (exact p < 0.001; topic-level p = 0.018, Holm-adjusted 0.036 within the three contrasts of that budget and 0.29 across all 18 follow-up tests), whereas under J-OSS it is −12, −4 and −7 and not significant at any budget (p ≥ 0.050). Restricted to the 57 propositions where both responses finished, the same split appears (J-QWEN 79% vs. 61%, p = 0.013; J-OSS 65% vs. 60%, p = 0.55).

**Table III caption**

> Output-budget follow-up: the same 300 prompts answered with 128, 512 and 1,024 tokens, each budget graded by both judges. Accuracy (%) per condition; gaps in points with exact McNemar p / topic-level permutation p. Cap: responses (of 100) that hit the output limit, EN-MATCH / CS-LAT / MIXED.

**VI-B conclusions**

> Three conclusions follow. First, the 128-token MIXED penalty is not evidence that script alternation harms recall: once the budget allows longer answers, no difference between mixed-script and Latin-script code-switched prompts is detected under either judge, and the intervals exclude a gap of the 128-token size. The pattern is consistent with Brahmic-script answers reaching the cap before reaching the fact, so that answers a human would call incomplete are graded as wrong; the EN-MATCH answer on the MTP Act, for instance, correctly states the one-practitioner rule for the first 20 weeks, is cut off before the 20–24-week rule, and is graded HALLUCINATED. Second, NATIVE and MIXED behave alike at 128 tokens (32% and 26%, p = 0.29) although MIXED has five script boundaries per prompt and NATIVE one, which also argues against a boundary-density account. Third, the English advantage is unstable: it grows with the budget under one judge and stays small under the other, and its topic-level significance under the first does not survive correction across the follow-up. We cannot tell from these data which judge is closer to a careful human reader, so the instability itself is the finding. Because most MIXED and many CS-LAT answers still reach the 1,024-token limit, the output budget remains a possible confound for any residual difference.

**VII heading**

> VII. JUDGE DEPENDENCE

**VII judge dependence**

> The judge matters in three ways. *Configuration.* Our first run graded the Indic conditions at temperature 0.3 with the answering system prompt and EN-MATCH at temperature 0 with an evaluator prompt. Harmonising the configuration changed 6–10% of the labels in each re-graded condition and moved CS-LAT accuracy from 43% to 49%, so the stored English–CS-LAT gap (17 points) exceeded the harmonised one (11). *Family.* Table IV gives agreement between J-QWEN and J-OSS by budget and condition. Agreement is 74.7% at 128 tokens (κ = 0.47), 80.0% at 512 (κ = 0.59) and 81.3% at 1,024 (κ = 0.61), with wide topic-bootstrap intervals for κ. Disagreements run mostly one way: J-QWEN labels CORRECT 30–36% of the answers J-OSS labels wrong, whereas J-OSS labels CORRECT 6–11% of the answers J-QWEN labels wrong. In the disagreements we inspected, J-QWEN accepted answers that were on topic and accurate but did not state the gold fact (for example, answers that only name the governing Act), and J-OSS rejected them; the rubric (“judge only factual correctness and whether it actually addresses the question”) does not say which reading is intended, and truncated answers make such cases common. *Conclusions.* The MIXED–CS-LAT conclusion depends on the judge at 128 tokens (significant under J-QWEN only) but not at 512 or 1,024 tokens (not significant under either). The English–CS-LAT conclusion depends on the judge at both larger budgets. No human gold-standard labels were collected for any output, so these results establish that conclusions are sensitive to the judge, not which judge is right.

**Table IV caption**

> Agreement between the two judges on the same 300 outputs at each budget. Agree: share of identical labels; κ: Cohen's kappa with topic-bootstrap 95% CI; Q✓O✗: J-QWEN CORRECT and J-OSS wrong; Q✗O✓: the reverse. No human labels were collected.

**VII tipping**

> Table V turns the remaining uncertainty into tipping points. Assuming English answers are judged without error, it gives the sensitivity the judge would need on the comparison condition for that condition's true accuracy to equal the reference's. A correction applied equally to both conditions (the Rogan–Gladen estimator [22]) divides a gap by TPR − FPR and can only enlarge it, so a common-error grid cannot show robustness; the relevant threat is differential error. At a false-accept rate of 0.08, erasing the CS-LAT gap would need a judge that rejects 24% of truly correct CS-LAT answers (sensitivity 0.76), and erasing the MIXED gap one that rejects 62% (0.38). These are hypothetical error rates, not estimates of the judge's actual errors, which are unknown; the cross-family disagreement shows they are not small. A crude check agrees: on the 330 outputs whose gold answer contains numerals, the J-QWEN label matches whether all gold numerals appear in the response 67% of the time, with disagreements in both directions (73 accepted answers lack the figure; 35 rejected ones contain it).

**Table V caption**

> Sensitivity the judge would need on the comparison condition for its true accuracy to equal the reference condition's, at the given false-accept rate (J-QWEN, 128 tokens). Reference answers assumed judged without error. Lower entries mean a larger error would be needed.

**VIII Discussion 1**

> What the data support is narrower than the design promised, and different from what our first run suggested. Evaluating multilingual LLMs across representation conditions is sensitive to the output-token budget and to the choice of evaluator, and observed differences should not automatically be interpreted as representation effects. For this model and these 20 topics, the clearest representation effect at a 128-token budget, the mixed-script penalty, is no longer detected when answers can be longer, under either judge. Since many answers still reach even the largest budget we tested, this shows that the 128-token estimate is sensitive to the budget; it does not provide a clean estimate of the script effect itself; the English advantage over code-switching appears or disappears with the judge. We do not claim that native script or code-switching damages factual recall, and we make no claim about other models.

**VIII Discussion 2**

> The practical lesson is methodological. Output caps are often set low to save cost, and tokenizers make some scripts more expensive per character, so a shared cap gives answers in those scripts less room. Studies that compare languages or scripts through generated answers should report how often the cap binds in each condition and show that conclusions hold at a non-binding budget; judges should be configured identically across conditions, at least two judges from different families should be used, and their agreement should be reported per condition. Whether this cautionary result is novel enough for a given venue depends on prior work on tokenization premiums and multilingual judge reliability [5], [6], [26], [27], which documents the ingredients but, to our knowledge, not their combined effect on paired representation contrasts. Table VI lists claims we examined.

**Table VI caption**

> Claims examined and not supported, or supported only under some evaluation settings.

**IX Limitations**

> **Topics.** Twenty topics with heavy within-topic concentration bound what any statistic can show (effective n ≈ 67 of 500). A 25-proposition expansion has been written but not evaluated. **Output budget.** At 1,024 tokens, 39 CS-LAT and 64 MIXED responses still hit the cap, so the budget is not fully removed as a confound; the 1,024-token run was added after the 512-token results were seen and is exploratory, and the budget comparison is a sensitivity analysis rather than a clean estimate of the script effect; we re-ran three of the six conditions and did not test an instruction fixing the answer language. **Equivalence.** No equivalence margin was pre-specified, so non-significant gaps are reported with intervals, not as equivalence. **Judges.** Two LLM judges that disagree on a fifth to a quarter of items, and no human labels on any output; a stratified, blinded sample of 210 outputs and an annotation protocol are released but not annotated. **Questions and gold answers.** One generic template that under-specifies the target for several topics; volunteer gold checks without an item-level record; one superseded scheme. **Prompts.** The fluent-speaker review was an informal yes/no check of the templates; CS-LAT and MIXED differ by one word in Telugu and Kannada, and Hindi ROMAN is not a transliteration of Hindi NATIVE. **Models and languages.** One informative model, served under an API identifier whose underlying weights we cannot independently verify, and five languages. **Single run.** No repeated sampling; hosted greedy decoding was not fully deterministic, and API behaviour can change over time.

**X Ethics**

> Evaluations like this one guide where civic and legal information systems are considered safe to deploy for speakers who write the way our conditions do. Overstated gaps could discourage building for these users; understated ones could hide failures. We therefore report effect sizes with their dependence on clustering, output budget and judge. The prompts contain no personal data. The benchmark contains legal and policy facts that become outdated (one already has) and should not be used as legal advice. We do not estimate how many people use each representation, and make no claim about it.

**Reproducibility**

> All numbers, tables and figures are produced from the raw files by the scripts in `paper_v2/scripts/` (Appendix E). The two follow-up runs cost $1.10 (512 tokens plus re-grading of the 128-token outputs) and $1.23 (1,024 tokens) at the provider's list prices in October 2026; all 2,700 follow-up judgements parsed, and no call failed after retries. The project's budget ledger records $0.21 for the earlier runs but priced every call at a flat $0.08 per million tokens; at list prices the Qwen3.8-27B generation and grading in EXP-002 and EXP-003 would cost about $2.1. The provider's billing record is the authoritative figure.

**App. A.1**

> Table VII lists the 20 topics, the provision against which each gold answer was verified, the outcome, and the number of languages (of five) in which each condition was answered correctly under J-QWEN. Topics are Indian public-policy and regulatory subjects, several comparing two schemes or institutions (e.g. NEFT vs. RTGS, Covaxin vs. Covishield, PSLV vs. GSLV Mk III); not all are statutes, so we call them public-policy topics. Gold column: *ok*, consistent and adequate; *simpl.*, a correct simplification; *narrow*, other correct answers to the generic question exist; *dated*, the scheme has been superseded.

**Table VII caption**

> Topics, provision used to verify the gold answer, verification outcome, and languages (of five) answered correctly per condition (Qwen3.8-27B, J-QWEN, 128 tokens).

**App. B**

> Excluding the three topics with narrow gold answers (GST, MTP Act, Environment Clearance; 85 propositions), the J-QWEN differences from EN-MATCH are −12 (CS-LAT, p = 0.16), −25 (ROMAN, p = 0.002), −32 (NATIVE, p < 0.001) and −35 points (MIXED, p < 0.001), and MIXED vs. CS-LAT is −23.5 points (p < 0.001; topic-level p = 0.007). Table VIII gives all pairwise contrasts and Table IX the GEE estimates.

**Table VIII caption**

> All pairwise contrasts, J-QWEN labels, 128 tokens (proposition-level exact McNemar; b: the second-named (reference) condition correct and the first wrong; c: the reverse; topic-level permutation p and bootstrap CI for the change, uncorrected). The first five rows are the primary family.

**Table IX caption**

> Logistic GEE (independence working correlation, robust covariance), J-QWEN labels, 128 tokens. β̂ is the log-odds difference from EN-MATCH (first four blocks, 500 observations) or from CS-LAT (last block, 200). Topic-level robust SEs with 20 clusters are anti-conservative.

**App. C**

> **Incompleteness rule.** A response is flagged when (i) it used the full 128 completion tokens, (ii) its last non-space character is not a sentence-final mark, (iii) the judge labelled it incorrect, and (iv) the judge's reason matches one of *incomplete, truncated, cut off, abrupt, unfinished, missing specific, missing parameter, fails to finish*. Condition (iv) depends on the judge's wording; the rule is a descriptive device, not a measure of truncation. **Judge prompt.** “You are grading whether a model's ANSWER to a user QUESTION is factually correct. You are given a trusted GOLD answer. The answer may mix an Indian language with English (code-switching) and may be phrased very differently from the gold—that is fine. Judge ONLY factual correctness and whether it actually addresses the question.” Output: `VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>`. **Judge settings.** Stored, EXP-002: Qwen3.8-27B, temperature 0.3, at most 256 tokens, system prompt “You are a helpful assistant answering questions from Indian users. Questions may mix an Indian language with English (code-switching). Answer accurately and concisely in the same mixed style the user used.” Stored, EXP-003, and J-QWEN: temperature 0, top-p 1, at most 256 tokens, system prompt “You are an expert factuality evaluator.” J-OSS: gpt-oss-120b, temperature 0, top-p 1, low reasoning effort, at most 1,024 tokens, same system prompt. All 2,700 follow-up judgements (1,800 at 128/512 tokens, 900 at 1,024 tokens) were parsed. **Script transitions.** Words are maximal letter runs, each labelled Latin or Brahmic (U+0900–U+0DFF); transitions are label changes between consecutive words, giving 5.0 per MIXED prompt, 1.0 per NATIVE prompt (the Latin topic string) and 0 elsewhere. **Mostly Brahmic.** More than half of a response's letters and combining marks lie in U+0900–U+0DFF. **Templates.** All 20 Indic templates are listed in the released prompt-validation protocol.

**App. D**

> A normal-approximation calculation for a 45-topic design (225 paired propositions, design effect 1 + (5 − 1)ρ, binary variance at p̄ = 0.4, two-sided α = 0.05) with ρ = 0.2663 and a 21-point effect gives power 88.6% (minimum detectable effect 18.6 points); the same formula gives 55.9% for the 20 evaluated topics. Those parameters come from the first English template and the stored labels. With the harmonised labels (ρ = 0.27) the 11-point English–CS-LAT gap would have power 38% with 45 topics and 19% with 20, and a 23-point gap 93% and 63%. The formula ignores pairing and is a rough projection; the 25 new propositions have not been evaluated.

**App. E**

> Python 3.11 with numpy, pandas, scipy, statsmodels, tokenizers and matplotlib. From the repository root, `python paper_v2/scripts/make_all.py` (stored labels) and `make_all.py --labels jqwen` read the two prediction files; `scripts/run_exp004_budget_rejudge.py` and `scripts/run_exp005_budget1024.py` (`--stage gen|judge`; Groq key required) produced the follow-ups, with finish reasons, failures and a per-call spend log in `results/EXP-004-budget-rejudge/` and `results/EXP-005-budget1024/`; `analyze_exp004.py`, `analyze_budgets.py` and `make_figures.py` write the remaining numbers and figures. The tokenizer check downloads the Qwen/Qwen2.5-7B and Qwen/Qwen3.8-27B tokenizers. Sign-flip tests enumerate all 2²⁰ patterns; bootstraps and the language permutation use fixed seeds. Topic-level p values in an earlier draft were Monte Carlo approximations and differ from the exact values here in the third decimal. That draft's language-dependence p value (0.15) and numeral check (60% agreement) could not be reproduced because the script that produced them was not in the repository; they are replaced by the procedures described above.

**New references [23]–[27]**

* [23] J. A. Husain *et al.*, “RomanSetu: Efficiently unlocking multilingual capabilities of large language models via Romanization,” in *Proceedings of the 62nd annual meeting of the association for computational linguistics*, 2024.
* [24] P. Wang *et al.*, “Large language models are not fair evaluators,” in *Proceedings of the 62nd annual meeting of the association for computational linguistics*, 2024.
* [25] Y. Dubois, B. Galambosi, P. Liang, and T. B. Hashimoto, “Length-controlled AlpacaEval: A simple way to debias automatic evaluators,” *arXiv preprint arXiv:2404.04475*, 2024.
* [26] I. Watts, V. Gumma, A. Yadavalli, V. Seshadri, M. Swaminathan, and S. Sitaram, “PARIKSHA: A large-scale investigation of human-LLM evaluator agreement on multilingual and multi-cultural data,” in *Proceedings of the 2024 conference on empirical methods in natural language processing*, 2024, pp. 7900–7932.
* [27] X. Fu and W. Liu, “How reliable is multilingual LLM-as-a-judge?” in *Findings of the association for computational linguistics: EMNLP 2025*, 2025, pp. 11040–11053.

