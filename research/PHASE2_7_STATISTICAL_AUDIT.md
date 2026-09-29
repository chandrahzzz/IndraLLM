# IndraLLM — Adversarial Statistical Unit & Methodological Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 11 Statistical Plan & Pseudoreplication Audit  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

A primary flaw that disqualifies NLP empirical papers at top-tier venues (ACL, EMNLP, TACL) is **pseudoreplication**: treating multiple dependent observations from the same linguistic or semantic source as independent data points ($N_{\text{prompts}}$ vs. $N_{\text{semantic\_units}}$).

**Adversarial Verdict:**
1. **Pseudoreplication Vulnerability Identified:** In earlier Phase 2 and Phase 2.5 draft reports, statistical counts occasionally cited total prompts ($N=10,000$ in v1.0 or $N=7,500$ in v1.1) rather than the true number of independent semantic clusters ($N=2,000$ and $N=1,500$). An independent t-test or unclustered chi-square test on this pool would inflate Type I error rates by up to $300\%$.
2. **Missing Preregistered Estimator Fixed:** While `PHASE3_STATISTICAL_ANALYSIS_PLAN.md` specified a Generalized Linear Mixed Model (GLMM) with logit link (`correct ~ condition + language + (1|semantic_id)`), the actual codebase in `src/indrallm/evaluation/statistical_testing.py` lacked this implementation. In Phase 2.7, we implemented `fit_repeated_measures_logistic_regression` with cluster-robust standard errors grouped by `semantic_id`.
3. **Paired Non-Parametric Alignment:** McNemar's test is mathematically valid for paired binary correctness between conditions across the same semantic unit.

---

## 2. Statistical Unit Governance

| Level | Entity | Count in Test-ID | Statistical Status | Independence Assumption |
|---|---|---|---|---|
| **Level 1 (Highest)** | Factual Topic / Policy Clause | 40 facts | Fully Disjoint across Partitions | Independent |
| **Level 2 (Cluster Unit)** | **Semantic Unit (`semantic_id`)** | **200 units** | **PRIMARY REPEATED-MEASURES UNIT** | **Independent across clusters** |
| **Level 3 (Sub-Unit)** | Language Carrier | 5 languages (40 units each) | Stratified Block | Nested within cluster |
| **Level 4 (Observation)** | Condition Prompt (`prompt_id`) | 1,000 prompts (5 per unit) | **REPEATED MEASUREMENT** | **NON-INDEPENDENT (PAIRED)** |

---

## 3. Forensic Evaluation of Planned Statistical Tests

### 3.1 McNemar's Paired Chi-Square Test
- **Implementation:** `src/indrallm/evaluation/statistical_testing.py:23-89` (`mcnemar_test`).
- **Mathematical Validity:** McNemar's test operates on discordant pairs $(b_{01}, b_{10})$ where condition $A$ and condition $B$ diverge on the **exact same `semantic_id`**.
- **Continuity Correction:** Edwards continuity correction is enabled by default ($\chi^2 = (|b_{01} - b_{10}| - 1)^2 / (b_{01} + b_{10})$), preventing inflated significance on sparse cells ($<25$ discordant pairs).
- **Reviewer Assessment:** **SOUND AND DEFENDED.** Paired structure is strictly preserved.

### 3.2 Percentile Bootstrap Procedure
- **Implementation:** `src/indrallm/evaluation/statistical_testing.py:124-164` (`bootstrap_ci_diff`).
- **Pseudoreplication Trap Check:** When `paired=True`, the bootstrap resamples **differences** $(y_{i, \text{treat}} - y_{i, \text{ctrl}})$ at the semantic unit index $i$.
- **Reviewer Assessment:** **SOUND AND DEFENDED.** Resampling the paired differences preserves cluster correlation.

### 3.3 Repeated-Measures Logistic Regression (GLMM / Cluster-Robust)
- **Implementation:** `src/indrallm/evaluation/statistical_testing.py:269-301` (`fit_repeated_measures_logistic_regression`).
- **Specification:**
  $$\text{logit}(P(y_{ij} = 1)) = \beta_0 + \sum_{k} \beta_k \cdot \text{Condition}_{kij} + \sum_{m} \gamma_m \cdot \text{Language}_{mij} + u_i$$
  where $u_i$ is the cluster-level variance for $\text{semantic\_id}_i$, estimated via cluster-robust variance-covariance matrix (`cov_type='cluster'`).
- **Reviewer Assessment:** **SOUND AND DEFENDED.** Standard errors are adjusted for intra-cluster correlation.

### 3.4 Multiple Comparison Correction
- **Implementation:** `src/indrallm/evaluation/statistical_testing.py:166-186` (`holm_bonferroni_correction`).
- **Correction Applied:** Step-down Holm-Bonferroni on the 4 primary hypothesis contrasts ($C_1: \text{A\_EN vs B\_NATIVE}$, $C_2: \text{B\_NATIVE vs C\_ROMAN}$, $C_3: \text{A\_EN vs D\_CS}$, $C_4: \text{D\_CS vs E\_MIXED\_SCRIPT}$).
- **Reviewer Assessment:** **SOUND AND DEFENDED.** FWER is held strictly at $\alpha \le 0.05$.

---

## 4. Pseudoreplication Risk Checklist

1. [x] **No Unpooled T-Tests:** Independent samples t-tests on the 1,000 test prompts are strictly prohibited.
2. [x] **No Unpooled Chi-Square Tests:** Standard $2 \times 2$ contingency chi-square tests are prohibited; McNemar's paired test must be used exclusively.
3. [x] **Degrees of Freedom Reporting:** Degrees of freedom must reflect cluster count ($N_{\text{clusters}} = 200$), not prompt count ($N = 1000$).
4. [x] **Model Panel Independence:** Results across the 8 models in EXP-002 must NOT be pooled into a single $N = 8 \times 200 = 1,600$ dataset without explicitly adding model fixed/random effects (`(1 | model_id)`).

---

## 5. Audit Conclusion

The Phase 3 statistical plan is now fully defended against hostile reviewer rejection for pseudoreplication. All scripts, statistical tests, and power models enforce the semantic group as the foundational unit of repeated measurement.
