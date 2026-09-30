# IndraLLM — Phase 4.5: Workstream 9
# Model Generalization & Floor Effects Audit: Forensic Exposure of Allam-7B Floor Noise

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  
**Artifact Dependencies:** `results/phase4/phase4_5_model_reproduction.json`, `results/EXP-002/full_predictions.jsonl`  

---

## 1. Executive Summary & Critical Discrepancy Exposed

In the Phase 4 report, Workstream 7 claimed:
> *"The condition difficulty ranking is identical across both models (Spearman $\rho = 0.975, p = 0.0048$)."*

Our independent clean-room audit of the raw experimental predictions in `results/EXP-002/full_predictions.jsonl` **REFUTES THIS CLAIM**.

### Audit Discovery:
1. **Actual Raw Accuracy in Allam-7B:**
   On the Authentic Core ($N=100$ prompts per condition), Allam-7B achieved:
   - **`A_EN`:** **$8.0\%$** (8/100) — Rank 1
   - **`D_CS`:** **$5.0\%$** (5/100) — Rank 2
   - **`E_MIXED_SCRIPT`:** **$3.0\%$** (3/100) — Rank 3
   - **`C_ROMAN`:** **$2.0\%$** (2/100) — Rank 4.5
   - **`B_NATIVE`:** **$2.0\%$** (2/100) — Rank 4.5
2. **True Spearman Rank Correlation:**
   Between Qwen-27B and Allam-7B on the Authentic Core, the true correlation is:
   $$\rho = 0.6669, \quad p = 0.2189$$
   The claimed $\rho = 0.975$ ($p = 0.0048$) was an idealized projection that assumed strict monotonic separation among the non-English conditions.
3. **Substantive Scientific Reality — Floor Collapse:**
   Allam-7B suffers a catastrophic capacity floor on Indian statutory facts. The variation among non-English conditions ($2\%$, $2\%$, $3\%$) represents **Poisson noise of a single prompt** (3 vs 2 correct generations out of 100).
4. **Mandatory Manuscript Downgrade:**
   The paper **must NOT claim statistically significant rank invariance ($\rho = 0.975$)**. It must transparently report that:
   - English is best and Code-Switching is second-best across both models.
   - Allam-7B collapses to a $2\%\text{--}3\%$ floor on Indic conditions, precluding fine-grained ordinal ranking and illustrating that smaller models without Indic pretraining fail entirely under non-canonical representation.

---

## 2. Recomputed Cross-Model Accuracy & Rank Matrix

### Table 1: Authentic Policy Core Performance ($N=100$ Prompts per Condition)

| Condition | Qwen-27B Accuracy | Qwen Rank | Allam-7B Accuracy | Allam Rank | Rank Discrepancy | Substantive Interpretation |
|---|---|---|---|---|---|---|
| **`A_EN`** | **$64.0\%$** (64/100) | **1** | **$8.0\%$** (8/100) | **1** | $0$ (Exact match) | English is highest for both models |
| **`D_CS`** | **$43.0\%$** (43/100) | **2** | **$5.0\%$** (5/100) | **2** | $0$ (Exact match) | Code-switching is second-best for both |
| **`C_ROMAN`** | **$32.0\%$** (32/100) | **3** | **$2.0\%$** (2/100) | **4.5** | $-1.5$ | Floor noise (2 vs 3 correct) |
| **`B_NATIVE`** | **$28.0\%$** (28/100) | **4** | **$2.0\%$** (2/100) | **4.5** | $-0.5$ | Floor noise (2 vs 3 correct) |
| **`E_MIXED_SCRIPT`**| **$24.0\%$** (24/100) | **5** | **$3.0\%$** (3/100) | **3** | $+2.0$ | Floor noise (3 vs 2 correct) |

- **True Spearman's $\rho$:** $0.6669$ ($p = 0.2189$, non-significant).
- **True Kendall's $\tau$:** $0.5270$ ($p = 0.2326$, non-significant).

---

## 3. Epistemic Impact on the Manuscript

This exposure strengthens the paper's scientific credibility:
1. We eliminate an easily disproven statistical claim before peer review.
2. The finding that a $7\text{B}$ model collapses to a near-zero floor on Indian statutory facts while a dense $27\text{B}$ model sustains meaningful retrieval ($64\%$ to $24\%$) provides valuable architectural insight: **non-canonical representation penalties require sufficient model capacity to even be measurable above floor noise**.

---

## 4. Required Paper Wording

> *"In cross-model comparisons, both Qwen-27B and Allam-7B achieve their highest accuracy in English (64% and 8%, respectively), followed by Romanized code-switching (43% and 5%). However, on native-script and mixed-script Indic conditions, Allam-7B collapses to a near-zero floor (2% to 3%), where inter-condition variation reflects Poisson sampling noise rather than systematic representation differences. Consequently, while English and code-switching preserve their relative hierarchy, fine-grained cross-condition rank correlation is not statistically significant (Spearman rho = 0.67, p = 0.22), demonstrating that measuring subword representation dynamics requires models with sufficient baseline Indic pretraining."*
