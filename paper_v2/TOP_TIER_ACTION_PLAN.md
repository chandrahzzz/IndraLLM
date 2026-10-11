# IndraLLM — Action plan to fix "Validation and evidence: 4.5/10"

The reviewer's three reasons, and what fixes each:

| Criticism | Fix | Who | Cost | Ready? |
|---|---|---|---|---|
| No human validation of judge labels | Human labelling of 216 blinded outputs by fluent readers (Step 1) | You + reviewers | Free (≈ 3–5 h for you and Akshith; ≈ 1 h each for Kapilan and Shamik) | **Yes**: workbooks built |
| One informative answering model | Second answering model, Gemini 3.1 Flash-Lite, same prompts, same two judges (Step 3) | Script | Answers free; judging ≈ $0.45 (≤ $0.74) | **Yes**: script tested (2-call pilot) |
| Residual truncation | Re-answer the 108 responses still capped at 1,024 tokens with 3,072 tokens (Step 2) | Script | ≈ $1.02 (≤ $1.73) | **Yes**: script ready (dry-run tested) |

**Budget decision needed from you.**
* Steps 2 and 3 together cost about $1.5 at Groq list prices (worst case about $2.5).
* Your target was $5 total, and the estimated spend so far is about $4.4. Running both puts the total at
  about $5.9: over the $5 target, under the $10 ceiling.
* Nothing will be spent until you run the commands yourself, or tell me to run them.

**Order:** start Step 1 now, because it takes the longest (people's time). Run Steps 2 and 3 in parallel.
Then do Steps 4 and 5.

---

## Step 1 — Human validation of the judges (most important)

### What is ready

| File | What it is | Give to reviewers? |
|---|---|---|
| `results/human_eval_v2/to_annotate/Chandrahas.xlsx` | Your workbook, 157 items | You |
| `results/human_eval_v2/to_annotate/Akshith.xlsx` | 161 items | Akshith |
| `results/human_eval_v2/to_annotate/Kapilan.xlsx` | 28 items (Tamil) | Kapilan |
| `results/human_eval_v2/to_annotate/Shamik.xlsx` | 27 items (Bengali) | Shamik |
| `results/human_eval_v2/to_annotate/TBD_second_Kannada_reader.xlsx` | 32 items | A second Kannada reader, if you can find one |
| `results/human_eval_v2/to_annotate/TBD_second_Bengali_reader.xlsx` | 27 items | A second Bengali reader, if you can find one |
| `results/human_eval_v2/key_v2.csv` | Answer key: condition, budget, both judges' labels, sampling weights | **No, keep it hidden** |
| `results/human_eval_v2/assignments_v2.csv` | Which reviewer has which item | No |
| `scripts/build_human_eval_v2.py` | Rebuilds everything above (seed fixed) | — |
| `scripts/analyze_human_eval.py` | Analyses the returned workbooks | — |

### Design

* **Frame:** 900 outputs: EN-MATCH, CS-LAT and MIXED × 128, 512 and 1,024 tokens × 100.
* **Sampling:** 216 items. In each of the 9 budget × condition cells there are up to 8 items where both
  judges said CORRECT, 8 where both said wrong, and 8 where they disagree. Draws are balanced by language.
* **Weights:** inverse sampling weights let the analysis estimate the error rates of **both judges** and
  the **human-assessed accuracy** for all 900 outputs.
* **Blinding:** reviewers see only item id, language, question, gold answer and model answer. They do not
  see the condition name, the budget or either judge's verdict. The script reveals the condition only
  where it is unavoidable.
* **Two readers per item where possible:**

| Language | Reviewers |
|---|---|
| English | Chandrahas, Akshith |
| Telugu | Chandrahas, Akshith |
| Hindi | Akshith, Chandrahas |
| Tamil | Kapilan, Chandrahas |
| Kannada | Akshith, plus a second reader still needed |
| Bengali | Shamik, plus a second reader still needed |

**Check this assignment first.** It assumes you read Telugu, Tamil and Hindi, and that Akshith reads
English, Telugu, Hindi and Kannada. If that is wrong, edit `READERS` at the top of
`scripts/build_human_eval_v2.py` and rebuild with `python scripts/build_human_eval_v2.py`. Rebuilding is
deterministic and costs nothing.

If you cannot find a second Kannada or Bengali reader, those 59 items stay single-labelled. Agreement is
then measured on the other items, and the paper says so.

### How to do it

1. **Check the workbooks.** Open `Chandrahas.xlsx`. You should see three sheets:
   * **Instructions:** the six labels and the rules;
   * **Items:** one row per answer, with a dropdown in the `label` column;
   * **Reviewer:** your name, languages, background, whether you were paid, and consent to be named.

   Confirm that no column reveals the condition, the budget or the judge.
2. **Send** each person only their own workbook. Ask them to read the Instructions sheet first, label
   alone, and not discuss items until everyone has finished. A Google Sheet works too, if you export it
   back to .xlsx with the same columns.
3. **Label your own workbook** under the same rules.
   * You built the study, so you could be biased. Label without looking at `key_v2.csv`, and do not reopen
     any results tables while labelling.
   * Expect about 1–2 minutes per item. Spread it over 3–4 sittings.
4. **Collect** the files into `results/human_eval_v2/returned/`, keeping the same file names. Rename a
   placeholder file to the real person's name, and change the same name in `assignments_v2.csv`.
5. **Run the analysis:**

```bash
PYTHONIOENCODING=utf-8 python scripts/analyze_human_eval.py
```

   It writes:
   * `paper_v2/output/human_eval_report.md`, readable by you;
   * `paper_v2/output/numbers_human_eval.json`, which the paper build reads;
   * `results/human_eval_v2/adjudication.xlsx`, listing every item where two reviewers disagree on
     CORRECT vs not.
6. **Adjudicate.** For each row in `adjudication.xlsx`, the two reviewers discuss, or a third person
   decides. Write the agreed label in `final_label` and one line in `rationale`. Then re-run step 5.
7. **Inspect the report.** Check:
   * **Completeness:** every reviewer has blank = 0 and invalid = 0.
   * **Inter-annotator κ:**
     * 0.6 or higher is solid;
     * 0.4–0.6 is moderate, which is acceptable if reported;
     * below 0.4 means the rubric needs a short calibration round. Discuss 10 items together, then
       re-label the disagreements.
   * **Judge validation table:** sensitivity (how often the judge accepts answers humans call correct) and
     specificity (how often it rejects answers humans call wrong), for J-QWEN and J-OSS. This answers which
     judge humans side with.
   * **Human accuracy and gaps:** look at MIXED − CS-LAT and CS-LAT − EN-MATCH at 512 and 1,024 tokens as
     judged by humans. The paper's claims change according to these numbers (Step 4).

### Spot-check before trusting the analysis (about 10 minutes)

* Pick 5 random item ids from your returned workbook. Look each up in `key_v2.csv` and check that the
  condition and budget make sense for the question and answer you saw. For example, Brahmic script in the
  answer should mean MIXED, and a long answer should mean a 512 or 1,024 budget.
* Count rows: the returned workbook should have as many items as `assignments_v2.csv` lists for that
  reviewer.

---

## Step 2 — Residual truncation (EXP-006)

The 1,024-token run still had 5 / 39 / 64 capped answers (EN-MATCH / CS-LAT / MIXED). EXP-006 re-answers
only those 108 with 3,072 tokens and keeps everything else the same. Combined with the 192 answers that
already finished, this gives a set where (nearly) every answer is complete.

```bash
PYTHONIOENCODING=utf-8 python scripts/run_exp006_complete_answers.py --dry-run   # cost estimate, no API calls
PYTHONIOENCODING=utf-8 python scripts/run_exp006_complete_answers.py --stage gen --limit 3   # pilot (~$0.03)
PYTHONIOENCODING=utf-8 python scripts/run_exp006_complete_answers.py --stage gen
PYTHONIOENCODING=utf-8 python scripts/run_exp006_complete_answers.py --stage judge
PYTHONIOENCODING=utf-8 python paper_v2/scripts/analyze_followups.py
```

* The run stops itself if EXP-006 spending passes $1.80.
* **What to inspect** in `paper_v2/output/numbers_followups.json`, section `exp006_complete_answers`:
  * `still_capped_at_3072` should be near 0. If not, the paper still says truncation remains.
  * `J-QWEN` and `J-OSS` → `contrasts`: the MIXED − CS-LAT and CS-LAT − EN-MATCH gaps on complete answers.
  * Note: about 15–20% of hosted greedy outputs can diverge from the earlier text. This is expected and is
    already disclosed in the paper.

---

## Step 3 — Second answering model (EXP-007)

**Why Gemini 3.1 Flash-Lite:**
* it is free with your existing Google key;
* it is a third model family, so neither judge grades its own family's output;
* `gemini-2.5-*` is no longer available to new keys (checked 2026-10-11);
* it uses a fixed model ID, not a `-latest` alias, so it stays reproducible.

**Settings:** same prompts and system prompt, temperature 0, top-p 1, thinking disabled, budgets 128 and
1,024. Default conditions are EN-MATCH, CS-LAT and MIXED; add NATIVE and ROMAN with
`--conditions EN-MATCH CS-LAT MIXED NATIVE ROMAN`.

```bash
PYTHONIOENCODING=utf-8 python scripts/run_exp007_second_model.py --dry-run
PYTHONIOENCODING=utf-8 python scripts/run_exp007_second_model.py --stage gen      # free; ~70 min; resumable
PYTHONIOENCODING=utf-8 python scripts/run_exp007_second_model.py --stage judge    # Groq judges, ~$0.45
PYTHONIOENCODING=utf-8 python paper_v2/scripts/analyze_followups.py
```

* **Pilot already done:** 2 Gemini answers are in `results/EXP-007-second-model/` (free).
* **Free-tier limits:** if the daily quota runs out, the script stops cleanly. Re-run the same command
  the next day; finished rows are kept.
* **What to inspect** in `numbers_followups.json` → `exp007_second_model`:
  * **Accuracy well above the floor** (not 2–10% like ALLaM). If Gemini is also near the floor, it does
    not count as a second informative model, and the paper must say so.
  * **Same pattern as Qwen?** Is the MIXED − CS-LAT gap large at 128 tokens and small at 1,024? Does the
    English − CS-LAT gap depend on the judge?
  * **`hit_cap` at 1,024:** how often the cap still binds for Gemini.
  * **`judge_agreement`:** whether the two judges disagree in the same lopsided way.

  If the pattern does **not** replicate, that is still a result. Report it honestly as model-dependence.

---

## Step 4 — Update the paper with the new evidence

When Steps 1–3 are done, tell the next session (or me): "update the paper with
`numbers_human_eval.json` and `numbers_followups.json`". These sections change, and the wording depends
on the numbers:

| Section | Change |
|---|---|
| Abstract / contributions | Add the human-validation result (inter-annotator κ; which judge humans agree with) and the second-model and complete-answer results |
| §III–IV | Describe the human-validation design (sample, blinding, readers, adjudication) and the two new runs |
| §VI (budget) | Add the complete-answer analysis; rephrase "64% still capped" if EXP-006 removes truncation |
| §VII (judges) | Replace "no human labels" with the measured judge sensitivity and specificity; keep "judge-dependent" only if humans do not settle it |
| New subsection | Second model (Gemini): table and short paragraph |
| Limitations | Shorter: remove what is fixed; keep 20 topics, one generic template, the remaining single-labelled languages, and author-as-annotator |
| Ethics / checklist | Reviewers' payment (Y/N) and consent to be named, from the Reviewer sheets |

**Decision rules (agree with them before seeing the results, so you are not tempted to choose
afterwards):**
* **If humans side clearly with one judge** (e.g. sensitivity and specificity both about 0.15 better),
  make that judge primary in the revised paper and report the other as a sensitivity analysis.
* **If humans show no MIXED − CS-LAT gap at 512 or 1,024 tokens**, the budget-sensitivity claim is
  confirmed by humans. If they do show one, report it, and soften the budget claim.
* **For the English gap,** report whatever humans show, with its interval.

---

## Step 5 — Build the conference paper

Follow `paper_v2/NEXT_SESSION_PROMPT_FULL.md`: the ACL two-column Word build, the 8-page plan, the
author–year citation map, rendering and checks.

Before that session, close Word, because an open Word window blocked the PDF export before.

---

## What this does and does not achieve

* **Achieves:** answers all three named weaknesses with real evidence, in about 1–2 weeks of calendar time,
  mostly waiting for reviewers.
* **Does not achieve:** 20 topics and one generic question template remain. A reviewer can still call the
  benchmark small. The 25 written-but-unrun propositions (v1.2-PILOT) could extend it to 45 topics later;
  that is a separate decision.
* **No guarantee of acceptance.** It makes the evidence defensible; novelty against prior work (tokenization
  premiums, multilingual judge reliability) is still judged by reviewers.
