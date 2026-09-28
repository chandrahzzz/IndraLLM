# IndraLLM-CS v1.0 — Comprehensive Dataset Statistics & Distribution Report

**Release Tag:** `IndraLLM-CS-v1.0`  
**Semantic Groups ($N_{groups}$):** 2,000  
**Total Condition Prompts ($N_{prompts}$):** 10,000  
**Languages Evaluated:** 5 (hi, ta, te, bn, kn)  
**Conditions Evaluated:** 5 (A_EN, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT)  

---

## 1. Categorical Distribution & Balance Audit

### Language Distribution
| Language Code | Language Name | Semantic Groups | Condition Prompts | Balance Ratio |
|---|---|---|---|---|
| `hi` | HI | 400 | 2000 | 20.0% |
| `ta` | TA | 400 | 2000 | 20.0% |
| `te` | TE | 400 | 2000 | 20.0% |
| `bn` | BN | 400 | 2000 | 20.0% |
| `kn` | KN | 400 | 2000 | 20.0% |

### Condition Distribution
| Condition | Description | Total Prompts | Script | Share |
|---|---|---|---|---|
| `A_EN` | Monolingual English Baseline | 2000 | Latin | 20.0% |
| `B_NATIVE` | Monolingual Native Indic Script | 2000 | Indic Scripts | 20.0% |
| `C_ROMAN` | Monolingual Romanized Indic | 2000 | Latin | 20.0% |
| `D_CS` | Natural Conversational Code-Switching | 2000 | Latin | 20.0% |
| `E_MIXED_SCRIPT` | Intra-sentential Mixed Script | 2000 | Mixed | 20.0% |

### Domain Distribution
| Domain | Prompts | Share |
|---|---|---|
| `governance` | 1675 | 16.8% |
| `science` | 1675 | 16.8% |
| `agriculture` | 1675 | 16.8% |
| `history` | 1675 | 16.8% |
| `education` | 1650 | 16.5% |
| `public_health` | 1650 | 16.5% |

---

## 2. Multidimensional Code-Mixing & Script Statistics

| Metric | Mean | Std Dev | Median | Q25 | Q75 | P95 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| `measured_cmi` | 15.4 | 17.881 | 9.09 | 0.0 | 27.27 | 50.0 | 0.0 | 50.0 |
| `english_token_ratio` | 0.627 | 0.36 | 0.75 | 0.429 | 0.929 | 1.0 | 0.0 | 1.0 |
| `indic_token_ratio` | 0.36 | 0.363 | 0.25 | 0.0 | 0.533 | 1.0 | 0.0 | 1.0 |
| `language_switch_count` | 2.193 | 2.343 | 2.0 | 0.0 | 5.0 | 6.0 | 0.0 | 7.0 |
| `switch_density` | 0.192 | 0.201 | 0.125 | 0.0 | 0.385 | 0.5 | 0.0 | 0.714 |
| `script_transitions` | 1.46 | 2.288 | 0.0 | 0.0 | 2.0 | 7.0 | 0.0 | 9.0 |
| `token_count` | 15.144 | 6.782 | 13.0 | 11.0 | 16.0 | 30.0 | 7.0 | 35.0 |
| `chars_per_token` | 5.771 | 2.1 | 5.92 | 4.57 | 6.77 | 9.44 | 2.32 | 12.11 |

### Cross-Condition Means
```
                measured_cmi  script_transitions  language_switch_count
condition                                                              
A_EN                    0.00                0.34                   0.00
B_NATIVE                0.43                0.80                   0.26
C_ROMAN                 9.34                0.34                   1.47
D_CS                   22.13                0.34                   4.07
E_MIXED_SCRIPT         45.10                5.50                   5.17
```

---

## 3. Data Leakage Verification
- All splits (`train`, `val`, `test`) are partitioned strictly by `semantic_id`.
- Leakage validation check: `overlap_train_val = 0`, `overlap_train_test = 0`, `overlap_val_test = 0`.
- Verdict: **ZERO DATA CONTAMINATION DETECTED.**