# Human validation of the answer judge — protocol (not yet executed)

Status, 2026-10-10: **no human has labelled any of the 600 evaluated Qwen outputs.**
This protocol and its sample (`results/EXP-004-budget-rejudge/human_eval/`) are
ready to run. Nothing in the manuscript reports human-judge agreement; once this
study is done, Section VII and Table IV should be revised with its results.

Two separate things are often confused, so this protocol keeps them apart:

| Activity | Question it answers | Status |
|---|---|---|
| Gold-answer verification | Is the benchmark's gold answer a true statement of the fact? Is it complete and unambiguous for the question asked? | Author and friends checked factual correctness (no per-item record). Completeness/ambiguity reviewed per topic in `research/gold_verification_ledger.csv`. |
| Judge validation (this protocol) | Given a correct gold answer, does the LLM judge label the model's answer the way a careful human would, equally across conditions? | **Not done.** |

## 1. Sample

`scripts/build_human_eval_sample.py` draws a stratified sample from the 600
original 128-token outputs (seed 20261010):

* 6 conditions × 2 judge verdicts (original stored verdict: CORRECT / HALLUCINATED)
  × 5 languages × 2 items = **120 items** (fewer where a stratum is smaller; MIXED and
  NATIVE have few judged-correct items in some languages, so the shortfall is drawn from
  other languages in the same condition-verdict cell).
* A supplementary set of up to 30 items where the two judges used in EXP-004
  (J-QWEN and J-OSS) disagree, if such items exist outside the main sample.
* The 512-token outputs are **not** in the main sample; a second wave can reuse
  the same procedure.

Sampling probabilities are stored in the key file so that per-condition accuracy
can be re-estimated with inverse-probability weights (the sample deliberately
over-represents the rarer verdict).

## 2. What reviewers see

Each item shows only: item ID, QUESTION (as the model saw it), GOLD ANSWER,
MODEL ANSWER. Reviewers do **not** see the condition label, the language tag,
either judge's verdict or reason, or the model name. Items are shuffled.

Blinding to condition is necessarily imperfect: script and language reveal much
of it. Blinding to the judge verdict is complete and is the property that matters
most for estimating judge error.

Every answer was cut off by the 128-token limit. Reviewers are told this, so that
a cut-off is not by itself treated as an error.

## 3. Reviewers

* At least two reviewers per item, each able to read the item's language and
  script (Hindi, Bengali, Tamil, Telugu, Kannada; English items need any reviewer).
* Reviewers record their name/initials, languages read, and relevant background
  in `reviewers.csv` before starting. Report the number of reviewers and their
  language coverage in the paper exactly as recorded; do not round up.
* A reviewer must not label items in a language they cannot read; such items are
  routed to another reviewer.

## 4. Rubric (one label per item)

| Label | Definition |
|---|---|
| `CORRECT` | The answer states the gold fact (paraphrase, translation, or transliteration is fine) and makes no claim that contradicts it. |
| `PARTIAL` | States part of the gold fact (e.g. one of two contrasted properties, or one of three thresholds) and nothing contradicting it. |
| `INCOMPLETE_NO_ERROR` | Cut off or generic before reaching the gold fact; no false statement about the asked fact. |
| `INCORRECT` | States something that contradicts the gold fact, or a false fact central to the question (e.g. wrong threshold, wrong expansion of a scheme name). |
| `CORRECT_OTHER_READING` | Wrong relative to the gold, but correct for a different reasonable reading of the (generic) question, e.g. the ₹20 lakh services threshold for GST. |
| `UNREADABLE` | Reviewer cannot assess (script/language/garbled). |

Reviewers also tick, independently of the label: `answer_language_matches_question`
(yes/no) and `gold_seems_wrong_or_outdated` (yes/no + note). The second flag feeds
back into the gold ledger; it does not change labels in this round.

## 5. Disagreement and adjudication

* Labels are collected independently (separate sheets; no discussion first).
* Agreement on the six-way label and on the binary collapse is reported before
  adjudication.
* Disagreements are adjudicated by a third reviewer, or by discussion between
  the two with the rationale written in `adjudication_note`. Adjudicated labels
  are the reference; pre-adjudication labels are kept.

## 6. Analysis (`scripts/analyze_human_eval.py`, to be written when labels exist)

1. Inter-rater agreement: Cohen's κ (binary, primary collapse) with bootstrap CI,
   and raw percent agreement on the six-way label.
2. Binary reference, **primary collapse**: CORRECT = 1; everything else = 0.
   Sensitivity analysis: CORRECT + PARTIAL + CORRECT_OTHER_READING = 1.
3. Per condition: judge sensitivity (P(judge CORRECT | human CORRECT)) and
   specificity, with Wilson intervals, for the stored judge and for J-QWEN/J-OSS.
4. Differential error: difference in judge sensitivity between EN-MATCH and each
   Indic condition (bootstrap over items, stratified).
5. Corrected accuracy per condition: P(judge=1)·PPV + P(judge=0)·(1−NPV),
   using inverse sampling weights; corrected contrasts EN-MATCH vs CS-LAT and
   CS-LAT vs MIXED with a stratified bootstrap. Compare with the tipping points in
   manuscript Table IV.
6. Share of `INCOMPLETE_NO_ERROR` among judge-HALLUCINATED items by condition:
   the direct, judge-independent measure of how much of the "error" rate is
   budget truncation rather than wrong content.

## 7. Size

120 items × 2 reviewers is small; per-condition sensitivity will have intervals of
roughly ±0.15. That is enough to detect gross differential bias (e.g. sensitivity
0.9 in English vs 0.6 in MIXED) but not subtle bias. If resources allow, double
the per-cell count to 4.

## 8. What must not be claimed

* Do not describe the author's gold-answer checks as validation of the judge.
* Do not report the κ = 0.719 or the 300-item "human validation" figures found in
  older project documents: no raw annotation files for them exist in the
  repository and they concern different data.
