"""Build IndraLLM_IEEE_REVISED.docx from the original manuscript source.

Edits paragraphs, tables and figures of paper_v2/source/IndraLLM_IEEE_FINAL.docx in place
(preserving the IEEE styles and section layout) and writes
paper_v2/revised/IndraLLM_IEEE_REVISED.docx.  Table values are read from the JSON files
written by make_all.py / analyze_exp004.py, not typed by hand.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import docx
from docx.shared import Emu, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_helpers import (  # noqa: E402
    add_column, add_runs, copy_table_after, delete_par, fill_table, insert_after,
    set_caption, set_cell, set_par,
)

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "paper_v2/source/IndraLLM_IEEE_FINAL.docx"
OUTDOC = ROOT / "paper_v2/revised/IndraLLM_IEEE_REVISED.docx"
NO = json.loads((ROOT / "paper_v2/output/numbers_original.json").read_text(encoding="utf-8"))
NJ = json.loads((ROOT / "paper_v2/output/numbers_jqwen.json").read_text(encoding="utf-8"))
NE = json.loads((ROOT / "paper_v2/output/numbers_exp004.json").read_text(encoding="utf-8"))
L6 = ["EN-ORIG", "EN-MATCH", "CS-LAT", "ROMAN", "NATIVE", "MIXED"]
SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def fp(p: float, sci_below: float = 1e-3) -> str:
    """p-value formatting used in tables."""
    if p < sci_below:
        m, e = f"{p:.2e}".split("e")
        return f"{m}×10{str(int(e)).translate(SUP)}"
    if p < 0.1:
        return f"{p:.3f}"
    return f"{p:.2f}"


def sgn(x: float) -> str:
    return f"{x:+.0f}".replace("-", "−")


def neg(s: str) -> str:
    return s.replace("-", "−")


TEXT = {}

TEXT["title"] = ("Representation Effects in Indic Factual Question Answering: "
                 "Script, Output Budget, and Judge Dependence")

TEXT["abstract"] = (
    "Cross-lingual factuality comparisons usually change a question's content or phrasing along with its "
    "language, so a drop in accuracy has no single cause. We hold the proposition fixed and vary only its "
    "representation. We build paired prompts for 100 propositions on 20 Indian public-policy topics in five "
    "Indic languages (Hindi, Bengali, Tamil, Telugu, Kannada), each rendered in English, native script, "
    "Romanized text, Latin-script code-switching (CS-LAT) and mixed-script code-switching (MIXED); in Hindi, "
    "Bengali and Tamil the last two differ only in the script of the Indic words. With Qwen3.8-27B "
    "(API identifier qwen/qwen3.8-27b), greedy decoding, a 128-token output cap and one judge configuration "
    "for all conditions, judge-assessed accuracy is 60% for a template-matched English prompt and 49%, 37%, "
    "32% and 26% for CS-LAT, Romanized, native-script and MIXED prompts; MIXED is 23 points below CS-LAT "
    "(exact McNemar p < 0.001; topic-level permutation p = 0.004). Two follow-up checks change how this "
    "should be read. Almost every response reached the cap, and Brahmic-script prompts elicit Brahmic-script answers "
    "that fit about half as many characters into it; with a 512-token cap the CS-LAT–MIXED gap disappears "
    "(+4 points, p = 0.57). A judge from another model family agrees with the self-judge on 76% of outputs "
    "and finds no significant CS-LAT–MIXED gap even at 128 tokens. The English–CS-LAT gap is not significant "
    "at the topic level in any analysis. For this model and benchmark, the apparent cost of script "
    "alternation is mainly an output-budget effect; representation effects should be measured with "
    "non-binding output budgets and more than one judge. Prompts, outputs, judgements, a gold-answer ledger "
    "and analysis code are released.")

TEXT["index"] = ("factual question answering, code-switching, script, Indic languages, output length, "
                 "LLM-as-a-judge, paired evaluation, cluster-robust inference")

TEXT[9] = (
    "We build the comparison so that they can be. Each of 100 propositions is rendered in five paired "
    "representations (Table I). Two of them, CS-LAT and MIXED, are meant to differ only in whether the Indic "
    "words are written in Latin or Brahmic script; this holds word for word in Hindi, Bengali and Tamil, "
    "while in Telugu and Kannada the question word also differs (Section III-A). We add a second English "
    "condition after finding that the original English template was more specific than the template shared "
    "by the other four conditions (Section III-B). We then ask whether the differences we measure survive "
    "two checks that representation studies rarely run: a larger output budget, and a judge from a "
    "different model family.")

TEXT["tab1"] = (
    "One proposition in all six conditions (Hindi). In Hindi, CS-LAT and MIXED contain the same words in the "
    "same order and differ only in the script of *ke*, *ya*, *kya hai* (also true for Bengali and Tamil; in "
    "Telugu and Kannada the question word differs, Section III-A). The topic string stays in Latin script in "
    "every condition, so NATIVE contains one Latin–Brahmic boundary per prompt.")

TEXT[13] = (
    "**Research questions.** RQ1: does judge-assessed answer accuracy depend on representation when the "
    "proposition is held fixed? RQ2: does mixed-script code-switching lower accuracy relative to the same "
    "code-switched words in Latin script? RQ3: does the effect differ across the five languages? RQ4: are the "
    "effects robust to the output budget and to the choice of judge? RQ5: is the script effect associated "
    "with input tokenization length? Hallucination detectors and mitigation are outside the scope of this "
    "paper.")

TEXT[14] = (
    "**Contributions.** (1) A paired six-condition design for Indic factual QA, with a matched-English "
    "control that removes a template confound we found in our first run. (2) Evidence that a binding output "
    "budget can manufacture a script effect: the 23-point MIXED penalty measured at 128 tokens disappears when "
    "the same prompts are answered with 512 tokens. (3) Evidence of judge dependence: grading all conditions "
    "with one judge configuration, rather than the two used in our first run, shrinks the English–code-"
    "switching gap from 17 to 11 points, and a cross-family judge changes which contrasts are significant. "
    "(4) Inference that treats the 20 topics, not the 500 prompts, as the unit of independent evidence, and a "
    "release of prompts, outputs, judgements, a gold-answer ledger, and protocols for the human validation "
    "that is still outstanding.")

TEXT[15] = (
    "**Findings in brief.** At a 128-token budget, accuracy falls from English to the Indic representations, "
    "and mixed script is lowest; under the self-judge the MIXED–CS-LAT gap is significant at prompt, "
    "proposition and topic level. It is not robust. Almost every response hits the cap, Brahmic-script answers "
    "are about half as long in characters, and with 512 tokens MIXED reaches CS-LAT (63% vs. 59%) and the "
    "level English reached with 128 tokens. A cross-family judge is much stricter (37% vs. 60% on English) "
    "and finds no significant MIXED–CS-LAT gap at either budget. The English advantage over Latin-script "
    "code-switching is not significant at the topic level in any analysis. Input characters per token, "
    "measured with the served model's tokenizer, shows no detectable association with correctness within "
    "the controlled contrast.")

TEXT[18] = (
    "**Multilingual evaluation for Indic languages.** IndicNLPSuite and IndicXTREME provide corpora and task "
    "benchmarks for Indic languages [2], [3], and MEGA compares generative models across many languages and "
    "tasks [1]. Such benchmarks answer how well a model performs per language, but their per-language items "
    "are not the same questions. Romanized input has itself been proposed as a bridge to Indic languages for "
    "LLMs [23]; our ROMAN condition measures the same factor on fixed propositions.")

TEXT[19] = (
    "**Tokenization.** Subword vocabularies fragment low-resource scripts into more tokens [7], [10], with "
    "measurable differences in cost and quality across languages [5], [6]. The same premium applies to "
    "generated text: an answer in a script that costs more tokens per character fits less content into a "
    "fixed output limit, which is the mechanism our budget experiment isolates. Our mediation analysis asks "
    "whether the input-side quantity explains the script contrast.")

TEXT[20] = (
    "**Factuality evaluation and LLM judges.** We use closed-book questions with a gold answer, closer in "
    "spirit to TruthfulQA-style checks than to long-form factual precision scoring [11], [12]. LLM graders "
    "are convenient but biased, for example towards their own outputs, answer position and length [13], "
    "[24], [25]; we therefore treat the judge as a central threat and grade with two judges from different "
    "model families.")

TEXT["fig1"] = (
    "Fig. 1. Study design. Each proposition is rendered in six conditions and answered once by Qwen3.8-27B "
    "under greedy decoding with a 128-token limit; responses are graded against the gold answer by the same "
    "model (J-QWEN). The follow-up (Section VI-B) re-answers three conditions with a 512-token limit and "
    "grades both budgets with J-QWEN and with gpt-oss-120b (J-OSS). Key contrasts: EN-MATCH vs. CS-LAT "
    "(code-switching) and CS-LAT vs. MIXED (script).")

TEXT[28] = (
    "Table I defines the six conditions. In NATIVE, ROMAN, CS-LAT and MIXED the question frame is one fixed "
    "template (“main rule, date or parameter regarding *X*”) with *X* the topic string; only the "
    "rendering varies. ROMAN and NATIVE render the same Indic frame in Latin and Brahmic script, except in "
    "Hindi, where ROMAN uses *tareekh* and NATIVE *tithi* for “date”. CS-LAT replaces part of the "
    "frame with English words (“main rule”, “date”, “parameter”, and in Hindi "
    "and Bengali also “regarding”), and MIXED writes the remaining Indic words of CS-LAT in native "
    "script. In Hindi, Bengali and Tamil, CS-LAT and MIXED are word-for-word transliterations of each other. "
    "In Telugu and Kannada they are not: the question word is *enti* vs. ఏమిటి (*emiti*) in Telugu and "
    "*yenu* vs. ಯಾವುದು (*yāvudu*, “which”) in Kannada. We report the CS-LAT–MIXED contrast on all "
    "100 propositions, as planned, and on the 60 word-identical ones as a sensitivity analysis. No fluent "
    "speaker has yet rated the naturalness or equivalence of these templates; the templates and a review "
    "protocol are released.")

TEXT[30] = (
    "In the first run (EXP-002) the English prompts used two question templates (“key structural or "
    "operational difference between *X*” and “specific prerequisite condition or timeline applies "
    "to *X*”), while all other conditions used the single generic template. English-versus-Indic "
    "comparisons were therefore confounded with question type, a flaw we found only when auditing the raw "
    "prompt strings. We added EN-MATCH, the generic template in English (100 prompts, same gold answers), "
    "and ran it in a second run (EXP-003) with the same model and decoding settings, without modifying the "
    "earlier results. The two runs did not grade alike: EXP-002 called the judge at temperature 0.3 with the "
    "answering system prompt, EXP-003 at temperature 0 with an evaluator system prompt (Section IV). We "
    "therefore re-graded all 600 outputs with the EXP-003 configuration; all comparisons below use these "
    "harmonised labels and EN-MATCH as the English reference. EN-ORIG and EN-MATCH do not differ detectably "
    "(70% vs. 60%; exact p = 0.10, topic-level p = 0.69).")

TEXT[34] = (
    "**Gold answers.** Each topic has one gold answer, shared by its five language groups and all six "
    "conditions. The benchmark stores an evidence snippet and a source URL with each; the snippets are "
    "template-generated paraphrases rather than quotations, and the URLs point to agency home pages (e.g. "
    "rbi.org.in) rather than to specific documents. The author and, separately, volunteer reviewers known to "
    "the author checked the gold answers for factual correctness against public sources. That check was not "
    "logged item by item, the reviewers were not trained annotators, and no agreement statistic was computed, "
    "so we report it as a check rather than a measurement. For this version we also matched each gold answer "
    "to its governing provision and reviewed it for currency and for completeness relative to the question "
    "actually asked (Appendix A, Table VIII; a per-topic ledger is released). All 20 answers are consistent with "
    "the provision identified. One describes a scheme that has since been replaced (Telangana's Rythu Bandhu, "
    "now Rythu Bharosa). Three are narrower than the generic question allows, so that other correct answers "
    "exist: the GST registration threshold (₹40 lakh applies to suppliers of goods, ₹20 lakh to services), "
    "the MTP Act (two practitioners are required only between 20 and 24 weeks) and the environmental-"
    "clearance public hearing (the gold lists two of several exemptions). Removing these three topics changes "
    "no conclusion (Appendix B). Gold-answer checks establish that the reference is right; they do not show "
    "that the judge grades model answers correctly, which no human has yet assessed on these outputs "
    "(Section VII). Agreement figures in older project documents (e.g. κ = 0.719) concern a different, earlier "
    "pilot whose annotation files are not in the repository, and are not used here.")

TEXT[36] = (
    "Fig. 1 summarizes the pipeline: 100 propositions are rendered in six conditions, answered once by the "
    "primary model under greedy decoding, graded against the gold answer, and analysed at three levels of "
    "clustering. Section VI-B adds a follow-up run with a larger output budget.")

TEXT[37] = (
    "**Models.** The primary model is served by Groq under the API identifier `qwen/qwen3.8-27b`, which is "
    "recorded in every prediction row and in the response metadata of the follow-up. The provider lists it as "
    "an Alibaba Cloud model, and a public checkpoint of that name exists (Qwen/Qwen3.8-27B, 27.8B parameters, "
    "Apache-2.0). That checkpoint's tokenizer reproduces the API's prompt-token counts for all 600 prompts up "
    "to a constant chat-template offset of 48 tokens, and counts 125–128 tokens for responses the API "
    "reports as 128, so the tokenizer is established; whether the provider serves exactly those weights, and "
    "at what numerical precision, we cannot verify. We call the model Qwen3.8-27B. Older project documents "
    "call it “Qwen-2.5-27B” and the repository configuration lists `qwen/qwen3.6-27b`; neither "
    "produced the reported outputs. The second model is ALLaM-2-7B (`allam-2-7b`) [14]. All results are "
    "single-run. Greedy decoding on the hosted API was not fully deterministic: in the follow-up, 84–85% of "
    "512-token responses begin with exactly the 128-token response to the same prompt, and the rest diverge.")

TEXT[38] = (
    "**Prompting and output budget.** Each prompt is sent with the system message “You are a helpful "
    "assistant answering questions from Indian users. Questions may mix an Indian language with English. "
    "Answer factually, accurately, and concisely.” Decoding is greedy (temperature 0, top-p 1) with at "
    "most 128 output tokens in the main runs. The model almost never stops on its own: 598 of 600 responses "
    "used all 128 tokens, and 82–95% end mid-sentence in every condition, English included. The provider's "
    "finish reason was not logged in the main runs; it was logged in the follow-up.")

TEXT[39] = (
    "**Judging.** A judge receives the question as the model saw it, the gold answer and the response, and "
    "returns CORRECT or HALLUCINATED with a short reason (Appendix C). Three label sets exist. *Stored*: the "
    "labels saved with the predictions; EXP-002 obtained them from Qwen3.8-27B at temperature 0.3 with the "
    "answering system prompt (a side effect of reusing the generation client), EXP-003 at temperature 0 with "
    "the system prompt “You are an expert factuality evaluator.” *J-QWEN*: all 600 outputs "
    "re-graded by Qwen3.8-27B with the EXP-003 configuration, the one the study intended; these labels are "
    "the primary analysis. *J-OSS*: the same rubric applied by gpt-oss-120b (`openai/gpt-oss-120b`, "
    "temperature 0, low reasoning effort), a judge from a different model family that did not produce the "
    "answers. J-QWEN reproduces the stored labels on all 100 EN-MATCH items (same configuration) and on "
    "90–94% of items in the other conditions. No judge has been validated against human labels on these "
    "outputs. “Accuracy” below is the share of responses a judge labels CORRECT: a judge-assessed "
    "quantity, not a direct measurement of recall.")

TEXT[40] = (
    "**Statistics.** Observations are nested. A *prompt* is one string sent to the model. A *proposition* is "
    "a fact in one language group, rendered as six paired prompts. A *topic* (e.g. NEFT vs. RTGS) contains "
    "five propositions, one per language, with the same gold answer; across the five matched-template "
    "conditions it contributes 25 prompts. A proposition-level test asks whether the model, given these 100 "
    "facts, does better in one representation than in another. A topic-level test asks whether the "
    "difference should be expected to recur on new topics; with 20 topics it has much less power, but it "
    "matches the generalisation most readers want, so we report both. At the proposition level we use exact "
    "McNemar tests [15] with Holm correction [16] within a pre-specified family of five contrasts: each of "
    "NATIVE, ROMAN, CS-LAT and MIXED against EN-MATCH, and MIXED against CS-LAT. At the topic level we use "
    "an exact sign-flip permutation test over all 2²⁰ sign patterns of the 20 per-topic accuracy differences "
    "and a percentile bootstrap over topics (10,000 resamples, fixed seed), with Holm correction within the "
    "same family. Logistic GEE with independence working correlation and robust covariance clustered at "
    "prompt, proposition and topic level [18] is reported for comparison; with 20 clusters robust standard "
    "errors are anti-conservative [19], [20], so topic-level conclusions do not rest on it. Wilson intervals "
    "[17] are given for single proportions; the design effect is 1 + (*m* − 1)ρ with ρ from the one-way "
    "ANOVA estimator [21]. The follow-up (Section VI-B) has three contrasts, fixed in the analysis script "
    "before its outputs were graded: CS-LAT vs. EN-MATCH and MIXED vs. CS-LAT at 512 tokens, and the change "
    "in each gap from 128 to 512 tokens. Everything else is exploratory. All numbers are recomputed from the "
    "raw files by the scripts in Appendix E.")

TEXT[41] = "V. RESULTS AT A 128-TOKEN BUDGET"

TEXT[43] = (
    "Table II and Fig. 2 give the main result under the harmonised judge. Relative to EN-MATCH (60%), "
    "accuracy is 49% for CS-LAT, 37% for ROMAN, 32% for NATIVE and 26% for MIXED, differences of 11, 23, 28 "
    "and 34 points. At the proposition level the ROMAN, NATIVE and MIXED differences are significant after "
    "Holm correction (adjusted p ≤ 0.002); the CS-LAT difference is not (p = 0.13). With the stored labels, "
    "which graded EN-MATCH and the Indic conditions under different judge settings, the CS-LAT gap was 17 "
    "points (p = 0.014): about a third of it came from the grading difference. The ordering among the three "
    "non-English-script conditions is uncertain: ROMAN vs. MIXED gives p = 0.052 and NATIVE vs. MIXED "
    "p = 0.29 (Table IX).")

TEXT["tab2"] = (
    "Qwen3.8-27B accuracy on the 100 paired propositions at a 128-token budget, harmonised judge (J-QWEN). "
    "Δ: difference in correct answers out of 100 relative to EN-MATCH. Exact p: two-sided exact McNemar; "
    "Holm: within the five primary contrasts (MIXED vs. CS-LAT is in the text and Table IX). Topic p: exact "
    "sign-flip permutation test on the 20 per-topic differences, Holm-adjusted in parentheses. Stored, J-OSS: "
    "accuracy (%) under the original labels and under the cross-family judge. †EN-ORIG vs. EN-MATCH, "
    "exploratory.")

TEXT["fig2"] = (
    "Fig. 2. (a) Accuracy (J-QWEN) with Wilson 95% intervals (n = 100 per condition; points not independent "
    "within topic). (b) Number of languages (of five) in which each topic is answered correctly, per "
    "condition. Topics sorted by EN-MATCH, then EN-ORIG.")

TEXT["fig3"] = "Fig. 3. Accuracy by language and condition (J-QWEN; n = 20 per cell)."

TEXT[53] = (
    "The uncertainty is larger than the Wilson intervals imply. Topic-bootstrap intervals are wider (for "
    "EN-MATCH [40, 80] against Wilson [50.2, 69.1]) because accuracy is concentrated by topic: two topics "
    "(Environment Clearance Public Hearing, IBC Section 7) are wrong in every condition, and twelve are right "
    "for English in all five languages (Fig. 2b). The two all-wrong topics fail for different reasons. For "
    "IBC the model gives the pre-2020 default threshold of ₹1 lakh, a genuine error; for Environment Clearance "
    "the gold answer lists exemptions that the generic question does not ask for (Section III-C).")

TEXT[54] = "B. Mixed vs. Latin-script code-switching"

TEXT[55] = (
    "Writing the code-switched prompt with its Indic words in Brahmic rather than Latin script lowers "
    "accuracy from 49% to 26%, a 23-point drop. Of 37 propositions that differ, 30 favour CS-LAT and 7 favour "
    "MIXED (exact p < 0.001, Holm p < 0.001). The drop appears in all five languages (Fig. 3); the mean of the "
    "20 per-topic differences is 23 points (bootstrap 95% CI [11, 35]; permutation p = 0.004, Holm-adjusted "
    "0.018; 14 of 20 topics differ), and the GEE odds ratio is 0.37 (topic-clustered 95% CI 0.21–0.65). On the "
    "60 propositions in Hindi, Bengali and Tamil, where the two prompts are word-for-word identical, the drop "
    "is 25 points (p = 0.0015; topic-level p = 0.016). Excluding the three topics with narrow gold answers "
    "leaves it at 23.5 points (p < 0.001). Under the stored labels it was 19 points (p = 0.003; topic-level "
    "p = 0.015, Holm-adjusted 0.072). At a 128-token budget, then, the mixed-script penalty is the most "
    "consistent result in the study.")

TEXT["tab3"] = (
    "Logistic GEE (independence working correlation, robust covariance), J-QWEN labels, 128 tokens. β̂ is the "
    "log-odds difference from EN-MATCH (first four blocks, 500 observations) or from CS-LAT (last block, 200). "
    "Topic-level robust SEs with 20 clusters are anti-conservative.")

TEXT[57] = (
    "Section VI shows that this result does not survive a larger output budget. Here we note only why that "
    "check is needed: 88% of MIXED responses are written mostly in Brahmic script, against 2% of CS-LAT "
    "responses, so the prompt script also changes the script of the answer, and with it how much answer fits "
    "into 128 tokens.")

TEXT[59] = (
    "Observations within a topic are strongly dependent. In the five matched-template conditions the "
    "intra-topic correlation is ρ = 0.27, the design effect 7.5 and the effective sample size 67 out of 500. "
    "Table III and Fig. 4a show what this does. For CS-LAT against EN-MATCH, the GEE p value is 0.12 at "
    "prompt level, 0.09 at proposition level and 0.37 at topic level, and the topic-level permutation test "
    "gives p = 0.42 (bootstrap 95% CI for the mean per-topic difference [−34, 13] points). For ROMAN, NATIVE "
    "and MIXED against EN-MATCH the topic-level permutation p values are 0.087, 0.031 and 0.030, and none "
    "survives Holm correction at topic level (smallest adjusted value 0.12). Only MIXED vs. CS-LAT survives "
    "Holm correction at every level (adjusted topic-level p = 0.018). The English-vs-Indic differences are "
    "consistent in direction, but at the level of topics only the larger ones approach significance, and the "
    "English–CS-LAT gap does not.")

TEXT["fig4"] = (
    "Fig. 4. (a) GEE log-odds differences from EN-MATCH (J-QWEN) with robust 95% CIs at three clustering "
    "levels (circle: prompt; square: proposition; diamond: topic). Intervals widen at topic level, where the "
    "CS-LAT and ROMAN intervals include zero. (b) Per-topic accuracy difference, CS-LAT minus MIXED (20 "
    "topics; band: bootstrap 95% CI of the mean; line: mean).")

TEXT[65] = (
    "Accuracy by language is in Fig. 3 and Appendix Table X. MIXED is below CS-LAT in all five languages; "
    "EN-MATCH is above CS-LAT in four and tied with it in Bengali. A permutation test of whether the "
    "condition profile depends on language (statistic: interaction sum of squares of the language × "
    "condition accuracy table; null: language labels permuted among the five propositions of each topic; "
    "10,000 permutations) gives p = 0.17. With 20 observations per cell this test has little power, so we "
    "report no detectable language dependence, not that languages behave alike; Bengali and Telugu differ "
    "visibly in the ROMAN column (20% vs. 50%), and nothing here can separate chance from effect.")

TEXT[66] = (
    "ALLaM-2-7B answers 10% of matched-English questions correctly and 5%, 2%, 2% and 3% in CS-LAT, ROMAN, "
    "NATIVE and MIXED (stored labels), so the representation contrast cannot be measured on it. The "
    "five-condition rank correlation with Qwen3.8-27B under the stored labels (ρ = 0.67, p = 0.22) describes "
    "a floor, not a replication. We make no claim about other model families.")

TEXT[67] = "VI. TOKENIZATION AND THE OUTPUT BUDGET"
TEXT[68] = "A. Input tokenization (exploratory)"

TEXT[69] = (
    "Subword fragmentation is a standard explanation for weaker performance on non-Latin scripts. Our earlier "
    "analysis measured characters per token with the Qwen2.5-7B tokenizer, which does not match the served "
    "model: it disagrees with the API's prompt-token counts and would put capped 128-token responses at "
    "120–305 tokens. With the Qwen3.8-27B tokenizer, which does match (Section IV), Brahmic text is less "
    "fragmented than that analysis implied: prompts average 2.43 characters per token in NATIVE and 3.70 in "
    "MIXED, against 4.65 in EN-MATCH and 4.11 in CS-LAT (previously 1.24 and 2.49 for NATIVE and MIXED). "
    "Within the CS-LAT–MIXED contrast, MIXED lowers characters per token (*a* = −0.41, SE 0.10), but once "
    "condition is controlled the mediator's association with correctness is not significant and has the "
    "wrong sign for a fragmentation account (*b* = −0.40, SE 0.23, p = 0.08; 95% CI −0.85 to 0.05; Sobel "
    "p = 0.11). The implied indirect effect is positive while the total effect is negative (−1.01). Because "
    "characters per token is almost determined by condition and language in this design, the test has "
    "little leverage: it is exploratory and does not rule out a tokenization effect. Across the six "
    "conditions, characters per token and accuracy are rank-correlated (ρ = 0.83), but six points that "
    "differ in language frame, script and answer length identify nothing (Fig. 5c).")

TEXT["fig5"] = (
    "Fig. 5. (a) Mean response length at 128 tokens (solid; labels: % of responses written mostly in Brahmic "
    "script) and, for three conditions, at 512 tokens (hatched). (b) Accuracy of the same 300 prompts at 128 "
    "and 512 tokens, graded by J-QWEN (solid) and J-OSS (dashed). (c) Condition-level prompt characters per "
    "token (Qwen3.8 tokenizer) against accuracy at 128 tokens (six points; descriptive only).")

TEXT[74] = "B. Response script, length and the output budget"

TEXT[75] = (
    "The prompt script largely determines the response script: 98% of NATIVE and 88% of MIXED responses are "
    "written mostly in Brahmic script (more than half of their letters), against 8% and 2% for ROMAN and "
    "CS-LAT and none for English. Brahmic answers cost more tokens per character (2.2–2.4 characters per "
    "token in NATIVE and MIXED responses against 4.1 in English ones), and nearly all responses used the full "
    "128 tokens, so mean response length is 529 characters in EN-MATCH but 279 in NATIVE and 303 in MIXED "
    "(Fig. 5a). Among errors, the share whose judge reason mentions an incomplete or missing answer (a keyword "
    "rule, Appendix C) is 0 of 40 in EN-MATCH, 11 of 51 in CS-LAT, 36 of 68 in NATIVE and 38 of 74 in MIXED. "
    "The rule depends on the judge's wording and does not measure truncation, but it points the same way.")

TEXT[76] = (
    "To separate script from budget we re-ran EN-MATCH, CS-LAT and MIXED (300 prompts) with a 512-token limit "
    "and nothing else changed: same model identifier, system prompt, decoding settings and prompts. Both the "
    "128-token and the 512-token responses were graded by J-QWEN and by J-OSS, so every comparison across "
    "budgets uses one judge. The limit still binds for most code-switched answers (58 of 100 EN-MATCH, 15 "
    "CS-LAT and 5 MIXED responses stopped before 512 tokens), but MIXED responses now average 1,122 "
    "characters, twice what English responses had at 128 tokens. Table IV gives the result. Under J-QWEN, "
    "MIXED rises from 26% to 63% and CS-LAT from 49% to 59%, so the MIXED–CS-LAT gap moves from −23 to +4 "
    "points (p = 0.57 at 512 tokens; change in the gap +27 points, topic-bootstrap CI [7, 45], permutation "
    "p = 0.018). Under J-OSS the gap is −8 points at 128 tokens and −6 at 512, neither significant. On the 60 "
    "word-identical propositions the picture is the same (J-QWEN, 512 tokens: 62% vs. 63%). MIXED with 512 "
    "tokens matches EN-MATCH with 128 (63% vs. 60%, p = 0.77). The English–CS-LAT gap behaves differently: "
    "under J-QWEN it widens to 21 points at 512 tokens (p < 0.001; topic-level p = 0.082), while under J-OSS "
    "it shrinks to 4 points (p = 0.57).")

TEXT["tab4"] = (
    "Output-budget follow-up. The same 300 prompts answered with 128 and 512 tokens; both budgets graded by "
    "the same judge. Accuracy (%); gaps in points, each followed by exact McNemar p / topic-level "
    "permutation p. Last row: responses (EN-MATCH, CS-LAT, MIXED) that stopped before the cap.")

TEXT[77] = (
    "Three conclusions follow. First, the 128-token MIXED penalty is not evidence that script alternation "
    "harms recall: given room, the model states the gold fact about equally often in the mixed-script and "
    "Latin-script code-switched conditions. Its most likely source is that Brahmic-script answers reach the "
    "cap before reaching the fact, and answers a human would call incomplete are then graded as wrong; the "
    "EN-MATCH answer on the MTP Act, for instance, correctly states the one-practitioner rule for the first 20 "
    "weeks, is cut off before the 20–24-week rule, and is graded HALLUCINATED. Second, NATIVE and MIXED behave "
    "alike at 128 tokens (32% and 26%, p = 0.29) although MIXED has five script boundaries per prompt and "
    "NATIVE one, which also argues against a boundary-density account. Third, the English advantage is "
    "unresolved: it persists under one judge and nearly vanishes under the other, which is a question about "
    "the judge (Section VII) as much as about the model.")

TEXT[78] = "VII. JUDGE DEPENDENCE"

TEXT[79] = (
    "The judge matters in three ways. *Configuration.* Our first run graded the Indic conditions at "
    "temperature 0.3 with the answering system prompt and EN-MATCH at temperature 0 with an evaluator prompt. "
    "Harmonising the configuration changed 6–10% of the labels in each re-graded condition and moved CS-LAT "
    "accuracy from 43% to 49%, which is why the stored English–CS-LAT gap (17 points) exceeded the harmonised "
    "one (11). *Family.* J-OSS, which did not produce the answers, is far stricter than the self-judge: on the "
    "128-token outputs it accepts 37% of EN-MATCH answers against 60% for J-QWEN, agrees with J-QWEN on 76% "
    "of items (κ = 0.33–0.62 by condition; Table V), and 128 of the 146 disagreements are answers J-QWEN "
    "accepts and J-OSS rejects. Inspection shows why: J-QWEN often accepts an answer that is on topic and "
    "accurate but does not state the gold fact (for example, one that only names the governing Act), whereas "
    "J-OSS requires the gold fact. The rubric (“judge only factual correctness and whether it actually "
    "addresses the question”) does not settle which is right, and truncated answers make the case "
    "common. *Differential error.* Neither judge has been compared with human labels, so we cannot say which "
    "is closer to a careful reader or whether either is harsher on one script. The two agree more often on "
    "NATIVE, ROMAN and MIXED (79–85%) than on English and CS-LAT (64–73%), so their disagreement is not "
    "concentrated on Brahmic text.")

TEXT["tab5"] = (
    "Judge agreement on the 600 outputs at 128 tokens. Stored vs. J-QWEN: share of identical labels (EN-MATCH "
    "was stored under the J-QWEN configuration). J-QWEN vs. J-OSS: share identical and Cohen's κ.")

TEXT[80] = (
    "Table VI turns the remaining uncertainty into tipping points. Assuming English answers are judged without "
    "error, it gives the sensitivity the judge would need on the comparison condition for that condition's "
    "true accuracy to equal the reference's. A correction applied equally to both conditions (the "
    "Rogan–Gladen estimator [22]) divides a gap by TPR − FPR and can only enlarge it, so a common-error grid "
    "cannot show robustness; the relevant threat is differential error. At a false-accept rate of 0.08, "
    "erasing the CS-LAT gap would need a judge that rejects 24% of truly correct CS-LAT answers "
    "(sensitivity 0.76), and erasing the MIXED gap one that rejects 62% (0.38). These are hypothetical error "
    "rates, not estimates of the judge's actual errors, which are unknown; the cross-family disagreement "
    "shows they are not small. A crude check agrees: on the 330 outputs whose gold answer contains numerals, "
    "the J-QWEN label matches whether all gold numerals appear in the response 67% of the time, with "
    "disagreements in both directions (73 accepted answers lack the figure; 35 rejected ones contain it).")

TEXT["tab6"] = (
    "Sensitivity the judge would need on the comparison condition for its true accuracy to equal the "
    "reference condition's, at the given false-accept rate (J-QWEN, 128 tokens). Reference answers assumed "
    "judged without error. Lower entries mean a larger error would be needed.")

TEXT[83] = (
    "What the data support is narrower than the design promised. For this model, these 20 topics and a "
    "128-token budget, restating a question in Romanized or Brahmic script, or as code-switched text, lowers "
    "the share of answers a judge accepts, and mixed script is lowest. Quadrupling the budget removes the "
    "mixed-script penalty relative to Latin-script code-switching under both judges, and MIXED then does as "
    "well as English did at 128 tokens. The parsimonious reading is that much of the representation effect "
    "at 128 tokens reflects how much answer fits into the budget in the response script, not comprehension "
    "of the prompt. Whether an English advantage remains once answers can be completed depends on the judge, "
    "and topic-level evidence for it is weak in every analysis.")

TEXT[84] = (
    "The practical lesson is methodological. Output caps are often set low to save cost, and tokenizers make "
    "some scripts more expensive per character; a shared cap then gives answers in those scripts less room. "
    "Studies that compare languages or scripts through generated answers should report how often the cap "
    "binds in each condition and check that conclusions survive a larger cap; judges should be configured "
    "identically across conditions, and at least one should come from a family other than the evaluated "
    "model's. Table VII lists claims we examined and could not support.")

TEXT["tab7"] = "Claims examined and not supported."

TEXT[87] = (
    "**Topics.** Twenty topics with heavy within-topic concentration bound what any statistic can show "
    "(effective n ≈ 67 of 500). A 25-proposition expansion has been written but not evaluated; its design "
    "power (Appendix D) is a projection. **Output budget.** Even 512 tokens bound most code-switched answers; "
    "we have not run an uncapped condition or one that fixes the answer language, and we re-ran three of the "
    "six conditions. **Judges.** Two LLM judges that disagree on a quarter of items, and no human labels on "
    "any output; a stratified, blinded sample of 210 outputs and an annotation protocol are prepared but not "
    "yet annotated. **Questions and gold answers.** One generic template that under-specifies the target for "
    "several topics; gold answers checked by the author and volunteers without an item-level record; one "
    "superseded scheme. **Prompts.** No fluent-speaker validation of naturalness or equivalence; CS-LAT and "
    "MIXED differ by one word in Telugu and Kannada, and Hindi ROMAN is not a transliteration of Hindi "
    "NATIVE. **Models and languages.** One informative model, whose served weights we cannot verify, and five "
    "languages. **Single run.** No repeated sampling; hosted greedy decoding was not fully deterministic, and "
    "API behaviour can change over time.")

TEXT[89] = (
    "Evaluations like this one guide where civic and legal information systems are considered safe to deploy "
    "for speakers who write the way our conditions do. Overstated gaps could discourage building for these "
    "users; understated ones could hide failures. We therefore report effect sizes with their dependence on "
    "clustering, output budget and judge. The prompts contain no personal data. The benchmark contains legal "
    "and policy facts that become outdated (one already has) and should not be used as legal advice. We do "
    "not estimate how many people use each representation, and make no claim about it.")

TEXT[91] = (
    "All numbers, tables and figures are produced from the raw files by `paper_v2/scripts/make_all.py` "
    "(128-token analyses; `--labels jqwen` for the harmonised labels), `analyze_exp004.py` (re-grading and "
    "budget follow-up) and `make_figures.py` (Appendix E). The follow-up cost $1.10 at the provider's list "
    "prices in October 2026. The project's budget ledger records $0.21 for all earlier runs, but it priced "
    "every call at a flat $0.08 per million tokens; at current list prices the Qwen3.8-27B generation and "
    "grading in EXP-002 and EXP-003 alone would cost about $2.1. The provider's billing record is the "
    "authoritative figure.")

TEXT[94] = (
    "Table VIII lists the 20 topics, the provision against which each gold answer was reviewed, the outcome of "
    "that review, and the number of languages (of five) in which each condition was answered correctly under "
    "J-QWEN. Topics are Indian public-policy and regulatory subjects, several comparing two schemes or "
    "institutions (e.g. NEFT vs. RTGS, Covaxin vs. Covishield, PSLV vs. GSLV Mk III); not all are statutes, "
    "so we call them public-policy topics. Gold column: *ok*, consistent and adequate; *simpl.*, a correct "
    "simplification; *narrow*, other correct answers to the generic question exist; *dated*, the scheme has "
    "been superseded.")

TEXT["tab9"] = (
    "Topics, provision used to review the gold answer, review outcome, and languages (of five) answered "
    "correctly per condition (Qwen3.8-27B, J-QWEN, 128 tokens).")

TEXT["appB"] = (
    "Excluding the three topics with narrow gold answers (GST, MTP Act, Environment Clearance; 85 "
    "propositions), the J-QWEN differences from EN-MATCH are −12 (CS-LAT, p = 0.16), −25 (ROMAN, p = 0.002), "
    "−32 (NATIVE, p < 0.001) and −35 points (MIXED, p < 0.001), and MIXED vs. CS-LAT is −23.5 points "
    "(p < 0.001; topic-level p = 0.007).")

TEXT["tab10"] = (
    "All pairwise contrasts, J-QWEN labels, 128 tokens (proposition-level exact McNemar; b: the second-named "
    "(reference) condition correct and the first wrong; c: the reverse; topic-level permutation p and "
    "bootstrap CI for the change, uncorrected). The first five rows are the primary family.")

TEXT["tab11"] = "Correct answers by language and condition, as percentages (J-QWEN; n = 20 per cell)."
TEXT["tab12"] = (
    "Correct answers out of 100 per model and condition, 128 tokens. ALLaM-2-7B has stored labels only; its "
    "Indic conditions were graded under the EXP-002 judge setting and EN-MATCH under the EXP-003 setting.")
TEXT["tab13"] = (
    "Response- and prompt-side descriptors by condition (Qwen3.8-27B, 128 tokens). Script transitions: "
    "Latin ↔ Brahmic changes between adjacent words in the prompt. Chars/tok: prompt characters per token, "
    "Qwen3.8-27B tokenizer. Brahmic: % of responses mostly in Brahmic script. Errors and Incompl.: J-QWEN "
    "labels and reasons; Incompl. is the keyword rule of Appendix C.")

TEXT[110] = (
    "**Incompleteness rule.** A response is flagged when (i) it used the full 128 completion tokens, (ii) its "
    "last non-space character is not a sentence-final mark, (iii) the judge labelled it incorrect, and (iv) "
    "the judge's reason matches one of *incomplete, truncated, cut off, abrupt, unfinished, missing specific, "
    "missing parameter, fails to finish*. Condition (iv) depends on the judge's wording; the rule is a "
    "descriptive device, not a measure of truncation. **Judge prompt.** “You are grading whether a "
    "model's ANSWER to a user QUESTION is factually correct. You are given a trusted GOLD answer. The answer "
    "may mix an Indian language with English (code-switching) and may be phrased very differently from the "
    "gold—that is fine. Judge ONLY factual correctness and whether it actually addresses the question.” "
    "Output: `VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>`. **Judge settings.** Stored, "
    "EXP-002: Qwen3.8-27B, temperature 0.3, at most 256 tokens, system prompt “You are a helpful "
    "assistant answering questions from Indian users. Questions may mix an Indian language with English "
    "(code-switching). Answer accurately and concisely in the same mixed style the user used.” Stored, "
    "EXP-003, and J-QWEN: temperature 0, top-p 1, at most 256 tokens, system prompt “You are an expert "
    "factuality evaluator.” J-OSS: gpt-oss-120b, temperature 0, top-p 1, low reasoning effort, at most "
    "1,024 tokens, same system prompt. All 1,800 follow-up judgements were parsed. **Script transitions.** "
    "Words are maximal letter runs, each labelled Latin or Brahmic (U+0900–U+0DFF); transitions are label "
    "changes between consecutive words, giving 5.0 per MIXED prompt, 1.0 per NATIVE prompt (the Latin topic "
    "string) and 0 elsewhere. **Mostly Brahmic.** More than half of a response's letters and combining marks "
    "lie in U+0900–U+0DFF. **Templates.** All 20 Indic templates are listed in the released prompt-validation "
    "protocol.")

TEXT[112] = (
    "A normal-approximation calculation for a 45-topic design (225 paired propositions, design effect "
    "1 + (5 − 1)ρ, binary variance at p̄ = 0.4, two-sided α = 0.05) with ρ = 0.2663 and a 21-point effect "
    "gives power 88.6% (minimum detectable effect 18.6 points); the same formula gives 55.9% for the 20 "
    "evaluated topics. Those parameters come from the first English template and the stored labels. With "
    "the harmonised labels (ρ = 0.27) the 11-point English–CS-LAT gap would have power 38% with 45 topics and "
    "19% with 20, and a 23-point gap 93% and 63%. The formula ignores pairing and is a rough projection; the "
    "25 new propositions have not been evaluated.")

TEXT[114] = (
    "Python 3.11 with numpy, pandas, scipy, statsmodels, tokenizers and matplotlib. From the repository root, "
    "`python paper_v2/scripts/make_all.py` (stored labels) and `make_all.py --labels jqwen` read the two "
    "prediction files and write `paper_v2/output/numbers_*.json`; `python scripts/run_exp004_budget_rejudge.py "
    "--stage gen|judge` produced the follow-up (Groq key required; outputs, finish reasons and a spend log in "
    "`results/EXP-004-budget-rejudge/`); `analyze_exp004.py` and `make_figures.py` write the remaining "
    "numbers and Figs. 2–5. The tokenizer check downloads the Qwen/Qwen2.5-7B and Qwen/Qwen3.8-27B tokenizers. "
    "Sign-flip tests enumerate all 2²⁰ patterns; bootstraps and the language permutation use fixed seeds. "
    "Topic-level p values in an earlier draft were Monte Carlo approximations and differ from the exact values "
    "here in the third decimal. That draft's language-dependence p value (0.15) and numeral check (60% "
    "agreement) could not be reproduced because the script that produced them was not in the repository; "
    "they are replaced by the procedures described above.")

NEW_REFS = [
    "J. Husain *et al.*, “RomanSetu: Efficiently unlocking multilingual capabilities of large language "
    "models via Romanization,” in *Proceedings of the 62nd annual meeting of the association for "
    "computational linguistics*, 2024.",
    "P. Wang *et al.*, “Large language models are not fair evaluators,” in *Proceedings of the 62nd "
    "annual meeting of the association for computational linguistics*, 2024.",
    "Y. Dubois, B. Galambosi, P. Liang, and T. B. Hashimoto, “Length-controlled AlpacaEval: A simple way "
    "to debias automatic evaluators,” *arXiv preprint arXiv:2404.04475*, 2024.",
]

PROVISION = {
    "Citizenship Amendment Act Cut-off": ("Citizenship (Amendment) Act 2019, s. 2", "ok"),
    "Companies Act CSR Mandate": ("Companies Act 2013, s. 135(1)", "ok"),
    "Covaxin vs Covishield": ("CDSCO approvals, Jan. 2021", "ok"),
    "GST Registration Exemption": ("CGST Act s. 22; Notif. 10/2019-CT", "narrow"),
    "Kharif vs Rabi Rice": ("ICAR crop-season references", "simpl."),
    "Lok Sabha vs Rajya Sabha Money Bill": ("Constitution, Arts. 109–110", "ok"),
    "National Park vs Wildlife Sanctuary": ("Wild Life (Protection) Act 1972, ss. 33, 35", "ok"),
    "Patents Act Compulsory License": ("Patents Act 1970, s. 84(1)", "ok"),
    "SEBI Insider Trading Pre-Clearance": ("SEBI PIT Regulations 2015, Sch. B", "ok"),
    "ISRO PSLV vs GSLV Mk III": ("ISRO launcher specifications", "ok"),
    "Arbitration Act Time Limit": ("Arbitration Act 1996, s. 29A", "ok"),
    "PMFBY vs WBCIS": ("PMFBY/RWBCIS operational guidelines", "ok"),
    "Classical Tamil vs Sanskrit Grammar": ("Philological references", "ok"),
    "Medical Termination of Pregnancy Act": ("MTP Act 1971 (am. 2021), s. 3(2)", "narrow"),
    "NEFT vs RTGS": ("RBI NEFT/RTGS directions", "ok"),
    "RTI Third Party Information": ("RTI Act 2005, s. 11(1)", "ok"),
    "Environment Clearance Public Hearing": ("EIA Notification 2006, para. 7", "narrow"),
    "IBC Section 7 Default Threshold": ("IBC 2016, s. 4 (₹1 crore from 2020)", "ok"),
    "PM-KISAN vs Rythu Bandhu": ("PM-KISAN guidelines; Telangana G.O.s", "dated"),
    "Supreme Court vs High Court Writ Jurisdiction": ("Constitution, Arts. 32, 226", "ok"),
}


def by_cmp(N, cmp_, ref):
    return next(c for c in N["contrasts"] if c["cmp"] == cmp_ and c["ref"] == ref)


def set_col_widths(table, widths_in: list[float]):
    from docx.oxml.ns import qn
    grid = table._tbl.tblGrid.gridCol_lst
    for g, w in zip(grid, widths_in):
        g.set(qn("w:w"), str(int(w * 1440)))
    for row in table.rows:
        for c, w in zip(row.cells, widths_in):
            c.width = Emu(int(w * 914400))


def main():
    d = docx.Document(SRC)
    P = list(d.paragraphs)
    T = list(d.tables)

    # ---------- front matter ----------
    set_par(P[0], TEXT["title"])
    set_par(P[4], "")
    add_runs(P[4], "Abstract—", bold=True, italic=True)
    add_runs(P[4], TEXT["abstract"], bold=True)
    set_par(P[5], "")
    add_runs(P[5], "Index Terms—", bold=True, italic=True)
    add_runs(P[5], TEXT["index"], bold=True)

    for i in [9, 13, 14, 15, 18, 19, 20, 28, 30, 34, 36, 37, 38, 39, 40, 41, 43, 53, 54, 55, 57, 59, 65, 66,
              67, 68, 69, 74, 75, 76, 77, 78, 79, 80, 83, 84, 87, 89, 91, 94, 110, 112, 114]:
        set_par(P[i], TEXT[i])
    for i, key in [(23, "fig1"), (49, "fig2"), (52, "fig3"), (62, "fig4"), (72, "fig5")]:
        set_par(P[i], TEXT[key])

    # ---------- Table I caption ----------
    set_caption(P[11], "TABLE I", TEXT["tab1"])

    # ---------- Table II (accuracy, J-QWEN) ----------
    set_caption(P[45], "TABLE II", TEXT["tab2"])
    acc = NJ["accuracy"]
    rows = []
    for c in L6:
        a = acc[c]
        k = a["k"]
        wl, wh = a["wilson"]
        bl, bh = a["topic_boot_ci"]
        st = NO["accuracy"][c]["k"]
        oss = NE["orig128"]["J-OSS"]["accuracy"][c]
        if c == "EN-MATCH":
            row = [c, f"{k:.1f} ({k}/100)", f"[{wl:.1f}, {wh:.1f}]", f"[{bl:.0f}, {bh:.0f}]", "ref.", "–", "–", "–"]
        elif c == "EN-ORIG":
            x = by_cmp(NJ, "EN-MATCH", "EN-ORIG")
            row = [c, f"{k:.1f} ({k}/100)", f"[{wl:.1f}, {wh:.1f}]", f"[{bl:.0f}, {bh:.0f}]",
                   f"{sgn(k - 60)}†", fp(x["p_exact"]), "–", fp(x["topic_perm_p"])]
        else:
            x = by_cmp(NJ, c, "EN-MATCH")
            row = [c, f"{k:.1f} ({k}/100)", f"[{wl:.1f}, {wh:.1f}]", f"[{bl:.0f}, {bh:.0f}]", sgn(k - 60),
                   fp(x["p_exact"]), fp(x["holm_exact"]), f"{fp(x['topic_perm_p'])} ({fp(x['holm_topic'])})"]
        rows.append(row + [f"{st}", f"{oss:.0f}"])
    t2 = T[1]
    add_column(t2, "Stored", [""] * 6)
    add_column(t2, "J-OSS", [""] * 6)
    fill_table(t2, rows, header=["Condition", "Acc. (%)", "Wilson CI", "Topic-boot. CI", "Δ", "Exact p",
                                 "Holm p", "Topic p (Holm)", "Stored", "J-OSS"])
    set_col_widths(t2, [0.75, 0.85, 0.85, 0.75, 0.45, 0.8, 0.8, 0.95, 0.5, 0.5])

    # ---------- Table III (GEE, J-QWEN) ----------
    set_caption(P[56], "TABLE III", TEXT["tab3"])
    g = NJ["gee"]
    rows = []
    for c in ["CS-LAT", "ROMAN", "NATIVE", "MIXED"]:
        for u, lab in [("prompt", "prompt (500)"), ("proposition", "proposition (100)"), ("topic", "topic (20)")]:
            x = g[c][u]
            rows.append([f"{c} vs. EN-MATCH" if u == "prompt" else "", lab, neg(f"{x['beta']:.3f}"),
                         f"{x['se_robust']:.3f}", fp(x["p"])])
    for u, lab in [("prompt", "prompt (200)"), ("proposition", "proposition (100)"), ("topic", "topic (20)")]:
        x = g["MIXED_vs_CS-LAT"][u]
        rows.append(["MIXED vs. CS-LAT" if u == "prompt" else "", lab, neg(f"{x['beta']:.3f}"),
                     f"{x['se_robust']:.3f}", fp(x["p"])])
    fill_table(T[2], rows, header=["Contrast", "Clustering unit (#)", "β̂", "SE", "p"])

    # ---------- Table IV (new): budget follow-up, after P[76] ----------
    B = NE["budget"]
    cap = P[81]  # old Table IV caption paragraph used as a template for new captions
    c4 = insert_after(P[76], cap)
    set_caption(c4, "TABLE IV", TEXT["tab4"])
    t4 = copy_table_after(c4, T[3])
    add_column(t4, "", [""] * 5)

    def gap(jn, budget, cmp_, ref):
        x = next(c for c in B[jn][f"contrasts_{budget}"] if c["cmp"] == cmp_ and c["ref"] == ref)
        pe = "<.001" if x["p_exact"] < 0.001 else fp(x["p_exact"]).lstrip("0")
        pt = "<.001" if x["topic_perm_p"] < 0.001 else fp(x["topic_perm_p"]).lstrip("0")
        return sgn(x["delta_pp"]), f"{pe} / {pt}"

    rows = []
    for c in ["EN-MATCH", "CS-LAT", "MIXED"]:
        rows.append([c] + [f"{B[j]['accuracy'][c][b]:.0f}" for j in ["J-QWEN", "J-OSS"] for b in ["128", "512"]])
    for lab, cmp_, ref in [("CS-LAT − EN-MATCH", "CS-LAT", "EN-MATCH"), ("MIXED − CS-LAT", "MIXED", "CS-LAT")]:
        gs = [gap(j, b, cmp_, ref) for j in ["J-QWEN", "J-OSS"] for b in ["128", "512"]]
        rows.append([lab] + [g_[0] for g_ in gs])
        rows.append(["   p exact / topic"] + [g_[1] for g_ in gs])
    G = NE["gen512_descriptives"]
    stop512 = ", ".join(str(G[c]["finished_stop"]) for c in ["EN-MATCH", "CS-LAT", "MIXED"])
    rows.append(["Stopped before cap", "0, 1, 0", stop512, "0, 1, 0", stop512])
    fill_table(t4, rows, header=["", "J-QWEN 128", "J-QWEN 512", "J-OSS 128", "J-OSS 512"])
    set_col_widths(t4, [1.15, 0.59, 0.59, 0.59, 0.59])

    # ---------- Table V (new): judge agreement, after P[79] ----------
    c5 = insert_after(P[79], cap)
    set_caption(c5, "TABLE V", TEXT["tab5"])
    t5 = copy_table_after(c5, T[3])
    A = NE["agreement_orig128"]
    fill_table(t5, [[c, f"{A[c]['stored_vs_jqwen']:.2f}", f"{A[c]['jqwen_vs_joss']:.2f}",
                     f"{A[c]['kappa_jqwen_joss']:.2f}"] for c in L6],
               header=["Condition", "Stored vs. J-QWEN", "J-QWEN vs. J-OSS", "κ"])

    # ---------- Table VI (old IV): tipping points, J-QWEN ----------
    set_caption(P[81], "TABLE VI", TEXT["tab6"])
    tp = NJ["tipping"]
    fill_table(T[3], [[f, f"{tp['CS-LAT_vs_EN-MATCH'][f]:.2f}", f"{tp['MIXED_vs_EN-MATCH'][f]:.2f}",
                       f"{tp['MIXED_vs_CS-LAT'][f]:.2f}"] for f in ["0.00", "0.04", "0.08", "0.12", "0.16"]],
               header=["FPR", "CS-LAT vs. EN-MATCH", "MIXED vs. EN-MATCH", "MIXED vs. CS-LAT"])

    # ---------- Table VII (old V): claims ----------
    set_caption(P[85], "TABLE VII", TEXT["tab7"])
    fill_table(T[4], [
        ["Script alternation (CS-LAT → MIXED) lowers recall", "Not supported: gap +4 at 512 tokens (p = 0.57); n.s. under J-OSS"],
        ["English advantage over CS-LAT at topic level", "Not supported (topic p ≥ 0.08 in all analyses)"],
        ["Prompt token fertility mediates CS-LAT → MIXED", "Not detected (p = 0.08, wrong sign; exploratory)"],
        ["Language dependence of the profile", "Not detected (p = 0.17), low power"],
        ["Rank agreement with ALLaM-2-7B", "Uninformative (floor; ρ = 0.67, p = 0.22)"],
        ["Errors rise with script transitions", "Not supported (NATIVE ≈ MIXED)"],
        ["Original 20-fold truncation ratio", "Not reproducible from files"],
    ], header=["Examined claim", "Outcome"])

    # ---------- Appendix A: Table IX (old VI) topics + provisions ----------
    set_caption(P[96], "TABLE VIII", TEXT["tab9"])
    t9 = T[5]
    add_column(t9, "", [""] * 20)
    add_column(t9, "", [""] * 20)
    topics = sorted(NJ["by_topic"], key=lambda t: (-NJ["by_topic"][t]["EN-MATCH"], -NJ["by_topic"][t]["EN-ORIG"], t))
    rows = [[t, PROVISION[t][0], PROVISION[t][1]] + [str(NJ["by_topic"][t][c]) for c in L6] for t in topics]
    fill_table(t9, rows, header=["Topic", "Provision reviewed", "Gold"] + L6)
    set_col_widths(t9, [1.75, 1.95, 0.45, 0.5, 0.55, 0.45, 0.45, 0.45, 0.45])

    # ---------- Appendix B ----------
    pb = insert_after(P[100], P[99])
    set_par(pb, TEXT["appB"])
    set_caption(P[102], "TABLE IX", TEXT["tab10"])
    order = [("CS-LAT", "EN-MATCH"), ("ROMAN", "EN-MATCH"), ("NATIVE", "EN-MATCH"), ("MIXED", "EN-MATCH"),
             ("MIXED", "CS-LAT"), ("EN-MATCH", "EN-ORIG"), ("MIXED", "ROMAN"), ("MIXED", "NATIVE"),
             ("ROMAN", "CS-LAT"), ("NATIVE", "CS-LAT"), ("NATIVE", "ROMAN")]
    rows = []
    for cmp_, ref in order:
        x = by_cmp(NJ, cmp_, ref)
        lo, hi = x["topic_boot_ci_pp"]
        rows.append([f"{cmp_} vs. {ref}", sgn(x["delta_pp"]), str(x["b"]), str(x["c"]), fp(x["p_exact"]),
                     fp(x["topic_perm_p"]), neg(f"[{lo:.0f}, {hi:.0f}]")])
    fill_table(T[6], rows, header=["Contrast", "Δ (pp)", "b", "c", "Exact p", "Topic p", "Topic 95% CI (pp)"])
    set_caption(P[104], "TABLE X", TEXT["tab11"])
    names = [("Hindi", "hi"), ("Bengali", "bn"), ("Tamil", "ta"), ("Telugu", "te"), ("Kannada", "kn")]
    rows = [[n] + [f"{NJ['by_language'][k][c]:.0f}" for c in L6] for n, k in names]
    rows.append(["All"] + [str(NJ["accuracy"][c]["k"]) for c in L6])
    fill_table(T[7], rows, header=["Language"] + L6)
    set_caption(P[105], "TABLE XI", TEXT["tab12"])
    t12 = T[8]
    add_column(t12, "", [""] * 6)
    rows = [[c, str(NO["accuracy"][c]["k"]), str(NJ["accuracy"][c]["k"]), str(NO["allam"][c]["k"]),
             f"[{NO['allam'][c]['wilson'][0]:.1f}, {NO['allam'][c]['wilson'][1]:.1f}]"] for c in L6]
    fill_table(t12, rows, header=["Condition", "Qwen stored", "Qwen J-QWEN", "ALLaM-2-7B", "ALLaM 95% CI"])
    set_caption(P[107], "TABLE XII", TEXT["tab13"])
    R = NJ["response"]
    cpt = NJ["tokenizer_check"]["Qwen3.8-27B"]["cpt_by_condition"]
    rows = [[c, f"{R[c]['prompt_script_transitions']:.1f}", f"{cpt[c]:.2f}", f"{R[c]['mean_chars']:.0f}",
             f"{R[c]['brahmic_majority_pct']:.0f}", str(R[c]["errors"]), str(R[c]["incomplete_rule"])] for c in L6]
    fill_table(T[9], rows, header=["Condition", "Script trans.", "Chars/tok", "Resp. chars", "Brahmic (%)",
                                   "Errors", "Incompl."])

    # ---------- References ----------
    last = P[137]
    for k, ref in enumerate(NEW_REFS, start=23):
        newp = insert_after(last, last)
        add_runs(newp, f"[{k}]\t" + ref)
        last = newp

    # ---------- Figures ----------
    media = {"rId21": "fig1.png", "rId30": "fig2.png", "rId33": "fig3.png", "rId38": "fig4.png", "rId44": "fig5.png"}
    for rel in d.part.rels.values():
        if rel.reltype.endswith("/image") and rel.rId in media:
            rel.target_part._blob = (ROOT / "paper_v2/output" / media[rel.rId]).read_bytes()

    for para in d.paragraphs:
        if para.text.startswith("TABLE ") or para.text.startswith("Fig. "):
            para.paragraph_format.keep_with_next = para.text.startswith("TABLE ")
    # document properties
    d.core_properties.title = TEXT["title"]
    OUTDOC.parent.mkdir(parents=True, exist_ok=True)
    d.save(OUTDOC)
    _fix_custom_abstract(OUTDOC, TEXT["abstract"])
    print("wrote", OUTDOC)


def _fix_custom_abstract(path: Path, abstract: str):
    """docProps/custom.xml carries a copy of the abstract (pandoc metadata); keep it in sync."""
    import re
    import shutil
    import zipfile
    from xml.sax.saxutils import escape
    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/custom.xml":
                txt = data.decode("utf-8")
                txt = re.sub(r'(name="abstract"><vt:lpwstr>).*?(</vt:lpwstr>)',
                             lambda m: m.group(1) + escape(abstract.replace("*", "")) + m.group(2), txt, flags=re.S)
                data = txt.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)


if __name__ == "__main__":
    main()
