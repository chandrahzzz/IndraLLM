# IndraLLM-CS-v1.1-CANDIDATE Distribution Statistics & Profiling

**Document Version:** 1.0 (Frozen Specification)  
**Target Specification:** Part 15, 16, 17, 18 & 26 Dataset Profiling  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Data Reference:** [`data/questions/IndraLLM-CS-v1.1-CANDIDATE/condition_prompts_7500.csv`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.1-CANDIDATE/condition_prompts_7500.csv)  

---

## 1. Executive Benchmark Summary

| Benchmark Dimension | Stated Metric |
|---|---|
| **Total Semantic Groups ($N$)** | **1,500** |
| **Total Condition Prompts** | **7,500** ($1,500 \times 5$ conditions) |
| **Target Languages** | Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Bengali (`bn`), Kannada (`kn`) |
| **Condition Prompts per Language** | **1,500** ($300$ semantic groups $\times$ 5 conditions) |
| **Condition Prompts per Condition** | **1,500** ($1,500$ each: `A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`) |
| **Unique Base Facts** | **300** verified institutional and statutory facts |
| **Template Families** | **12** (`TF-01` to `TF-12`) |
| **Domains Covered** | Governance, Agriculture, Science, History, Education, Public Health |
| **Cross-Partition Contamination** | **0.0%** across all 10 analytical levels |

---

## 2. Partition Allocations & Composition

| Partition | Semantic Groups | Condition Prompts | Template Families | Purpose & Isolation |
|---|---|---|---|---|
| **DEVELOPMENT** | 1,000 | 5,000 | `TF-01` to `TF-10` | In-distribution baseline model training & prompt development |
| **VALIDATION** | 200 | 1,000 | `TF-01` to `TF-10` | Parameter tuning & threshold optimization (0% overlap with Dev) |
| **TEST-ID** | 200 | 1,000 | `TF-01` to `TF-10` | Primary in-distribution evaluation (0% overlap with Dev/Val) |
| **TEST-OOD** | 100 | 500 | `TF-11` & `TF-12` | Structural out-of-distribution evaluation (unseen template families) |
| **Total** | **1,500** | **7,500** | **TF-01 to TF-12** | **Full Benchmark Corpus** |

---

## 3. Condition-Level Multidimensional CMI Distributions

Across all $N = 1,500$ prompts per condition:

| Condition | Mean CMI (%) | SD | Variance ($\sigma^2$) | Median | IQR | Min (%) | Max (%) |
|---|---|---|---|---|---|---|---|
| **A_EN** | 0.03 | 0.48 | 0.23 | 0.00 | 0.00 | 0.00 | 8.33 |
| **B_NATIVE** | 16.75 | 3.20 | 10.25 | 17.39 | 3.85 | 4.35 | 29.17 |
| **C_ROMAN** | 14.55 | 7.90 | 62.35 | 9.09 | 10.45 | 6.67 | 38.46 |
| **D_CS** | 17.29 | 4.79 | 22.91 | 18.18 | 6.25 | 7.14 | 33.33 |
| **E_MIXED_SCRIPT**| 38.90 | 7.90 | 62.38 | 42.86 | 11.54 | 20.00 | 50.00 |

### Key Variance Findings
1. **Sufficient Within-Condition Variance:** Both `D_CS` ($\sigma^2 = 22.91$, range $7.14\% - 33.33\%$) and `E_MIXED_SCRIPT` ($\sigma^2 = 62.38$, range $20.00\% - 50.00\%$) possess substantial within-condition variability, preventing condition and CMI from collapsing into collinear proxies.
2. **Realistic Technical Native Mixing:** In `B_NATIVE`, the mean CMI is $16.75\%$ due to official acronyms (e.g., GST, PM-KISAN, MSME, ISRO, DNA, WHO) retained in Latin or transliterated forms, reflecting authentic contemporary Indian vernacular usage.

---

## 4. Disentangling Script Hopping vs. Language Switching

| Condition | Script Transitions (mean $\pm$ SD) | Language Switches (mean $\pm$ SD) | Switch Density (switches / token) | Token Count (Llama-3) |
|---|---|---|---|---|
| **A_EN** | $1.41 \pm 0.49$ | $0.01 \pm 0.08$ | $0.00 \pm 0.01$ | $13.75 \pm 2.10$ |
| **B_NATIVE** | $1.73 \pm 0.44$ | $1.00 \pm 0.05$ | $0.04 \pm 0.01$ | $24.01 \pm 3.45$ |
| **C_ROMAN** | $1.42 \pm 0.49$ | $2.40 \pm 0.49$ | $0.20 \pm 0.04$ | $12.61 \pm 1.95$ |
| **D_CS** | $1.42 \pm 0.49$ | $2.60 \pm 0.49$ | $0.23 \pm 0.04$ | $12.21 \pm 1.85$ |
| **E_MIXED_SCRIPT**| $5.73 \pm 0.88$ | $5.00 \pm 0.15$ | $0.38 \pm 0.05$ | $14.41 \pm 2.05$ |

- **Orthogonality in D_CS:** Script transitions remain at the single-script Latin baseline ($1.42$), while language switches are active ($2.60$).
- **Script Contrast:** Comparing `D_CS` to `E_MIXED_SCRIPT` isolates a $+4.31$ increase in script transitions while holding the underlying language mixing active.
- **Tokenization Gap:** `B_NATIVE` exhibits severe subword fragmentation ($24.01$ tokens vs $12.61$ for `C_ROMAN` and $13.75$ for `A_EN`), confirming the critical need to control for token fertility in regression models.
