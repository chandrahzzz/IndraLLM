# IndraLLM — Adversarial Statistical Power & Sample Size Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 10 From-Scratch Power & Precision Recalculation  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

In experimental NLP, authors frequently inflate statistical power by treating repeated measurements on the same factual item as independent observations ($N_{\text{prompts}} = 5 \times N_{\text{groups}}$).

**Adversarial Rigor Mandate:**
The fundamental statistical unit of observation in IndraLLM is the **semantic group (`semantic_id`)**, NOT the individual prompt condition. The 5 conditions (`A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`) are **paired repeated measurements** on the same factual unit.

This audit recalculates statistical power, minimum detectable effect (MDE), and 95% confidence interval precision **strictly at the semantic cluster level**:
- **Test-ID:** $N = 200$ independent semantic groups (1,000 paired prompts).
- **Test-OOD:** $N = 100$ independent semantic groups (500 paired prompts).

**Key Finding:** 
While **Test-ID ($N=200$)** is sufficiently powered ($\ge 88\%$) to detect anticipated medium-to-large effects ($\ge 10\%$), **Test-OOD ($N=100$) is severely underpowered for subtle effects**: it has only $20.1\%$ power to detect a $5\%$ effect and $60.9\%$ power to detect a $10\%$ effect. All Test-OOD findings must be framed as exploratory rather than confirmatory.

---

## 2. Mathematical Power Formulation (McNemar Paired Test)

For paired binary factuality outcomes ($y \in \{0, 1\}$), power is governed by the discordant pair rate $p_{\text{disc}} = p_{10} + p_{01}$ and the true effect size $\Delta = |p_{10} - p_{01}|$:

$$\text{Power} = 1 - \Phi\left(z_{1 - \alpha/2} - \frac{N \cdot \Delta}{\sqrt{N \cdot p_{\text{disc}}}}\right) + \Phi\left(-z_{1 - \alpha/2} - \frac{N \cdot \Delta}{\sqrt{N \cdot p_{\text{disc}}}}\right)$$

The expected 95% Confidence Interval full width for the paired difference in proportions is:
$$W_{95\% \text{ CI}} = 2 \cdot z_{1 - \alpha/2} \cdot \sqrt{\frac{p_{\text{disc}}}{N}}$$

---

## 3. From-Scratch Statistical Power Recalculation

### 3.1 Test-ID ($N = 200$ Semantic Groups)

| Discordant Proportion ($p_{\text{disc}}$) | MDE at 80% Power ($\alpha=0.05$) | MDE at 90% Power ($\alpha=0.05$) | Expected 95% CI Width | Power ($\Delta = 5\%$) | Power ($\Delta = 8\%$) | Power ($\Delta = 10\%$) | Power ($\Delta = 15\%$) |
|---|---|---|---|---|---|---|---|
| **$15.0\%$** | **$7.67\%$** | $8.88\%$ | $\pm 5.37\%$ ($10.74\%$) | $44.7\%$ | $83.2\%$ | $95.5\%$ | $100.0\%$ |
| **$20.0\%$** (Baseline) | **$8.86\%$** | $10.25\%$ | $\pm 6.20\%$ ($12.40\%$) | $35.3\%$ | $71.6\%$ | **$88.5\%$** | **$99.7\%$** |
| **$25.0\%$** | **$9.91\%$** | $11.46\%$ | $\pm 6.93\%$ ($13.86\%$) | $29.3\%$ | $61.9\%$ | $80.7\%$ | $98.9\%$ |
| **$30.0\%$** | **$10.85\%$** | $12.55\%$ | $\pm 7.59\%$ ($15.18\%$) | $25.2\%$ | $54.2\%$ | $73.3\%$ | $97.2\%$ |

### 3.2 Test-OOD ($N = 100$ Semantic Groups)

| Discordant Proportion ($p_{\text{disc}}$) | MDE at 80% Power ($\alpha=0.05$) | MDE at 90% Power ($\alpha=0.05$) | Expected 95% CI Width | Power ($\Delta = 5\%$) | Power ($\Delta = 8\%$) | Power ($\Delta = 10\%$) | Power ($\Delta = 15\%$) |
|---|---|---|---|---|---|---|---|
| **$15.0\%$** | **$10.85\%$** | $12.55\%$ | $\pm 7.59\%$ ($15.18\%$) | $25.2\%$ | $54.2\%$ | $73.3\%$ | $97.2\%$ |
| **$20.0\%$** (Baseline) | **$12.53\%$** | $14.50\%$ | $\pm 8.77\%$ ($17.53\%$) | **$20.1\%$** | **$43.2\%$** | **$60.9\%$** | **$91.8\%$** |
| **$25.0\%$** | **$14.01\%$** | $16.21\%$ | $\pm 9.80\%$ ($19.60\%$) | $17.0\%$ | $36.0\%$ | $51.6\%$ | $85.1\%$ |
| **$30.0\%$** | **$15.34\%$** | $17.75\%$ | $\pm 10.74\%$ ($21.47\%$) | $15.0\%$ | $30.9\%$ | $44.7\%$ | $78.2\%$ |

---

## 4. Primary Planned Contrasts Power Evaluation

| Planned Contrast | Research Question Tested | Target Split | Anticipated Effect ($\Delta$) | Projected Statistical Power | Reviewer Risk & Guidance |
|---|---|---|---|---|---|
| **$C_1$: A_EN vs B_NATIVE** | Cross-Lingual Gap (English vs Vernacular) | Test-ID ($N=200$) | $12.0\% - 18.0\%$ | **$95.0\% - 99.9\%$** | Low risk; robustly powered for primary claim. |
| **$C_2$: B_NATIVE vs C_ROMAN** | Script Penalty (Devanagari/Dravidian vs Latin) | Test-ID ($N=200$) | $6.0\% - 10.0\%$ | **$55.0\% - 88.5\%$** | Moderate risk; if effect is $<8\%$, report confidence intervals rather than claiming null. |
| **$C_3$: A_EN vs D_CS** | Code-Switching Penalty (English vs Hinglish) | Test-ID ($N=200$) | $10.0\% - 15.0\%$ | **$88.5\% - 99.7\%$** | Low risk; adequately powered for core hypothesis H1. |
| **$C_4$: D_CS vs E_MIXED_SCRIPT** | Dual Script Switching Degradation | Test-ID ($N=200$) | $8.0\% - 12.0\%$ | **$71.6\%$ - $95.0\%$** | Adequate power for moderate differences. |
| **$C_5$: ID vs OOD Degradation** | Structural Generalization Gap | ID vs OOD ($N=100$) | $10.0\%$ | **$60.9\%$** | **HIGH RISK / UNDERPOWERED.** Wide CI ($\pm 8.8\%$). Must not claim subtle effect. |

---

## 5. Reviewer Vulnerability & Preregistration Protocol

1. **Do Not Treat Prompts as Independent:** In the final paper, do NOT report degrees of freedom or sample sizes based on $N = 1000$ (Test-ID) or $N = 500$ (Test-OOD). Always state: *"Evaluated across $N = 200$ and $N = 100$ independent semantic items with paired repeated measures."*
2. **Explicit Underpower Disclosure for Test-OOD:** In the Methodology section, explicitly declare that Test-OOD is powered for effects $\ge 12.5\%$, and that absence of statistically significant differences on smaller shifts cannot be interpreted as evidence of invariance.
3. **Multiple Testing Correction:** The 4 primary contrasts ($C_1$ to $C_4$) must be adjusted using the Holm-Bonferroni step-down procedure (`holm_bonferroni_correction`) to control the family-wise error rate at $\alpha = 0.05$.
