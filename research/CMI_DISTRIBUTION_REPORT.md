# Benchmark CMI Distribution and Variance Report

**Document Version:** 1.0 (Frozen for Phase 2.5)  
**Target Specification:** Part 6 & 7 Research Integrity Audit  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Data Reference:** [`data/questions/IndraLLM-CS-v1.0/condition_prompts_10000.csv`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.0/condition_prompts_10000.csv)

---

## 1. Executive Summary

This report establishes the empirical distribution of the Gambäck & Das (2014) Code-Mixing Index (CMI) across all 10,000 condition prompts in IndraLLM-CS-v1.0. 

A primary vulnerability in multilingual LLM benchmarks is treating a continuous metric (CMI) as identical to a categorical condition. We demonstrate that:
1. While CMI strongly differentiates the 5 experimental conditions, **substantial within-condition variance exists within the code-switched conditions** (`D_CS` variance = 59.13; `E_MIXED_SCRIPT` variance = 19.03).
2. The benchmark avoids collinearity traps between CMI and token length ($r = -0.2742$) and character density ($r = -0.0086$).
3. We explicitly document the statistical limitation that monolingual conditions (`A_EN` and `B_NATIVE`) exhibit near-zero variance, requiring continuous regression analyses of CMI to be stratified or conditioned on representation category.

---

## 2. Condition-Level CMI Distribution Statistics

The table below reports non-parametric and parametric distribution metrics across all $N = 2,000$ prompts per condition:

| Condition | Description | Mean | SD | Median | IQR | 95th %ile | Min | Max |
|---|---|---|---|---|---|---|---|---|
| **A_EN** | Monolingual English | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **B_NATIVE** | Monolingual Native Script | 0.43 | 1.11 | 0.00 | 0.00 | 3.45 | 0.00 | 3.57 |
| **C_ROMAN** | Romanized Indic | 9.34 | 9.70 | 10.00 | 12.50 | 33.33 | 0.00 | 33.33 |
| **D_CS** | Romanized Code-Switched | 22.13 | 7.69 | 23.08 | 8.33 | 37.50 | 9.09 | 40.00 |
| **E_MIXED_SCRIPT**| Mixed-Script Code-Switched | 45.10 | 4.36 | 46.15 | 7.14 | 50.00 | 33.33 | 50.00 |

*Note on B_NATIVE:* Non-zero CMI ($0.43\%$) in native script prompts stems from sparse English technical abbreviations (e.g., DNA, GDP, UNESCO) retained in original script where no natural vernacular transliteration exists.

---

## 3. Disaggregated CMI Distribution by Language & Condition

For each language ($N = 400$ per condition-language cell):

### 3.1 Condition D_CS (Intra-Utterance Code-Switching)
| Language | Mean CMI (%) | SD | Variance ($\sigma^2$) | Min (%) | Median (%) | Max (%) |
|---|---|---|---|---|---|---|
| **Bengali (bn)** | 19.54 | 6.80 | 46.22 | 9.09 | 20.00 | 30.77 |
| **Hindi (hi)** | 26.07 | 9.00 | 80.92 | 10.00 | 27.27 | 40.00 |
| **Kannada (kn)** | 24.18 | 5.16 | 26.66 | 16.67 | 25.00 | 33.33 |
| **Tamil (ta)** | 22.76 | 8.07 | 65.20 | 11.11 | 20.00 | 37.50 |
| **Telugu (te)** | 18.11 | 5.85 | 34.17 | 9.09 | 22.22 | 25.00 |
| **All Languages** | **22.13** | **7.69** | **59.13** | **9.09** | **23.08** | **40.00** |

*Finding:* In `D_CS`, CMI spans continuously from $9.09\%$ to $40.00\%$, with all 2,000 items having strictly non-zero mixing. This enables within-condition dose-response testing.

### 3.2 Condition E_MIXED_SCRIPT (Orthographic & Script Mixing)
| Language | Mean CMI (%) | SD | Variance ($\sigma^2$) | Min (%) | Median (%) | Max (%) |
|---|---|---|---|---|---|---|
| **Bengali (bn)** | 44.45 | 5.65 | 31.94 | 33.33 | 45.30 | 50.00 |
| **Hindi (hi)** | 46.12 | 3.88 | 15.03 | 38.46 | 46.41 | 50.00 |
| **Kannada (kn)** | 43.84 | 4.41 | 19.43 | 35.71 | 43.65 | 50.00 |
| **Tamil (ta)** | 45.95 | 4.08 | 16.68 | 41.18 | 46.43 | 50.00 |
| **Telugu (te)** | 45.11 | 2.91 | 8.48 | 41.67 | 46.15 | 50.00 |
| **All Languages** | **45.10** | **4.36** | **19.03** | **33.33** | **46.15** | **50.00** |

---

## 4. Analysis of Variance (Between vs Within-Condition)

To quantify how much variance in CMI is attributable to the condition design versus within-condition linguistic variation, a one-way ANOVA was conducted on the full dataset:

- **Between-Condition Sum of Squares:** $SS_{\text{between}} = 2,850,193.93$ ($df = 4$)
- **Within-Condition Sum of Squares:** $SS_{\text{within}} = 346,942.26$ ($df = 9,995$)
- **Effect Size:** $\eta^2 = 0.8915$
- **F-statistic:** $F(4, 9995) = 20,527.69$ ($p < 10^{-300}$)

### Scientific Interpretation
1. The 5 conditions successfully manipulate code-switching intensity across 5 distinct plateaus ($\eta^2 = 0.8915$).
2. Crucially, the residual within-condition sum of squares ($SS = 346,942.26$) is substantial. Within `D_CS` and `E_MIXED_SCRIPT`, prompts naturally vary in token length, switch frequency, and grammatical clause insertion.
3. Therefore, **regressing hallucination on continuous CMI within conditions D and E is methodologically valid**, whereas a naive global regression across all conditions would be dominated by the discrete condition jumps.

---

## 5. Correlation with Competing Covariates

To ensure CMI does not act as a mere proxy for prompt formatting artifacts, we report Pearson correlations ($N = 10,000$):

| Variable 1 | Variable 2 | Pearson $r$ | $p$-value | Reviewer Vulnerability Addressed |
|---|---|---|---|---|
| `measured_cmi` | `language_switch_count` | $+0.9205$ | $< 10^{-300}$ | Validates CMI measures true linguistic alternations. |
| `measured_cmi` | `switch_density` | $+0.8741$ | $< 10^{-300}$ | Confirms switch frequency per unit token. |
| `measured_cmi` | `script_transitions` | $+0.7319$ | $< 10^{-300}$ | Expectedly correlated globally, but orthogonal in `D_CS` ($r = 0.00$). |
| `measured_cmi` | `token_count` | $-0.2742$ | $< 10^{-150}$ | Refutes claim that higher CMI is an artifact of longer prompts. |
| `measured_cmi` | `chars_per_token` | $-0.0086$ | $0.388$ (n.s.) | CMI is independent of orthographic character density. |
| `measured_cmi` | `english_token_ratio` | $-0.0784$ | $< 10^{-15}$ | CMI captures balance, not raw English dominance. |

---

## 6. Pre-Registered Modeling Guardrails

Based on this audit, Phase 3 empirical analyses must adhere to the following rules:
1. **Never report a single pooled CMI regression coefficient as proof of "code-switching causality."**
2. In mixed-effects models, `condition` must be modeled as a primary categorical factor, and `measured_cmi` must be evaluated either as:
   - A within-condition continuous covariate for `D_CS` and `E_MIXED_SCRIPT`; or
   - Group-mean centered: $\text{CMI}_{ij} - \overline{\text{CMI}}_{j}$.
