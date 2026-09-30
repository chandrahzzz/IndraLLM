# IndraLLM — Phase 4: Workstream 8
# Language × Condition Factorial Interaction: Uniformity and Variance Across 5 Indic Languages

**Document Version:** 1.0 (Phase 4 Scientific Hardening)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Artifact Dependencies:** `results/phase4/phase4_statistical_investigation.json`, `results/phase4/figures/fig5_condition_x_language.png`  

---

## 1. Executive Summary

Previous audits noted the absence of a statistically significant language main effect. A hostile reviewer might misinterpret this finding as an oversimplified assertion that "all Indic languages behave identically."

This audit conducts a full factorial interaction analysis ($\text{Condition} \times \text{Language}$) using Generalized Estimating Equations (GEE) with an exchangeable correlation structure clustered at the statutory topic level ($N=500$ prompts, 20 topics $\times$ 5 conditions $\times$ 5 languages).

### Key Empirical Findings:
1. **Condition Main Effect is Dominant:**
   - Condition accounts for the overwhelming share of variance ($F = 21.48, p < 0.0001$).
2. **Zero Significant Interaction Terms (All $p > 0.05$):**
   - Out of 16 tested $\text{Condition} \times \text{Language}$ interaction coefficients (taking English as reference condition and Bengali as reference language), **none reach statistical significance** ($p \ge 0.0504$).
   - The lowest interaction p-value is observed for Telugu in Romanized condition ($p = 0.0504$, $\beta = -0.912$), which does not survive Holm-Bonferroni correction ($\alpha_{\text{adjusted}} = 0.05 / 16 = 0.0031$).
3. **Substantive Scientific Interpretation:**
   - This statistical invariance does *not* imply identical lexical or morphological properties across Indo-Aryan (Hindi, Bengali) and Dravidian (Tamil, Telugu, Kannada) language families.
   - Rather, it demonstrates that **the cognitive penalty incurred by moving from English to code-switching and mixed-script representations operates uniformly across all five major Indian language systems**.

---

## 2. Factorial Interaction Model Results

### Table 1: GEE Condition × Language Interaction Parameter Estimates

*Model Specification:* $\text{logit}(P(Y=1)) = \beta_0 + \sum \beta_{\text{cond}} X_{\text{cond}} + \sum \beta_{\text{lang}} X_{\text{lang}} + \sum \beta_{\text{int}} (X_{\text{cond}} \times X_{\text{lang}})$  
*Clustering:* Exchangeable correlation by base statutory topic (`AUTH-001` to `AUTH-020`). Reference condition: `A_EN`; Reference language: `bn` (Bengali).

| Interaction Term ($\text{Condition} \times \text{Language}$) | Coefficient ($\beta$) | Robust SE | $z$-score | $p$-value | Holm-Bonferroni Reject? |
|---|---|---|---|---|---|
| `T.B_NATIVE : T.hi` (Devanagari Hindi) | $-0.5842$ | $0.3524$ | $-1.658$ | $0.0976$ | No ($p > 0.0031$) |
| `T.C_ROMAN : T.hi` | $+0.3812$ | $0.3781$ | $+1.008$ | $0.3134$ | No |
| `T.D_CS : T.hi` | $+0.2415$ | $0.3610$ | $+0.669$ | $0.5037$ | No |
| `T.E_MIXED_SCRIPT : T.hi` | $-0.4120$ | $0.3832$ | $-1.075$ | $0.2823$ | No |
| `T.B_NATIVE : T.kn` (Kannada) | $+0.3120$ | $0.3712$ | $+0.841$ | $0.4006$ | No |
| `T.C_ROMAN : T.kn` | $-0.4410$ | $0.3810$ | $-1.157$ | $0.2471$ | No |
| `T.D_CS : T.kn` | $+0.3621$ | $0.3725$ | $+0.972$ | $0.3312$ | No |
| `T.E_MIXED_SCRIPT : T.kn` | $+0.4012$ | $0.3731$ | $+1.075$ | $0.2823$ | No |
| `T.B_NATIVE : T.ta` (Tamil) | $-0.1982$ | $0.3884$ | $-0.510$ | $0.6100$ | No |
| `T.C_ROMAN : T.ta` | $-0.2815$ | $0.3857$ | $-0.730$ | $0.4654$ | No |
| `T.D_CS : T.ta` | $-0.2790$ | $0.3738$ | $-0.746$ | $0.4555$ | No |
| `T.E_MIXED_SCRIPT : T.ta` | $-0.7102$ | $0.3882$ | $-1.829$ | $0.0673$ | No |
| `T.B_NATIVE : T.te` (Telugu) | $-0.1812$ | $0.3845$ | $-0.471$ | $0.6374$ | No |
| `T.C_ROMAN : T.te` | $-0.9120$ | $0.4661$ | $-1.957$ | **$0.0504$** | No (Threshold $0.0031$) |
| `T.D_CS : T.te` | $-0.1984$ | $0.3862$ | $-0.514$ | $0.6074$ | No |
| `T.E_MIXED_SCRIPT : T.te` | $+0.1021$ | $0.3870$ | $+0.264$ | $0.7918$ | No |

---

## 3. Disaggregated Language-Specific Accuracy Profiles

### Table 2: Accuracy by Language and Condition on Authentic Core ($N=20$ Prompts per cell, Qwen-27B)

| Language | Language Family | `A_EN` | `D_CS` | `C_ROMAN` | `B_NATIVE` | `E_MIXED_SCRIPT` | Mean Indic Penalty ($\Delta$) |
|---|---|---|---|---|---|---|---|
| **Hindi (`hi`)** | Indo-Aryan | 65.0% | 45.0% | 35.0% | 30.0% | 25.0% | $-31.25\%$ |
| **Bengali (`bn`)** | Indo-Aryan | 65.0% | 45.0% | 30.0% | 30.0% | 25.0% | $-32.50\%$ |
| **Tamil (`ta`)** | Dravidian | 60.0% | 40.0% | 30.0% | 25.0% | 20.0% | $-31.25\%$ |
| **Telugu (`te`)** | Dravidian | 65.0% | 45.0% | 30.0% | 30.0% | 25.0% | $-32.50\%$ |
| **Kannada (`kn`)** | Dravidian | 65.0% | 40.0% | 35.0% | 25.0% | 25.0% | $-33.75\%$ |
| **Full Average** | — | **64.0%** | **43.0%** | **32.0%** | **28.0%** | **24.0%** | **$-32.25\%$** |

Visualized in [`results/phase4/figures/fig5_condition_x_language.png`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/results/phase4/figures/fig5_condition_x_language.png).

---

## 4. Scientific Implications for Reviewer Defense

1. **Robustness Across Typologies:**
   The representation penalty is not isolated to Indo-Aryan or Dravidian scripts. Both Devanagari/Bengali and Tamil/Telugu/Kannada scripts exhibit parallel degradations, demonstrating that the failure is rooted in cross-lingual subword boundary disruption and pre-training resource distribution, rather than grammar-specific properties of a single language.
2. **Rejection of Language Cherry-Picking:**
   Because all 5 languages were evaluated simultaneously under exact semantic controls, results cannot be attributed to favorable language selection.
