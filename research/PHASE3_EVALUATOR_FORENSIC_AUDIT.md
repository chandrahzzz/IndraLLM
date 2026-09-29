# IndraLLM — Phase 3.5: Audit 5 — Evaluator Bias & Rogan-Gladen Forensic Audit
## Deep-Dive on Evaluator Asymmetry, False-Positive Dynamics, and Prevalence Truncation Artifacts

**Document Version:** 1.0 (Post-Execution Forensic Audit)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `1d4a65c`  

---

## 1. Executive Summary

A core vulnerability in LLM-as-a-judge benchmarking is **evaluator bias**—the tendency of automated factual judges to exhibit differential sensitivity and specificity across languages, scripts, and code-switched inputs.

Phase 2.7 established that the tri-layer factual judge (`qwen/qwen3.8-27b`) achieves an overall accuracy of $88.3\%$ and Cohen's $\kappa = 0.761$ against human gold annotations, but exhibits an asymmetric **$+10\%$ false-positive rate (FPR)** on code-switched and Indic completions compared to English.

In Phase 3, a **Rogan-Gladen prevalence adjustment** was introduced to correct for this bias. This forensic audit reveals a major mathematical artifact in how that correction was applied, provides the rigorous corrected formulation, and proves that the true representation penalty is **larger, not smaller**, than raw metrics suggest.

---

## 2. Forensic Discovery: The Truncation Artifact on Full Benchmark

In `research/PHASE3_EXP002_RESULTS.md` (Table 3.2), the adjusted condition accuracy on the Full Candidate Benchmark was reported as:
$$\text{A\_EN}: 21.98\%, \quad \text{B\_NATIVE}: 0.00\%, \quad \text{C\_ROMAN}: 0.00\%, \quad \text{D\_CS}: 3.15\%, \quad \text{E\_MIXED\_SCRIPT}: 0.00\%$$

### Why did three conditions collapse to exactly 0.00%?
The classical Rogan-Gladen estimator for true prevalence ($P_{\text{true}}$) given observed prevalence ($P_{\text{obs}}$), true positive rate ($\text{TPR}$), and false positive rate ($\text{FPR}$) is:
$$P_{\text{true}} = \frac{P_{\text{obs}} - \text{FPR}}{\text{TPR} - \text{FPR}}$$

For non-English conditions, the calibrated parameters were:
$$\text{TPR} = 0.86, \quad \text{FPR} = 0.12, \quad \implies \quad \text{TPR} - \text{FPR} = 0.74$$

On the Full Benchmark ($N=300$ groups per model), the observed accuracies were:
- `B_NATIVE`: $P_{\text{obs}} = 0.0933$ ($9.33\%$)
- `C_ROMAN`: $P_{\text{obs}} = 0.1100$ ($11.00\%$)
- `E_MIXED_SCRIPT`: $P_{\text{obs}} = 0.0800$ ($8.00\%$)

**Crucial Mathematical Reality:** Because the Synthetic Scaling Tier ($2/3$ of the benchmark) scored $0\%$, the overall observed prevalence fell **strictly below the evaluator false-positive rate ($\text{FPR} = 0.12$)**!
- `B_NATIVE`: $\frac{0.0933 - 0.12}{0.74} = \mathbf{-0.0360} \implies \text{clamped to } \mathbf{0.00\%}$
- `C_ROMAN`: $\frac{0.1100 - 0.12}{0.74} = \mathbf{-0.0135} \implies \text{clamped to } \mathbf{0.00\%}$
- `E_MIXED_SCRIPT`: $\frac{0.0800 - 0.12}{0.74} = \mathbf{-0.0541} \implies \text{clamped to } \mathbf{0.00\%}$

### Scientific Verdict on the Artifact:
The reported $0.00\%$ values in the Phase 3 report were **boundary-clamping truncation artifacts** caused by pooling zero-accuracy synthetic questions into the prevalence estimator. A fundamental assumption of Rogan-Gladen estimation ($P_{\text{obs}} > \text{FPR}$) was violated on the synthetic pool.

---

## 3. Validated Rogan-Gladen Calibration on Authentic Core

When the Rogan-Gladen adjustment is applied where it is mathematically valid—on the Authentic Core, where models exhibit genuine parametric retrieval above the evaluator noise floor ($P_{\text{obs}} \ge 0.24 > 0.12$)—zero truncation occurs:

### Table 1: Raw vs. Rogan-Gladen Calibrated Metrics (Authentic Core, $N=100$)
| Condition | Observed Accuracy ($P_{\text{obs}}$) | Evaluator TPR | Evaluator FPR | Rogan-Gladen Adjusted ($P_{\text{adj}}$) | Standard Error ($\text{SE}_{\text{adj}}$) | 95% Adjusted Confidence Interval | Truncation Occurred? |
|---|---|---|---|---|---|---|---|
| **`A_EN`** | **$64.0\%$** | $0.93$ | $0.02$ | **$68.13\%$** | $5.27\%$ | $[57.79\%, 78.47\%]$ | **NO** |
| **`B_NATIVE`** | **$28.0\%$** | $0.86$ | $0.12$ | **$21.62\%$** | $6.07\%$ | $[9.73\%, 33.51\%]$ | **NO** |
| **`C_ROMAN`** | **$33.0\%$** | $0.86$ | $0.12$ | **$28.38\%$** | $6.35\%$ | $[15.92\%, 40.83\%]$ | **NO** |
| **`D_CS`** | **$43.0\%$** | $0.86$ | $0.12$ | **$41.89\%$** | $6.69\%$ | $[28.78\%, 55.00\%]$ | **NO** |
| **`E_MIXED_SCRIPT`** | **$24.0\%$** | $0.86$ | $0.12$ | **$16.22\%$** | $5.77\%$ | $[4.90\%, 27.53\%]$ | **NO** |

---

## 4. The Adjusted Representation and Orthographic Penalties

Because the automated judge tends to over-credit non-English hallucinations (+10% FPR), removing this bias **widens the performance gaps**:

1. **English vs. Code-Switching Deficit ($A\_EN$ vs $D\_CS$):**
   $$\text{Raw Gap}: 64.0\% - 43.0\% = \mathbf{21.00\%}$$
   $$\text{Rogan-Gladen Adjusted Gap}: 68.13\% - 41.89\% = \mathbf{26.24\%} \quad (+5.24\% \text{ wider})$$
2. **Code-Switching vs. Dual-Script Penalty ($D\_CS$ vs $E\_MIXED\_SCRIPT$):**
   $$\text{Raw Gap}: 43.0\% - 24.0\% = \mathbf{19.00\%}$$
   $$\text{Rogan-Gladen Adjusted Gap}: 41.89\% - 16.22\% = \mathbf{25.67\%} \quad (+6.67\% \text{ wider})$$

### Core Scientific Conclusion:
Evaluator bias was **masking the true severity** of model failure. The higher false-positive rate on code-switched answers was artificially propping up non-English performance. When properly adjusted using epidemiological prevalence correction, the linguistic representation penalty is **more severe than originally reported**.

---

## 5. Formal Rogan-Gladen Assumptions Audit

| Rogan-Gladen Assumption | Mathematical Requirement | Status in IndraLLM | Scientific Impact |
|---|---|---|---|
| **Assumption 1: Nondifferential Error** | Evaluator error is independent of the model's true accuracy state. | **SATISFIED WITHIN CONDITION.** Handled via stratified TPR/FPR vectors by condition. | Prevents cross-condition confounding. |
| **Assumption 2: Parameter Precision** | TPR and FPR are known with high precision. | **PARTIALLY SATISFIED.** Pilot validation ($N=150$) provided $\pm 3\%$ precision. | Variance propagated via Delta method SEs. |
| **Assumption 3: Super-Threshold Prevalence** | $P_{\text{obs}} > \text{FPR}$. | **VIOLATED ON SYNTHETIC TIER.** Satisfied on Authentic Core. | Disallows applying Rogan-Gladen to the synthetic scaling tier. |
| **Assumption 4: Representativeness** | Validation sample matches evaluation test distribution. | **SATISFIED.** Validation sample was drawn from same gazette topics. | Validates transferability of TPR/FPR estimates. |

### Prescribed Action for Publication:
1. Remove all Full-Benchmark clamped $0.00\%$ adjusted tables.
2. Present Rogan-Gladen adjustments **exclusively on the Authentic Core**, accompanied by propagated Delta-method 95% confidence intervals.
3. Explicitly report both raw and adjusted figures in the primary results table.
