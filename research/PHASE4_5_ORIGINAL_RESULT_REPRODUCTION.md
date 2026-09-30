# IndraLLM — Phase 4.5: Workstream 5
# Original 20-Topic Forensic Reproduction Audit: Exact Verification

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  
**Artifact Dependencies:** `results/phase4/phase4_5_original_reproduction.json`, `results/EXP-002/full_predictions.jsonl`  

---

## 1. Executive Summary

This audit independently executed a clean-room statistical reproduction of the original 20-topic Authentic Core results directly from raw model generations (`results/EXP-002/full_predictions.jsonl`).

### Independent Reproduction Findings:
- **Intra-Cluster Correlation ($\text{ICC}_{\text{Topic}}$):** **`0.2663`** (Exact match).
- **Design Effect ($\text{DEFF}$):** **`7.3916`** (Exact match).
- **Effective Sample Size ($N_{\text{eff}}$):** **`67.64`** (Exact match: reported $67.6$).
- **Statistical Power for $\Delta = 21\%$ at $N=20$:** **`55.93%`** (Exact match).
- **English vs. Code-Switching GEE ($p$-value at Level 3):** **`0.0528`** ($\beta = -0.8572, \text{SE} = 0.4426$) (Exact match).

Every numerical value reported in Phase 4 is mathematically verified and derived from the raw underlying prediction records.

---

## 2. Recomputed Parameter and Variance Matrix

### Table 1: Model Estimates and Significance Across Clustered Levels

| Contrast / Parameter | Level 1: Unclustered Naive ($N=500$) | Level 2: Semantic Group GEE ($N=100$) | Level 3: Base Topic GEE ($N=20$) |
|---|---|---|---|
| **Intercept** | $\beta = +0.5754, p = 0.0057$ | $\beta = +0.5754, p = 0.0057$ | $\beta = +0.5754, p = 0.1962$ |
| **`B_NATIVE` vs `A_EN`** | $\beta = -1.5198, p < 0.0001$ | $\beta = -1.5198, p < 0.0001$ | $\beta = -1.5198, p < 0.0001$ |
| **`C_ROMAN` vs `A_EN`** | $\beta = -1.2835, p < 0.0001$ | $\beta = -1.2835, p < 0.0001$ | $\beta = -1.2835, p = 0.0004$ |
| **`D_CS` vs `A_EN`** | $\beta = -0.8572, p = 0.0031$ | $\beta = -0.8572, p = 0.0010$ | $\beta = -0.8572, p = 0.0528$ |
| **`E_MIXED_SCRIPT` vs `A_EN`** | $\beta = -1.7280, p < 0.0001$ | $\beta = -1.7280, p < 0.0001$ | $\beta = -1.7280, p = 0.0005$ |

---

## 3. Substantive Scientific Verification

1. **Parameter Invariance:** Across all three levels of aggregation, the regression coefficient $\beta$ remains strictly invariant (e.g., $\beta = -0.8572$ for `D_CS`, corresponding to an odds ratio of $\text{OR} = 0.4243$). The underlying estimated effect size does not shrink under clustering; only its standard error expands.
2. **Robustness of Non-English Contrasts:** Three of the four non-English conditions (`B_NATIVE`, `C_ROMAN`, `E_MIXED_SCRIPT`) remain overwhelmingly significant ($p \le 0.0005$) even under the coarsest Level 3 topic clustering.
3. **Transparency Regarding `D_CS`:** The borderline $p = 0.0528$ for `D_CS` at Level 3 is a direct consequence of the sample size constraint ($N=20$ clusters, $N_{\text{eff}} = 67.6$) and $55.9\%$ power, which our expanded benchmark design (`AUTH-021` to `AUTH-045`) is specifically engineered to resolve.
