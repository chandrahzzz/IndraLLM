# IndraLLM — Manuscript Build Guide (10-page IEEE version)

> **Superseded in part (2026-10-10).** This guide was written before the 1,024-token experiment
> (EXP-005). Its 128- and 512-token numbers remain correct, but the sentence "the English–CS-LAT gap is
> not significant at the topic level in any analysis" is no longer true: under J-QWEN at 1,024 tokens it
> is −24 points, topic p = 0.018. For the final text, the three-budget tables and the judge-agreement
> results, use `paper_v2/FULL_REVISION_REPORT.md` (Part G) and `paper_v2/scripts/build_paper.py`.

This file contains everything you need to build the revised manuscript yourself:
the page plan, final text for every section, every table with its exact values,
every figure (file + caption), a registry of every number with its source file,
what was implemented in the repository, and what must not be claimed.

All numbers below were produced by the scripts in `paper_v2/scripts/` from the raw
prediction and judgement files. You can regenerate any of them (Section 11).

Conventions used throughout:

* Condition names are written in small caps in the paper: EN-ORIG, EN-MATCH, CS-LAT,
  ROMAN, NATIVE, MIXED (in Word: lowercase text + Font ▸ Small caps).
* Model name in the text: **Qwen3.8-27B**; API identifier `qwen/qwen3.8-27b`
  (monospace). Never "Qwen-27B", never "Qwen-2.5-27B".
* Judges: **J-QWEN** (Qwen3.8-27B, temperature 0, evaluator system prompt — the primary
  labels), **J-OSS** (gpt-oss-120b), **stored** (labels saved with the original runs).
* "Accuracy" always means *judge-assessed accuracy* (share of responses a judge labels
  CORRECT). Do not call it "factual recall".
* p-values: two decimals if ≥ 0.1, three decimals if 0.001–0.1, scientific below 0.001
  (in text "p < 0.001" is fine).

---

## 0. What changed and why (one-paragraph summary for you)

The original manuscript's central claim — that writing code-switched Indic words in
Brahmic script (MIXED) instead of Latin script (CS-LAT) lowers factual accuracy — does not
survive two checks. (1) Every original response was cut off at 128 output tokens, and
Brahmic answers fit about half as many characters into that budget. Rerunning EN-MATCH,
CS-LAT and MIXED with 512 tokens removes the MIXED–CS-LAT gap (J-QWEN: 59% vs 63%, p = 0.57).
(2) The original runs graded the Indic conditions with the judge at temperature 0.3 and
EN-MATCH at temperature 0; re-grading all 600 outputs with one configuration shrinks the
English–CS-LAT gap from 17 to 11 points (no longer significant). A second, cross-family
judge (gpt-oss-120b) agrees with the self-judge on only 76% of outputs and finds no
significant MIXED–CS-LAT gap even at 128 tokens. The paper is therefore reframed as a
methods result: representation effects measured with a binding output budget and a single
self-judge are unreliable; the design, analysis and corrections are the contribution.

---

## 1. Page plan (IEEE conference template, two columns, 10 pages total)

| Page | Content |
|---|---|
| 1 | Title, author, abstract (≤ 250 words), index terms, §I Introduction (start) |
| 2 | §I (rest): Table I (full width, top), research questions, contributions, findings; §II Related work |
| 3 | Fig. 1 (full width, top); §III Benchmark and design (A, B, C) |
| 4 | §IV Experimental setup (models, prompting, judging, statistics) |
| 5 | §V Results at 128 tokens: Table II (full width), Fig. 2 (full width) |
| 6 | §V-B, §V-C, §V-D; Fig. 3 (one column); Fig. 4 (full width) |
| 7 | §VI Tokenization and output budget: Fig. 5 (full width), Table III (one column, budget) |
| 8 | §VII Judge dependence: Table IV (agreement, one column), Table V (tipping, one column); §VIII Discussion; Table VI (claims, one column) |
| 9 | §IX Limitations; §X Ethics; Reproducibility; References |
| 10 | Appendix A (Table VII topics + provisions, full width), Appendix B (Table VIII pairwise, Table IX GEE), Appendix C (rubric, judge settings), Appendix D (design calculation), Appendix E (reproducibility) |

How to stay at 10 pages (compared with the 13-page draft):

* Do **not** include separate tables for per-language accuracy, model comparison, or
  response descriptors. Fig. 3 shows per-language accuracy; the ALLaM numbers and the
  response descriptors are stated in the text (values in §8 below).
* Move the GEE table to Appendix B (it is a robustness check, not a primary result).
* Keep figures at the sizes of the original draft: Fig. 1 5.8 × 2.9 in, Fig. 2 5.8 × 2.65 in,
  Fig. 3 3.4 × 2.75 in (single column), Fig. 4 5.8 × 2.45 in, Fig. 5 5.8 × 2.3 in.
* Table captions above tables ("TABLE I" on its own line, caption below it, centered);
  figure captions below figures ("Fig. 1." + caption). Keep each table caption with its
  table (Word: Paragraph ▸ Line and Page Breaks ▸ Keep with next).
* Body 10 pt Times; tables and captions 8 pt; references 8 pt.
* Final table numbering in this 10-page plan: I prompts, II accuracy, III budget follow-up,
  IV judge agreement, V tipping points, VI claims not supported, VII topics (App. A),
  VIII pairwise contrasts (App. B), IX GEE (App. B). The text below already uses this
  numbering.

---

## 2. Title, author, abstract, index terms

**Title**

> Representation Effects in Indic Factual Question Answering: Script, Output Budget, and Judge Dependence

**Author block** (unchanged): Chandrahas Reddy · Independent researcher · kurkurrereddy@gmail.com
(For ACL/EMNLP review, remove the author block — anonymous submission.)

**Abstract** (240 words)

> Cross-lingual factuality comparisons usually change a question's content or phrasing along with its language, so a drop in accuracy has no single cause. We hold the proposition fixed and vary only its representation. We build paired prompts for 100 propositions on 20 Indian public-policy topics in five Indic languages (Hindi, Bengali, Tamil, Telugu, Kannada), each rendered in English, native script, Romanized text, Latin-script code-switching (CS-LAT) and mixed-script code-switching (MIXED). With Qwen3.8-27B, greedy decoding, a 128-token output cap and one judge configuration for all conditions, judge-assessed accuracy is 60% for a template-matched English prompt and 49%, 37%, 32% and 26% for CS-LAT, Romanized, native-script and MIXED prompts; MIXED is 23 points below CS-LAT (exact McNemar p < 0.001; topic-level permutation p = 0.004). Two checks change how this should be read. Almost every response reached the cap, and Brahmic-script prompts elicit Brahmic-script answers that fit about half as many characters into it; with a 512-token cap the CS-LAT–MIXED gap disappears (+4 points, p = 0.57). A judge from another model family agrees with the self-judge on 76% of outputs and finds no significant CS-LAT–MIXED gap even at 128 tokens. The English–CS-LAT gap is not significant at the topic level in any analysis. For this model and benchmark, the apparent cost of script alternation is mainly an output-budget effect; representation effects should be measured with non-binding output budgets and more than one judge. Prompts, outputs, judgements, a gold-answer ledger and code are released.

**Index Terms** — factual question answering, code-switching, script, Indic languages, output length, LLM-as-a-judge, paired evaluation, cluster-robust inference

---

## 3. Section-by-section final text

Paste these paragraphs as written. Bold run-in headings are marked `**...**`; italics `*...*`.

### I. INTRODUCTION

**¶1 (keep from original draft, unchanged)**

> A farmer who wants to know whether crop insurance under PMFBY pays out on measured yield loss or on a weather index can type that question in at least five ways: in English; entirely in Devanagari; in Latin-script Hindi; in the Hindi–English mixture people actually text, still in Latin script; or in the same mixture with Hindi particles in Devanagari and the scheme names and terms such as *main rule* left in Latin letters. All five ask for the same fact. If a model answers some of them correctly and others not, what changed? The knowledge is the same, and so is the target answer. What differs is the surface form.

**¶2 (keep from original draft, unchanged)**

> Existing multilingual evaluations rarely isolate this variable. Many benchmarks translate or re-author questions per language, so content, difficulty and phrasing move together with the language [1], [2], [3]. Code-switching benchmarks mostly measure task performance on naturally occurring text rather than recall of a fixed proposition [4]. Work on tokenization shows that some languages cost more tokens per unit of content [5], [6], [7], but that is usually inferred from corpus-level correlations, not from controlled prompt pairs. A fall in accuracy for "Indian-language prompts" could therefore reflect missing knowledge, harder questions, Romanization, the presence of English insertions, script, or tokenization, and these cannot be separated after the fact.

**¶3**

> We build the comparison so that they can be. Each of 100 propositions is rendered in five paired representations (Table I). Two of them, CS-LAT and MIXED, are meant to differ only in whether the Indic words are written in Latin or Brahmic script; this holds word for word in Hindi, Bengali and Tamil, while in Telugu and Kannada the question word also differs (Section III-A). We add a second English condition after finding that the original English template was more specific than the template shared by the other four conditions (Section III-B). We then ask whether the differences we measure survive two checks that representation studies rarely run: a larger output budget, and a judge from a different model family.

**[Table I goes here — full width, see §4]**

**¶4 Research questions**

> **Research questions.** RQ1: does judge-assessed answer accuracy depend on representation when the proposition is held fixed? RQ2: does mixed-script code-switching lower accuracy relative to the same code-switched words in Latin script? RQ3: does the effect differ across the five languages? RQ4: are the effects robust to the output budget and to the choice of judge? RQ5: is the script effect associated with input tokenization length? Hallucination detectors and mitigation are outside the scope of this paper.

**¶5 Contributions**

> **Contributions.** (1) A paired six-condition design for Indic factual QA, with a matched-English control that removes a template confound we found in our first run. (2) Evidence that a binding output budget can manufacture a script effect: the 23-point MIXED penalty measured at 128 tokens disappears when the same prompts are answered with 512 tokens. (3) Evidence of judge dependence: grading all conditions with one judge configuration, rather than the two used in our first run, shrinks the English–code-switching gap from 17 to 11 points, and a cross-family judge changes which contrasts are significant. (4) Inference that treats the 20 topics, not the 500 prompts, as the unit of independent evidence, and a release of prompts, outputs, judgements, a gold-answer ledger, and protocols for the human validation that is still outstanding.

**¶6 Findings in brief**

> **Findings in brief.** At a 128-token budget, accuracy falls from English to the Indic representations, and mixed script is lowest; under the self-judge the MIXED–CS-LAT gap is significant at prompt, proposition and topic level. It is not robust. Almost every response hits the cap, Brahmic-script answers are about half as long in characters, and with 512 tokens MIXED reaches CS-LAT (63% vs. 59%) and the level English reached with 128 tokens. A cross-family judge is much stricter (37% vs. 60% on English) and finds no significant MIXED–CS-LAT gap at either budget. The English advantage over Latin-script code-switching is not significant at the topic level in any analysis. Input characters per token, measured with the served model's tokenizer, shows no detectable association with correctness within the controlled contrast.

### II. RELATED WORK

> **Code-switching and LLMs.** GLUECoS evaluates code-switched understanding across tasks and language pairs including Hindi–English [4]. More recent studies find that large multilingual models are unreliable on code-switched tasks and when asked to generate code-mixed text [8], [9]. These works vary the task or the generated text; we hold the proposition fixed and vary only its rendering.

> **Multilingual evaluation for Indic languages.** IndicNLPSuite and IndicXTREME provide corpora and task benchmarks for Indic languages [2], [3], and MEGA compares generative models across many languages and tasks [1]. Such benchmarks answer how well a model performs per language, but their per-language items are not the same questions. Romanized input has itself been proposed as a bridge to Indic languages for LLMs [23]; our ROMAN condition measures the same factor on fixed propositions.

> **Tokenization.** Subword vocabularies fragment low-resource scripts into more tokens [7], [10], with measurable differences in cost and quality across languages [5], [6]. The same premium applies to generated text: an answer in a script that costs more tokens per character fits less content into a fixed output limit, which is the mechanism our budget experiment isolates. Our mediation analysis asks whether the input-side quantity explains the script contrast.

> **Factuality evaluation and LLM judges.** We use closed-book questions with a gold answer, closer in spirit to TruthfulQA-style checks than to long-form factual precision scoring [11], [12]. LLM graders are convenient but biased, for example towards their own outputs, answer position and length [13], [24], [25]; we therefore treat the judge as a central threat and grade with two judges from different model families.

**[Fig. 1 goes here — full width]**

### III. BENCHMARK AND PAIRED DESIGN

**A. Propositions, languages and conditions**

> The evaluated core contains 100 semantic groups: 20 topics, each instantiated once per language in Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te) and Kannada (kn). A group has one gold answer and evidence snippet, shared by its prompts in all conditions. The 20 topics are Indian public-policy and regulatory subjects (for example PMFBY vs. WBCIS, NEFT vs. RTGS, RTI third-party information, Companies Act CSR thresholds, IBC Section 7 default threshold, Citizenship Amendment Act cut-off); the full list is in Appendix A. Topics are crossed with languages, so language effects are not confounded with topic.

> Table I defines the six conditions. In NATIVE, ROMAN, CS-LAT and MIXED the question frame is one fixed template ("main rule, date or parameter regarding *X*") with *X* the topic string; only the rendering varies. ROMAN and NATIVE render the same Indic frame in Latin and Brahmic script, except in Hindi, where ROMAN uses *tareekh* and NATIVE *tithi* for "date". CS-LAT replaces part of the frame with English words ("main rule", "date", "parameter", and in Hindi and Bengali also "regarding"), and MIXED writes the remaining Indic words of CS-LAT in native script. In Hindi, Bengali and Tamil, CS-LAT and MIXED are word-for-word transliterations of each other. In Telugu and Kannada they are not: the question word is *enti* vs. ఏమిటి (*emiti*) in Telugu and *yenu* vs. ಯಾವುದು (*yāvudu*, "which") in Kannada. We report the CS-LAT–MIXED contrast on all 100 propositions, as planned, and on the 60 word-identical ones as a sensitivity analysis. Fluent speakers of all five languages, including the author (Telugu) and a teammate (Hindi, Telugu, Kannada), reviewed the templates and judged them natural and correct; the review was a yes/no check without item-level ratings. The templates and a structured review protocol are released.

(Word tip: the Telugu and Kannada words need a font with those scripts — Nirmala UI works on Windows. Check they render in the PDF.)

**B. Amendment: matched English and judge configuration**

> In the first run (EXP-002) the English prompts used two question templates ("key structural or operational difference between *X*" and "specific prerequisite condition or timeline applies to *X*"), while all other conditions used the single generic template. English-versus-Indic comparisons were therefore confounded with question type, a flaw we found only when auditing the raw prompt strings. We added EN-MATCH, the generic template in English (100 prompts, same gold answers), and ran it in a second run (EXP-003) with the same model and decoding settings, without modifying the earlier results. The two runs did not grade alike: EXP-002 called the judge at temperature 0.3 with the answering system prompt, EXP-003 at temperature 0 with an evaluator system prompt (Section IV). We therefore re-graded all 600 outputs with the EXP-003 configuration; all comparisons below use these harmonised labels and EN-MATCH as the English reference. EN-ORIG and EN-MATCH do not differ detectably (70% vs. 60%; exact p = 0.10, topic-level p = 0.69).

> Because the English prompt is identical across the five language tags of a topic and decoding is greedy, English outcomes are near-duplicated within topic: in EN-MATCH, 12 topics are correct in all five groups and 8 in none. The English condition therefore carries about 20 independent observations, not 100, which is why we report topic-level bootstrap intervals next to Wilson intervals.

**C. Provenance and gold answers**

> The core is the out-of-distribution test partition of IndraLLM-CS v1.1-CANDIDATE (1,500 semantic groups, 7,500 prompts; development, validation, in-distribution and out-of-distribution partitions, twelve template families). Version 1.0 (2,000 groups, 10,000 prompts) was retired after an internal audit showed that train and test partitions shared prompts, answers, entity pairs and templates, so it supports no generalization claim. The 1,000 in-distribution prompts per model that were also run (EXP-002) contain fictitious entities, and 2 of 2,000 responses were judged correct; they carry no information about recall and are excluded (Appendix A). A further 25 propositions (version 1.2-PILOT) have been written but not evaluated by any model.

> **Gold answers.** Each topic has one gold answer, shared by its five language groups and all six conditions. The benchmark stores an evidence snippet and a source URL with each; the snippets are template-generated paraphrases rather than quotations, and the URLs point to agency home pages rather than to specific documents. The author and, separately, volunteer reviewers checked the gold answers for factual correctness against public sources, and the author verified each answer against its governing provision for currency and for completeness relative to the question actually asked (Appendix A, Table VII; a per-topic ledger is released). The volunteer check was not logged item by item and no agreement statistic was computed, so we report it as a check rather than a measurement. All 20 answers are consistent with the provision identified. One describes a scheme that has since been replaced (Telangana's Rythu Bandhu, now Rythu Bharosa). Three are narrower than the generic question allows, so that other correct answers exist: the GST registration threshold (₹40 lakh applies to suppliers of goods, ₹20 lakh to services), the MTP Act (two practitioners are required only between 20 and 24 weeks) and the environmental-clearance public hearing (the gold lists two of several exemptions). Removing these three topics changes no conclusion (Appendix B). Gold-answer checks establish that the reference is right; they do not show that the judge grades model answers correctly, which no human has yet assessed on these outputs (Section VII).

(If you can, add one sentence with the number of volunteer reviewers and their background, e.g. "Two volunteer reviewers (graduate students in law and economics) …" — only with the real facts.)

### IV. EXPERIMENTAL SETUP

> Fig. 1 summarizes the pipeline: 100 propositions are rendered in six conditions, answered once by the primary model under greedy decoding, graded against the gold answer, and analysed at three levels of clustering. Section VI-B adds a follow-up run with a larger output budget.

> **Models.** The primary model is served by Groq under the API identifier `qwen/qwen3.8-27b`, which is recorded in every prediction row and in the response metadata of the follow-up. The provider lists it as an Alibaba Cloud model, and a public checkpoint of that name exists (Qwen/Qwen3.8-27B, 27.8B parameters, Apache-2.0). That checkpoint's tokenizer reproduces the API's prompt-token counts for all 600 prompts up to a constant chat-template offset of 48 tokens, and counts 125–128 tokens for responses the API reports as 128, so the tokenizer is established; whether the provider serves exactly those weights, and at what numerical precision, we cannot verify. We call the model Qwen3.8-27B. The second model is ALLaM-2-7B (`allam-2-7b`) [14]. All results are single-run. Greedy decoding on the hosted API was not fully deterministic: in the follow-up, 84–85% of 512-token responses begin with exactly the 128-token response to the same prompt, and the rest diverge.

> **Prompting and output budget.** Each prompt is sent with the system message "You are a helpful assistant answering questions from Indian users. Questions may mix an Indian language with English. Answer factually, accurately, and concisely." Decoding is greedy (temperature 0, top-p 1) with at most 128 output tokens in the main runs. The model almost never stops on its own: 598 of 600 responses used all 128 tokens, and 82–95% end mid-sentence in every condition, English included. The provider's finish reason was not logged in the main runs; it was logged in the follow-up.

> **Judging.** A judge receives the question as the model saw it, the gold answer and the response, and returns CORRECT or HALLUCINATED with a short reason (Appendix C). Three label sets exist. *Stored*: the labels saved with the predictions; EXP-002 obtained them from Qwen3.8-27B at temperature 0.3 with the answering system prompt (a side effect of reusing the generation client), EXP-003 at temperature 0 with the system prompt "You are an expert factuality evaluator." *J-QWEN*: all 600 outputs re-graded by Qwen3.8-27B with the EXP-003 configuration, the one the study intended; these labels are the primary analysis. *J-OSS*: the same rubric applied by gpt-oss-120b (`openai/gpt-oss-120b`, temperature 0, low reasoning effort), a judge from a different model family that did not produce the answers. J-QWEN reproduces the stored labels on all 100 EN-MATCH items (same configuration) and on 90–94% of items in the other conditions. No judge has been validated against human labels on these outputs. "Accuracy" below is the share of responses a judge labels CORRECT: a judge-assessed quantity, not a direct measurement of recall.

> **Statistics.** Observations are nested. A *prompt* is one string sent to the model. A *proposition* is a fact in one language group, rendered as six paired prompts. A *topic* (e.g. NEFT vs. RTGS) contains five propositions, one per language, with the same gold answer; across the five matched-template conditions it contributes 25 prompts. A proposition-level test asks whether the model, given these 100 facts, does better in one representation than in another. A topic-level test asks whether the difference should be expected to recur on new topics; with 20 topics it has much less power, but it matches the generalisation most readers want, so we report both. At the proposition level we use exact McNemar tests [15] with Holm correction [16] within a pre-specified family of five contrasts: each of NATIVE, ROMAN, CS-LAT and MIXED against EN-MATCH, and MIXED against CS-LAT. At the topic level we use an exact sign-flip permutation test over all 2²⁰ sign patterns of the 20 per-topic accuracy differences and a percentile bootstrap over topics (10,000 resamples, fixed seed), with Holm correction within the same family. Logistic GEE with independence working correlation and robust covariance clustered at prompt, proposition and topic level [18] is reported in Appendix B; with 20 clusters robust standard errors are anti-conservative [19], [20], so topic-level conclusions do not rest on it. Wilson intervals [17] are given for single proportions; the design effect is 1 + (*m* − 1)ρ with ρ from the one-way ANOVA estimator [21]. The follow-up (Section VI-B) has three contrasts, fixed in the analysis script before its outputs were graded: CS-LAT vs. EN-MATCH and MIXED vs. CS-LAT at 512 tokens, and the change in each gap from 128 to 512 tokens. Everything else is exploratory. All numbers are recomputed from the raw files by the scripts in Appendix E.

### V. RESULTS AT A 128-TOKEN BUDGET

**A. Accuracy falls with representation**

> Table II and Fig. 2 give the main result under the harmonised judge. Relative to EN-MATCH (60%), accuracy is 49% for CS-LAT, 37% for ROMAN, 32% for NATIVE and 26% for MIXED, differences of 11, 23, 28 and 34 points. At the proposition level the ROMAN, NATIVE and MIXED differences are significant after Holm correction (adjusted p ≤ 0.002); the CS-LAT difference is not (p = 0.13). With the stored labels, which graded EN-MATCH and the Indic conditions under different judge settings, the CS-LAT gap was 17 points (p = 0.014): about a third of it came from the grading difference. The ordering among the three non-English-script conditions is uncertain: ROMAN vs. MIXED gives p = 0.052 and NATIVE vs. MIXED p = 0.29 (Table VIII).

**[Table II full width; Fig. 2 full width]**

> The uncertainty is larger than the Wilson intervals imply. Topic-bootstrap intervals are wider (for EN-MATCH [40, 80] against Wilson [50.2, 69.1]) because accuracy is concentrated by topic: two topics (Environment Clearance Public Hearing, IBC Section 7) are wrong in every condition, and twelve are right for English in all five languages (Fig. 2b). The two all-wrong topics fail for different reasons. For IBC the model gives the pre-2020 default threshold of ₹1 lakh, a genuine error; for Environment Clearance the gold answer lists exemptions that the generic question does not ask for (Section III-C).

**B. Mixed vs. Latin-script code-switching**

> Writing the code-switched prompt with its Indic words in Brahmic rather than Latin script lowers accuracy from 49% to 26%, a 23-point drop. Of 37 propositions that differ, 30 favour CS-LAT and 7 favour MIXED (exact p < 0.001, Holm p < 0.001). The drop appears in all five languages (Fig. 3); the mean of the 20 per-topic differences is 23 points (bootstrap 95% CI [11, 35]; permutation p = 0.004, Holm-adjusted 0.018; 14 of 20 topics differ), and the GEE odds ratio is 0.37 (topic-clustered 95% CI 0.21–0.65). On the 60 propositions in Hindi, Bengali and Tamil, where the two prompts are word-for-word identical, the drop is 25 points (p = 0.0015; topic-level p = 0.016). Excluding the three topics with narrow gold answers leaves it at 23.5 points (p < 0.001). Under the stored labels it was 19 points (p = 0.003; topic-level p = 0.015, Holm-adjusted 0.072). At a 128-token budget, then, the mixed-script penalty is the most consistent result in the study.

> Section VI shows that this result does not survive a larger output budget. Here we note only why that check is needed: 88% of MIXED responses are written mostly in Brahmic script, against 2% of CS-LAT responses, so the prompt script also changes the script of the answer, and with it how much answer fits into 128 tokens.

**C. Clustering changes the strength of the English–code-switching gap**

> Observations within a topic are strongly dependent. In the five matched-template conditions the intra-topic correlation is ρ = 0.27, the design effect 7.5 and the effective sample size 67 out of 500. Fig. 4a and Table IX show what this does. For CS-LAT against EN-MATCH, the GEE p value is 0.12 at prompt level, 0.09 at proposition level and 0.37 at topic level, and the topic-level permutation test gives p = 0.42 (bootstrap 95% CI for the mean per-topic difference [−34, 13] points). For ROMAN, NATIVE and MIXED against EN-MATCH the topic-level permutation p values are 0.087, 0.031 and 0.030, and none survives Holm correction at topic level (smallest adjusted value 0.12). Only MIXED vs. CS-LAT survives Holm correction at every level (adjusted topic-level p = 0.018). The English-vs-Indic differences are consistent in direction, but at the level of topics only the larger ones approach significance, and the English–CS-LAT gap does not.

**D. Languages and models**

> Accuracy by language is in Fig. 3. MIXED is below CS-LAT in all five languages; EN-MATCH is above CS-LAT in four and tied with it in Bengali. A permutation test of whether the condition profile depends on language (statistic: interaction sum of squares of the language × condition accuracy table; null: language labels permuted among the five propositions of each topic; 10,000 permutations) gives p = 0.17. With 20 observations per cell this test has little power, so we report no detectable language dependence, not that languages behave alike; Bengali and Telugu differ visibly in the ROMAN column (20% vs. 50%), and nothing here can separate chance from effect.

> ALLaM-2-7B answers 10% of matched-English questions correctly and 5%, 2%, 2% and 3% in CS-LAT, ROMAN, NATIVE and MIXED (stored labels; Wilson 95% CI for EN-MATCH [5.5, 17.4]), so the representation contrast cannot be measured on it. The five-condition rank correlation with Qwen3.8-27B under the stored labels (ρ = 0.67, p = 0.22) describes a floor, not a replication. We make no claim about other model families.

### VI. TOKENIZATION AND THE OUTPUT BUDGET

**A. Input tokenization (exploratory)**

> Subword fragmentation is a standard explanation for weaker performance on non-Latin scripts. Our earlier analysis measured characters per token with the Qwen2.5-7B tokenizer, which does not match the served model: it disagrees with the API's prompt-token counts and would put capped 128-token responses at 120–305 tokens. With the Qwen3.8-27B tokenizer, which does match (Section IV), Brahmic text is less fragmented than that analysis implied: prompts average 2.43 characters per token in NATIVE and 3.70 in MIXED, against 4.65 in EN-MATCH and 4.11 in CS-LAT (previously 1.24 and 2.49 for NATIVE and MIXED). Within the CS-LAT–MIXED contrast, MIXED lowers characters per token (*a* = −0.41, SE 0.10), but once condition is controlled the mediator's association with correctness is not significant and has the wrong sign for a fragmentation account (*b* = −0.40, SE 0.23, p = 0.08; 95% CI −0.85 to 0.05; Sobel p = 0.11). The implied indirect effect is positive while the total effect is negative (−1.01). Because characters per token is almost determined by condition and language in this design, the test has little leverage: it is exploratory and does not rule out a tokenization effect. Across the six conditions, characters per token and accuracy are rank-correlated (ρ = 0.83), but six points that differ in language frame, script and answer length identify nothing (Fig. 5c).

**[Fig. 5 full width]**

**B. Response script, length and the output budget**

> The prompt script largely determines the response script: 98% of NATIVE and 88% of MIXED responses are written mostly in Brahmic script (more than half of their letters), against 8% and 2% for ROMAN and CS-LAT and none for English. Brahmic answers cost more tokens per character (2.2–2.4 characters per token in NATIVE and MIXED responses against 4.1 in English ones), and nearly all responses used the full 128 tokens, so mean response length is 529 characters in EN-MATCH but 279 in NATIVE and 303 in MIXED (Fig. 5a). Among errors, the share whose judge reason mentions an incomplete or missing answer (a keyword rule, Appendix C) is 0 of 40 in EN-MATCH, 11 of 51 in CS-LAT, 36 of 68 in NATIVE and 38 of 74 in MIXED. The rule depends on the judge's wording and does not measure truncation, but it points the same way.

> To separate script from budget we re-ran EN-MATCH, CS-LAT and MIXED (300 prompts) with a 512-token limit and nothing else changed: same model identifier, system prompt, decoding settings and prompts. Both the 128-token and the 512-token responses were graded by J-QWEN and by J-OSS, so every comparison across budgets uses one judge. The limit still binds for most code-switched answers (58 of 100 EN-MATCH, 15 CS-LAT and 5 MIXED responses stopped before 512 tokens), but MIXED responses now average 1,122 characters, twice what English responses had at 128 tokens. Table III gives the result. Under J-QWEN, MIXED rises from 26% to 63% and CS-LAT from 49% to 59%, so the MIXED–CS-LAT gap moves from −23 to +4 points (p = 0.57 at 512 tokens; change in the gap +27 points, topic-bootstrap CI [7, 45], permutation p = 0.018). Under J-OSS the gap is −8 points at 128 tokens and −6 at 512, neither significant. On the 60 word-identical propositions the picture is the same (J-QWEN, 512 tokens: 62% vs. 63%). MIXED with 512 tokens matches EN-MATCH with 128 (63% vs. 60%, p = 0.77). The English–CS-LAT gap behaves differently: under J-QWEN it widens to 21 points at 512 tokens (p < 0.001; topic-level p = 0.082), while under J-OSS it shrinks to 4 points (p = 0.57).

**[Table III one column]**

> Three conclusions follow. First, the 128-token MIXED penalty is not evidence that script alternation harms recall: given room, the model states the gold fact about equally often in the mixed-script and Latin-script code-switched conditions. Its most likely source is that Brahmic-script answers reach the cap before reaching the fact, and answers a human would call incomplete are then graded as wrong; the EN-MATCH answer on the MTP Act, for instance, correctly states the one-practitioner rule for the first 20 weeks, is cut off before the 20–24-week rule, and is graded HALLUCINATED. Second, NATIVE and MIXED behave alike at 128 tokens (32% and 26%, p = 0.29) although MIXED has five script boundaries per prompt and NATIVE one, which also argues against a boundary-density account. Third, the English advantage is unresolved: it persists under one judge and nearly vanishes under the other, which is a question about the judge (Section VII) as much as about the model.

### VII. JUDGE DEPENDENCE

> The judge matters in three ways. *Configuration.* Our first run graded the Indic conditions at temperature 0.3 with the answering system prompt and EN-MATCH at temperature 0 with an evaluator prompt. Harmonising the configuration changed 6–10% of the labels in each re-graded condition and moved CS-LAT accuracy from 43% to 49%, which is why the stored English–CS-LAT gap (17 points) exceeded the harmonised one (11). *Family.* J-OSS, which did not produce the answers, is far stricter than the self-judge: on the 128-token outputs it accepts 37% of EN-MATCH answers against 60% for J-QWEN, agrees with J-QWEN on 76% of items (κ = 0.33–0.62 by condition; Table IV), and 128 of the 146 disagreements are answers J-QWEN accepts and J-OSS rejects. Inspection shows why: J-QWEN often accepts an answer that is on topic and accurate but does not state the gold fact (for example, one that only names the governing Act), whereas J-OSS requires the gold fact. The rubric ("judge only factual correctness and whether it actually addresses the question") does not settle which is right, and truncated answers make the case common. *Differential error.* Neither judge has been compared with human labels, so we cannot say which is closer to a careful reader or whether either is harsher on one script. The two agree more often on NATIVE, ROMAN and MIXED (79–85%) than on English and CS-LAT (64–73%), so their disagreement is not concentrated on Brahmic text.

**[Table IV one column]**

> Table V turns the remaining uncertainty into tipping points. Assuming English answers are judged without error, it gives the sensitivity the judge would need on the comparison condition for that condition's true accuracy to equal the reference's. A correction applied equally to both conditions (the Rogan–Gladen estimator [22]) divides a gap by TPR − FPR and can only enlarge it, so a common-error grid cannot show robustness; the relevant threat is differential error. At a false-accept rate of 0.08, erasing the CS-LAT gap would need a judge that rejects 24% of truly correct CS-LAT answers (sensitivity 0.76), and erasing the MIXED gap one that rejects 62% (0.38). These are hypothetical error rates, not estimates of the judge's actual errors, which are unknown; the cross-family disagreement shows they are not small. A crude check agrees: on the 330 outputs whose gold answer contains numerals, the J-QWEN label matches whether all gold numerals appear in the response 67% of the time, with disagreements in both directions (73 accepted answers lack the figure; 35 rejected ones contain it).

**[Table V one column]**

### VIII. DISCUSSION

> What the data support is narrower than the design promised. For this model, these 20 topics and a 128-token budget, restating a question in Romanized or Brahmic script, or as code-switched text, lowers the share of answers a judge accepts, and mixed script is lowest. Quadrupling the budget removes the mixed-script penalty relative to Latin-script code-switching under both judges, and MIXED then does as well as English did at 128 tokens. The parsimonious reading is that much of the representation effect at 128 tokens reflects how much answer fits into the budget in the response script, not comprehension of the prompt. Whether an English advantage remains once answers can be completed depends on the judge, and topic-level evidence for it is weak in every analysis.

> The practical lesson is methodological. Output caps are often set low to save cost, and tokenizers make some scripts more expensive per character; a shared cap then gives answers in those scripts less room. Studies that compare languages or scripts through generated answers should report how often the cap binds in each condition and check that conclusions survive a larger cap; judges should be configured identically across conditions, and at least one should come from a family other than the evaluated model's. Table VI lists claims we examined and could not support.

**[Table VI one column]**

### IX. LIMITATIONS

> **Topics.** Twenty topics with heavy within-topic concentration bound what any statistic can show (effective n ≈ 67 of 500). A 25-proposition expansion has been written but not evaluated; its design power (Appendix D) is a projection. **Output budget.** Even 512 tokens bound most code-switched answers; we have not run an uncapped condition or one that fixes the answer language, and we re-ran three of the six conditions. **Judges.** Two LLM judges that disagree on a quarter of items, and no human labels on any output; a stratified, blinded sample of 210 outputs and an annotation protocol are prepared but not yet annotated. **Questions and gold answers.** One generic template that under-specifies the target for several topics; volunteer gold checks without an item-level record; one superseded scheme. **Prompts.** Fluent-speaker review of the templates was an informal yes/no check without item-level ratings or agreement statistics; CS-LAT and MIXED differ by one word in Telugu and Kannada, and Hindi ROMAN is not a transliteration of Hindi NATIVE. **Models and languages.** One informative model, whose served weights we cannot verify, and five languages. **Single run.** No repeated sampling; hosted greedy decoding was not fully deterministic, and API behaviour can change over time.

### X. ETHICS AND BROADER IMPACT

> Evaluations like this one guide where civic and legal information systems are considered safe to deploy for speakers who write the way our conditions do. Overstated gaps could discourage building for these users; understated ones could hide failures. We therefore report effect sizes with their dependence on clustering, output budget and judge. The prompts contain no personal data. The benchmark contains legal and policy facts that become outdated (one already has) and should not be used as legal advice. We do not estimate how many people use each representation, and make no claim about it.

### REPRODUCIBILITY (unnumbered heading)

> All numbers, tables and figures are produced from the raw files by `paper_v2/scripts/make_all.py` (128-token analyses; `--labels jqwen` for the harmonised labels), `analyze_exp004.py` (re-grading and budget follow-up) and `make_figures.py` (Appendix E). The follow-up cost $1.10 at the provider's list prices in October 2026. The project's budget ledger records $0.21 for all earlier runs, but it priced every call at a flat $0.08 per million tokens; at current list prices the Qwen3.8-27B generation and grading in EXP-002 and EXP-003 alone would cost about $2.1. The provider's billing record is the authoritative figure.

### APPENDIX A: BENCHMARK DETAILS

> **A.1 Topics.** Table VII lists the 20 topics, the provision against which each gold answer was verified, the outcome, and the number of languages (of five) in which each condition was answered correctly under J-QWEN. Topics are Indian public-policy and regulatory subjects, several comparing two schemes or institutions (e.g. NEFT vs. RTGS, Covaxin vs. Covishield, PSLV vs. GSLV Mk III); not all are statutes, so we call them public-policy topics. Gold column: *ok*, consistent and adequate; *simpl.*, a correct simplification; *narrow*, other correct answers to the generic question exist; *dated*, the scheme has been superseded.

> **A.2 Partitions and the unevaluated expansion.** Version 1.1-CANDIDATE: development 1,000 groups, validation 200, in-distribution test 200, out-of-distribution test 100 (the evaluated core). The 200 in-distribution test groups were run in EXP-002 for both models; they use fictitious entities, and 2 of 2,000 responses were judged correct, so they are not informative about recall. The prospective 1.2-PILOT adds 25 propositions (125 prompts) on topics with zero entity overlap with the evaluated 20; no model has been run on them.

### APPENDIX B: ADDITIONAL RESULTS

> Excluding the three topics with narrow gold answers (GST, MTP Act, Environment Clearance; 85 propositions), the J-QWEN differences from EN-MATCH are −12 (CS-LAT, p = 0.16), −25 (ROMAN, p = 0.002), −32 (NATIVE, p < 0.001) and −35 points (MIXED, p < 0.001), and MIXED vs. CS-LAT is −23.5 points (p < 0.001; topic-level p = 0.007). Table VIII gives all pairwise contrasts and Table IX the GEE estimates.

### APPENDIX C: RULES AND RUBRICS

> **Incompleteness rule.** A response is flagged when (i) it used the full 128 completion tokens, (ii) its last non-space character is not a sentence-final mark, (iii) the judge labelled it incorrect, and (iv) the judge's reason matches one of *incomplete, truncated, cut off, abrupt, unfinished, missing specific, missing parameter, fails to finish*. Condition (iv) depends on the judge's wording; the rule is a descriptive device, not a measure of truncation. **Judge prompt.** "You are grading whether a model's ANSWER to a user QUESTION is factually correct. You are given a trusted GOLD answer. The answer may mix an Indian language with English (code-switching) and may be phrased very differently from the gold—that is fine. Judge ONLY factual correctness and whether it actually addresses the question." Output: `VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>`. **Judge settings.** Stored, EXP-002: Qwen3.8-27B, temperature 0.3, at most 256 tokens, system prompt "You are a helpful assistant answering questions from Indian users. Questions may mix an Indian language with English (code-switching). Answer accurately and concisely in the same mixed style the user used." Stored, EXP-003, and J-QWEN: temperature 0, top-p 1, at most 256 tokens, system prompt "You are an expert factuality evaluator." J-OSS: gpt-oss-120b, temperature 0, top-p 1, low reasoning effort, at most 1,024 tokens, same system prompt. All 1,800 follow-up judgements were parsed. **Script transitions.** Words are maximal letter runs, each labelled Latin or Brahmic (U+0900–U+0DFF); transitions are label changes between consecutive words, giving 5.0 per MIXED prompt, 1.0 per NATIVE prompt (the Latin topic string) and 0 elsewhere. **Mostly Brahmic.** More than half of a response's letters and combining marks lie in U+0900–U+0DFF. **Templates.** All 20 Indic templates are listed in the released prompt-validation protocol.

### APPENDIX D: PROSPECTIVE DESIGN CALCULATION

> A normal-approximation calculation for a 45-topic design (225 paired propositions, design effect 1 + (5 − 1)ρ, binary variance at p̄ = 0.4, two-sided α = 0.05) with ρ = 0.2663 and a 21-point effect gives power 88.6% (minimum detectable effect 18.6 points); the same formula gives 55.9% for the 20 evaluated topics. Those parameters come from the first English template and the stored labels. With the harmonised labels (ρ = 0.27) the 11-point English–CS-LAT gap would have power 38% with 45 topics and 19% with 20, and a 23-point gap 93% and 63%. The formula ignores pairing and is a rough projection; the 25 new propositions have not been evaluated.

### APPENDIX E: REPRODUCIBILITY

> Python 3.11 with numpy, pandas, scipy, statsmodels, tokenizers and matplotlib. From the repository root, `python paper_v2/scripts/make_all.py` (stored labels) and `make_all.py --labels jqwen` read the two prediction files and write `paper_v2/output/numbers_*.json`; `python scripts/run_exp004_budget_rejudge.py --stage gen|judge` produced the follow-up (Groq key required; outputs, finish reasons and a spend log in `results/EXP-004-budget-rejudge/`); `analyze_exp004.py` and `make_figures.py` write the remaining numbers and Figs. 2–5. The tokenizer check downloads the Qwen/Qwen2.5-7B and Qwen/Qwen3.8-27B tokenizers. Sign-flip tests enumerate all 2²⁰ patterns; bootstraps and the language permutation use fixed seeds. Topic-level p values in an earlier draft were Monte Carlo approximations and differ from the exact values here in the third decimal. That draft's language-dependence p value (0.15) and numeral check (60% agreement) could not be reproduced because the script that produced them was not in the repository; they are replaced by the procedures described above.

### REFERENCES

Keep the original [1]–[22] exactly as in the draft. Append:

* [23] J. Husain *et al.*, "RomanSetu: Efficiently unlocking multilingual capabilities of large language models via Romanization," in *Proceedings of the 62nd annual meeting of the association for computational linguistics*, 2024.
* [24] P. Wang *et al.*, "Large language models are not fair evaluators," in *Proceedings of the 62nd annual meeting of the association for computational linguistics*, 2024.
* [25] Y. Dubois, B. Galambosi, P. Liang, and T. B. Hashimoto, "Length-controlled AlpacaEval: A simple way to debias automatic evaluators," *arXiv preprint arXiv:2404.04475*, 2024.

(Strict IEEE style numbers references in order of first citation; [23]–[25] are first cited in §II after [13]. If a reviewer cares, renumber; otherwise appending is common in practice.)

---

## 4. Tables (exact values)

Source for every value: `paper_v2/output/numbers_jqwen.json` (J-QWEN labels),
`numbers_original.json` (stored labels, ALLaM), `numbers_exp004.json` (J-OSS, budget).
Regenerate with `python paper_v2/scripts/dump_tables_md.py`.

### TABLE I — One proposition in all six conditions (Hindi) — full width

Caption:
> One proposition in all six conditions (Hindi). In Hindi, CS-LAT and MIXED contain the same words in the same order and differ only in the script of *ke*, *ya*, *kya hai* (also true for Bengali and Tamil; in Telugu and Kannada the question word differs, Section III-A). The topic string stays in Latin script in every condition, so NATIVE contains one Latin–Brahmic boundary per prompt.

| Condition | Prompt (topic: PMFBY vs. WBCIS, Hindi group) | Script of Indic words |
|---|---|---|
| EN-ORIG | What is the key structural or operational difference between PMFBY vs WBCIS? | (English) |
| EN-MATCH | What is the main rule, date or parameter regarding PMFBY vs WBCIS? | (English) |
| NATIVE | PMFBY vs WBCIS के संबंध में मुख्य नियम, तिथि या मापदंड क्या है? | Devanagari |
| ROMAN | PMFBY vs WBCIS ke sambandh mein mukhya niyam, tareekh ya mapdand kya hai? | Latin |
| CS-LAT | PMFBY vs WBCIS ke regarding main rule, date ya parameter kya hai? | Latin |
| MIXED | PMFBY vs WBCIS के regarding main rule, date या parameter क्या है? | Devanagari |

### TABLE II — Accuracy at 128 tokens (J-QWEN primary) — full width

Caption:
> Qwen3.8-27B accuracy on the 100 paired propositions at a 128-token budget, harmonised judge (J-QWEN). Δ: difference in correct answers out of 100 relative to EN-MATCH. Exact p: two-sided exact McNemar; Holm: within the five primary contrasts (MIXED vs. CS-LAT is in the text and Table VIII). Topic p: exact sign-flip permutation test on the 20 per-topic differences, Holm-adjusted in parentheses. Stored, J-OSS: accuracy (%) under the original labels and under the cross-family judge. †EN-ORIG vs. EN-MATCH, exploratory.

| Condition | Acc. (%) | Wilson CI | Topic-boot. CI | Δ | Exact p | Holm p | Topic p (Holm) | Stored | J-OSS |
|---|---|---|---|---|---|---|---|---|---|
| EN-ORIG | 70.0 (70/100) | [60.4, 78.1] | [50, 90] | +10† | 0.099 | – | 0.69 | 64 | 40 |
| EN-MATCH | 60.0 (60/100) | [50.2, 69.1] | [40, 80] | ref. | – | – | – | 60 | 37 |
| CS-LAT | 49.0 (49/100) | [39.4, 58.7] | [34, 64] | −11 | 0.13 | 0.13 | 0.42 (0.42) | 43 | 25 |
| ROMAN | 37.0 (37/100) | [28.2, 46.8] | [24, 50] | −23 | 0.001 | 0.002 | 0.087 (0.17) | 33 | 24 |
| NATIVE | 32.0 (32/100) | [23.7, 41.7] | [18, 46] | −28 | 2.54×10⁻⁵ | 1.02×10⁻⁴ | 0.031 (0.12) | 28 | 21 |
| MIXED | 26.0 (26/100) | [18.4, 35.4] | [12, 41] | −34 | 5.38×10⁻⁶ | 2.69×10⁻⁵ | 0.030 (0.12) | 24 | 17 |

### TABLE III — Output-budget follow-up — one column

Caption:
> Output-budget follow-up. The same 300 prompts answered with 128 and 512 tokens; both budgets graded by the same judge. Accuracy (%); gaps in points, each followed by exact McNemar p / topic-level permutation p. Last row: responses (EN-MATCH, CS-LAT, MIXED) that stopped before the cap.

| | J-QWEN 128 | J-QWEN 512 | J-OSS 128 | J-OSS 512 |
|---|---|---|---|---|
| EN-MATCH | 60 | 80 | 37 | 58 |
| CS-LAT | 49 | 59 | 25 | 54 |
| MIXED | 26 | 63 | 17 | 48 |
| CS-LAT − EN-MATCH | −11 | −21 | −12 | −4 |
|   p exact / topic | .13 / .42 | <.001 / .082 | .050 / .22 | .57 / .76 |
| MIXED − CS-LAT | −23 | +4 | −8 | −6 |
|   p exact / topic | <.001 / .004 | .57 / .65 | .18 / .24 | .34 / .44 |
| Stopped before cap | 0, 1, 0 | 58, 15, 5 | 0, 1, 0 | 58, 15, 5 |

### TABLE IV — Judge agreement at 128 tokens — one column

Caption:
> Judge agreement on the 600 outputs at 128 tokens. Stored vs. J-QWEN: share of identical labels (EN-MATCH was stored under the J-QWEN configuration). J-QWEN vs. J-OSS: share identical and Cohen's κ.

| Condition | Stored vs. J-QWEN | J-QWEN vs. J-OSS | κ |
|---|---|---|---|
| EN-ORIG | 0.94 | 0.64 | 0.33 |
| EN-MATCH | 1.00 | 0.73 | 0.49 |
| CS-LAT | 0.90 | 0.72 | 0.43 |
| ROMAN | 0.94 | 0.81 | 0.56 |
| NATIVE | 0.92 | 0.85 | 0.62 |
| MIXED | 0.92 | 0.79 | 0.39 |

Overall J-QWEN × J-OSS cross-tab (600 outputs): both correct 146, both wrong 308, J-QWEN correct & J-OSS wrong 128, J-QWEN wrong & J-OSS correct 18 → agreement 75.7%.

### TABLE V — Tipping points (J-QWEN, 128 tokens) — one column

Caption:
> Sensitivity the judge would need on the comparison condition for its true accuracy to equal the reference condition's, at the given false-accept rate (J-QWEN, 128 tokens). Reference answers assumed judged without error. Lower entries mean a larger error would be needed.

| FPR | CS-LAT vs. EN-MATCH | MIXED vs. EN-MATCH | MIXED vs. CS-LAT |
|---|---|---|---|
| 0.00 | 0.82 | 0.43 | 0.53 |
| 0.04 | 0.79 | 0.41 | 0.49 |
| 0.08 | 0.76 | 0.38 | 0.45 |
| 0.12 | 0.74 | 0.35 | 0.41 |
| 0.16 | 0.71 | 0.33 | 0.36 |

Formula: required sensitivity = (acc_cmp − FPR·(1 − acc_ref)) / acc_ref.

### TABLE VI — Claims examined and not supported — one column

| Examined claim | Outcome |
|---|---|
| Script alternation (CS-LAT → MIXED) lowers recall | Not supported: gap +4 at 512 tokens (p = 0.57); n.s. under J-OSS |
| English advantage over CS-LAT at topic level | Not supported (topic p ≥ 0.08 in all analyses) |
| Prompt token fertility mediates CS-LAT → MIXED | Not detected (p = 0.08, wrong sign; exploratory) |
| Language dependence of the profile | Not detected (p = 0.17), low power |
| Rank agreement with ALLaM-2-7B | Uninformative (floor; ρ = 0.67, p = 0.22) |
| Errors rise with script transitions | Not supported (NATIVE ≈ MIXED) |
| Original 20-fold truncation ratio | Not reproducible from files |

### TABLE VII (Appendix A) — Topics, provision, gold status, correct languages — full width

Caption:
> Topics, provision used to verify the gold answer, verification outcome, and languages (of five) answered correctly per condition (Qwen3.8-27B, J-QWEN, 128 tokens).

| Topic | Provision verified | Gold | EN-ORIG | EN-MATCH | CS-LAT | ROMAN | NATIVE | MIXED |
|---|---|---|---|---|---|---|---|---|
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

### TABLE VIII (Appendix B) — All pairwise contrasts, J-QWEN — full width

Caption:
> All pairwise contrasts, J-QWEN labels, 128 tokens (proposition-level exact McNemar; b: the second-named (reference) condition correct and the first wrong; c: the reverse; topic-level permutation p and bootstrap CI for the change, uncorrected). The first five rows are the primary family.

| Contrast | Δ (pp) | b | c | Exact p | Topic p | Topic 95% CI (pp) |
|---|---|---|---|---|---|---|
| CS-LAT vs. EN-MATCH | −11 | 27 | 16 | 0.13 | 0.42 | [−34, 13] |
| ROMAN vs. EN-MATCH | −23 | 35 | 12 | 0.001 | 0.087 | [−46, 0] |
| NATIVE vs. EN-MATCH | −28 | 36 | 8 | 2.54×10⁻⁵ | 0.031 | [−49, −6] |
| MIXED vs. EN-MATCH | −34 | 45 | 11 | 5.38×10⁻⁶ | 0.030 | [−59, −7] |
| MIXED vs. CS-LAT | −23 | 30 | 7 | 1.91×10⁻⁴ | 0.004 | [−35, −11] |
| EN-MATCH vs. EN-ORIG | −10 | 20 | 10 | 0.099 | 0.69 | [−35, 15] |
| MIXED vs. ROMAN | −11 | 19 | 8 | 0.052 | 0.069 | [−21, −1] |
| MIXED vs. NATIVE | −6 | 14 | 8 | 0.29 | 0.46 | [−18, 6] |
| ROMAN vs. CS-LAT | −12 | 25 | 13 | 0.073 | 0.057 | [−22, −2] |
| NATIVE vs. CS-LAT | −17 | 27 | 10 | 0.008 | 0.033 | [−30, −4] |
| NATIVE vs. ROMAN | −5 | 16 | 11 | 0.44 | 0.37 | [−13, 3] |

### TABLE IX (Appendix B) — Logistic GEE, J-QWEN — one column

Caption:
> Logistic GEE (independence working correlation, robust covariance), J-QWEN labels, 128 tokens. β̂ is the log-odds difference from EN-MATCH (first four blocks, 500 observations) or from CS-LAT (last block, 200). Topic-level robust SEs with 20 clusters are anti-conservative.

| Contrast | Clustering unit (#) | β̂ | SE | p |
|---|---|---|---|---|
| CS-LAT vs. EN-MATCH | prompt (500) | −0.445 | 0.286 | 0.12 |
| | proposition (100) | −0.445 | 0.264 | 0.091 |
| | topic (20) | −0.445 | 0.493 | 0.37 |
| ROMAN vs. EN-MATCH | prompt (500) | −0.938 | 0.291 | 0.001 |
| | proposition (100) | −0.938 | 0.273 | 5.95×10⁻⁴ |
| | topic (20) | −0.938 | 0.494 | 0.058 |
| NATIVE vs. EN-MATCH | prompt (500) | −1.159 | 0.296 | 9.00×10⁻⁵ |
| | proposition (100) | −1.159 | 0.263 | 1.06×10⁻⁵ |
| | topic (20) | −1.159 | 0.473 | 0.014 |
| MIXED vs. EN-MATCH | prompt (500) | −1.451 | 0.306 | 2.10×10⁻⁶ |
| | proposition (100) | −1.451 | 0.310 | 2.89×10⁻⁶ |
| | topic (20) | −1.451 | 0.606 | 0.017 |
| MIXED vs. CS-LAT | prompt (200) | −1.006 | 0.303 | 9.11×10⁻⁴ |
| | proposition (100) | −1.006 | 0.257 | 8.96×10⁻⁵ |
| | topic (20) | −1.006 | 0.293 | 5.88×10⁻⁴ |

(MIXED vs. CS-LAT odds ratio exp(−1.006) = 0.37; topic-clustered 95% CI 0.21–0.65.)

---

## 5. Figures (files + captions)

All PNG files are in `paper_v2/output/`, 300 dpi. In Word: Insert ▸ Pictures, then set the
width listed. Full-width figures need a one-column section (Layout ▸ Breaks ▸ Continuous,
then Columns ▸ One) before them and a two-column section after them — copy the structure
used for the original Fig. 1.

| Figure | File | Width | Layout |
|---|---|---|---|
| Fig. 1 | `fig1.png` | 5.8 in | full width |
| Fig. 2 | `fig2.png` | 5.8 in | full width |
| Fig. 3 | `fig3.png` | 3.4 in | one column |
| Fig. 4 | `fig4.png` | 5.8 in | full width |
| Fig. 5 | `fig5.png` | 5.8 in | full width |

Captions:

* **Fig. 1.** Study design. Each proposition is rendered in six conditions and answered once by Qwen3.8-27B under greedy decoding with a 128-token limit; responses are graded against the gold answer by the same model (J-QWEN). The follow-up (Section VI-B) re-answers three conditions with a 512-token limit and grades both budgets with J-QWEN and with gpt-oss-120b (J-OSS). Key contrasts: EN-MATCH vs. CS-LAT (code-switching) and CS-LAT vs. MIXED (script).
* **Fig. 2.** (a) Accuracy (J-QWEN) with Wilson 95% intervals (n = 100 per condition; points not independent within topic). (b) Number of languages (of five) in which each topic is answered correctly, per condition. Topics sorted by EN-MATCH, then EN-ORIG.
* **Fig. 3.** Accuracy by language and condition (J-QWEN; n = 20 per cell).
* **Fig. 4.** (a) GEE log-odds differences from EN-MATCH (J-QWEN) with robust 95% CIs at three clustering levels (circle: prompt; square: proposition; diamond: topic). Intervals widen at topic level, where the CS-LAT and ROMAN intervals include zero. (b) Per-topic accuracy difference, CS-LAT minus MIXED (20 topics; band: bootstrap 95% CI of the mean; line: mean).
* **Fig. 5.** (a) Mean response length at 128 tokens (solid; labels: % of responses written mostly in Brahmic script) and, for three conditions, at 512 tokens (hatched). (b) Accuracy of the same 300 prompts at 128 and 512 tokens, graded by J-QWEN (solid) and J-OSS (dashed). (c) Condition-level prompt characters per token (Qwen3.8 tokenizer) against accuracy at 128 tokens (six points; descriptive only).

What each figure shows (so you can check it): Fig. 2a points at 70, 60, 49, 37, 32, 26.
Fig. 3 lines: values in §8.4. Fig. 5b lines: J-QWEN 60→80, 49→59, 26→63; J-OSS 37→58, 25→54, 17→48.

---

## 6. Numbers registry (every number used in the text, with source)

File abbreviations: **J** = `numbers_jqwen.json`, **O** = `numbers_original.json`, **E** = `numbers_exp004.json` (all in `paper_v2/output/`).

### 6.1 Main accuracies, 128 tokens (n = 100 each)

| Condition | J-QWEN (primary) | Stored | J-OSS | Source |
|---|---|---|---|---|
| EN-ORIG | 70 | 64 | 40 | J / O / E |
| EN-MATCH | 60 | 60 | 37 | |
| CS-LAT | 49 | 43 | 25 | |
| ROMAN | 37 | 33 | 24 | |
| NATIVE | 32 | 28 | 21 | |
| MIXED | 26 | 24 | 17 | |

### 6.2 Primary contrasts under each label set

Stored labels (the numbers in the original PDF; all reproduced exactly):

| Contrast | Δ | b | c | Exact p | Holm | Topic p | Holm topic |
|---|---|---|---|---|---|---|---|
| CS-LAT vs EN-MATCH | −17 | 30 | 13 | 0.014 | 0.014 | 0.19 | 0.19 |
| ROMAN vs EN-MATCH | −27 | 37 | 10 | 9.85×10⁻⁵ | 2.95×10⁻⁴ | 0.036 | 0.073 |
| NATIVE vs EN-MATCH | −32 | 39 | 7 | 1.83×10⁻⁶ | 9.16×10⁻⁶ | 0.014 | 0.072 |
| MIXED vs EN-MATCH | −36 | 47 | 11 | 2.03×10⁻⁶ | 9.16×10⁻⁶ | 0.021 | 0.072 |
| MIXED vs CS-LAT | −19 | 29 | 10 | 0.003 | 0.007 | 0.015 | 0.072 |

J-QWEN: see Table II and Table VIII. J-OSS:

| Contrast | Δ | b | c | Exact p | Holm | Topic p | Holm topic |
|---|---|---|---|---|---|---|---|
| CS-LAT vs EN-MATCH | −12 | 22 | 10 | 0.050 | 0.10 | 0.22 | 0.45 |
| ROMAN vs EN-MATCH | −13 | 22 | 9 | 0.029 | 0.088 | 0.15 | 0.44 |
| NATIVE vs EN-MATCH | −16 | 20 | 4 | 0.002 | 0.008 | 0.035 | 0.18 |
| MIXED vs EN-MATCH | −20 | 29 | 9 | 0.002 | 0.008 | 0.067 | 0.27 |
| MIXED vs CS-LAT | −8 | 18 | 10 | 0.18 | 0.18 | 0.24 | 0.45 |

### 6.3 Clustering (J-QWEN)

* ICC ρ = 0.271; design effect 7.51; effective n 66.5 of 500 (m = 25, k = 20). [J `icc`]
* Stored labels: ρ = 0.204, design effect 5.89, n_eff 84.8 (matches original PDF). [O]
* EN-MATCH: 12 topics 5/5 correct, 8 topics 0/5. EN-ORIG (J-QWEN): 14 and 6.
* MIXED vs CS-LAT: mean per-topic difference 23 pp, bootstrap CI [11, 35], 14 of 20 topics differ.
* Language-dependence permutation: J-QWEN p = 0.17; stored p = 0.23 (10,000 permutations, seed 0).

### 6.4 Sensitivity analyses (J-QWEN)

* Word-identical languages (hi, ta, bn; 60 propositions): CS-LAT 51.7%, MIXED 26.7%, Δ −25, b 18, c 3, exact p = 0.0015, topic p = 0.016. At 512 tokens: 61.7% vs 63.3% (b 7, c 8, p = 1.0). J-OSS 128: 30.0 vs 16.7 (p = 0.096); J-OSS 512: 55.0 vs 48.3 (p = 0.48).
* te/kn only (stored labels): 40.0% vs 27.5%, p = 0.33.
* Excluding GST, MTP, Environment Clearance (85 propositions): CS-LAT −11.8 (p = 0.16, topic 0.47), ROMAN −24.7 (p = 0.002, topic 0.11), NATIVE −31.8 (p < 0.001, topic 0.038), MIXED −35.3 (p < 0.001, topic 0.050), MIXED vs CS-LAT −23.5 (p < 0.001, topic 0.007).

### 6.5 Budget follow-up (EXP-004)

Generation at 512 tokens (300 prompts; finish reason logged) [E `gen512_descriptives`]:

| Condition | Stopped before 512 | Mean completion tokens | Mean chars | Mostly Brahmic % | Starts with exact 128-token text |
|---|---|---|---|---|---|
| EN-MATCH | 58/100 | 438 | 1,771 | 0 | 84/100 |
| CS-LAT | 15/100 | 484 | 1,601 | 2 | 85/100 |
| MIXED | 5/100 | 508 | 1,122 | 96 | 84/100 |

Within-condition change 128 → 512 (same judge):

| Judge | Condition | 128 | 512 | b (lost) | c (gained) | Exact p | Topic p | Topic CI |
|---|---|---|---|---|---|---|---|---|
| J-QWEN | EN-MATCH | 60 | 80 | 0 | 20 | 1.9×10⁻⁶ | 0.12 | [5, 40] |
| J-QWEN | CS-LAT | 49 | 59 | 11 | 21 | 0.11 | 0.22 | [−2, 24] |
| J-QWEN | MIXED | 26 | 63 | 5 | 42 | 2.5×10⁻⁸ | 0.003 | [18, 57] |
| J-OSS | EN-MATCH | 37 | 58 | 3 | 24 | 4.9×10⁻⁵ | 0.043 | [5, 39] |
| J-OSS | CS-LAT | 25 | 54 | 3 | 32 | 4.2×10⁻⁷ | <0.001 | [16, 43] |
| J-OSS | MIXED | 17 | 48 | 3 | 34 | 1.2×10⁻⁷ | <0.001 | [19, 43] |

Contrasts (comparison vs reference; b = reference correct & comparison wrong):

| Judge | Budget | Contrast | Δ | b | c | Exact p | Topic p | Topic CI |
|---|---|---|---|---|---|---|---|---|
| J-QWEN | 512 | CS-LAT vs EN-MATCH | −21 | 28 | 7 | 5.1×10⁻⁴ | 0.082 | [−41, −1] |
| J-QWEN | 512 | MIXED vs CS-LAT | +4 | 12 | 16 | 0.57 | 0.65 | [−8, 15] |
| J-QWEN | 512 | MIXED vs EN-MATCH | −17 | 24 | 7 | 0.003 | 0.13 | [−35, 3] |
| J-OSS | 512 | CS-LAT vs EN-MATCH | −4 | 16 | 12 | 0.57 | 0.76 | [−22, 15] |
| J-OSS | 512 | MIXED vs CS-LAT | −6 | 17 | 11 | 0.34 | 0.44 | [−18, 6] |
| J-OSS | 512 | MIXED vs EN-MATCH | −10 | 19 | 9 | 0.087 | 0.31 | [−26, 6] |

Change in gap from 128 to 512 (per-topic difference-in-differences):

| Judge | Gap | at 128 | at 512 | Change | Topic CI | Topic p |
|---|---|---|---|---|---|---|
| J-QWEN | MIXED − CS-LAT | −23 | +4 | +27 | [7, 45] | 0.018 |
| J-QWEN | CS-LAT − EN-MATCH | −11 | −21 | −10 | [−31, 9] | 0.41 |
| J-QWEN | MIXED − EN-MATCH | −34 | −17 | +17 | [−4, 39] | 0.18 |
| J-OSS | MIXED − CS-LAT | −8 | −6 | +2 | [−11, 16] | 0.89 |
| J-OSS | CS-LAT − EN-MATCH | −12 | −4 | +8 | [−8, 23] | 0.42 |
| J-OSS | MIXED − EN-MATCH | −20 | −10 | +10 | [−6, 26] | 0.30 |

MIXED at 512 vs EN-MATCH at 128: J-QWEN 63 vs 60 (b 21, c 24, p = 0.77, topic p 0.88); J-OSS 48 vs 37 (p = 0.12).

Cost of EXP-004 (list prices 2026-10-10: Qwen3.8-27B $0.80/M in, $4.00/M out; gpt-oss-120b $0.15/M in, $0.60/M out):
Qwen 1,200 calls, 404,527 in / 166,298 out tokens, $0.989; gpt-oss 900 calls, 394,936 in / 78,730 out, $0.106; **total $1.095**.

### 6.6 Response side, 128 tokens (J-QWEN for errors and incompleteness)

| Condition | Script transitions | Prompt chars/token (Qwen3.8) | (old Qwen2.5) | Response chars | Mostly Brahmic % | Ends mid-sentence | Errors | Incomplete rule |
|---|---|---|---|---|---|---|---|---|
| EN-ORIG | 0.0 | 5.83 | 5.82 | 538 | 0 | 82 | 30 | 0 |
| EN-MATCH | 0.0 | 4.65 | 4.64 | 529 | 0 | 87 | 40 | 0 |
| CS-LAT | 0.0 | 4.11 | 4.02 | 423 | 2 | 90 | 51 | 11 |
| ROMAN | 0.0 | 3.15 | 2.90 | 390 | 8 | 91 | 63 | 18 |
| NATIVE | 1.0 | 2.43 | 1.24 | 279 | 98 | 95 | 68 | 36 |
| MIXED | 5.0 | 3.70 | 2.49 | 303 | 88 | 92 | 74 | 38 |

* Responses hitting 128 tokens: 598 of 600 (the two exceptions: S001412 CS-LAT ta, 94 tokens; S001462 ROMAN ta, 87 tokens).
* Response chars per token (Qwen3.8): EN-ORIG 4.21, EN-MATCH 4.14, CS-LAT 3.32, ROMAN 3.06, NATIVE 2.18, MIXED 2.37.
* Stored-label incompleteness counts (original PDF): EN-MATCH 0/40, CS-LAT 15/57, NATIVE 42/72, MIXED 41/76 — reproduced exactly.

### 6.7 Tokenizer and mediation

* Qwen3.8-27B tokenizer: API prompt_tokens − local count = 48 for all 600 OOD prompts (1,600 including in-distribution rows); 128-token responses count 125–128 locally.
* Qwen2.5-7B tokenizer: offsets vary from 1 to 48; 128-token responses count 120–305 locally → mismatch.
* Mediation (CS-LAT vs MIXED, 200 rows, J-QWEN, Qwen3.8 tokenizer): a = −0.406 (SE 0.098); b = −0.403 (SE 0.230, p = 0.080, 95% CI −0.853 to 0.048); total −1.006; direct −1.192; Sobel z = 1.61, p = 0.107.
* Same with stored labels: b = −0.304, p = 0.19; Sobel p = 0.21. Original PDF (Qwen2.5 tokenizer, stored): a = −1.529, b = −0.248, Sobel p = 0.31 — reproduced exactly, but uses the wrong tokenizer.
* Six-condition Spearman ρ (chars/token vs accuracy): 0.83 (Qwen3.8, J-QWEN); original 0.94 (Qwen2.5, stored).

### 6.8 Judge diagnostics

* Stored vs J-QWEN identical labels: EN-ORIG 94%, EN-MATCH 100%, CS-LAT 90%, ROMAN 94%, NATIVE 92%, MIXED 92%.
* J-QWEN vs J-OSS: 75.7% agreement overall; cross-tab 146 / 308 / 128 / 18 (see Table IV note).
* Numeral check (330 outputs from the 11 topics whose gold contains numerals): J-QWEN agreement 67.3%, 73 accepted without the numeral, 35 rejected with it. Stored labels: 65.2%, 73 / 42. Normalising native digits changes almost nothing (65.8%).
* All 1,800 EXP-004 judgements parsed (no parse failures); no stored labels unparsed.

### 6.9 Other

* ALLaM-2-7B (stored): EN-ORIG 8 [4.1, 15.0], EN-MATCH 10 [5.5, 17.4], CS-LAT 5 [2.2, 11.2], ROMAN 2 [0.6, 7.0], NATIVE 2 [0.6, 7.0], MIXED 3 [1.0, 8.5]; Spearman with Qwen (5 conditions) ρ = 0.667, p = 0.219.
* In-distribution partition (fictitious entities): 2 of 2,000 responses judged correct.
* Per-language accuracy (J-QWEN, %), order EN-ORIG / EN-MATCH / CS-LAT / ROMAN / NATIVE / MIXED:
  Hindi 70/60/45/40/40/30 · Bengali 70/60/60/20/20/35 · Tamil 70/60/50/35/35/15 · Telugu 70/60/40/50/30/35 · Kannada 70/60/50/40/35/15.
* Power (Appendix D formula): stored ρ 0.2663 & 21 pp → 88.6% (45 topics), 55.9% (20); stored ρ 0.204 & 17 pp → 78.0%, 44.5%; J-QWEN ρ 0.271 & 11 pp → 37.8%, 19.5%; & 23 pp → 93.2%, 63.3%.

---

## 7. What was implemented in the repository

### 7.1 New experiment: EXP-004 (output budget + re-judging)

* Script: `scripts/run_exp004_budget_rejudge.py` (stages `gen` and `judge`; resumable; append-only;
  logs finish reason, served model, system fingerprint, request id, token usage, and a per-call
  spend record priced at Groq list prices; aborts above a $1.60 ceiling).
* `gen`: Qwen3.8-27B, same system prompt as EXP-002/003, temperature 0, top-p 1, **max_tokens 512**,
  on EN-MATCH, CS-LAT, MIXED (300 prompts). Output: `results/EXP-004-budget-rejudge/gen512_predictions.jsonl`.
* `judge`: original rubric applied by J-QWEN (Qwen3.8-27B, T 0, max 256, evaluator system prompt)
  and J-OSS (gpt-oss-120b, T 0, reasoning effort low, max 1,024) to the 600 original 128-token outputs
  and the 300 new 512-token outputs = 1,800 judgements. Output: `results/EXP-004-budget-rejudge/judgements.jsonl`.
* Spend log: `results/EXP-004-budget-rejudge/spend_log.jsonl` (2,100 records, $1.095).

### 7.2 Analysis code (`paper_v2/scripts/`)

| File | What it does |
|---|---|
| `stats_lib.py` | Wilson CI, exact McNemar, Holm, exact sign-flip permutation (all 2²⁰), topic bootstrap, Brahmic share, script transitions, numeral check, incompleteness rule |
| `make_all.py` | Recomputes every 128-token number (accuracy, CIs, 11 contrasts, Holm, GEE at 3 levels, ICC/design effect, language permutation, topic and language tables, tipping points, ALLaM, response descriptors, numeral check, power, tokenizer check with both tokenizers, mediation, sensitivity analyses). `--labels jqwen` uses the harmonised labels. Writes `output/numbers_original.json` or `output/numbers_jqwen.json`. |
| `analyze_exp004.py` | Judge agreement and κ, accuracy and primary contrasts under stored / J-QWEN / J-OSS, budget descriptives (finish reasons, prefix consistency), within-condition changes, 128 and 512 contrasts, gap changes, MIXED-512 vs EN-128, spend. Writes `output/numbers_exp004.json`. |
| `make_figures.py` | Figs. 2–5 (J-QWEN labels; new Fig. 5 with the budget result). |
| `make_fig1.py` | Fig. 1 design diagram (correct model name, both judges, follow-up). |
| `build_revised_docx.py`, `docx_helpers.py` | Built the 13-page draft DOCX from the original source (optional; you are building the document yourself). |
| `dump_tables_md.py` | Prints every table in this guide from the JSON files. |

`paper_v2/scripts/make_all.py` now exists at the path the manuscript cites (it did not exist before).

### 7.3 Research records (`research/`, `results/`)

| File | Content |
|---|---|
| `research/gold_verification_ledger.csv` | 20 topics × gold answer, recorded source URL, governing provision, factual status, completeness, currency note, notes, author-verification fields |
| `research/HUMAN_EVAL_PROTOCOL.md` | Judge-validation protocol: sampling, blinding, rubric (CORRECT / PARTIAL / INCOMPLETE_NO_ERROR / INCORRECT / CORRECT_OTHER_READING / UNREADABLE), adjudication, analysis plan |
| `results/EXP-004-budget-rejudge/human_eval/` | `items_blinded.csv` (150 items: 120 stratified by condition × verdict × language + 30 judge-disagreement items), `key.csv`, `items_blinded_512.csv` (60 items at 512 tokens), `key_512.csv`, `reviewers.csv` template. Built by `scripts/build_human_eval_sample.py` (seed 20261010). |
| `research/PROMPT_VALIDATION_PROTOCOL.md` | All 20 Indic templates verbatim, the lexical-identity findings, and a fluent-speaker review protocol |

### 7.4 Preserved originals

`paper_v2/source/IndraLLM_IEEE_FINAL.docx` and `.pdf` are byte-identical copies of your
original files (SHA-256 105b6933… and 68743145…). Nothing in `results/EXP-002` or
`results/EXP-003-matched-en` was modified.

---

## 8. Corrections relative to the original PDF (change log)

| Location (original PDF) | Old | New | Reason / evidence |
|---|---|---|---|
| Title | Representation Fragility … Separating Script Alternation from Code-Switching | Representation Effects … Script, Output Budget, and Judge Dependence | Script effect does not survive 512 tokens (§6.5) |
| Abstract | Accuracies 60/43/33/28/24 (stored), "28.0and" typo, 19-pt MIXED drop as headline | Harmonised 60/49/37/32/26, 512-token result, cross-judge result | Judge config mismatch; EXP-004 |
| Abstract, §I, §III-A | CS-LAT and MIXED "contain the same words" | True only for hi, bn, ta | Template strings (`PROMPT_VALIDATION_PROTOCOL.md`) |
| §I Findings | MIXED penalty "survives every level of clustering" | Survives clustering at 128 tokens but not a larger budget or a second judge | EXP-004 |
| §III-B | EN-MATCH run "with identical decoding and judging" | Decoding identical; judging was not (T 0.3 vs T 0); all outputs re-graded | `run_exp002.py` uses `GroqClient.generate` → `config.yaml` T 0.3 |
| §III-C | Gold answers "not independently re-verified"; no human annotated | Author + volunteers checked; author verified each answer against its provision; ledger; 1 dated, 3 narrow | Author clarification; ledger |
| §IV Models | qwen3.8-27b, checkpoint unknown; "Qwen-2.5-27B" in docs | Tokenizer established (constant 48-token offset); weights unverifiable; name Qwen3.8-27B | Tokenizer check (§6.7) |
| §IV Prompting | (no cap statistics) | 598/600 hit 128 tokens; 82–95% end mid-sentence in every condition | Prediction files |
| §IV Judging | One judge, "temperature 0, 256 tokens" | Three label sets; J-QWEN primary; J-OSS cross-family | EXP-004 |
| §IV Statistics | (units not explained) | Plain-language prompt / proposition / topic explanation; exact sign-flip | — |
| §V-A | CS-LAT −17 significant after Holm | −11, p = 0.13 (stored −17 explained) | Harmonised labels |
| §V-B | 43 → 24, b 29 c 10, OR 0.42 | 49 → 26, b 30 c 7, OR 0.37; hi/ta/bn subset −25 | J-QWEN |
| §V-C | ρ 0.204, deff 5.89, n_eff 84.8 | ρ 0.27, deff 7.5, n_eff 67 | J-QWEN |
| §V-D | Language test p = 0.15; "EN-MATCH > CS-LAT in all five" | p = 0.17 (defined test); tied in Bengali | Original script absent; J-QWEN table |
| §VI-A | Qwen2.5-7B tokenizer; NATIVE 1.24, MIXED 2.49 chars/token; Sobel p 0.31 | Qwen3.8 tokenizer; 2.43, 3.70; b p 0.08 wrong sign; exploratory | Tokenizer mismatch |
| §VI-B | 100% NATIVE, 97% MIXED "mostly Brahmic"; "would cost a few cents" follow-up | 98% / 88% (defined); follow-up executed ($1.10) with results | Recount; EXP-004 |
| §VII | Tipping table on stored labels; numeral check 60%, 63/69 | Tipping on J-QWEN (0.76 / 0.38 at FPR 0.08); numeral check 67%, 73/35; judge agreement table | J-QWEN; reproducible check |
| Table V (claims) | 6 rows | 7 rows incl. script-alternation claim not supported | — |
| Table VII (pairwise) | Caption "b: first condition correct, second wrong" (wrong for rows as listed) | "b: second-named (reference) correct, first wrong" | b counts reference-correct |
| Table IX (models) | Qwen stored only | Stored and J-QWEN noted in text | — |
| Table X (descriptors) | Qwen2.5 chars/token | Qwen3.8 chars/token | Tokenizer |
| Reproducibility | `paper_v2/scripts/make_all.py` (did not exist); spend $0.21 | Script now exists; follow-up $1.10; ledger underpriced, ~$2.1 at list prices | Repo search; Groq pricing |
| Appendix E | Hub "not reachable", tokenizer quantities not recomputed | Recomputed with both tokenizers | — |
| References | 22 | + RomanSetu, Wang et al., Length-controlled AlpacaEval | Related work on romanization and judge bias |
| Figures | Fig. 1 says "Qwen-27B", one judge; Figs. 2–5 stored labels; Fig. 5c Qwen2.5 | All regenerated: correct name, J-QWEN, new Fig. 5 with the budget result | — |

---

## 9. Claims you must not make

* That script alternation (or mixed script) harms factual recall.
* That any result is "robust", "survives every level", or holds "at every level" without naming the budget and judge.
* "Factual recall" as the measured quantity — say judge-assessed accuracy.
* That a human validated the judge, or any human-judge agreement number.
* κ = 0.719, naturalness 4.74/5, or the 300-item "human validation" document (no raw annotation files exist; different data).
* A measured naturalness score or agreement statistic for the prompts (the fluent-speaker review was a yes/no check; say "reviewed by fluent speakers and judged natural and correct").
* That ALLaM-2-7B replicates anything.
* That tokenization is irrelevant (the mediation test is exploratory and weak).
* That the served weights are exactly the public Qwen3.8-27B checkpoint.
* Causal mechanisms (attention, "script boundaries cause …").
* Generalization beyond one model, 20 topics, five languages.

---

## 10. Before submitting to ACL / EMNLP (not needed for the IEEE 10-page version)

Required:
1. Annotate the human-evaluation sample (`results/EXP-004-budget-rejudge/human_eval/`, 210 items) by ≥ 2 readers per language, following `research/HUMAN_EVAL_PROTOCOL.md`; report κ and per-condition judge sensitivity/specificity. This decides which judge is closer to humans.
2. ~~Fluent-speaker check of the 20 templates~~ — **done** (informal yes/no review by speakers of all five languages; record in `research/PROMPT_VALIDATION_PROTOCOL.md` §0: Telugu — Chandrahas Reddy, Akshith Chawla; Hindi, Kannada — Akshith Chawla; Tamil — Kapilan; Bengali — Shamik Mukherjee). Optional: per-item ratings if reviewers ask. Thank the reviewers by name in the Acknowledgements of the camera-ready version (not in the anonymous submission).
3. One more budget run: max_tokens ≥ 1,024 (or an instruction fixing the answer language) on the same 300 prompts, so the cap no longer binds. Estimated cost $1–2 at list prices.
4. Convert to the ACL template: anonymize, 8-page main text, mandatory Limitations section after the conclusion, references before appendices.

Optional: a second informative model (not near floor); more topics (the 25 written propositions).

---

## 11. Regenerating everything

```bash
# from the repository root
python paper_v2/scripts/make_all.py                 # stored labels  -> numbers_original.json
python paper_v2/scripts/make_all.py --labels jqwen  # J-QWEN labels  -> numbers_jqwen.json
python paper_v2/scripts/analyze_exp004.py           # EXP-004        -> numbers_exp004.json
python paper_v2/scripts/make_figures.py             # fig2-fig5.png
python paper_v2/scripts/make_fig1.py                # fig1.png
python paper_v2/scripts/dump_tables_md.py           # all tables as Markdown
python scripts/build_human_eval_sample.py           # human-eval sample (no API calls)
# re-running EXP-004 itself needs GROQ_API_KEY and costs about $1.10:
python scripts/run_exp004_budget_rejudge.py --stage gen
python scripts/run_exp004_budget_rejudge.py --stage judge
```

Dependencies: Python 3.11, numpy, pandas, scipy, statsmodels, tokenizers, matplotlib,
python-docx, openai, python-dotenv. The tokenizer check downloads `Qwen/Qwen2.5-7B` and
`Qwen/Qwen3.8-27B` tokenizers from the Hugging Face hub.
