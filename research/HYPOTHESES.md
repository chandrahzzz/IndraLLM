# IndraLLM — Pre-Registered Scientific Hypotheses

**Document Version:** 1.0 (Pre-Registration)  
**Date:** 2026-09-29  
**Status:** Frozen Prior to Benchmark Scaling  
**Primary Research Question:**  
*When underlying semantic content is held constant, how does linguistic code-switching, script choice, and code-switch intensity affect factual reliability in Large Language Models for Indian languages?*

---

## Methodological Commitment to Scientific Honesty
In accordance with pre-registration standards (Nosek et al., 2018; van Miltenburg et al., 2021 for NLP):
1. **Hypotheses are immutable post-registration:** No hypothesis defined herein will be modified, re-framed, or post-hoc justified after empirical results are collected.
2. **Null Results are First-Class Scientific Findings:** If empirical evidence fails to reject the null hypothesis, the null result will be reported in full detail in `research/NEGATIVE_RESULTS.md` and in the final publication.
3. **Exploratory vs. Confirmatory Distinction:** All statistical tests mapped to H1–H8 are confirmatory. Any subsequent unplanned analyses will be explicitly designated as *exploratory*.

---

## Pre-Registered Hypotheses (H1 – H8)

### H1: Condition-Dependent Factual Reliability
- **Formal Statement:** Controlling for underlying semantic content via matched query tuples, model factual accuracy and hallucination rates differ between code-switched inputs and monolingual controls (English and Native-script).
- **Null Hypothesis ($H_{0,1}$):** $\theta_{\text{CS}} = \theta_{\text{Control}}$, where $\theta$ represents the factual accuracy rate on semantically paired questions.
- **Alternative Hypothesis ($H_{1,1}$):** $\theta_{\text{CS}} \neq \theta_{\text{Control}}$.
- **Operationalization:** Paired binary outcomes on matched semantic IDs across Condition A (English), Condition B (Native Monolingual), Condition D (Natural Code-Switching).
- **Primary Statistical Test:** McNemar's paired test for binary accuracy across matched pairs; two-sided paired permutation test; 95% bootstrap confidence intervals for difference in proportions ($\Delta \theta$).
- **Family-wise Error Rate Control:** Holm-Bonferroni step-down procedure ($\alpha = 0.05$).

### H2: Code-Switch Intensity Gradient
- **Formal Statement:** Within code-switched interactions, factual reliability varies monotonically or non-linearly with measured linguistic code-switch intensity (Code-Mixing Index, CMI).
- **Null Hypothesis ($H_{0,2}$):** The regression coefficient $\beta_{\text{CMI}} = 0$ in a mixed-effects logistic regression predicting binary hallucination.
- **Alternative Hypothesis ($H_{1,2}$):** $\beta_{\text{CMI}} \neq 0$.
- **Operationalization:** CMI computed at the token level using validated token-level Language Identification (LID):
  $$\text{CMI} = \begin{cases} 100 \times \left(1 - \frac{\max(w_{lang})}{n - u}\right) & \text{if } n > u \\ 0 & \text{otherwise} \end{cases}$$
- **Primary Statistical Test:** Generalized Linear Mixed-Effects Model (GLMM) with logit link, controlling for question length, language, and random intercepts for question ID and model ID.

### H3: Orthographic vs. Linguistic Disentanglement
- **Formal Statement:** The effect of Romanization (Latin script rendering of Indic phonology) on factual reliability is statistically distinguishable from the effect of lexical code-switching itself.
- **Null Hypothesis ($H_{0,3}$):** $\Delta_{\text{Native} \to \text{Roman}} = \Delta_{\text{Native} \to \text{CS}}$, meaning orthographic transliteration produces no distinct error margin relative to lexical language switching.
- **Alternative Hypothesis ($H_{1,3}$):** Orthographic shift (Condition B $\to$ Condition C) accounts for a significant fraction of variance independent of lexical mixing (Condition B $\to$ Condition D).
- **Primary Statistical Test:** Two-way repeated-measures ANOVA / ordinal regression comparing orthogonal factors: Script (Native vs. Latin) $\times$ Lexical State (Monolingual vs. Code-Switched).

### H4: Heterogeneity Across Languages and Model Architectures
- **Formal Statement:** The magnitude and direction of the code-switching effect on factual reliability vary significantly across the 5 target Indian languages (Hindi, Tamil, Telugu, Bengali, Kannada) and across model architectures (Indic-focused vs. multilingual generalist).
- **Null Hypothesis ($H_{0,4}$):** Interaction terms $\beta_{\text{Condition} \times \text{Language}} = 0$ and $\beta_{\text{Condition} \times \text{ModelFamily}} = 0$.
- **Alternative Hypothesis ($H_{1,4}$):** Interaction terms are non-zero ($p < 0.05$).
- **Operationalization:** Multi-factor mixed-effects logistic regression testing interaction effects between condition, language family/resource tier, and model pre-training exposure.

### H5: Tokenizer Fragmentation as a Mechanical Correlate
- **Formal Statement:** Elevated token fragmentation (higher subword tokens per word / lower fertility) under code-switched and Romanized conditions is positively associated with factual failure rates.
- **Null Hypothesis ($H_{0,5}$):** The correlation between token fertility ratio $\rho_{\text{fertility}} = \frac{N_{\text{subwords}}}{N_{\text{words}}}$ and hallucination probability is zero ($\tau = 0$).
- **Alternative Hypothesis ($H_{1,5}$):** Kendalls's $\tau > 0$ or Spearman's $\rho > 0$ ($p < 0.01$).
- **Operationalization:** Subword segmentation profile calculated for each tokenizer (Llama-3 tiktoken, Qwen BPE, IndicBERT SentencePiece, Sarvam tokenizer). Token fertility plotted against empirical error rate across conditions.

### H6: Vulnerability of Hallucination Detectors to Distribution Shifts
- **Formal Statement:** Hallucination detectors trained on in-distribution (ID) code-switched data experience significant performance degradation when evaluated under language-disjoint, model-disjoint, or domain-disjoint shifts.
- **Null Hypothesis ($H_{0,6}$):** $\text{PR-AUC}_{\text{OOD}} \ge \text{PR-AUC}_{\text{ID}} - \epsilon$ (where $\epsilon = 0.05$).
- **Alternative Hypothesis ($H_{1,6}$):** $\text{PR-AUC}_{\text{OOD}} < \text{PR-AUC}_{\text{ID}} - 0.05$ across at least 3 of 4 out-of-distribution evaluation splits.
- **Operationalization:** Leave-One-Language-Out (LOLO), Leave-One-Model-Out (LOMO), and Leave-One-Domain-Out (LODO) cross-validation evaluation.

### H7: Robustness Gain via Multimodal Linguistic & Token Features
- **Formal Statement:** A hallucination detector that incorporates explicit code-switching indicators (CMI, script transitions) and token fragmentation features achieves higher out-of-distribution PR-AUC than text-only or artifact-only baselines.
- **Null Hypothesis ($H_{0,7}$):** $\text{PR-AUC}_{\text{Proposed, OOD}} \le \text{PR-AUC}_{\text{Text-Only Baseline, OOD}}$.
- **Alternative Hypothesis ($H_{1,7}$):** $\text{PR-AUC}_{\text{Proposed, OOD}} > \text{PR-AUC}_{\text{Text-Only Baseline, OOD}}$ with $p < 0.05$ via Delong's test / bootstrap test for difference in PR-AUC.

### H8: Factuality Mitigation Trade-off Constraint
- **Formal Statement:** Factuality-targeted fine-tuning (distillation / preference optimization) can achieve significant hallucination reduction while maintaining code-switching fidelity (CMI within 10% of reference) and conversational naturalness as evaluated by human bilingual judges.
- **Null Hypothesis ($H_{0,8}$):** Factuality reduction occurs only with a concomitant collapse in code-switch fidelity ($|\Delta \text{CMI}| > 25\%$) or significant increase in refusal rate ($p < 0.05$).
- **Alternative Hypothesis ($H_{1,8}$):** The Pareto frontier allows $\ge 30\%$ relative hallucination reduction with $< 10\%$ shift in CMI and $< 5\%$ shift in refusal rate.
- **Operationalization:** Joint evaluation of Hallucination Rate, CMI Retention, Language Identification distribution, and Human Naturalness Likert scores (1–5) on matched test samples.

---

## Summary Protocol & Decision Thresholds

| Hypothesis | Primary Target Metric | Confirmatory Test | Significance Level ($\alpha$) |
|---|---|---|---|
| **H1** | $\Delta$ Factual Accuracy | McNemar's Test + Bootstrap 95% CI | $\alpha = 0.05$ (Holm-corrected) |
| **H2** | Hallucination Odds vs. CMI | GLMM logit slope $\beta_{\text{CMI}}$ | $\alpha = 0.01$ |
| **H3** | Native vs. Roman vs. CS Variance | 2-way RM-ANOVA / Ordinal GLM | $\alpha = 0.05$ |
| **H4** | Condition $\times$ Language Interaction | GLMM Wald Chi-square test | $\alpha = 0.05$ |
| **H5** | Token Fertility vs. Error | Kendall's $\tau$ correlation | $\alpha = 0.01$ |
| **H6** | $\Delta \text{PR-AUC}$ (ID vs. OOD) | Bootstrap PR-AUC difference | $\alpha = 0.05$ |
| **H7** | Feature-augmented OOD Gain | DeLong's test / Bootstrap PR-AUC | $\alpha = 0.05$ |
| **H8** | Multi-objective Pareto retention | Paired t-test on human Likert + CMI $\Delta$ | $\alpha = 0.05$ |
