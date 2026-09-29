# IndraLLM — Phase 3.5: Audit 4 — Multiple Comparisons & FWER Audit
## Family-Wise Error Rate Control, Hidden Multiple Testing Audit, and All-Pairs Stress Test

**Document Version:** 1.0 (Post-Execution Forensic Audit)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `1d4a65c`  

---

## 1. Executive Summary

When testing multiple experimental conditions across multiple languages and models, unadjusted $p$-values rapidly inflate the Type I error rate. A frequent methodological weakness identified by ACL/EMNLP reviewers is **selective contrast reporting**—reporting only significant pairwise contrasts while concealing non-significant tests or failing to correct for the complete hypothesis family.

This audit:
1. Completely enumerates every statistical hypothesis test performed in EXP-002.
2. Audits the pre-registered 4-contrast Holm-Bonferroni correction.
3. Conducts an all-pairs sensitivity stress test across all $\binom{5}{2} = 10$ possible pairwise condition contrasts.

### Key Audit Finding:
All primary scientific discoveries—including the English vs. Code-Switching deficit ($p = 0.00229$) and the Code-Switching vs. Dual-Script penalty ($p = 0.00395$)—**survive full 10-contrast Family-Wise Error Rate (FWER) control** at $\alpha = 0.05$.

---

## 2. Complete Enumeration of Statistical Hypothesis Tests

| Test ID | Hypothesis | Target Contrast / Predictor | Model & Data Split | Statistical Test | Sample Size ($N$) | Raw $p$-value | Preregistered? | Status |
|---|---|---|---|---|---|---|---|---|
| **`T-01`** | H1 (Representation Penalty) | `A_EN` vs `D_CS` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 9.30$) | 100 clusters | $p = 0.002289$ | **YES (Primary C3)** | **SIGNIFICANT** |
| **`T-02`** | H3 (Orthographic Disruption) | `D_CS` vs `E_MIXED_SCRIPT` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 8.31$) | 100 clusters | $p = 0.003948$ | **YES (Primary C4)** | **SIGNIFICANT** |
| **`T-03`** | Native Script Deficit | `A_EN` vs `B_NATIVE` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 30.62$) | 100 clusters | $p = 3.13 \times 10^{-8}$ | **YES (Primary C1)** | **SIGNIFICANT** |
| **`T-04`** | Romanization Effect | `B_NATIVE` vs `C_ROMAN` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 0.52$) | 100 clusters | $p = 0.472498$ | **YES (Primary C2)** | **NOT SIGNIFICANT** |
| **`T-05`** | Dual-Script Overall Deficit | `A_EN` vs `E_MIXED_SCRIPT` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 30.34$) | 100 clusters | $p = 3.48 \times 10^{-8}$ | Secondary / Exploratory | **SIGNIFICANT** |
| **`T-06`** | Romanized Indic Deficit | `A_EN` vs `C_ROMAN` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 21.95$) | 100 clusters | $p = 2.80 \times 10^{-6}$ | Secondary / Exploratory | **SIGNIFICANT** |
| **`T-07`** | Native vs Code-Switch | `B_NATIVE` vs `D_CS` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 4.36$) | 100 clusters | $p = 0.036888$ | Exploratory | Not significant under 10-pair FWER |
| **`T-08`** | Roman vs Code-Switch | `C_ROMAN` vs `D_CS` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 1.93$) | 100 clusters | $p = 0.164915$ | Exploratory | **NOT SIGNIFICANT** |
| **`T-09`** | Roman vs Mixed-Script | `C_ROMAN` vs `E_MIXED_SCRIPT` | Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 2.06$) | 100 clusters | $p = 0.150763$ | Exploratory | **NOT SIGNIFICANT** |
| **`T-10`** | Native vs Mixed-Script | `B_NATIVE` vs `E_MIXED_SCRIPT`| Qwen-27B (Authentic Core) | Paired McNemar ($\chi^2 = 0.35$) | 100 clusters | $p = 0.556298$ | Exploratory | **NOT SIGNIFICANT** |
| **`T-11`** | H2 (Language Invariance) | Joint Language Main Effect | Qwen-27B (Authentic Core) | Clustered Wald $\chi^2(4) = 2.41$ | 100 clusters | $p = 0.6608$ | **YES (Primary)** | **NOT SIGNIFICANT (Invariance)** |
| **`T-12`** | Model Capability Effect | Qwen-27B vs Allam-7B | Both Models (Full Test) | Clustered Paired Wald Test | 300 clusters | $p < 10^{-12}$ | Secondary | **SIGNIFICANT** |

---

## 3. Preregistered Family Correction Audit

Phase 3 defined a primary contrast family of 4 hypothesis tests:
$$\mathcal{F}_{\text{pre}} = \{C_1: \text{A\_EN vs B\_NATIVE}, \quad C_2: \text{B\_NATIVE vs C\_ROMAN}, \quad C_3: \text{A\_EN vs D\_CS}, \quad C_4: \text{D\_CS vs E\_MIXED\_SCRIPT}\}$$

### Step-Down Holm-Bonferroni Procedure ($\alpha = 0.05$):
1. **Rank 1 ($C_1$):** $p = 3.13 \times 10^{-8} \le \frac{0.05}{4} = 0.0125 \implies \mathbf{REJECT\ H_0}$ (Significant)
2. **Rank 2 ($C_3$):** $p = 0.002289 \le \frac{0.05}{3} = 0.01667 \implies \mathbf{REJECT\ H_0}$ (Significant)
3. **Rank 3 ($C_4$):** $p = 0.003948 \le \frac{0.05}{2} = 0.0250 \implies \mathbf{REJECT\ H_0}$ (Significant)
4. **Rank 4 ($C_2$):** $p = 0.472498 > \frac{0.05}{1} = 0.0500 \implies \mathbf{RETAIN\ H_0}$ (Not Significant)

*Audit Verification:* The Holm correction was executed with exact step-down thresholds and proper index alignment. No selective threshold manipulation occurred.

---

## 4. All-Pairs Stress Test (Full 10 Pairwise Contrasts)

To simulate an adversarial reviewer who demands correction across all possible condition comparisons ($\binom{5}{2} = 10$), we executed the step-down Holm-Bonferroni correction over the full 10-contrast set:

| Sorted Rank ($k$) | Comparison Pair | Raw McNemar $p$-value | Step-Down Threshold ($\frac{\alpha}{10 - k + 1}$) | FWER Decision | Odds Ratio |
|---|---|---|---|---|---|
| **1** | `A_EN` vs `B_NATIVE` | **$3.13 \times 10^{-8}$** | $0.00500$ | **REJECT $H_0$ (Significant)** | $19.00$ |
| **2** | `A_EN` vs `E_MIXED_SCRIPT` | **$3.48 \times 10^{-8}$** | $0.00556$ | **REJECT $H_0$ (Significant)** | $9.00$ |
| **3** | `A_EN` vs `C_ROMAN` | **$2.80 \times 10^{-6}$** | $0.00625$ | **REJECT $H_0$ (Significant)** | $7.20$ |
| **4** | `A_EN` vs `D_CS` | **$0.002289$** | $0.00714$ | **REJECT $H_0$ (Significant)** | $2.91$ |
| **5** | `D_CS` vs `E_MIXED_SCRIPT` | **$0.003948$** | $0.00833$ | **REJECT $H_0$ (Significant)** | $2.90$ |
| **6** | `B_NATIVE` vs `D_CS` | $0.036888$ | $0.01000$ | Retain $H_0$ (Not Significant) | $0.50$ |
| **7** | `C_ROMAN` vs `E_MIXED_SCRIPT`| $0.150763$ | $0.01250$ | Retain $H_0$ (Not Significant) | $1.82$ |
| **8** | `C_ROMAN` vs `D_CS` | $0.164915$ | $0.01667$ | Retain $H_0$ (Not Significant) | $0.62$ |
| **9** | `B_NATIVE` vs `C_ROMAN` | $0.472498$ | $0.02500$ | Retain $H_0$ (Not Significant) | $0.72$ |
| **10** | `B_NATIVE` vs `E_MIXED_SCRIPT`| $0.556298$ | $0.05000$ | Retain $H_0$ (Not Significant) | $1.36$ |

### Scientific Conclusion
Even under strict 10-contrast FWER control:
- The representation penalty ($A\_EN$ vs $D\_CS$) remains statistically significant ($p = 0.00229 < 0.00714$).
- The orthographic penalty ($D\_CS$ vs $E\_MIXED\_SCRIPT$) remains statistically significant ($p = 0.00395 < 0.00833$).
- The native and romanized deficits remain overwhelmingly significant ($p < 10^{-5}$).

The Phase 3 statistical conclusions are **completely robust to multiple-testing corrections**.
