# IndraLLM — Phase 4.5: Workstream 10
# Evaluator Robustness & Rogan–Gladen Sensitivity Surface Audit

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  
**Artifact Dependencies:** `results/phase4/phase4_statistical_investigation.json`  

---

## 1. Executive Summary & Epistemic Recalibration

A central reviewer concern regarding LLM-as-a-judge benchmarking is that automated evaluators may grade code-switched text more harshly than standard English. 

In Phase 4, Workstream 9 computed a 25-point 2D sensitivity surface across:
$$\text{TPR}_{\text{CS}} \in [0.80, 0.96], \quad \text{FPR}_{\text{CS}} \in [0.04, 0.16]$$
reporting that the adjusted English vs. CS performance gap ranges from $+16.82\%$ to $+34.38\%$.

### Tone and Scientific Recalibration:
- In Phase 4 documentation, the verdict was described as *"INCONTROVERTIBLE"*.
- **As a senior ACL reviewer and statistical auditor, we reject this terminology.** No empirical finding relying on finite-sample epidemiological inversion is "incontrovertible."
- Instead, the mathematically precise and defensible conclusion is:
  > *"Across a broad 2D sensitivity grid encompassing all plausible evaluator error rates, the estimated English vs. Code-Switching gap remains substantial ($\Delta \ge 16.82\%$), demonstrating that evaluator imperfection alone cannot account for the observed representation deficit."*

---

## 2. Mathematical Verification of the 2D Grid

The classical Rogan–Gladen inversion formula is:

$$\pi = \frac{P_{\text{obs}} - \text{FPR}}{\text{TPR} - \text{FPR}}$$

With observed $P_{\text{obs}}(\text{A\_EN}) = 0.64$ and $P_{\text{obs}}(\text{D\_CS}) = 0.43$:
- **Baseline English Latent Accuracy ($\pi_{\text{EN}}$):**
  With calibrated $\text{TPR}_{\text{EN}} = 0.93, \text{FPR}_{\text{EN}} = 0.02$:
  $$\pi_{\text{EN}} = \frac{0.64 - 0.02}{0.93 - 0.02} = \frac{0.62}{0.91} \approx 68.13\%$$
- **Worst-Case Leniency for Code-Switching:**
  Setting $\text{TPR}_{\text{CS}} = 0.80$ (evaluator misses $20\%$ of correct answers) and $\text{FPR}_{\text{CS}} = 0.04$ (virtually zero false alarms):
  $$\pi_{\text{CS}} = \frac{0.43 - 0.04}{0.80 - 0.04} = \frac{0.39}{0.76} = 51.32\%$$
  $$\text{Minimum Net Gap: } \Delta_{\min} = 68.13\% - 51.32\% = \mathbf{+16.82\%}$$
- **Worst-Case Stringency for Code-Switching:**
  Setting $\text{TPR}_{\text{CS}} = 0.96$ and $\text{FPR}_{\text{CS}} = 0.16$:
  $$\pi_{\text{CS}} = \frac{0.43 - 0.16}{0.96 - 0.16} = \frac{0.27}{0.80} = 33.75\%$$
  $$\text{Maximum Net Gap: } \Delta_{\max} = 68.13\% - 33.75\% = \mathbf{+34.38\%}$$

---

## 3. Boundary & Probability Validity Check

1. **Probability Bounding:** All grid points were evaluated using $\pi = \min(1.0, \max(0.0, \pi_{\text{calc}}))$. No cell produced out-of-bounds probabilities ($\pi < 0$ or $\pi > 1$).
2. **Break-Even Threshold Analysis:** For the true performance gap to collapse to zero ($\pi_{\text{EN}} = \pi_{\text{CS}} = 68.13\%$), the code-switching judge would have to exhibit an absurd error profile:
   $$0.6813 = \frac{0.43 - \text{FPR}}{\text{TPR} - \text{FPR}} \implies \text{TPR} \le 0.58 \text{ when } \text{FPR} = 0.10$$
   This would require the judge to misclassify more than $42\%$ of correct code-switched answers as incorrect, which is directly contradicted by our human validation audit ($\text{TPR}_{\text{human}} = 0.88, \kappa = 0.824$).

---

## 4. Required Paper Wording

> *"To account for the possibility of condition-dependent judge bias, we performed a 2D sensitivity analysis over the Rogan–Gladen epidemiological estimator, sweeping evaluator sensitivity (0.80 to 0.96) and false-positive rates (0.04 to 0.16). Across all 25 parameter configurations, the adjusted performance gap between English and code-switching remains substantial (+16.8% to +34.4%). While automated evaluation introduces measurement uncertainty, the primary representation effect cannot be attributed to judge bias alone."*
