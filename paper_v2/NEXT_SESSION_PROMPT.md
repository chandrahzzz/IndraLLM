# Handoff: build the IndraLLM paper as a two-column, top-tier-conference Word document

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
