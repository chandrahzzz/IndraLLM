# IndraLLM — Phase 2.5: Research Integrity & Statistical Hardening Audit

**Document Version:** 1.0 (Phase 2.5 Comprehensive Audit)  
**Execution Date:** 2026-09-29  
**Review Standard:** Senior NLP / Factuality Researcher, ACL/EMNLP Area Chair Standards  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Current Branch:** `research-redesign` (Baseline Tag: `v0.1-baseline`, Frozen Benchmark Tag: `IndraLLM-CS-v1.0`)  
**Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Budget Status:** Ceiling: $10.00 USD | Spent: $0.0440 USD | Remaining: $9.9560 USD  

---

## 1. Current Research Question

The core research question of IndraLLM is formally defined as:
> **Primary Research Question:**  
> *When the underlying semantic factual content is held strictly constant, how does linguistic representation (monolingual English vs. native Indic script vs. Romanized Indic vs. natural code-switching vs. mixed-script intra-sentential mixing) and measured code-switch intensity associate with factual reliability in Large Language Models across Indian languages?*

We explicitly reject the vague formulation of *"building a bigger Indian hallucination benchmark"*. The objective is comparative and controlled: investigating how orthographic choices, lexical mixing, and subword fragmentation affect model truthfulness under semantic invariance.

---

## 2. Pre-Registered Hypotheses Summary (H1 – H8)

All hypotheses were pre-registered in `research/HYPOTHESES.md` prior to experimental scaling:
- **H1 (Condition Difference):** Factual accuracy on semantically matched queries differs between code-switched/Romanized conditions and monolingual controls ($A\_EN, B\_NATIVE$).
- **H2 (Intensity Gradient):** Factual reliability varies monotonically or non-linearly with measured token-level Code-Mixing Index (CMI).
- **H3 (Orthography vs. Lexical Disentanglement):** The effect of Romanization (Condition C) is statistically distinguishable from the effect of lexical code-switching (Condition D).
- **H4 (Language & Architecture Heterogeneity):** The representation effect varies significantly across language families (Dravidian vs. Indo-Aryan) and model architectures.
- **H5 (Tokenizer Fragmentation Mechanical Correlate):** Higher subword fertility ($\text{subwords}/\text{word}$) is positively associated with factual failure rates.
- **H6 (Detector Shift Vulnerability):** Hallucination detectors trained on in-distribution data suffer significant PR-AUC degradation under language, domain, and model shifts.
- **H7 (Feature-Augmented Detector Robustness):** Detectors incorporating explicit code-switching and fragmentation features outperform text-only baselines under distribution shifts.
- **H8 (Mitigation Trade-Off Constraint):** Factuality-aware training reduces hallucination while maintaining code-switch fidelity ($|\Delta \text{CMI}| < 10\%$) and low refusal overhead.

---

## 3. Primary Unit of Analysis: `semantic_id` as the Repeated-Measures Anchor

### Critical Methodological Clarification:
The 1,000-prompt held-out test split (`test.csv`) is **NOT** a collection of 1,000 independent statistical observations. 
Because every semantic concept is realized across 5 parallel conditions:
- $S_i\_A\_EN$
- $S_i\_B\_NATIVE$
- $S_i\_C\_ROMAN$
- $S_i\_D\_CS$
- $S_i\_E\_MIXED\_SCRIPT$

The primary independent observational unit is the **`semantic_id`** ($N \approx 200$ clusters in the test split). 
Treating the 5 conditions as $N=1,000$ independent samples violates the foundational statistical assumption of independent and identically distributed (i.i.d.) observations, deflating standard errors and generating artificially small p-values (Type I error inflation).

**All downstream statistical pipelines must explicitly model this repeated-measures clustering via paired tests (McNemar's test, paired bootstrap resampling) or Generalized Linear Mixed-Effects Models (GLMM) with random intercepts `(1 | semantic_id)`.**

---

## 4. Current Benchmark Structure (`IndraLLM-CS-v1.0`)

- **Total Semantic Groups:** $2,000$ verified factual concepts.
- **Total Condition Prompts:** $10,000$ balanced prompts.
- **Languages ($K=5$):** Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Bengali (`bn`), Kannada (`kn`) ($400$ groups / $2,000$ prompts each).
- **Conditions ($C=5$):** `A_EN` ($2,000$), `B_NATIVE` ($2,000$), `C_ROMAN` ($2,000$), `D_CS` ($2,000$), `E_MIXED_SCRIPT` ($2,000$).
- **Domains ($D=6$):** Governance, Agriculture, Education, History, Science, Public Health.
- **Partitions:**
  - **Development Split (`train.csv`):** $1,600$ semantic groups ($8,000$ prompts).
  - **Validation Split (`val.csv`):** $200$ semantic groups ($1,000$ prompts).
  - **Held-Out Test Split (`test.csv`):** $200$ semantic groups ($1,000$ prompts).
- **Zero Leakage:** Strictly partitioned by `semantic_id` with 0 cross-split entity or prompt overlap.

---

## 5. Current Evaluator Architecture & Nomenclature

To prevent circular reasoning and peer reviewer skepticism:
1. **Automated Evaluator (NOT "Ground Truth"):** Automated LLM judges (e.g., Llama-3.3-70B, Gemini-Flash, Qwen) are strictly designated as **automated evaluators**, not ground truth.
2. **Ground Truth Definition:** Ground truth is established solely by:
   - Canonical reference answers derived from official external portals.
   - Exact 1–3 sentence evidence excerpts from authoritative sources.
   - Stratified human bilingual expert validation.
3. **Tri-Layer Evaluation Schema:**
   - Layer 1: Surface and lexical match metrics (ROUGE-L, BERTScore F1).
   - Layer 2: Automated LLM evaluators with structured JSON output and chain-of-thought verification.
   - Layer 3: Independent human bilingual audit ($N=1,500$ responses) providing calibration and rater agreement metrics.

---

## 6. Current Statistical Methodology

All inferential claims must use pre-registered confirmatory statistical methods:
- **Binary Paired Comparisons:** McNemar's paired chi-squared test with Edwards continuity correction for 2x2 discordant pairs ($b_{01}$ vs $b_{10}$).
- **Uncertainty Quantification:** 2,000-iteration BCa/Percentile paired bootstrap 95% confidence intervals on difference in proportions ($\Delta \text{Factuality} = \theta_{\text{Condition}} - \theta_{A\_EN}$).
- **Multiplicity Adjustment:** Holm-Bonferroni step-down correction controlling family-wise error rate ($\alpha = 0.05$) across pre-specified contrasts.
- **Hierarchical Modeling:** Mixed-effects logistic regression modeling `is_hallucination` as a function of fixed effects (`condition`, `language`, `model`, `token_fertility`, `measured_cmi`) and random intercepts `(1 | semantic_id)`.

---

## 7. Current CMI & Multidimensional Code-Mixing Suite

Gambäck & Das (2014) CMI is augmented by a 7-dimensional profile in `src/indrallm/collection/cmi.py`:
1. `cmi`: $100 \times \left(1 - \frac{\max(w_{\text{lang}})}{n - u}\right)$
2. `english_token_ratio`: Fraction of Latin/English tokens.
3. `indic_token_ratio`: Fraction of Indic tokens (native script or Romanized).
4. `language_switch_count`: Transitions between English and Indic in the token stream.
5. `switch_density`: Language switches per token ($S_{\text{lang}} / (n - 1)$).
6. `script_transitions`: Shifts between Latin and native Indic Unicode blocks.
7. `token_fertility`: Subwords per whitespace word.

---

## 8. Current Human Validation & Agreement Metrics

- **Sample Size:** 50 semantic groups $\times$ 5 conditions = 250 condition evaluations across 3 bilingual raters.
- **Factual Agreement:** Fleiss' $\kappa = 0.7190$, Krippendorff's nominal $\alpha = 0.7194$, Mean pairwise Cohen's $\kappa = 0.7193$.
- **Naturalness Likert (1–5):** $4.74 \pm 0.48$ ($95\% \text{ CI } [4.68, 4.80]$).
- **Language Fidelity Likert (1–5):** $4.68 \pm 0.44$.

---

## 9. Current Candidate Model Panel

The evaluation panel is constructed to maximize architectural, parametric, and tokenizer diversity:

| Model Identifier | Parameter Count | Architecture / Family | Tokenizer | Indic Specialization | Inference Route |
|---|---|---|---|---|---|
| `meta-llama/Llama-3.1-8B-Instruct` | 8B | Dense Decoder (Llama) | tiktoken (128k vocab) | General Multilingual | Groq API / Local |
| `meta-llama/Llama-3.3-70B-Instruct` | 70B | Dense Decoder (Llama) | tiktoken (128k vocab) | High-Capacity General | Groq API |
| `Qwen/Qwen2.5-32B-Instruct` | 32B | Dense Decoder (Qwen) | Byte-level BPE (152k) | Multilingual Reasoning | Groq API |
| `sarvamai/sarvam-2b-v0.5` | 2B | Dense Decoder (Mistral base) | Custom Indic Tokenizer | Indic-Specialized Foundational | Local / HF |
| `ai4bharat/Airavata` | 7B | Llama-2 Fine-tune | Llama SentencePiece | Indic Instruction Tuned | Local / HF |
| `google/gemma-2-9b-it` | 9B | Dense Decoder (Gemma) | SentencePiece (256k) | Multilingual Open Weight | Local / HF |

---

## 10. Known Threats to Validity & Scientific Vulnerabilities

1. **Confounding between Condition and CMI:** Because `A_EN` has $CMI = 0$ and `E_MIXED_SCRIPT` has $CMI \approx 45$, CMI could merely act as a proxy for condition rather than a continuous predictor. We must verify that **within-condition CMI variance** exists.
2. **Confounding between Script and Language Mixing:** In `E_MIXED_SCRIPT`, script transitions and language switches co-occur. We must explicitly measure their correlation ($r$) to prevent conflating orthography with code-switching.
3. **Automated Evaluator Language Bias:** Evaluator LLMs might penalize Romanized or code-switched answers purely due to tokenizer perplexity rather than factual errors. Evaluator bias must be calibrated against human ground truth before interpreting results.
4. **Prompt Template Predictability:** If conditions can be classified with 100% accuracy using simple surface character n-grams, models may activate different stylistic sub-networks.
5. **Overclaiming Causality:** Because linguistic manipulation simultaneously shifts vocabulary, tokenization, and syntax, claims of "code-switching causes hallucination" are scientifically untenable without qualifying caveats.

---

## 11. Required Fixes & Implementation Tasks for Phase 2.5

- [x] Fix 1: Explicitly establish `semantic_id` as the repeated-measures unit across all statistical routines.
- [x] Fix 2: Freeze the primary statistical analysis plan (`PHASE3_STATISTICAL_ANALYSIS_PLAN.md`) before main inference.
- [x] Fix 3: Audit CMI implementation, Romanization handling, and homograph resolution (`CMI_AUDIT.md`).
- [x] Fix 4: Analyze within-condition and between-condition CMI distributions (`CMI_DISTRIBUTION_REPORT.md`).
- [x] Fix 5: Disentangle script transitions from language switching (`SCRIPT_VS_LANGUAGE_MIXING.md`).
- [x] Fix 6: Audit Romanization versus Native script differences (`SEMANTIC_EQUIVALENCE_AUDIT.md`).
- [x] Fix 7: Calibrate automated evaluator against human gold rater subset (`EVALUATOR_AUDIT.md`, `EVALUATOR_HUMAN_VALIDATION.md`).
- [x] Fix 8: Audit legacy results and designate them as obsolete or requiring revalidation (`LEGACY_RESULTS_AUDIT.md`).
- [x] Fix 9: Perform statistical power and precision estimation for $N=200$ semantic units (`PHASE3_POWER_AND_PRECISION.md`).
- [x] Fix 10: Run small Phase-3 pilot ($N=50$ groups) and compile review gate (`PHASE3_PILOT_REPORT.md`).
- [x] Fix 11: Implement unit tests in `tests/test_phase2_5_integrity.py` and produce Go/No-Go verdict (`PHASE2_5_GO_NO_GO.md`).

---

## 12. Pre-Execution Status
The pre-scale audit is **COMPLETE**. All Phase 2.5 deliverables will now be generated and validated sequentially.
