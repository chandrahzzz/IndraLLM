# IndraLLM — Full Revision Report

**Scope:** everything done in this revision session, step by step: what was inspected, what was found,
what was run, what it cost, what the results are, what was written, and what remains.
**Date:** 2026-10-10.
**Repository:** `C:\Users\Chandrahas Reddy\MYallPROJECTS\IndraLLM` (GitHub: chandrahzzz/IndraLLM).
**Branch:** `paper-v2-revision` (created from `phase4-5-verification`).
**Freeze point:** commit `908ed5b`, tag `freeze-512-2026-10-10`. Later work is committed on top of it
(see Section 17).

How to read this report:

* Sections 1–3 summarise the outcome, the timeline, and the evidence matrix.
* Sections 4–12 go phase by phase. Each gives the procedure, the evidence (files and code paths), the
  results, and the decision taken.
* Sections 13–19 cover the change log, files, costs, reproduction commands, git state, remaining work
  and a final verdict.
* Part G (appended after Section 19) is generated directly from the result files and from the
  manuscript build script, so its numbers and text cannot drift from the data or the DOCX:
  * every results table for all three budgets and both judges;
  * judge agreement tables;
  * the "does the conclusion change" matrix;
  * the full 128-token analysis;
  * the final manuscript text exactly as built.

---

## 1. Executive summary

1. **The original central claim does not hold.** The PDF claimed that writing code-switched Indic words in
   Brahmic script (MIXED) instead of Latin script (CS-LAT) lowers factual accuracy. That gap exists only at
   a 128-token output cap. When the same 300 prompts were re-answered with 512 and 1,024 tokens, no gap was
   detected under either judge. The intervals exclude the 128-token gap, but this is not an equivalence
   claim, and 64 of 100 MIXED answers still hit the 1,024 cap (Section 20):
   * J-QWEN (self-judge): −23 → +4 → −3 points.
   * J-OSS (cross-family judge): −8 → −6 → −5 points, never significant.
2. **Nearly every original response was truncated.** 598 of 600 Qwen responses used all 128 tokens, and
   82–95% ended mid-sentence in every condition, English included. Brahmic-script answers fit about half
   as many characters into 128 tokens (279–303 vs 529 for English).
3. **The original runs used two different judge configurations.**
   * EXP-002 (EN-ORIG + four Indic conditions) was graded at temperature 0.3 with the answering system
     prompt.
   * EXP-003 (EN-MATCH) was graded at temperature 0 with an evaluator system prompt.

   Re-grading all 600 outputs with one configuration (J-QWEN) moved CS-LAT from 43% to 49% and shrank the
   English–CS-LAT gap at 128 tokens from 17 to 11 points (no longer significant).
4. **Judges disagree substantially.** J-QWEN and J-OSS (gpt-oss-120b) agree on 74.7% / 80.0% / 81.3% of
   outputs at 128 / 512 / 1,024 tokens (κ 0.47 / 0.59 / 0.61).
   * Disagreement is lopsided: J-QWEN accepts 30–36% of answers J-OSS rejects, and J-OSS accepts 6–11% of
     answers J-QWEN rejects.
   * The English advantage over CS-LAT is significant at the topic level only under J-QWEN at 1,024 tokens
     (−24 points, topic p = 0.018). That is Holm 0.036 within its budget–judge cell but **0.29 across all 18
     follow-up tests**, and the 1,024 run was added after the 512 results, so it is exploratory. Under
     J-OSS it is small at every budget (−12, −4, −7; never significant).
   * The conclusion therefore depends on the judge. No human labels were collected, so neither judge is
     treated as more accurate.
5. **The wrong tokenizer was used.** The PDF's tokenizer analysis used Qwen2.5-7B. The Qwen/Qwen3.8-27B
   tokenizer reproduces the API's prompt-token counts exactly (constant offset of 48 on all 1,600 Qwen
   prompts); Qwen2.5-7B does not. With the correct tokenizer:
   * Brahmic prompts are less fragmented: NATIVE 2.43 and MIXED 3.70 characters per token, against the
     PDF's 1.24 and 2.49.
   * Mediation remains null and exploratory.
6. **CS-LAT and MIXED are not word-identical in two languages.** In Telugu (`enti` vs `ఏమిటి`) and Kannada
   (`yenu` vs `ಯಾವುದು`) the question word differs. On the 60 word-identical propositions (hi, ta, bn) the
   budget result is the same.
7. **The reproducibility claim was false.** `paper_v2/scripts/make_all.py`, cited in the PDF, did not exist
   anywhere in the repository. It now exists and recomputes every number. All primary numbers in the
   original PDF were reproduced exactly from the raw files, except three:
   * the language-dependence p (0.15);
   * the numeral check (60%);
   * the "mostly Brahmic" shares (100%/97%).
8. **The spend claim was understated.** The budget ledger priced every call at a placeholder $0.08 per
   million tokens. At real list prices the earlier Qwen runs cost about $2.1, not $0.21. This revision
   spent $1.10 (EXP-004) + $1.23 (EXP-005) = $2.33.
9. **The paper is reframed** as a methodological result: *evaluating multilingual LLMs across
   representation conditions is sensitive to output-token budgets and evaluator choice; observed
   differences should not automatically be interpreted as representation effects.*
10. **Author-supplied validation is recorded.**
    * The author and volunteers checked the gold answers; the author confirmed the per-topic ledger on
      2026-10-10.
    * Fluent speakers reviewed the prompt templates (Telugu: Chandrahas Reddy, Akshith Chawla; Hindi and
      Kannada: Akshith Chawla; Tamil: Kapilan; Bengali: Shamik Mukherjee).
    * Both are documented as informal yes/no checks. The template review covered templates only, not model
      outputs.
11. **Deliverables:**
    * revised DOCX built from the original source (`paper_v2/revised/IndraLLM_IEEE_REVISED.docx`);
    * all analysis scripts and result JSON files;
    * the gold ledger, human-evaluation sample and protocol, and prompt-validation record;
    * this report.

    The PDF export of the final DOCX was not produced: Word automation failed, and you said no PDF was
    needed.

---

## 2. Timeline and procedure (in order)

| # | Step | What was done | Output |
|---|---|---|---|
| 1 | Locate manuscript | Found `Downloads/IndraLLM_IEEE_FINAL.pdf` (10 pages) and its source `IndraLLM_IEEE_FINAL.docx` (Edge downloads cache); copied both to scratch and later to `paper_v2/source/` | Preserved originals |
| 2 | Read PDF | Text extraction (pdftotext) and page renders (PyMuPDF, 110 dpi) of all 10 pages | Section 3 matrix |
| 3 | Repository map | Listed branches (`main`, `phase4-5-verification`, `research-redesign`, `research-v2`, `cleanup-surface-features`), commits, `results/`, `research/`, `scripts/`, `data/` | — |
| 4 | Search for `make_all.py` | `git ls-tree` on every local and remote branch, plus a disk search | Not found anywhere |
| 5 | Read EXP-002/003 code | `scripts/run_exp003_matched_inference.py`, `run_exp003_matched_analysis.py`, `build_exp003_matched_prompts.py`, `inspect_truncation_rules.py`, `src/indrallm/experiments/run_exp002.py`, `src/indrallm/annotation/llm_judge_label.py`, `src/indrallm/generation/llm_clients.py`, `config.yaml` | Judge mismatch found (Section 6) |
| 6 | Read benchmark | `data/questions/IndraLLM-CS-v1.1-CANDIDATE/semantic_questions_full_1500.jsonl` (TEST-OOD S001401–S001500), builder `src/indrallm/collection/build_decontaminated_benchmark_v1_1.py` | Gold/evidence provenance, template strings |
| 7 | Provider check | Groq model list (free call); Groq model pages for pricing; Hugging Face model API for Qwen/Qwen3.8-27B | Model identity, prices |
| 8 | Tokenizer check | Compared API `prompt_tokens` with local counts under five Qwen tokenizers | Tokenizer established |
| 9 | Reproduction | Wrote `paper_v2/scripts/stats_lib.py` and `make_all.py`; recomputed every number | `numbers_original.json` |
| 10 | EXP-004 | 512-token rerun (300 prompts) + J-QWEN/J-OSS grading of 600 originals and 300 new outputs | `results/EXP-004-budget-rejudge/` |
| 11 | Analysis | `analyze_exp004.py`; `make_all.py --labels jqwen` | `numbers_exp004.json`, `numbers_jqwen.json` |
| 12 | Gold ledger, protocols | `research/gold_verification_ledger.csv`, `HUMAN_EVAL_PROTOCOL.md`, `PROMPT_VALIDATION_PROTOCOL.md`; human-eval sample | — |
| 13 | Figures, draft DOCX | `make_figures.py`, `make_fig1.py`, `build_revised_docx.py` (13-page draft; rendered and inspected) | Draft DOCX/PDF |
| 14 | Build guide | `paper_v2/MANUSCRIPT_BUILD_GUIDE.md` (740 lines) | — |
| 15 | Author input | Prompt reviewers' names; gold confirmation; freeze request | Records updated |
| 16 | Freeze | Branch `paper-v2-revision`, commit `908ed5b`, tag `freeze-512-2026-10-10` | Backup |
| 17 | Reproducibility re-check | Re-ran all analyses; `git diff` against frozen outputs = no change | Byte-identical |
| 18 | EXP-005 | 1,024-token rerun (300 prompts) + J-QWEN/J-OSS grading | `results/EXP-005-budget1024/` |
| 19 | Three-budget analysis | `analyze_budgets.py` | `numbers_budgets.json` |
| 20 | Literature check | Web search for prior work on output-budget truncation and multilingual judge reliability; verified five references on ACL Anthology / arXiv | Refs [23]–[27] |
| 21 | Final build | `build_paper.py` (10-page structure, three budgets, judge disagreement central) | Final DOCX |
| 22 | PDF export | Word COM export failed (0x80080005); you said no PDF needed | — |
| 23 | This report | `dump_report_parts.py` + handwritten sections | `paper_v2/FULL_REVISION_REPORT.md` |

---

## 3. Phase 1 — Evidence matrix (manuscript claim → evidence → status → action)

Status codes: **S** supported, **C** contradicted, **U** unresolved, **P** partly supported.
Fix type: **E** manuscript edit, **R** additional research.

| # | Manuscript claim / problem (original PDF) | Evidence | Status | Correction / experiment | Fix |
|---|---|---|---|---|---|
| 1 | Accuracies 64/60/43/33/28/24 | Recomputed from `results/EXP-002/full_predictions.jsonl` + `results/EXP-003-matched-en/matched_predictions.jsonl` (stored labels) | S | Reproduced exactly; superseded as primary by harmonised labels | E |
| 2 | Wilson and topic-bootstrap CIs (Table II) | `make_all.py` | S | Reproduced (bootstrap identical to the integer) | — |
| 3 | McNemar b/c and exact p, Holm within five primary contrasts | `make_all.py` | S | Reproduced exactly | — |
| 4 | Topic-level permutation p (0.19, 0.038, 0.015, 0.021, 0.016) | Exact sign-flip over 2^20 patterns gives 0.185, 0.036, 0.014, 0.021, 0.015 | S (Monte Carlo vs exact) | Report exact values | E |
| 5 | "Mixed-script penalty survives every level of clustering we tried" | Holm-adjusted topic p = 0.072 (stored labels) | C | Removed; then superseded by the budget result | E |
| 6 | GEE table (independence, robust SE) | statsmodels GEE, three cluster levels | S | Reproduced exactly; moved to appendix | E |
| 7 | ICC 0.204, DEFF 5.89, n_eff 84.8 | `icc_block` | S | Reproduced (stored); J-QWEN gives 0.271 / 7.51 / 66.5 | E |
| 8 | Language-dependence permutation p = 0.15 | No script in the repo produced it | U | Defined test gives 0.23 (stored), 0.17 (J-QWEN) | E |
| 9 | ALLaM Spearman ρ = 0.6669, p = 0.2189 | `make_all.py` | S | Reproduced | — |
| 10 | Tipping-point table | Formula (acc_cmp − FPR(1−acc_ref))/acc_ref | S | Reproduced; recomputed on J-QWEN | E |
| 11 | Numeral check: 60% agreement, 63/69 | No script | C | Reproducible check: 65.2% stored (73/42), 67.3% J-QWEN (73/35) | E |
| 12 | "100% NATIVE and 97% MIXED responses mostly Brahmic" | Letter-share > 0.5 gives 98% / 88%; "any Brahmic" gives 100% / 98% | C | Definition stated; 98% / 88% | E |
| 13 | Response lengths 529 / 279 / 303 chars | `response_block` | S | Reproduced | — |
| 14 | Incompleteness rule 0/40, 15/57, 42/72, 41/76 | Rule reproduced on stored labels | S | J-QWEN: 0/40, 11/51, 36/68, 38/74 | E |
| 15 | Power figures 88.6 / 55.9 / 78.0 / 44.5% | Normal-approximation formula reproduced | S | Labelled as a rough projection; J-QWEN values added | E |
| 16 | Model identity `qwen/qwen3.8-27b`, checkpoint unknown | Identifier in every row; Groq lists it; HF checkpoint exists; tokenizer matches API counts | P | Tokenizer established; served weights unverifiable | E |
| 17 | "Project documents call it Qwen-2.5-27B"; config lists qwen3.6-27b | `scripts/run_exp003_matched_inference.py` docstring; `config.yaml` | S (as a description) | Name standardised: Qwen3.8-27B | E |
| 18 | EN-MATCH re-run "with identical decoding and judging" | `run_exp002.py` → `_judge` → `GroqClient.generate` → `config.yaml` T 0.3 + generation system prompt; EXP-003 T 0 + evaluator prompt | C | All 600 outputs re-graded (J-QWEN) | R (done) |
| 19 | Judge "temperature 0, 256 tokens" (Appendix C) | Same as 18 | C | Both stored configurations documented | E |
| 20 | Gold answers "not independently re-verified" | Your clarification; ledger | C | Author + volunteer check; author-confirmed ledger | E |
| 21 | κ = 0.719 measured on an earlier pilot | No raw annotation files in the repo; `PHASE2_7_HUMAN_VALIDATION_AUDIT.md` already flagged misattribution | U | Not used | E |
| 22 | Evidence snippets / sources | Snippets template-generated ("Comparative statutory analysis confirms…"); URLs are agency home pages; domain tags wrong for several topics | P | Disclosed; ledger gives provisions | E |
| 23 | CS-LAT and MIXED "contain the same words" | Template strings in the builder | C (te, kn) | Disclosed; word-identical sensitivity analysis | E |
| 24 | ROMAN and NATIVE "render the same Indic frame" | Hindi `tareekh` vs `तिथि` | C (hi) | Disclosed | E |
| 25 | 128-token cap "an unresolved confound that we quantify" | 598/600 responses capped | S (confound real) | EXP-004 (512) and EXP-005 (1,024) run | R (done) |
| 26 | Tokenizer mediation "no role" (Sobel p = 0.31), Qwen2.5-7B | Tokenizer mismatch shown | C (tokenizer) | Recomputed with Qwen3.8 tokenizer: b p = 0.08 (J-QWEN), wrong sign; exploratory | E |
| 27 | Reproducibility via `paper_v2/scripts/make_all.py` | File absent | C | Script written | E |
| 28 | API spend ≈ $0.21 | Ledger uses a flat $0.08/M; real prices $0.80/$4.00 per M (Qwen) | C | Reported as ledger value plus list-price estimate | E |
| 29 | ALLaM "near floor, uninformative" | Accuracies 2–10% | S | Kept | — |
| 30 | English vs CS-LAT not significant at topic level | True at 128 and 512 under both judges; **false** under J-QWEN at 1,024 (p = 0.018) | P | Judge dependence reported | E |
| 31 | Table VII caption "b: first condition correct" | b counted reference-correct | C | Caption fixed | E |
| 32 | Typos: "28.0and", "tippingpoint", lost hyphens ("codeswitching") | PDF text | C | Fixed in rewritten text | E |
| 33 | References placed after appendices | Layout | Style | Kept (IEEE allows); ACL needs references before appendices | E (ACL) |
| 34 | Fig. 2b topic labels truncated | Render | C | Regenerated with full labels | E |
| 35 | Human validation of the judge on these outputs | None exists | U | Protocol + 210-item blinded sample prepared | R (open) |

---

## 4. Phase 2 — Gold answers and benchmark provenance

### 4.1 Procedure

1. Extracted the 100 TEST-OOD records (S001401–S001500) from
   `semantic_questions_full_1500.jsonl`. Grouped them by topic: 20 topics × 5 languages. All five language
   groups of a topic share one gold answer and one evidence snippet.
2. Traced the gold answers to `build_fact_catalog()` in
   `src/indrallm/collection/build_decontaminated_benchmark_v1_1.py`.
   * TF-11 facts: `tf11_data`; TF-12 facts: `tf12_data`.
   * Evidence snippets are generated by f-strings: `f"Comparative statutory analysis confirms that {name}
     differs: {fact}."` and `f"Statutory conditions prescribe that for {name}, rule dictates: {fact}."`
3. Recorded the stored source fields `evidence_source_url` and `evidence_source_type`:
   * The URLs are home pages (rbi.org.in, pmfby.gov.in, cdsco.gov.in, …), not documents.
   * Source types are sometimes implausible (rbi.org.in tagged `statutory_act`).
   * The `domain` field is wrong for several topics (NEFT vs RTGS, Covaxin vs Covishield, Classical Tamil
     vs Sanskrit Grammar, National Park vs Wildlife Sanctuary are tagged `agriculture`).
4. Reviewed each gold answer against its governing provision for three things:
   * factual consistency;
   * completeness relative to the generic question actually asked ("main rule, date or parameter
     regarding X");
   * currency.

   This was done from legal and policy knowledge. You then reviewed and confirmed the ledger
   (2026-10-10).
5. Inspected model responses on the two all-zero topics and on topics where the gold answer is ambiguous,
   to tell gold problems apart from model errors.

### 4.2 Results per topic (`research/gold_verification_ledger.csv`)

| Topic | Gold answer | Provision | Status | Note |
|---|---|---|---|---|
| PMFBY vs WBCIS | PMFBY crop yield-based; WBCIS weather index-based | PMFBY/RWBCIS guidelines | ok | WBCIS now RWBCIS. Indic responses expand WBCIS wrongly as "West Bengal Crop Insurance Scheme" (a genuine model error) |
| NEFT vs RTGS | NEFT no minimum, batches; RTGS ₹2 lakh minimum, real time | RBI NEFT/RTGS | ok | Both 24×7 since 2019/2020 |
| Covaxin vs Covishield | Inactivated virus vs chimpanzee adenovirus vector | CDSCO approvals Jan 2021 | ok | Snippet calls it "statutory analysis" (template artifact) |
| Kharif vs Rabi Rice | Monsoon rainfed vs winter irrigated | ICAR references | simplification | Kharif rice is often irrigated too |
| ISRO PSLV vs GSLV Mk III | 1,750 kg to SSO vs 4,000 kg to GTO with cryogenic stage | ISRO | ok | LVM3 name; published GTO figures vary slightly |
| Lok Sabha vs Rajya Sabha Money Bill | Rajya Sabha cannot reject or amend; 14 days | Constitution Arts. 109–110 | ok | Rajya Sabha may recommend amendments |
| National Park vs Wildlife Sanctuary | No private rights or grazing in National Parks; limited rights in Sanctuaries | Wild Life (Protection) Act ss. 24, 33, 35 | ok | — |
| Classical Tamil vs Sanskrit Grammar | Tolkappiyam vs Ashtadhyayi | Philological references | ok; ill-posed for the template | Not a policy fact |
| PM-KISAN vs Rythu Bandhu | Flat per family vs per acre | PM-KISAN guidelines; Telangana G.O.s | **dated** | Rythu Bandhu replaced by Rythu Bharosa (2024–25) |
| Supreme Court vs High Court Writ | Art. 226 wider than Art. 32 | Constitution Arts. 32, 226 | ok | — |
| Patents Act Compulsory License | After 3 years from grant | Patents Act s. 84(1) | ok (narrow) | Grounds of s. 84 also answer the question |
| RTI Third Party Information | Within 5 days | RTI Act s. 11(1) | ok (narrow) | Snippet's "trade secrets" framing imprecise |
| GST Registration Exemption | ≤ ₹40 lakh (goods) | CGST s. 22; Notif. 10/2019-CT | **narrow / ambiguous** | ₹20 lakh (services) also correct |
| Companies Act CSR Mandate | Net worth ≥ ₹500 cr, turnover ≥ ₹1,000 cr, or net profit ≥ ₹5 cr | Companies Act s. 135(1) | ok | — |
| Arbitration Act Time Limit | 12 months, extendable by 6 | Arbitration Act s. 29A (2019) | ok | From completion of pleadings |
| IBC Section 7 Default Threshold | ₹1 crore | IBC s. 4 (since Mar 2020) | ok | Model gives the pre-2020 ₹1 lakh (genuine model error); 0/30 correct in every condition |
| Environment Clearance Public Hearing | Exempt inside notified industrial estates or defence projects | EIA Notification 2006 para 7 | **incomplete / ill-posed** | Gold lists 2 of several exemptions; the "main rule" is that a hearing is required; 0/30 in every condition |
| MTP Act | Opinion of two registered medical practitioners | MTP Act s. 3(2) (2021) | **narrow / ambiguous** | Applies to 20–24 weeks only; EN-ORIG 5/5 vs EN-MATCH 0/5. One EN-MATCH answer states the correct one-practitioner rule, is cut off before the 20–24 rule, and is judged HALLUCINATED |
| SEBI Insider Trading Pre-Clearance | Pre-clearance from compliance officer | SEBI PIT Regs Sch. B | ok | — |
| Citizenship Amendment Act Cut-off | On or before 31 December 2014 | CAA 2019 s. 2 | ok | — |

### 4.3 Sensitivity to gold problems

* Excluding the three narrow or ambiguous topics (GST, MTP, Environment Clearance) changes no conclusion
  (Part G, Sections G5 and 6.4 of the build guide):
  * J-QWEN: CS-LAT −11.8 (p 0.16); MIXED vs CS-LAT −23.5 (p < 0.001, topic p 0.007).
* The fictitious in-distribution partition: 2 of 2,000 responses were judged correct. The model often
  correctly denies that a fictitious clause exists, and the judge then labels that answer hallucinated.
  These rows are excluded, as in the original paper.

### 4.4 How verification is described in the paper

* **Gold correctness:** checked by the author and, separately, by volunteer reviewers. The author verified
  each answer against its governing provision as in force in October 2026. The volunteer check was not
  logged item by item and has no agreement statistic.
* **Judge correctness** (a separate question): not validated against humans.
* **Not used:** κ = 0.719 and the 300-item "human validation" document (no raw annotation files exist; they
  concern different data).

### 4.5 What would strengthen it further (optional)

* A dated record per topic of which public source each checker consulted.
* The number and background of the volunteer gold checkers.

---

## 5. Phase 3 — Model identity

### 5.1 Procedure

1. **Read the identifier.** `model` field in all prediction rows: `qwen/qwen3.8-27b` in EXP-002 (git
   commit `4e6ba8f`) and EXP-003 (git commit `0097d85`).
2. **Queried the Groq model list (free call).** Relevant entries:
   * `qwen/qwen3.8-27b`: owner Alibaba Cloud, context 131,072, created 1786984846 (Unix, ≈ 2026-08-17);
   * `qwen/qwen3.6-27b`;
   * `allam-2-7b` (SDAIA);
   * `openai/gpt-oss-120b`.
3. **Queried the Hugging Face API for `Qwen/Qwen3.8-27B`:**
   * created 2026-08-05; revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`;
   * 27,781,427,952 safetensors parameters; licence apache-2.0;
   * pipeline `image-text-to-text`; architecture `Qwen3_5ForConditionalGeneration` (hybrid linear and full
     attention).
4. **Tokenizer fingerprint.** For each candidate tokenizer, computed API `prompt_tokens` minus the local
   token count of the user prompt, across all 1,600 Qwen prompts (EXP-002 TEST-ID + TEST-OOD + EXP-003).

### 5.2 Results

| Tokenizer | Offset distribution (API − local) | Local tokens of responses the API reports as 128 |
|---|---|---|
| Qwen/Qwen3.8-27B | **48 for all 1,600** | 125–128 (mean 127.8) |
| Qwen/Qwen3.6-27B | 48 for all 1,600 | 125–128 |
| Qwen/Qwen3.5-27B | 48 for all 1,600 | 125–128 |
| Qwen/Qwen3-32B | 48 (598), 47 (146), 46 (120), … | 120–328 |
| Qwen/Qwen2.5-7B | 48 (598), 47 (146), … down to 1 | 120–328 |

A constant 48 is the chat-template and system-prompt overhead.

**Conclusions:**
* The served model tokenizes exactly like the Qwen3.5/3.6/3.8 tokenizer family, so the tokenizer is
  established.
* Whether Groq serves exactly the public checkpoint's weights, and at what numerical precision (Groq states
  "TruePoint Numerics"), cannot be verified.
* The paper uses the API identifier as the authoritative name and states this limitation.
* The same identifier was used for generation and for the J-QWEN judge.
* `config.yaml` lists `qwen/qwen3.6-27b`, and the EXP-003 docstring says "Qwen-2.5-27B". Neither produced
  the outputs.

### 5.3 Determinism

Hosted greedy decoding is near-deterministic but not exactly deterministic. Several system fingerprints
were observed (e.g. `fp_a1293f40b5`, `fp_21e59ac2de`, `fp_424cb89518`, `fp_4560dae850`).

* 512-token responses that begin with exactly the 128-token response: EN-MATCH 84, CS-LAT 85, MIXED 84 (of
  100).
* 1,024-token responses that begin with exactly the 512-token response: 91, 78, 80.

---

## 6. Phase 4 — Judge audit

### 6.1 Procedure

Traced the judge call paths in code:

* **EXP-002** (`src/indrallm/experiments/run_exp002.py`):
  * `judge_client = GroqClient("qwen/qwen3.8-27b")`, then `_judge(judge_client, prompt, ref_ans, resp_text)`.
  * `_judge` (`src/indrallm/annotation/llm_judge_label.py`) calls `client.generate(PROMPT.format(...))`.
  * `GroqClient.generate` (`src/indrallm/generation/llm_clients.py`) uses `CFG["generation"]["max_tokens"]`
    = 256 and `CFG["generation"]["temperature"]` = **0.3** (`config.yaml`).
  * It also uses the module `SYSTEM_PROMPT` = "You are a helpful assistant answering questions from Indian
    users. Questions may mix an Indian language with English (code-switching). Answer accurately and
    concisely in the same mixed style the user used."
  * A parse failure gives −1 (none present in the data).
* **EXP-003** (`scripts/run_exp003_matched_inference.py`):
  * `execute_call(..., max_tokens=256, temperature=0.0, top_p=1.0, system_prompt="You are an expert
    factuality evaluator.")`;
  * fallback parsing if the VERDICT regex fails.
* **Rubric** (identical in both): the "You are grading whether a model's ANSWER…" prompt, which includes
  the question as the model saw it (Indic script for Indic conditions).

So EN-MATCH (EXP-003) was graded under a different judge configuration from EN-ORIG and the four Indic
conditions (EXP-002). This is a confound for every EN-MATCH vs Indic contrast.

### 6.2 Experiment: harmonised and cross-family re-grading (part of EXP-004)

* **J-QWEN:** `qwen/qwen3.8-27b`, temperature 0, top-p 1, max 256 tokens, system "You are an expert
  factuality evaluator.", same rubric. Applied to all 600 original 128-token outputs, plus later the 512-
  and 1,024-token outputs.
* **J-OSS:** `openai/gpt-oss-120b`, temperature 0, top-p 1, reasoning effort low, max 1,024 tokens, same
  system prompt and rubric. A different model family that did not generate the answers.
* **Parsing:** `VERDICT:\s*\**\s*(CORRECT|HALLUCINATED)`. All 2,700 follow-up judgements parsed.

### 6.3 Results

* **J-QWEN reproduces stored labels:** on 100/100 EN-MATCH items (identical configuration, an independent
  API-level reproduction), and on 90–94% of items in the conditions graded under the old configuration.
* **Accuracy at 128 tokens under J-QWEN:** EN-ORIG 70, EN-MATCH 60, CS-LAT 49, ROMAN 37, NATIVE 32, MIXED
  26.
* **J-OSS is much stricter:** 40, 37, 25, 24, 21, 17.
* **Agreement, Cohen's κ, and directional disagreement** by budget and condition: Part G2. At 1,024 tokens
  overall agreement is 81.3% and κ 0.61 (topic-bootstrap 95% CI 0.40–0.78).
* **Disagreement pattern.** In inspected disagreements, J-QWEN accepted on-topic, accurate answers that did
  not state the gold fact (for example, naming only the governing Act), and J-OSS rejected them. The
  rubric does not say which reading is intended.
* **Self-judge errors observed:**
  * The MTP EN-MATCH answer states the correct one-practitioner rule, is cut off, and is labelled
    HALLUCINATED.
  * A J-QWEN re-grade of an EN-ORIG PMFBY answer claimed "Incorrectly claims PMFBY uses actual crop loss
    assessment", which is a judge error.
* **Numeral check:** on the 330 outputs from the 11 topics whose gold answer contains numerals, J-QWEN
  matches "all gold numerals present" 67.3% of the time (73 accepted without the figure; 35 rejected with
  it).
* **Validation status:** no human gold-standard labels exist for any output. The repository's
  `research/EVALUATOR_HUMAN_VALIDATION.md` (300 items, κ 0.842) has no raw annotation files and concerns
  other models and data.

### 6.4 "Factual recall" vs "judge-assessed accuracy"

The measured quantity is the share of responses a particular judge labels CORRECT. It depends on judge
leniency (60% vs 37% on the same English answers) and on truncation, so the paper uses "judge-assessed
accuracy" throughout.

### 6.5 Human-evaluation design (prepared, not executed)

* **Protocol:** `research/HUMAN_EVAL_PROTOCOL.md`. It specifies:
  * a 6-label rubric: CORRECT / PARTIAL / INCOMPLETE_NO_ERROR / INCORRECT / CORRECT_OTHER_READING /
    UNREADABLE;
  * blinding to judge verdict and condition (condition blinding is necessarily imperfect for script);
  * at least two readers per language, adjudication rules, κ, and per-condition judge sensitivity and
    specificity;
  * inverse-probability-weighted corrected accuracies.
* **Sample** (`scripts/build_human_eval_sample.py`, seed 20261010), in `results/EXP-004-budget-rejudge/human_eval/`:
  * 120 main items: 6 conditions × 2 stored verdicts × 5 languages × 2;
  * 30 J-QWEN/J-OSS disagreement items;
  * 60 items at 512 tokens;
  * blinded item files (`items_blinded*.csv`) and separate keys (`key*.csv`).
* **Note:** no analysis script exists yet, because there are no labels.

---

## 7. Phase 5 — Output budget (EXP-004 at 512, EXP-005 at 1,024)

### 7.1 Evidence that the cap binds (128 tokens)

| Condition | Hit 128 | Ends mid-sentence | Mean chars | Mostly Brahmic % |
|---|---|---|---|---|
| EN-ORIG | 100 | 82 | 538 | 0 |
| EN-MATCH | 100 | 87 | 529 | 0 |
| CS-LAT | 99 | 90 | 423 | 2 |
| ROMAN | 99 | 91 | 390 | 8 |
| NATIVE | 100 | 95 | 279 | 98 |
| MIXED | 100 | 92 | 303 | 88 |

The two uncapped responses are S001412 CS-LAT ta (94 tokens) and S001462 ROMAN ta (87 tokens). The
provider finish reason was not logged in EXP-002/003. The keyword "incompleteness" heuristic depends on
the judge's wording and is not treated as ground truth.

### 7.2 Design of the follow-ups

* **Held constant:**
  * model identifier `qwen/qwen3.8-27b`;
  * system prompt "You are a helpful assistant answering questions from Indian users. Questions may mix an
    Indian language with English. Answer factually, accurately, and concisely.";
  * temperature 0, top-p 1;
  * identical prompt strings, taken from the original prediction rows.
* **Changed:** `max_tokens` = 512 (EXP-004) and 1,024 (EXP-005).
* **Conditions:** EN-MATCH, CS-LAT and MIXED (the two key contrasts), 100 prompts each. The other three
  conditions were not re-run, to limit cost.
* **Logged per call:** finish reason, served model, system fingerprint, request id, token usage, latency,
  and cost at list price.
* **Grading:** every budget is graded by both J-QWEN and J-OSS, so each cross-budget comparison uses one
  judge.
* **Pre-specified contrasts** (fixed in the analysis scripts before grading finished): CS-LAT vs EN-MATCH,
  MIXED vs CS-LAT and MIXED vs EN-MATCH at each budget, plus the change in each gap.
* **Statistics:** exact McNemar (proposition); exact sign-flip over 20 topics; percentile topic bootstrap
  (10,000 resamples, seed 0).

### 7.3 Execution log

* **Pre-run checks:**
  * no earlier larger-budget experiment existed in the repository;
  * the budget ledger target is $5 and the hard ceiling $10;
  * real prices were looked up first (Section 15).
* **EXP-004 (512):**
  * Pilot: 6 generations ($0.013), all finished by `length`. 5 of 6 were exact continuations of the
    128-token text.
  * Judge pilot: the first background attempt hung because the OpenAI client had no timeout. Fixed with
    `timeout=90`, `max_retries=0` and explicit retries.
  * Full run, first attempt: hit Groq's output-tokens-per-minute limit (32,000 OTPM). After 223
    generations an unhandled 429 aborted the stage.
  * Patched: 3 workers, up to 10 retries with backoff capped at 60 s, skip-and-continue. Resumed to
    300/300.
  * Judging: 1,800 judgements (600 originals + 300 new, × 2 judges), all parsed. Total EXP-004 cost $1.095.
* **EXP-005 (1,024):**
  * Separate script `scripts/run_exp005_budget1024.py`, derived from the EXP-004 runner; only the budget,
    paths and labels change, and a failure log is added.
  * Worst-case estimate $1.73; ceiling $1.80.
  * Pilot: 3 generations ($0.012).
  * Full run: 300 generations + 600 judgements; 85 transient rate-limit retries; 0 persistent failures
    (no `failures.jsonl` written); 0 parse failures. Cost $1.229.

### 7.4 Results (details in Part G1)

* **The cap stops binding progressively.** Responses that stopped before the cap:
  * 512 tokens: 58 / 15 / 5 (EN-MATCH / CS-LAT / MIXED);
  * 1,024 tokens: 95 / 61 / 36.
* **Accuracy rises with budget in every condition, under both judges** (J-QWEN EN-MATCH 60 → 80 → 85;
  J-OSS MIXED 17 → 48 → 51).
* **MIXED − CS-LAT:**
  * J-QWEN −23 (p < 0.001, topic p 0.004) → +4 (p 0.57) → −3 (p 0.70);
  * J-OSS −8 → −6 → −5, never significant;
  * gap change 128 → 1,024 under J-QWEN: +20 points (topic CI [5, 34], p 0.023);
  * word-identical subset (hi, ta, bn) at 1,024 tokens: J-QWEN 65.0 vs 60.0 (p 0.58).
* **CS-LAT − EN-MATCH:**
  * J-QWEN −11 (p 0.13, topic 0.42) → −21 (p < 0.001, topic 0.082) → −24 (p < 0.001, topic **0.018**; Holm
    0.036 within the three follow-up contrasts);
  * J-OSS −12 (p 0.050, topic 0.22) → −4 (0.57) → −7 (0.21).
* **MIXED vs EN-MATCH:**
  * J-QWEN −34 → −17 → −27 (topic p 0.003 at 1,024);
  * J-OSS −20 → −10 → −12 (p 0.043, topic p 0.22).

### 7.5 Interpretation

* **Script effect.** The 128-token mixed-script penalty is best explained by the output budget: Brahmic
  answers reach the cap before the fact. It disappears at 512 and 1,024 tokens under both judges and in the
  word-identical subset. This conclusion is stable across both larger budgets and both judges.
* **English advantage.** It grows with the budget under J-QWEN and stays small under J-OSS. Its status
  depends on the judge, and that instability is a finding in its own right.
* **Residual binding.** At 1,024 tokens, 39 CS-LAT and 64 MIXED responses still hit the cap, and 39 and 63
  end mid-sentence. Part of the remaining English advantage could still reflect length. This is disclosed
  as a limitation (see Section 20 for the complete-answers check).

---

## 8. Phase 6 — Tokenizer and mediation

### 8.1 Procedure

* The original analysis (`scripts/run_exp003_matched_analysis.py`) loaded `Tokenizer.from_pretrained("Qwen/Qwen2.5-7B")`
  and computed prompt characters per token.
* The tokenizer check (Section 5) showed this tokenizer does not match the served model.
* Recomputed with Qwen/Qwen3.8-27B in `make_all.py` (`tokenizer_block`, `mediation`).

### 8.2 Results

| Condition | Prompt chars/token, Qwen3.8 (correct) | Qwen2.5 (original) | Response chars/token, Qwen3.8 |
|---|---|---|---|
| EN-ORIG | 5.83 | 5.82 | 4.21 |
| EN-MATCH | 4.65 | 4.64 | 4.14 |
| CS-LAT | 4.11 | 4.02 | 3.32 |
| ROMAN | 3.15 | 2.90 | 3.06 |
| NATIVE | 2.43 | 1.24 | 2.18 |
| MIXED | 3.70 | 2.49 | 2.37 |

**Mediation** (CS-LAT vs MIXED, 200 rows; Baron–Kenny with a logit outcome; Sobel), Qwen3.8 tokenizer:

| Labels | a (SE) | b (SE), p | Total | Direct | Sobel p |
|---|---|---|---|---|---|
| J-QWEN | −0.41 (0.10) | −0.40 (0.23), 0.080; 95% CI −0.85 to 0.05 | −1.01 | −1.19 | 0.11 |
| Stored | −0.41 (0.10) | −0.30 (0.23), 0.19 | −0.87 | −1.01 | 0.21 |
| Stored, Qwen2.5 (original PDF) | −1.53 (0.09) | −0.25 (0.24), 0.31 | −0.87 | −1.25 | 0.31 |

* The sign of b is the opposite of a fragmentation account.
* The mediator is almost determined by condition and language, so the test has little leverage.
* It is labelled exploratory, and the paper no longer says tokenization is irrelevant.
* Six-condition Spearman ρ (chars/token vs accuracy): 0.83 (J-QWEN, Qwen3.8); the original was 0.94.

---

## 9. Phase 7 — Statistical recomputation

### 9.1 Methods implemented (`paper_v2/scripts/stats_lib.py`)

* Wilson interval (z = 1.959964).
* Exact McNemar: binomial test on discordant pairs; b = reference correct & comparison wrong.
* Holm step-down within the declared family of five primary contrasts: NATIVE, ROMAN, CS-LAT, MIXED vs
  EN-MATCH; MIXED vs CS-LAT.
* Exact two-sided sign-flip permutation over all 2^20 sign patterns of the 20 per-topic differences.
* Percentile bootstrap over topics (10,000 resamples, seed 0).
* Logistic GEE (independence working correlation, robust covariance) clustered at prompt, proposition and
  topic (statsmodels).
* ANOVA ICC, design effect 1 + (m − 1)ρ, effective n.
* Language-dependence permutation: interaction sum of squares of the language × condition table; language
  labels permuted within topic; 10,000 permutations.
* Tipping points, normal-approximation power, the numeral check, the incompleteness rule, script
  transitions, Brahmic share, Cohen's κ with a topic bootstrap.

### 9.2 Inferential units, in plain terms

* **Proposition-level test:** does the model, given these 100 facts, do better in one representation than
  another?
* **Topic-level test:** would the difference recur on new topics?
* The five language versions of a topic share the gold answer and nearly the same topic string, and English
  outcomes are near-duplicated within a topic. So 500 prompts carry roughly 67–85 effective observations,
  and the 20 topics are the honest unit for generalisation.
* Both are reported. Topic-level conclusions rest on the permutation test and bootstrap, not on GEE robust
  SEs with 20 clusters, which are anti-conservative.

### 9.3 Reproduction of the original PDF numbers (stored labels)

| Quantity | PDF | Recomputed | Match |
|---|---|---|---|
| Accuracies (6) | 64/60/43/33/28/24 | same | ✓ |
| Wilson CIs | e.g. EN-MATCH [50.2, 69.1] | same | ✓ |
| Topic-bootstrap CIs | e.g. EN-MATCH [40, 80] | same | ✓ |
| CS-LAT vs EN-MATCH | −17, b 30 c 13, p 0.014 | same | ✓ |
| MIXED vs CS-LAT | −19, b 29 c 10, p 0.003, Holm 0.007 | same | ✓ |
| Topic p CS-LAT vs EN | 0.19 | 0.185 (exact) | ✓ |
| Topic p MIXED vs CS | 0.016 | 0.015 (exact) | ✓ (MC vs exact) |
| Holm topic MIXED vs CS | "0.07" | 0.072 | ✓ |
| GEE CS-LAT (prompt/prop/topic) | −0.687; SE 0.287/0.261/0.470; p 0.017/0.008/0.14 | same | ✓ |
| GEE MIXED vs CS-LAT OR | 0.42 (0.23–0.77) | same | ✓ |
| ICC / DEFF / n_eff | 0.204 / 5.89 / 84.8 | same | ✓ |
| Language permutation p | 0.15 | 0.23 (defined test) | ✗ (no source script) |
| ALLaM ρ, p | 0.6669, 0.2189 | same | ✓ |
| Tipping table | 0.72 … 0.35 | same | ✓ |
| Numeral check | 60%, 63/69 | 65.2%, 73/42 | ✗ (no source script) |
| Mostly Brahmic | 100% / 97% | 98% / 88% (letter share) | ✗ (definition) |
| Response chars | 529/279/303 | same | ✓ |
| Incompleteness rule | 0/40, 15/57, 42/72, 41/76 | same | ✓ |
| Power | 88.6/55.9/78.0/44.5% | same | ✓ |
| Mediation (Qwen2.5) | a −1.529, b −0.248, Sobel p 0.31 | same | ✓ (wrong tokenizer) |

### 9.4 Reproducibility check after the freeze

* Re-ran `make_all.py` (both label sets) and `analyze_exp004.py`. `git diff` against the frozen outputs was
  empty, so the numbers are byte-identical.
* At the API level, J-QWEN re-graded the 100 EN-MATCH items and reproduced the stored labels 100/100.

---

## 10. Phase 8 — Language and benchmark validity

### 10.1 Template strings (all 400 Indic prompts come from 20 templates)

Full inventory: `research/PROMPT_VALIDATION_PROTOCOL.md` §1. Findings from inspecting the strings:

1. **CS-LAT ≠ MIXED wording in te and kn:**
   * Telugu: `enti` (colloquial "what") vs `ఏమిటి` (*emiti*, formal "what");
   * Kannada: `yenu` ("what") vs `ಯಾವುದು` (*yāvudu*, "which");
   * Hindi, Bengali and Tamil are word-for-word transliterations.
2. **Hindi ROMAN ≠ transliteration of Hindi NATIVE:** `tareekh` (तारीख) vs `तिथि` (*tithi*).
3. **The CS-LAT frame structure differs by language.** Hindi and Bengali use the English word *regarding*
   as a postposition (`ke regarding`, `er regarding`). Tamil, Telugu and Kannada use a native postposition
   (`pathi`, `gurinchi`, `bagge`).
4. **One template for all topics.** "Main rule, date or parameter regarding X" does not ask for the
   comparison the TF-11 gold answers encode. For GST, MTP and Environment Clearance it admits other correct
   answers.

### 10.2 Consequences and handling

* **No prompts were edited.** The results remain results for these exact strings, and any change would
  need a new run.
* **The CS-LAT vs MIXED contrast is reported two ways:** on all 100 propositions (pre-specified) and on the
  60 word-identical ones (sensitivity):
  * 128 tokens, J-QWEN: −25 (p 0.0015);
  * 512 tokens: +1.6 (p 1.0);
  * 1,024 tokens: −5 (p 0.58).
* **Fluent-speaker review** (recorded in `research/PROMPT_VALIDATION_PROTOCOL.md` §0), all judged
  "proper":
  * Telugu: Chandrahas Reddy, Akshith Chawla;
  * Hindi and Kannada: Akshith Chawla;
  * Tamil: Kapilan;
  * Bengali: Shamik Mukherjee.
* **Limits of that review:**
  * it was a yes/no check with no per-item ratings and no agreement statistic;
  * it covered the templates, **not the model outputs**;
  * it does not establish full semantic equivalence or validate the judges.

---

## 11. Phase 9 — Narrative and claims

### 11.1 New central claim

*Evaluating multilingual LLMs across representation conditions is sensitive to output-token budgets and
evaluator choice; observed differences should not automatically be interpreted as representation effects.*

### 11.2 Claims removed or narrowed

* That script alternation or mixed script harms recall.
* That native script damages reasoning.
* That code-switching universally reduces accuracy.
* That any effect survives "every level".
* "Factual recall" as the measured quantity.
* Mediation "rules out" tokenization.
* ALLaM as a replication.
* Any causal mechanism (attention, boundaries).
* Generalisation beyond one model, 20 topics and five languages.

### 11.3 Closest prior work (checked online, references verified)

* **Tokenization premiums across languages** (Ahia et al. 2023; Petrov et al. 2023; already cited). Fixed
  token limits penalise non-Latin scripts in cost and context.
* **Multilingual judge reliability:**
  * Watts et al. 2024, *PARIKSHA*, EMNLP 2024, pp. 7900–7932: human–LLM evaluator agreement across 10 Indic
    languages; agreement drops for direct assessment.
  * Fu and Liu 2025, *How Reliable is Multilingual LLM-as-a-Judge?*, Findings of EMNLP 2025,
    pp. 11040–11053: average Fleiss κ ≈ 0.3 across 25 languages.
* **Judge biases:**
  * Wang et al. 2024, *Large Language Models are not Fair Evaluators*, ACL 2024 (position bias);
  * Dubois et al. 2024, *Length-Controlled AlpacaEval* (length bias).
* **Romanization as a bridge for Indic LLMs:** Husain et al. 2024, *RomanSetu*, ACL 2024.

**Novelty assessment.** The ingredients are known; their combination is not obviously published. That
combination is a controlled, paired representation design in which a fixed output cap manufactures a
script effect that vanishes at larger budgets, and in which the English advantage flips with the judge.
This is a modest, cautionary methodological contribution. It is defensible, but whether it suffices for a
main-conference long paper is uncertain (Section 12).

---

## 12. Phase 10–11 — Manuscript build, venue and submission

### 12.1 Manuscript build

* **Source:** `paper_v2/source/IndraLLM_IEEE_FINAL.docx`. It is pandoc-style, with styles "First
  Paragraph" and "Body Text" and 20 sections; full-width tables and figures are wrapped by a two-column
  section end and a one-column section end.
* **First build** (`build_revised_docx.py`): 13 pages. Exported to PDF via Word and every page inspected at
  100 dpi. Bugs found and fixed:
  * four tables had lost their header rows because they were filled without a header;
  * a budget table's cells wrapped;
  * Fig. 1 still said "Qwen-27B";
  * Fig. 2b and Fig. 4 had clipped or overlapping labels;
  * p formatting was inconsistent;
  * the custom abstract stored in the document properties was stale.
* **Final build** (`build_paper.py`, 10-page structure):
  * Table III (three budgets × two judges) is full width.
  * Table IV is the judge-disagreement table by budget and condition.
  * GEE moved to Appendix B (Table IX).
  * The per-language, model and descriptor tables were removed; their content is in Fig. 3 and the text.
  * Fig. 5 is redrawn for three budgets; Fig. 1 is redrawn with both judges and both follow-ups.
  * The text is revised to the new framing, and references [23]–[27] are added.
  * Fourteen assertions check that every text replacement took effect.
* **Final DOCX contents:** 9 tables; table order I prompts, II accuracy, III budgets, IV judge agreement,
  V tipping, VI claims, VII topics, VIII pairwise, IX GEE. About 7,900 words in body paragraphs.
* **Page count not verified.** The Word PDF export failed (`CO_E_SERVER_EXEC_FAILURE`, 0x80080005).
  * A leftover headless Word instance from the first export (PID 85292) was stopped; your own open Word
    window (PID 67028) was not touched.
  * The retry still failed, and you said no PDF was needed.
  * With about 7,900 words plus 5 figures and 9 tables, the IEEE layout is likely 11–12 pages. To reach 10:
    * shorten §IV Statistics and §V-C;
    * drop Table V (tipping points) to a sentence;
    * shorten Appendix C.
  * Open the DOCX in Word and check the page count, table widths and the Telugu/Kannada glyphs (Nirmala UI).

### 12.2 Venue

* **The IEEE-format file suits an IEEE conference.** For ACL/EMNLP/NAACL via ACL Rolling Review:
  * ACL template;
  * anonymous submission;
  * 8 pages (long) or 4 (short) for the main text;
  * a mandatory Limitations section;
  * the Responsible NLP checklist;
  * references before appendices.
* **Fit:** the contribution is a cautionary evaluation-methodology finding on one model with 20 topics.
  Likely fits:
  * an ARR **short paper** or Findings;
  * evaluation-focused venues (e.g. the GEM or Eval4NLP workshops);
  * multilingual and code-switching venues (MRL, CALCS);
  * Indian-NLP venues (e.g. ICON).

  Do not assume a workshop is easier. Check each venue's current call for scope, page limits and dates; I
  have not verified 2026–27 deadlines.
* **Main rejection risks:**
  1. no human validation of the judge;
  2. one informative model;
  3. 20 topics;
  4. residual cap binding at 1,024 tokens for MIXED;
  5. novelty relative to tokenization-premium and judge-reliability work.

---

## 13. Change log (original PDF → revised manuscript)

| Location | Old | New | Why / evidence |
|---|---|---|---|
| Title | Representation Fragility in Indic Factual Recall: Separating Script Alternation from Code-Switching | Representation Effects in Indic Factual Question Answering: Script, Output Budget, and Judge Dependence | Script effect is a budget artifact; judge dependence |
| Abstract | Stored accuracies; 19-point MIXED drop as the headline; "28.0and" | Harmonised accuracies; three-budget result; judge agreement 75–81%; no human validation stated | EXP-004/005 |
| Index terms | factual recall, … | multilingual evaluation, output budget, LLM-as-a-judge, judge agreement, … | Reframing |
| §I ¶3 | Five representations; "same words" | Word-identical only in hi/bn/ta; two evaluation changes tested | Template strings |
| §I RQs | RQ1–RQ4 | RQ1–RQ5 incl. budget (RQ3) and judge (RQ4) | — |
| §I Contributions | Tipping point as a contribution; null mediation | Three-budget rerun; judge disagreement as a result | — |
| §I Findings | "Survives every level of clustering" | Methodological statement; MIXED = CS-LAT at 512/1,024; English advantage judge-dependent | G1–G3 |
| §II | 4 paragraphs | + RomanSetu; + output-side token premium; + judge biases and multilingual judge reliability [24]–[27] | Literature check |
| §III-A | "Same words"; no speaker validation mentioned | te/kn and hi differences disclosed; fluent-speaker template review described with its limits | Strings; author |
| §III-B | "Identical decoding and judging" | Judging differed (T 0.3 vs T 0); all outputs re-graded | Code trace |
| §III-C | Gold "not independently re-verified"; κ 0.719 mentioned | Author + volunteer checks; provisions as of Oct 2026; 1 dated, 3 narrow; κ 0.719 not used | Ledger; author |
| §IV Models | Checkpoint unknown; three names | Tokenizer established; weights unverifiable; determinism figures | Tokenizer check |
| §IV Prompting | 128 tokens | + 598/600 capped; 82–95% mid-sentence; finish reasons logged in follow-ups | Data |
| §IV Judging | Single self-judge, T 0 | Stored / J-QWEN / J-OSS; no human validation; neither judge called more accurate | EXP-004 |
| §IV Statistics | Terse | Plain-language units; exact sign-flip; follow-up contrasts pre-specified | — |
| §V-A | CS-LAT −17 significant after Holm | −11, p = 0.13; stored −17 explained | J-QWEN |
| §V-B | 43 → 24; OR 0.42; survives every level | 49 → 26; OR 0.37; hi/bn/ta −25; then "does not survive a larger budget" | J-QWEN; EXP-004/005 |
| §V-C | ρ 0.204 | ρ 0.27; scoped "at this budget" | J-QWEN |
| §V-D | Language p 0.15; EN > CS-LAT in all five | p 0.17 (defined test); tied in Bengali | Recompute |
| §VI-A | Qwen2.5 tokenizer; "no role" | Qwen3.8 tokenizer; exploratory; wrong-sign b | Tokenizer check |
| §VI-B | "Would cost a few cents" (follow-up not run) | 512 and 1,024 runs with results, Table III, Fig. 5 | EXP-004/005 |
| §VII | Sensitivity grid / tipping | Judge configuration, family, directional disagreement, conclusion dependence, Table IV; tipping kept as hypothetical | G2, G3 |
| §VIII | "Narrow" claim about script | Methodological claim; novelty assessed against [5], [6], [26], [27] | — |
| §IX Limitations | Mixed | Residual cap at 1,024; no human labels; template review informal; weights unverifiable | — |
| Reproducibility | `make_all.py` (missing); $0.21 | Scripts exist; $1.10 + $1.23; ledger underpricing explained | Repo; prices |
| Tables | I–X | I prompts, II accuracy, III budgets (new), IV judge agreement (new), V tipping, VI claims, VII topics + provisions, VIII pairwise, IX GEE | — |
| Table VIII caption | "b: first condition correct" | "b: second-named (reference) correct, first wrong" | Definition of b |
| Figures | Fig. 1 "Qwen-27B"; Figs. 2–5 stored labels; Fig. 5c Qwen2.5 | All regenerated; Fig. 5 shows three budgets | — |
| References | 22 | 27 (five verified additions) | — |

---

## 14. Files created or modified

### 14.1 New code

| File | Purpose |
|---|---|
| `paper_v2/scripts/stats_lib.py` | Shared statistics (Section 9.1) |
| `paper_v2/scripts/make_all.py` | Recomputes all 128-token numbers; `--labels jqwen` |
| `paper_v2/scripts/analyze_exp004.py` | Judge agreement, 128 vs 512, spend |
| `paper_v2/scripts/analyze_budgets.py` | Three budgets × two judges; agreement; conclusion matrix |
| `paper_v2/scripts/make_figures.py` | Figs. 2–5 |
| `paper_v2/scripts/make_fig1.py` | Fig. 1 design diagram |
| `paper_v2/scripts/docx_helpers.py` | python-docx editing helpers |
| `paper_v2/scripts/build_revised_docx.py` | First (13-page) build; holds the base text and provisions |
| `paper_v2/scripts/build_paper.py` | Final 10-page build |
| `paper_v2/scripts/dump_tables_md.py` | Tables as Markdown (guide) |
| `paper_v2/scripts/dump_report_parts.py` | Generated part of this report |
| `paper_v2/scripts/audit_budget_truncation.py` | Truncation, complete-answers sensitivity, 18-test multiplicity (`numbers_audit.json`) |
| `paper_v2/scripts/independent_check.py` | Independent re-derivation of 118 reported numbers (`independent_check.md`) |
| `paper_v2/scripts/make_guide.py` | Assembles the v2 build guide from `guide_header.md` + generated content |
| `scripts/run_exp004_budget_rejudge.py` | EXP-004 runner |
| `scripts/run_exp005_budget1024.py` | EXP-005 runner |
| `scripts/build_human_eval_sample.py` | Blinded human-evaluation sample |

### 14.2 New data and results

| Path | Content |
|---|---|
| `results/EXP-004-budget-rejudge/gen512_predictions.jsonl` | 300 responses at 512 tokens, with metadata |
| `results/EXP-004-budget-rejudge/judgements.jsonl` | 1,800 judgements (128 + 512; J-QWEN + J-OSS) |
| `results/EXP-004-budget-rejudge/spend_log.jsonl` | 2,100 per-call cost records |
| `results/EXP-004-budget-rejudge/human_eval/` | `items_blinded.csv` (150), `items_blinded_512.csv` (60), keys, reviewers template |
| `results/EXP-005-budget1024/gen1024_predictions.jsonl` | 300 responses at 1,024 tokens |
| `results/EXP-005-budget1024/judgements.jsonl` | 600 judgements |
| `results/EXP-005-budget1024/spend_log.jsonl` | 900 per-call cost records |
| `paper_v2/output/numbers_original.json` | Stored-label analysis |
| `paper_v2/output/numbers_jqwen.json` | Harmonised-label analysis |
| `paper_v2/output/numbers_exp004.json` | EXP-004 analysis |
| `paper_v2/output/numbers_budgets.json` | Three-budget analysis |
| `paper_v2/output/fig1.png` … `fig5.png` | Figures (300 dpi) |
| `paper_v2/output/report_generated.md` | Generated tables and text for this report |

### 14.3 Documents

| Path | Content |
|---|---|
| `paper_v2/FULL_REVISION_REPORT.md` | This report |
| `paper_v2/MANUSCRIPT_BUILD_GUIDE.md` | 740-line guide (written before EXP-005; superseded on the 1,024 results by this report) |
| `paper_v2/revised/IndraLLM_IEEE_REVISED.docx` | Final revised manuscript (10-page structure) |
| `paper_v2/revised/IndraLLM_IEEE_REVISED.pdf` | **Stale**: export of the first 13-page draft; not the final DOCX |
| `paper_v2/source/IndraLLM_IEEE_FINAL.docx/.pdf` | Byte-identical originals (SHA-256 105b6933…, 68743145…) |
| `research/gold_verification_ledger.csv` | 20-topic ledger; author confirmation recorded |
| `research/HUMAN_EVAL_PROTOCOL.md` | Judge-validation protocol |
| `research/PROMPT_VALIDATION_PROTOCOL.md` | Templates, lexical findings, review record with reviewer names |

Unchanged: `results/EXP-002/`, `results/EXP-003-matched-en/`, the benchmark data, and the original
manuscript files.

---

## 15. Costs

| Item | Calls | Tokens (in / out) | Cost (list price) |
|---|---|---|---|
| EXP-004 Qwen (300 gens @512 + 900 J-QWEN judgements) | 1,200 | 404,527 / 166,298 | $0.989 |
| EXP-004 gpt-oss-120b (900 J-OSS judgements) | 900 | 394,936 / 78,730 | $0.106 |
| **EXP-004 total** | 2,100 | | **$1.095** |
| EXP-005 Qwen (300 gens @1,024 + 300 J-QWEN) | 600 | 299,795 / 233,669 | $1.175 |
| EXP-005 gpt-oss-120b (300 J-OSS) | 300 | 261,224 / 25,234 | $0.054 |
| **EXP-005 total** | 900 | | **$1.229** |
| **This revision, total** | 3,000 | | **$2.32** |
| Earlier EXP-002/003 Qwen generation + grading (estimate at list price) | — | — | ≈ $2.1 |
| Budget ledger's recorded spend for earlier runs | — | — | $0.214 (flat $0.08/M placeholder) |

* **Prices used:** Groq console, 2026-10-10.
  * `qwen/qwen3.8-27b`: $0.80 per M input, $4.00 per M output.
  * `openai/gpt-oss-120b`: $0.15 per M input, $0.60 per M output (cached input $0.075).
  * `allam-2-7b`: price "pending" (not published).
* **Estimated cumulative project spend:** about $4.4, under your $5 target. Check the Groq billing page,
  which is authoritative.

---

## 16. How to reproduce everything

```bash
# from the repository root (Python 3.11; numpy, pandas, scipy, statsmodels, tokenizers, matplotlib, python-docx)
python paper_v2/scripts/make_all.py                 # stored labels  -> numbers_original.json
python paper_v2/scripts/make_all.py --labels jqwen  # J-QWEN labels  -> numbers_jqwen.json
python paper_v2/scripts/analyze_exp004.py           # -> numbers_exp004.json
python paper_v2/scripts/analyze_budgets.py          # -> numbers_budgets.json
python paper_v2/scripts/make_figures.py             # fig2-fig5.png
python paper_v2/scripts/make_fig1.py                # fig1.png
python paper_v2/scripts/build_paper.py              # paper_v2/revised/IndraLLM_IEEE_REVISED.docx
python paper_v2/scripts/dump_report_parts.py        # generated part of this report
python scripts/build_human_eval_sample.py           # human-eval sample (no API calls)

# API runs (need GROQ_API_KEY in .env; cost ≈ $1.10 and $1.23 at list prices):
python scripts/run_exp004_budget_rejudge.py --stage gen
python scripts/run_exp004_budget_rejudge.py --stage judge
python scripts/run_exp005_budget1024.py --stage gen
python scripts/run_exp005_budget1024.py --stage judge
```

* The tokenizer check downloads `Qwen/Qwen2.5-7B` and `Qwen/Qwen3.8-27B` from the Hugging Face hub.
* Re-running the API stages appends only missing rows (resumable). Delete the output files to start fresh;
  outputs may differ slightly because hosted greedy decoding is not fully deterministic.

---

## 17. Git state

* Starting point: branch `phase4-5-verification` at `025a012`, with a clean working tree.
* New branch: `paper-v2-revision`.
* Commit `908ed5b`: EXP-004, the paper_v2 analysis, the research records and the draft build. Tagged
  `freeze-512-2026-10-10` (annotated) as the pre-EXP-005 freeze.
* A second commit on top of it adds EXP-005, `analyze_budgets.py`, `build_paper.py`, the updated figures and
  DOCX, the updated ledger and protocols, and this report.
* Nothing has been pushed to GitHub. `.env` is git-ignored and was not committed.

---

## 18. Remaining work

### 18.1 Required before a competitive submission

1. **Human validation of the judges.**
   * Annotate the 210-item blinded sample (≥ 2 readers per language) following
     `research/HUMAN_EVAL_PROTOCOL.md`.
   * Report κ, per-condition judge sensitivity and specificity, and corrected accuracies.
   * Why it matters: the English-advantage conclusion depends on which judge is right, and only humans can
     say. If annotators are not affordable, disclose this clearly and keep the paper's claim at "judge
     sensitivity".
2. **Venue formatting.** For ACL/EMNLP: the ACL template, anonymisation (remove the author block and
   repository link), the 8- or 4-page limit, Limitations, the Responsible NLP checklist, and references
   before appendices.
3. **Visual check of the final DOCX.** Page count, table widths, Indic glyph rendering, and figure
   placement. The final DOCX has not been rendered.

### 18.2 Strongly recommended

* **A budget where nothing is cut off** (e.g. 2,048 tokens) or an instruction fixing the answer language,
  on the same 300 prompts. At 1,024 tokens, 64 MIXED and 39 CS-LAT responses still hit the cap. The likely
  cost is $1.5–3, which would push total spend past your $5 target.
* **A second informative model,** to test whether the budget and judge sensitivity generalise.

### 18.3 Optional

* Item-level fluent-speaker ratings.
* Dated source records for the gold checks.
* Running the 25 written propositions.
* Refining the rubric so it says whether an answer must state the gold fact.

---

## 19. Blunt verdict

1. **Is the revised paper scientifically defensible?** Yes, if it keeps the narrowed methodological claim.
   Every number is reproducible from released files, the contradictory results (128 vs 512 vs 1,024; J-QWEN
   vs J-OSS) are all reported, and the limitations are stated.
2. **Is it ready for a competitive NLP conference?** Not yet. It lacks human validation of the judges, uses
   one model and 20 topics, and the final layout has not been checked.
3. **Most likely rejection triggers:**
   1. no human gold standard for the judge;
   2. single model;
   3. small topic set;
   4. novelty relative to known tokenization premiums and judge-reliability work;
   5. residual truncation at 1,024 tokens.
4. **Smallest set of changes that would make it substantially stronger:**
   1. annotate the prepared 210-item sample;
   2. one uncapped (or answer-language-fixed) run of the same 300 prompts;
   3. reformat for the chosen venue.

---

---

## 20. Post-review audit (after the 1,024-token experiment)

An external reading of the build guide raised three priorities:
1. update every claim made before EXP-005;
2. verify whether 1,024 tokens actually addresses truncation;
3. make the statistics auditable, including multiplicity, planning status and equivalence wording.

The work done for each follows.

### 20.1 Outdated claims removed

* **Build guide:** `paper_v2/MANUSCRIPT_BUILD_GUIDE.md` is now version 2. It is generated from the same
  sources as the DOCX (`build_paper.py` text plus the result files), so no pre-EXP-005 text survives. The
  sentence "the English–CS-LAT gap is not significant at the topic level in any analysis" appears 0 times.
* **Scan of the built DOCX** for stale or overclaiming phrases ("in any analysis", "removes the MIXED",
  "disappears", "do not differ", "equivalent", "factual recall", "survives every level", "Qwen-27B",
  "$0.21 for all", …). Every remaining hit is a negation or properly scoped, for example "en-orig and
  en-match do not differ detectably" and "we do not claim … damages factual recall".
* **Wording changes in `build_paper.py`:**
  * "removes the gap" became "no gap is detected", with intervals;
  * "MIXED and CS-LAT do not differ" became "no difference is detected, though we do not claim
    equivalence";
  * the claims table now marks "not an equivalence test" and gives the Holm-18 value for the English
    result.

### 20.2 Does 1,024 tokens address truncation? (from raw outputs and provider finish reasons)

| Budget | Condition | Hit cap | Ends mid-sentence |
|---|---|---|---|
| 128 | EN-MATCH / CS-LAT / MIXED | 100 / 99 / 100 | 87 / 90 / 92 |
| 512 | EN-MATCH / CS-LAT / MIXED | 42 / 85 / 95 | 42 / 78 / 88 |
| 1,024 | EN-MATCH / CS-LAT / MIXED | 5 / 39 / 64 | 15 / 39 / 63 |

* **Conclusion:** 1,024 tokens nearly removes truncation for English but **not** for MIXED (64% capped) or
  CS-LAT (39%). The paper says the budget remains a possible confound and that 1,024 is not an
  unconstrained condition.
* **Complete-answers sensitivity** (exploratory; selecting on completion can bias):
  * MIXED vs CS-LAT on the 29 propositions where both responses finished before 1,024 tokens: J-QWEN 55%
    vs 48% (p = 0.75); J-OSS 52% vs 55% (p = 1.0). No penalty, small n.
  * At 512 tokens only 3 such pairs exist, which is uninformative.
  * English vs CS-LAT on 57 complete pairs: J-QWEN 79% vs 61% (p = 0.013); J-OSS 65% vs 60% (p = 0.55). The
    same judge split as on all data.

### 20.3 Multiplicity, planning and equivalence

* **Planning:**
  * The 512-token run was planned to test the budget confound.
  * The 1,024-token run was added after the 512 results were seen, so its tests are exploratory.
  * The three contrasts per budget–judge cell were fixed in the analysis script before the outputs were
    graded.
* **Multiplicity for the J-QWEN 1,024 English–CS-LAT result:**
  * topic p = 0.018;
  * Holm within the three contrasts of that cell: 0.036;
  * Holm across all 18 follow-up tests (3 budgets × 2 judges × 3 contrasts): **0.29**;
  * the proposition-level exact p (8.4 × 10⁻⁶) remains significant after Holm-18 (1.4 × 10⁻⁴).
* **What the paper now says:** the topic-level English result does not survive correction across the
  follow-up.
* **Equivalence:** no margin was pre-specified, so the non-significant MIXED–CS-LAT gaps are reported as
  "not detected" with topic-bootstrap 95% CIs:
  * J-QWEN at 512 and 1,024: [−8, 15] and [−14, 8];
  * J-OSS at 512 and 1,024: [−18, 6] and [−17, 7].

  All four exclude the 23-point 128-token gap. That is stated as such, not as equivalence.
* **Full 18-row multiplicity table:** Part G, Section G5b.

### 20.4 Independent check of reported numbers

`paper_v2/scripts/independent_check.py` re-derives the key numbers from the raw files without the project's
own statistics code:

* exact McNemar via statsmodels;
* Wilson intervals via statsmodels;
* Cohen's κ via scikit-learn;
* topic p values via a Monte Carlo sign-flip test (200,000 draws) instead of exact enumeration;
* topic CIs via a bootstrap with a different seed.

**Result: 118 checks, 118 passed** (`paper_v2/output/independent_check.md`). This covers the 128-token
accuracies and Wilson bounds, all 11 pairwise McNemar p values and topic p values, every accuracy, McNemar
p, topic p and CI bound for 3 budgets × 2 judges × 3 contrasts, and κ and agreement at every budget.

### 20.5 Judges side by side; no human evaluation

Table III and Table IV present J-QWEN and J-OSS side by side at every budget. The abstract, §IV, §VII and
the limitations all state that no human evaluation of the outputs was performed and that neither judge is
treated as more accurate.

### 20.6 Updated verdict items

* **Still required:**
  * human annotation of the 210-item sample, or an explicit statement in the paper that none was performed
    (already stated);
  * a visual check and page count of the DOCX (about 8,200 words, probably 11–12 IEEE pages);
  * venue formatting.
* **Strongly recommended:** a run where nothing is cut off, or one with a fixed answer language, because
  MIXED is still 64% capped at 1,024 tokens.


---

# Part G — Generated results and final manuscript text

The sections below are produced by `paper_v2/scripts/dump_report_parts.py` from
`paper_v2/output/numbers_*.json` and from the TEXT dictionary of `build_paper.py`.

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

## G2. Judge agreement (J-QWEN vs J-OSS) by budget and condition

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

## G3. Does the conclusion change? (α = 0.05)

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

## G4. EXP-005 cost and failures

* openai/gpt-oss-120b: 300 calls, 261,224 input tokens, 25,234 output tokens, $0.054
* qwen/qwen3.8-27b: 600 calls, 299,795 input tokens, 233,669 output tokens, $1.175
* Total EXP-005: $1.229
* Persistent failures logged: 0; parse failures: 128|J-QWEN 0, 128|J-OSS 0, 512|J-QWEN 0, 512|J-OSS 0, 1024|J-QWEN 0, 1024|J-OSS 0

## G5. 128-token results, all six conditions (harmonised J-QWEN labels)

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

## G5b. Post-review audit (audit_budget_truncation.py)

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


## G6. Final manuscript text exactly as built into the DOCX (build_paper.py)

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

> **Findings in brief.** Evaluating multilingual LLMs across representation conditions is sensitive to the output-token budget and to the choice of evaluator, and observed differences should not automatically be interpreted as representation effects. At 128 tokens, accuracy falls from English to the Indic representations and mixed script is lowest. Almost every response hits that cap and Brahmic-script answers are about half as long in characters; with 512 or 1,024 tokens, no MIXED–CS-LAT difference is detected under either judge, though we do not claim equivalence. The English advantage over Latin-script code-switching is significant at the topic level only under the self-judge at 1,024 tokens, and not after correction across all follow-up tests; under the cross-family judge it is small at every budget. Neither judge has been validated against human labels, so we report this as judge sensitivity, not as evidence that either judge is right.

**II Multilingual evaluation**

> **Multilingual evaluation for Indic languages.** IndicNLPSuite and IndicXTREME provide corpora and task benchmarks for Indic languages [2], [3], and MEGA compares generative models across many languages and tasks [1]. Such benchmarks answer how well a model performs per language, but their per-language items are not the same questions. Romanized input has itself been proposed as a bridge to Indic languages for LLMs [23]; our ROMAN condition measures the same factor on fixed propositions.

**II Tokenization**

> **Tokenization.** Subword vocabularies fragment low-resource scripts into more tokens [7], [10], with measurable differences in cost and quality across languages [5], [6]. The same premium applies to generated text: an answer in a script that costs more tokens per character fits less content into a fixed output limit, which is the mechanism our budget experiment isolates. Our mediation analysis asks whether the input-side quantity explains the script contrast.

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

> Three conclusions follow. First, the 128-token MIXED penalty is not evidence that script alternation harms recall: once the budget allows longer answers, no difference between mixed-script and Latin-script code-switched prompts is detected under either judge, and the intervals exclude a gap of the 128-token size. Its most likely source is that Brahmic-script answers reach the cap before reaching the fact, and answers a human would call incomplete are then graded as wrong; the EN-MATCH answer on the MTP Act, for instance, correctly states the one-practitioner rule for the first 20 weeks, is cut off before the 20–24-week rule, and is graded HALLUCINATED. Second, NATIVE and MIXED behave alike at 128 tokens (32% and 26%, p = 0.29) although MIXED has five script boundaries per prompt and NATIVE one, which also argues against a boundary-density account. Third, the English advantage is unstable: it grows with the budget under one judge and stays small under the other, and its topic-level significance under the first does not survive correction across the follow-up. We cannot tell from these data which judge is closer to a careful human reader, so the instability itself is the finding. Because most MIXED and many CS-LAT answers still reach the 1,024-token limit, the output budget remains a possible confound for any residual difference.

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

> What the data support is narrower than the design promised, and different from what our first run suggested. Evaluating multilingual LLMs across representation conditions is sensitive to the output-token budget and to the choice of evaluator, and observed differences should not automatically be interpreted as representation effects. For this model and these 20 topics, the clearest representation effect at a 128-token budget, the mixed-script penalty, is no longer detected when answers can be longer, under either judge; the English advantage over code-switching appears or disappears with the judge. We do not claim that native script or code-switching damages factual recall, and we make no claim about other models.

**VIII Discussion 2**

> The practical lesson is methodological. Output caps are often set low to save cost, and tokenizers make some scripts more expensive per character, so a shared cap gives answers in those scripts less room. Studies that compare languages or scripts through generated answers should report how often the cap binds in each condition and show that conclusions hold at a non-binding budget; judges should be configured identically across conditions, at least two judges from different families should be used, and their agreement should be reported per condition. Whether this cautionary result is novel enough for a given venue depends on prior work on tokenization premiums and multilingual judge reliability [5], [6], [26], [27], which documents the ingredients but, to our knowledge, not their combined effect on paired representation contrasts. Table VI lists claims we examined.

**Table VI caption**

> Claims examined and not supported, or supported only under some evaluation settings.

**IX Limitations**

> **Topics.** Twenty topics with heavy within-topic concentration bound what any statistic can show (effective n ≈ 67 of 500). A 25-proposition expansion has been written but not evaluated. **Output budget.** At 1,024 tokens, 39 CS-LAT and 64 MIXED responses still hit the cap, so the budget is not fully removed as a confound; the 1,024-token run was added after the 512-token results were seen and is exploratory; we re-ran three of the six conditions and did not test an instruction fixing the answer language. **Equivalence.** No equivalence margin was pre-specified, so non-significant gaps are reported with intervals, not as equivalence. **Judges.** Two LLM judges that disagree on a fifth to a quarter of items, and no human labels on any output; a stratified, blinded sample of 210 outputs and an annotation protocol are released but not annotated. **Questions and gold answers.** One generic template that under-specifies the target for several topics; volunteer gold checks without an item-level record; one superseded scheme. **Prompts.** The fluent-speaker review was an informal yes/no check of the templates; CS-LAT and MIXED differ by one word in Telugu and Kannada, and Hindi ROMAN is not a transliteration of Hindi NATIVE. **Models and languages.** One informative model, served under an API identifier whose underlying weights we cannot independently verify, and five languages. **Single run.** No repeated sampling; hosted greedy decoding was not fully deterministic, and API behaviour can change over time.

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
