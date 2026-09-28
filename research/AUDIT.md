# IndraLLM — Scientific Audit & Methodological Critical Review

**Date:** 2026-09-29  
**Reviewer Profile:** Senior NLP / Multilingual LLM Researcher, Factuality Experimentalist, Peer Reviewer (ACL/EMNLP/TACL)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Baseline Tag:** `v0.1-baseline` (Commit `7c9680a2efc08e2c8d12010a911f92cdf857d9a2`)  
**Status:** Pre-transformation Comprehensive Audit  

---

## 1. Executive Summary & Review Verdict

IndraLLM was originally conceived as an end-to-end pipeline to benchmark, detect, and mitigate hallucinations in Large Language Models (LLMs) when prompted with code-switched Indian language text (Hindi, Tamil, Telugu, Bengali, Kannada mixed with English). The preliminary pipeline demonstrates notable software engineering discipline (e.g., QID-level grouped splitting to prevent leakage, early detection and correction of a BERTScore linguistic confound). 

However, from the standpoint of publication in a premier NLP venue (ACL, EMNLP, NAACL, TACL), **the current incarnation is methodologically fragile and scientifically incomplete**. It treats code-switching as an unstructured monolith, relies on unverified teacher generations and single-model automated LLM judging without human grounding, lacks matched experimental controls, and reports raw point estimates devoid of statistical uncertainty or formal significance testing.

This audit provides an unvarnished dissection of the existing system across architecture, datasets, models, evaluation, detection, mitigation, claims, and vulnerabilities.

---

## A. Current Architecture

The legacy pipeline follows an eight-stage serial flow:
```
[1. Collection: Hand-written + Gemini Seeds + Scraped Reddit]
                           │
                           ▼
         [2. Code-Switch Filter (Token / Script / Lexicon)]
                           │
                           ▼
           [3. Gold Context & QA Generation (Gemini)]
                           │
                           ▼
       [4. Answering Models (4 Groq APIs: Llama/Qwen/GPT)]
                           │
                           ▼
   [5. Automated LLM Judge (Llama-3.1-8B-Instant via Groq)]
                           │
                           ▼
          [6. Benchmark Consolidation & QID Splitting]
                ├── Train (80%) ── Val (10%) ── Test (10%)
                │
                ├── [7. Detector: IndicBERTv2 Binary Classifier]
                │
                └── [8. Mitigation: Teacher Distillation (LoRA SFT on Sarvam-2B)]
```

### Architectural Analysis:
- **Modularity:** Modules are separated into `indrallm.collection`, `indrallm.annotation`, `indrallm.generation`, `indrallm.detection`, and `indrallm.mitigation`.
- **Failure Point 1 (Serial Dependency on Unverified LLM Outputs):** Gemini synthesizes the context and gold answers; Llama-3-70B synthesizes the teacher targets; Llama-3.1-8B judges correctness. Synthetic data passes into synthetic evaluation without external human calibration or factual ground-truthing against verified corpora.
- **Failure Point 2 (Absence of Controlled Semantic Counterparts):** Questions are created in isolation. Answering models receive code-switched queries without parallel evaluation on monolingual English or native-script baselines, rendering it impossible to isolate the causal effect of code-switching from question difficulty or domain sparsity.

---

## B. Current Datasets

### 1. Sizes and Distributions
- **Total benchmark items:** 2,649 judged `(question, model_answer)` pairs.
- **Unique Questions ($N_{qid}$):** 702 distinct prompts.
- **Languages:** 5 Indic languages paired with English (all romanized or mixed):
  - Tamil (`ta`): ~140 QIDs, ~530 evaluated pairs
  - Hindi (`hi`): ~140 QIDs, ~530 evaluated pairs
  - Telugu (`te`): ~140 QIDs, ~530 evaluated pairs
  - Bengali (`bn`): ~140 QIDs, ~530 evaluated pairs
  - Kannada (`kn`): ~142 QIDs, ~529 evaluated pairs
- **Domains:** 4 nominal domains: Health (744 pairs), Government (717 pairs), Education (600 pairs), Agriculture (588 pairs).
- **Label Distribution:** 270 hallucinated pairs (10.19%), 2,379 faithful pairs (89.81%).

### 2. Code-Switching Construction & Scripts
- Questions are overwhelmingly **Romanized Indic mixed with English** (e.g., *"Tamil Nadu oda capital enna?"*).
- Filtering logic (`codeswitch_filter.py`) accepts an input if:
  1. It mixes native Unicode script blocks and Latin script ($min\_ratio \ge 0.15$), OR
  2. fastText (`lid.176.bin`) detects bilingual language distribution, OR
  3. A heuristic token-vote matches high-frequency romanized function-word lexicons (e.g., *enna, iruku, chahiye, kavali, korbo, beku*).
- **Critical Flaw:** The dataset treats Romanized Indic, native Indic, and mixed-script text as an undifferentiated group. It does not measure or manipulate Code-Mixing Index (CMI), switch-point frequency, or burstiness.

### 3. Splits & Leakage
- **Split Strategy:** Stratified random split grouped strictly by `qid` (Train: 491 QIDs, Val: 105 QIDs, Test: 106 QIDs).
- **Leakage Assessment:** QID-level grouping successfully prevents verbatim question leakage across train/test splits. 
- **Vulnerability:** **Semantic leakage across domains and question templates remains unconstrained**. Many questions were synthetically generated in batches by Gemini from similar seed prompts, producing near-duplicate syntactic structures and identical factual entities across splits.

---

## C. Current Models

The existing repository incorporates an ad-hoc selection of models across distinct functional roles:

| Role | Model Identifier | Parameter Count | Host / Provider | Context / Config |
|---|---|---|---|---|
| **Answering Model 1** | `llama-3.1-8b-instant` | 8B | Groq Cloud API | Temp: 0.3, Max tokens: 256 |
| **Answering Model 2** | `llama-3.3-70b-versatile` | 70B | Groq Cloud API | Temp: 0.3, Max tokens: 256 |
| **Answering Model 3** | `qwen/qwen3.6-27b` | 27B | Groq Cloud API | Temp: 0.3, Max tokens: 256 |
| **Answering Model 4** | `openai/gpt-oss-20b` | 20B | Groq Cloud API | Temp: 0.3, Max tokens: 256 |
| **Seed & Gold Generator** | `gemini-2.5-flash` / `lite` | Proprietary | Google AI Studio | Default generation API |
| **LLM Judge** | `llama-3.1-8b-instant` | 8B | Groq Cloud API | Greedy (Temp: 0.0), Single line |
| **Detector** | `ai4bharat/IndicBERTv2-MLM-only` | 278M | PyTorch / HF (Colab T4) | 5 epochs, lr=2e-5, max_len=256 |
| **Mitigation Student** | `sarvamai/sarvam-2b-v0.5` | 2B | HF Local (4-bit QLoRA) | $r=8, \alpha=16$, lr=2e-4 |
| **Mitigation Teacher** | `llama-3.3-70b-versatile` | 70B | Groq Cloud API | Zero-shot code-switch prompt |

---

## D. Current Evaluation

### 1. Hallucination Definition & Operationalization
- Hallucination is defined in `llm_judge_label.py` purely as a binary verdict:
  ```
  VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>
  ```
- **Operational Deficiencies:**
  - No taxonomy of errors (e.g., entity substitution vs. fabricated relation vs. temporal inconsistency vs. unanswerable extrapolation).
  - No distinction between minor partial hallucination (e.g., correct entity, incorrect date) and catastrophic confabulation.
  - No penalty or explicit category for refusals, evasion, or language collapse (reverting to English).

### 2. Judge Model Prompt & Vulnerabilities
- Prompt instructs: *"You are grading whether a model's ANSWER to a user QUESTION is factually correct. You are given a trusted GOLD answer... Judge ONLY factual correctness."*
- **Vulnerabilities:**
  - Evaluated on a relatively small model (`llama-3.1-8b-instant`). 8B models are known to exhibit position bias, length bias, and severe comprehension deficits in romanized South Asian languages.
  - No calibration, no confidence scores, no temperature sampling.
  - Zero inter-rater reliability validation against human bilingual experts.

### 3. Statistical Testing & Aggregation
- **Absence of Uncertainty:** Hallucination rates are reported purely as unweighted sample means (e.g., "Sarvam-2B 64.9%", "Qwen 0.4%").
- **Zero statistical hypothesis testing:** No bootstrap confidence intervals, no McNemar's tests, no permutation tests, no ANOVA or mixed-effects models.

---

## E. Current Detector

### 1. Architecture & Input Pipeline
- **Base Model:** `ai4bharat/IndicBERTv2-MLM-only` (12-layer transformer, ALBERT-style parameters).
- **Input Representation:** `"<question> [SEP] <answer>"`.
- **Loss:** Class-weighted Cross-Entropy loss ($w_1 = \frac{N_{negative}}{N_{positive}} \approx 9.8$) to mitigate extreme class imbalance (~10% positive).

### 2. Performance Metrics Reported
- Test ROC-AUC: **0.75** (per-language: Tamil 0.86, Bengali 0.77, Telugu 0.77, Kannada 0.68, Hindi 0.65).
- Test F1: **0.35** (at argmax 0.5 decision threshold).

### 3. Critical Detector Weaknesses
- **Confounded Supervision:** IndicBERT is trained against Llama-3.1-8B LLM-judge labels, meaning it trains on the judge's systemic biases.
- **Inadequate Metric:** Reporting ROC-AUC on a 90:10 imbalanced dataset is deceptive; PR-AUC (Precision-Recall AUC) is the required standard for rare-class detection.
- **No Out-of-Distribution (OOD) Testing:** The detector is tested only on an in-distribution random split of questions. It has never been tested on unseen models, unseen domains, unseen languages, or unseen code-switching styles.
- **Surface Artifact Susceptibility:** The model may simply learn to associate specific token patterns, answer lengths, or vocabulary distributions with errors rather than verifying factual consistency.

---

## F. Current Mitigation

### 1. Distillation Methodology
- **Objective:** Sequence-level knowledge distillation via QLoRA SFT on `sarvamai/sarvam-2b-v0.5`.
- **Target Selection:** For each QID, the best performing answering model (`qwen` > `llama70b` > `llama3` > `gpt-oss`) that received a `judge_label == 0` is selected, with Gemini gold as fallback.
- **Reported Result:** Sarvam-2B hallucination rate dropped from **64.9% → 26.8% (-58.7% relative)** on a test set of $N=100$.

### 2. Methodological Weaknesses
- **Tiny Test Sample Size:** Evaluated on only $N=100$ test questions ($n \approx 17-20$ per language). An empirical shift of 38 percentage points on 100 items has wide binomial confidence intervals ($\pm 9.5\%$) and was evaluated over a single unseeded run.
- **Circular Judge Evaluation:** The exact same LLM judge (`llama-3.1-8b-instant`) that filtered the training data was used to evaluate the test reduction, introducing massive circular evaluation bias.
- **Untracked Trade-offs:** Did the model simply learn to give short, generic answers? Did it lose grammatical coherence? The reported increase in "code-switching" was measured via a crude lexicon-hit heuristic, not human evaluation or validated CMI.

---

## G. Critical Audit of Current Claims

| Claim in Repository | Classification | Scientific Justification |
|---|---|---|
| *"Benchmark: 2,649 judged QA pairs across 5 languages"* | **Experimentally Supported** (with caveats) | The rows exist and labels are parsed, but labels are solely machine-generated without human gold calibration. |
| *"Detector: IndicBERT hallucination detector at ROC-AUC 0.75"* | **Weakly Supported** | ROC-AUC is 0.75 on random test split, but F1 is only 0.35, PR-AUC is unreported, and cross-distribution generalization is unproven. |
| *"Mitigation: Teacher distillation cuts Sarvam-2B hallucination 64.9% -> 26.8%"* | **Weakly Supported / Potentially Misleading** | Evaluated on only $N=100$ items, using the same LLM judge as supervisor; no multi-seed verification, no human validation. |
| *"Confound gone: corr(indic_fraction, label) = +0.04"* | **Experimentally Supported** | Linear correlation between Indic character fraction and binary judge label is indeed low ($r \approx 0.04$). |
| *"Surface-linguistic features cannot detect hallucinations (AUC ~0.50)"* | **Weakly Supported** | True for the 3 specific ad-hoc features implemented, but does not prove linguistic features have zero utility when conditioned on semantics or tokenization. |

---

## H. Reviewer Attack Simulation (Hostile but Fair ACL/EMNLP Reviewer)

> ### Reviewer 1 (Score: 2/5 — Reject)
> *"This paper introduces another benchmark for Indian languages, but the contribution is primarily an engineering artifact. The entire dataset relies on LLM-generated questions, LLM-generated gold answers, and an 8B LLM judge. There is no human evaluation whatsoever. How do we know the LLM judge is not hallucinating its verdicts? Furthermore, the mitigation claims are based on an evaluation of just 100 examples. Without human gold validation, statistical significance testing, or a controlled experimental variable, this does not meet the scientific standards of ACL."*

> ### Reviewer 2 (Score: 2.5/5 — Reject)
> *"The central premise claims to study code-switching, but the experimental design has no controls. If an LLM hallucinates on a code-switched Hindi question, is it because of the code-switching, because the question is difficult, or because the model has weak Hindi representations? Without matched monolingual English and native-script Hindi baselines for the exact same semantic question, causal claims cannot be substantiated."*

> ### Reviewer 3 (Score: 2/5 — Reject)
> *"The detector section lacks basic rigorous evaluation. Reporting ROC-AUC on a 90:10 imbalanced dataset masks severe precision issues (F1 is only 0.35). Moreover, there is no out-of-distribution evaluation: does the detector generalize across unseen models or unseen languages, or is it merely memorizing vocabulary artifacts from the training split?"*

---

## Summary of Architectural Transitions Required

| Dimension | Legacy IndraLLM (`v0.1-baseline`) | Transformed IndraLLM (`research-redesign`) |
|---|---|---|
| **Core Research Question** | "Can we build a benchmark and train a detector?" | "How do code-switching, script choice, and mixing intensity causally affect factual reliability when semantic content is held constant?" |
| **Dataset Structure** | Independent isolated code-switched questions | Semantically matched 5-condition tuples ($S_{qid\_EN}, S_{qid\_Native}, S_{qid\_Roman}, S_{qid\_CS}, S_{qid\_Mixed}$) |
| **Ground Truth** | Gemini synthetic gold | Authoritative evidence-backed reference answers with verifiable sources |
| **Evaluation Layers** | Single 8B LLM judge | Tri-layer: Automated metrics + Multi-LLM panel + Human bilingual gold validation |
| **Code-Switching** | Binary classification via lexicon hits | Quantified continuous metric (CMI, switch points, script transitions) |
| **Detector Benchmark** | Single IndicBERT model | Multi-model benchmark (TF-IDF, XLM-R, IndicBERT, Feature-augmented) across 6 distribution shifts |
| **Mitigation Study** | Single LoRA distillation run ($N=100$) | Full controlled ablation ($M_0$ Base, $M_1$ SFT, $M_2$ Distill, $M_3$ Filtered Distill, $M_4$ DPO) with human preference evaluation |
| **Statistics** | Raw percentages | McNemar's tests, Bootstrap 95% CIs, Holm-Bonferroni corrections, Mixed-effects logistic regression |
