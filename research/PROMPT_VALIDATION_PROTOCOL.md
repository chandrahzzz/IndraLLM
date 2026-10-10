# Prompt inventory, audit findings, and fluent-speaker validation protocol

Status, 2026-10-10: **fluent-speaker review completed (informal).** The prompt
templates of the 100 evaluated groups (IndraLLM-CS v1.1, TEST-OOD) were reviewed
by speakers of all five languages and judged proper (natural and correct). See the
review record in Section 0. The naturalness score of 4.74/5 and κ = 0.719 in older
documents refer to an earlier 150-group pilot whose raw annotation files are not in
the repository; they must not be cited for these prompts.

## 0. Fluent-speaker review record

As reported by the author (Chandrahas Reddy), 2026-10-10:

| Language | Reviewer(s) | Outcome |
|---|---|---|
| Telugu | Chandrahas Reddy (author; speaks Telugu, English); Akshith Chawla (teammate) | Proper |
| Hindi | Akshith Chawla (teammate; speaks Hindi, Telugu, Kannada) | Proper |
| Kannada | Akshith Chawla | Proper |
| Tamil | Kapilan (friend of the author) | Proper |
| Bengali | Shamik Mukherjee (friend of the author) | Proper |

Scope and form: reviewers checked the templates as used in the evaluated prompts and
reported them proper. The review was a yes/no judgement; no per-item 1–5 ratings,
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

## 1. Inventory of templates (exactly as used)

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

## 2. Findings from inspecting the strings (no speaker judgement involved)

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

## 3. Consequences for the current results

* No prompt was edited after the runs. The results remain results for these exact
  strings. If any template is corrected, all affected conditions must be re-run and
  reported as a new experiment; the old results cannot be relabelled.
* The CS-LAT vs MIXED contrast is reported on all 100 propositions (pre-specified)
  and, as a sensitivity analysis, on the 60 word-identical propositions.

## 4. Fluent-speaker validation protocol (to run)

**Reviewers.** At least two fluent readers per language (hi, bn, ta, te, kn), each
literate in the native script and familiar with romanised chat-style writing.
Record languages, region and background in `prompt_reviewers.csv`.

**Items.** The 20 templates above (instantiated with three topics each, e.g.
PMFBY vs WBCIS, GST Registration Exemption, Citizenship Amendment Act Cut-off), plus
the EN-MATCH English sentence for reference. 60 items per language.

**Per item, rate independently:**

| Dimension | Scale |
|---|---|
| Semantic equivalence to EN-MATCH | 1 (different question) – 5 (same question) |
| Naturalness (would someone write this?) | 1 – 5 |
| Spelling / transliteration correct | yes / no + correction |
| Script renders correctly (no broken conjuncts, ZWJ/ZWNJ issues) | yes / no |
| CS-LAT vs MIXED: same words, only script differs? | yes / no + which word differs |
| ROMAN vs NATIVE: transliteration of the same words? | yes / no |

**Analysis.** Report per-language means with ranges, Krippendorff's α (ordinal) for
the two 1–5 scales, and list every flagged string verbatim. Pre-register a
threshold (e.g. mean equivalence ≥ 4 and no "different question" rating) below
which a template is corrected and re-run.

**Status:** an informal yes/no review by speakers of all five languages has been
done (Section 0). The structured protocol above remains available if reviewers ask
for per-item ratings or agreement statistics.
