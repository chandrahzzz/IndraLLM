# IndraLLM — Phase 3.5: Audit 2 — Hierarchical Unit-of-Analysis Audit
## Multi-Level Clustering, Pseudoreplication Detection, and Degrees of Freedom

**Document Version:** 1.0 (Post-Execution Forensic Audit)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `1d4a65c`  

---

## 1. Executive Summary

A critical threat to experimental validity in NLP benchmarking is **pseudoreplication**—treating correlated prompts derived from the same question or template as mutually independent observations. This artificially inflates sample size $N$, shrinks standard errors, and produces spuriously low $p$-values.

This audit investigated the hierarchical dependency structure of `IndraLLM-CS-v1.1-CANDIDATE` and evaluated whether the Phase 3 statistical conclusions survive when degrees of freedom are restricted to higher-order clusters.

### Key Audit Findings:
1. **Three-Level Hierarchical Nesting:** The Authentic Core (`Test-OOD`) contains:
   - **Level 1 (Prompt Observations):** $N = 500$ prompts per model.
   - **Level 2 (Semantic Group Clusters):** $N = 100$ semantic clusters (each containing 5 condition prompts).
   - **Level 3 (Base Factual Topics):** $N = 20$ base statutory propositions (each replicated across 5 target languages).
2. **Phase 3 Statistical Rigor:** Phase 3 correctly rejected naive prompt-level independence ($N=500$) and conducted its primary paired tests on Level 2 (`semantic_id`, $N=100$).
3. **Conservative Level 3 Stress Test ($N=20$):** When clustered at the coarsest level (20 base factual topics):
   - **Orthographic Alternation (`E_MIXED_SCRIPT`):** Remains rock-solid significant ($\beta = -1.7280, p = 0.0005$).
   - **Native Brahmic Script (`B_NATIVE`):** Remains rock-solid significant ($\beta = -1.5198, p < 0.0001$).
   - **Romanized Indic (`C_ROMAN`):** Remains rock-solid significant ($\beta = -1.2835, p = 0.0004$).
   - **Romanized Code-Switching (`D_CS`):** Becomes marginally significant ($\beta = -0.8572, p = 0.0528$), revealing that the $D\_CS$ contrast is sensitive to topic-level clustering power.

---

## 2. Experimental Hierarchy & Structural Nesting

```
[Level 3: Base Factual Topics] (N = 20 Unique Statutory Entities in Test-OOD)
       │ (e.g. "PMFBY vs WBCIS", "Patents Act Compulsory License", "SEBI Pre-Clearance")
       ▼  Replicated across 5 target Indic languages (hi, ta, te, bn, kn)
[Level 2: Semantic Group Clusters] (N = 100 Unique semantic_id values)
       │ (e.g. S001401 [hi], S001402 [ta], S001403 [te] ...)
       ▼  Replicated across 5 linguistic conditions (A_EN, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT)
[Level 1: Prompt Observations] (N = 500 Evaluated Prompts per Model)
```

### Table 1: Nesting Levels and Independence Status
| Level | Identifier | Sample Size ($N$) | Independence Assumption | Statistical Validity |
|---|---|---|---|---|
| **Level 1** | `prompt_id` | $500$ | Independent | **INVALID (Pseudoreplication).** Standard $\chi^2$ or pooled $t$-tests over-count sample size by $5\times$. |
| **Level 2** | `semantic_id` | $100$ | Independent clusters | **VALID (Preregistered Standard).** Controls for intra-prompt correlation across the 5 conditions. |
| **Level 3** | `base_question_id` | $20$ | Independent topics | **ULTRA-CONSERVATIVE STRESS TEST.** Controls for cross-language topic correlation. |

---

## 3. Clustered GEE Logistic Regression: Level 2 vs. Level 3

To test whether Phase 3 results depend on treating language-replicated semantic groups as independent, we fitted Generalized Estimating Equations (GEE) with an exchangeable correlation structure across both clustering regimes.

$$\text{logit}(P(\text{Correct})) = \beta_0 + \beta_B \cdot \text{B\_NATIVE} + \beta_C \cdot \text{C\_ROMAN} + \beta_D \cdot \text{D\_CS} + \beta_E \cdot \text{E\_MIXED\_SCRIPT}$$

### Table 2: Model Estimates across Clustering Regimes (Qwen-27B on Authentic Core)
| Predictor Term | Coefficient ($\beta$) | Level 2 Standard Error (`semantic_id`, $N=100$) | Level 2 $p$-value | Level 3 Standard Error (`base_question`, $N=20$) | Level 3 $p$-value | Sensitivity Verdict |
|---|---|---|---|---|---|---|
| **Intercept (`A_EN`)** | $+0.5754$ | $0.2083$ | $p = 0.0057$ | $0.4452$ | $p = 0.1962$ | Baseline intercept |
| **`B_NATIVE`** | $-1.5198$ | $0.2413$ | **$p < 0.0001$** | $0.3650$ | **$p < 0.0001$** | **Robust across all levels** |
| **`C_ROMAN`** | $-1.2835$ | $0.2482$ | **$p < 0.0001$** | $0.3604$ | **$p = 0.0004$** | **Robust across all levels** |
| **`D_CS`** | $-0.8572$ | $0.2614$ | **$p = 0.0010$** | $0.4426$ | **$p = 0.0528$** | **Marginally significant at Level 3** |
| **`E_MIXED_SCRIPT`** | $-1.7280$ | $0.2844$ | **$p < 0.0001$** | $0.4936$ | **$p = 0.0005$** | **Robust across all levels** |

---

## 4. Methodological Findings & Implications

1. **The Representation Penalty is Invariant to Clustering for Scripts:**
   The massive performance degradation observed in `B_NATIVE` ($-36\%$), `C_ROMAN` ($-31\%$), and `E_MIXED_SCRIPT` ($-40\%$) relative to English survives even when degrees of freedom are collapsed to $N=20$ independent base questions ($p \le 0.0005$).
2. **The Code-Switching Deficit (`D_CS`):**
   When clustered by `semantic_id` ($N=100$), the Romanized code-switching deficit is highly significant ($p = 0.0010$). However, because standard errors widen from $0.2614$ to $0.4426$ under $N=20$ topic clustering, $p$ increases to $0.0528$.
3. **Scientific Recommendation for Manuscript:**
   - Report the preregistered `semantic_id` paired McNemar test as the primary inferential test.
   - Explicitly disclose the 20-topic GEE stress test in the methodology section.
   - Frame the `D_CS` deficit as: *"Statistically significant under semantic cluster pairing ($p = 0.0023$, McNemar; $p = 0.0010$, GEE), with marginal significance ($p = 0.053$) under strict 20-topic cluster aggregation."*
