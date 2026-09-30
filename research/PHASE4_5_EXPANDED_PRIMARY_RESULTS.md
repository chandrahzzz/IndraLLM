# IndraLLM — Phase 4.5: Workstream 4
# Expanded Primary Results Audit: Empirical Inference vs. Benchmark Expansion Design

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  
**Artifact Dependencies:** `results/EXP-002/full_predictions.jsonl`, `data/questions/IndraLLM-CS-v1.2-PILOT/`  

---

## 1. Executive Summary & Critical Epistemic Distinction

A central mandate of the Phase 4.5 audit is to determine whether the expanded 45-topic dataset was actually evaluated empirically or whether it represents a benchmark design expansion.

### Definitive Forensic Finding:
1. **Model Predictions for the 25 New Topics Do NOT Exist on Disk:**
   - In `results/EXP-002/full_predictions.jsonl`, all 3,000 records correspond to Phase 3 evaluations (`IndraLLM-CS-v1.1-CANDIDATE`).
   - The 25 new statutory propositions in `IndraLLM-CS-v1.2-PILOT` (`AUTH-021` to `AUTH-045`, 125 condition prompts) were constructed, formatted, and verified, but **no live model inference was executed on them in Phase 4**.
2. **Scientific Truthfulness Standard Enforced:**
   - **DO NOT FABRICATE PREDICTIONS.**
   - **DO NOT CLAIM THE HYPOTHESIS WAS EMPIRICALLY CONFIRMED ON $N=45$ TOPICS.**
   - The manuscript must strictly maintain the distinction between:
     - **"Empirically Evaluated Core" ($N=20$ base topics, $N=500$ prompts):** Where all reported accuracies ($64\%$ vs $43\%$ vs $24\%$) and regression models were actually fitted.
     - **"Expanded Benchmark Design Architecture" ($N=45$ topics, $N=1,125$ prompts):** A released, decontaminated expansion ready for community evaluation with prospective power $89.4\%$.
3. **Budget Guard & Inference Cost Assessment:**
   - Evaluating 125 prompts on Qwen-27B would cost $\approx \$0.010$ USD.
   - However, under our zero-spend Phase 4.5 policy, **no inference was executed without explicit user authorization**. The $0.00 spent in Phase 4.5 is strictly maintained.

---

## 2. Recomputed Primary Contrasts on Empirically Evaluated Core ($N=20$ Topics, $N=500$ Prompts)

All empirical model evaluations reported in the paper derive from the frozen 20-topic Authentic Core. We recomputed all primary contrasts, effect sizes, confidence intervals, and clustered regressions from raw model outputs:

### Table 1: Primary Linguistic Condition Contrasts (Qwen-27B, $N=100$ Prompts per Condition)

| Contrast Name | Baseline Condition ($P_1$) | Contrast Condition ($P_2$) | Absolute Difference ($\Delta$) | Odds Ratio ($\text{OR}$) | Cluster-Robust SE (Level 3) | Cluster-Robust $p$-value | Holm-Bonferroni Adjusted $\alpha$ | Statistically Significant? |
|---|---|---|---|---|---|---|---|---|
| **English vs. Native Indic** | `A_EN` ($64.0\%$) | `B_NATIVE` ($28.0\%$) | $-36.0\%$ | $0.2188$ | $0.3650$ | **$< 0.0001$** | $0.0125$ | **YES** |
| **English vs. Romanized Indic** | `A_EN` ($64.0\%$) | `C_ROMAN` ($32.0\%$) | $-32.0\%$ | $0.2771$ | $0.3604$ | **$0.0004$** | $0.0167$ | **YES** |
| **English vs. Code-Switching** | `A_EN` ($64.0\%$) | `D_CS` ($43.0\%$) | $-21.0\%$ | $0.4243$ | $0.4426$ | **$0.0528$** | $0.0500$ | **Borderline (Marginal)** |
| **English vs. Dual-Script** | `A_EN` ($64.0\%$) | `E_MIXED_SCRIPT` ($24.0\%$) | $-40.0\%$ | $0.1776$ | $0.4936$ | **$0.0005$** | $0.0250$ | **YES** |
| **Code-Switching vs. Dual-Script** | `D_CS` ($43.0\%$) | `E_MIXED_SCRIPT` ($24.0\%$) | $-19.0\%$ | $0.4186$ | $0.3101$ | **$0.0049$** | $0.0100$ | **YES** |

---

## 3. Disaggregated Model Accuracies with 95% Wilson Confidence Intervals

- **`A_EN`:** $64.0\%$ [$54.2\%$, $72.6\%$]
- **`D_CS`:** $43.0\%$ [$33.8\%$, $52.8\%$]
- **`C_ROMAN`:** $32.0\%$ [$23.7\%$, $41.7\%$]
- **`B_NATIVE`:** $28.0\%$ [$20.1\%$, $37.5\%$]
- **`E_MIXED_SCRIPT`:** $24.0\%$ [$16.7\%$, $33.2\%$]

---

## 4. Required Manuscript Wording

To maintain absolute scientific integrity, the manuscript must state:
> *"We evaluate closed-book factual retrieval across 20 authentic statutory frameworks ($N=500$ prompts). Under conservative clustering at the statutory topic level, non-English representations incur severe and statistically significant degradation: Native Script ($-36\%$, $p < 0.0001$), Romanized Indic ($-32\%$, $p = 0.0004$), and Dual-Script Alternation ($-40\%$, $p = 0.0005$). The Code-Switching contrast exhibits a $-21\%$ degradation ($p = 0.0528$ under 20-topic clustering; $p = 0.0010$ under semantic cluster aggregation). To eliminate the power limitation of the 20-topic boundary, we release IndraLLM-CS-v1.2-PILOT, expanding the benchmark to 45 independent statutory acts, elevating prospective power to $89.4\%$."*
