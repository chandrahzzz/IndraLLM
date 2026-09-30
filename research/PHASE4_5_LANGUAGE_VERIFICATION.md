# IndraLLM — Phase 4.5: Workstream 8
# Language Interaction & Cross-Lingual Generalization Audit

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  
**Artifact Dependencies:** `results/phase4/phase4_5_language_reproduction.json`, `results/EXP-002/full_predictions.jsonl`  

---

## 1. Executive Summary

In Phase 4, the analysis reported that "no significant Condition $\times$ Language interactions were detected ($p \ge 0.0504$)." 

A central mandate of this Phase 4.5 statistical audit is to enforce methodological rigor: **failing to reject the null hypothesis of no interaction ($p \ge 0.05$) must NEVER be interpreted as "proving the languages behave identically."**

### Headline Methodological Findings:
1. **No Detectable Interaction Under Multiple Testing Control:**
   - Across all 16 tested $\text{Condition} \times \text{Language}$ interaction terms, zero terms survive Holm-Bonferroni correction ($\alpha_{\text{adjusted}} = 0.05 / 16 = 0.0031$).
   - The unadjusted minimum $p$-values are $p = 0.0504$ (clustered by `semantic_id`) and $p = 0.0168$ (clustered by `base_topic_id`), neither of which achieves family-wise significance.
2. **Distinguishing "Equivalence" from "Insufficient Power":**
   - With $N=20$ prompts per language-condition cell, standard errors on interaction coefficients range between $0.35$ and $0.55$. The test is powered only to detect extreme cross-lingual divergence ($\Delta > 30\%$).
   - Therefore, the data exhibits **approximate qualitative consistency**, but **cannot support a claim of genuine mathematical equivalence**.
3. **Calibrated Manuscript Interpretation:**
   - The paper must state that the representation penalty operates directionally across all five tested languages without statistically detectable interaction, while explicitly acknowledging that small per-cell sample sizes ($N=20$) preclude definitive claims of cross-lingual invariance.

---

## 2. Disaggregated Performance Matrix by Language and Condition

### Table 1: Raw Accuracy Across Language Cells ($N=20$ Prompts per Cell, Qwen-27B)

| Language | Family | `A_EN` | `D_CS` | `C_ROMAN` | `B_NATIVE` | `E_MIXED_SCRIPT` | Mean Indic Condition Accuracy | Net Representation Deficit ($\Delta_{\text{EN} - \text{Indic}}$) |
|---|---|---|---|---|---|---|---|---|
| **Hindi (`hi`)** | Indo-Aryan | 65.0% | 45.0% | 35.0% | 45.0% | 20.0% | 36.25% | **$-28.75\%$** |
| **Bengali (`bn`)** | Indo-Aryan | 60.0% | 50.0% | 15.0% | 15.0% | 35.0% | 28.75% | **$-31.25\%$** |
| **Kannada (`kn`)** | Dravidian | 65.0% | 35.0% | 35.0% | 30.0% | 20.0% | 30.00% | **$-35.00\%$** |
| **Tamil (`ta`)** | Dravidian | 65.0% | 40.0% | 30.0% | 25.0% | 10.0% | 26.25% | **$-38.75\%$** |
| **Telugu (`te`)** | Dravidian | 65.0% | 45.0% | 50.0% | 25.0% | 35.0% | 38.75% | **$-26.25\%$** |
| **All Languages** | Combined | **64.0%** | **43.0%** | **33.0%** | **28.0%** | **24.0%** | **32.00%** | **$-32.00\%$** |

---

## 3. Substantive Linguistic Observations

1. **Directional Invariance:** In every single language, `A_EN` (English) achieves the highest accuracy ($60.0\%\text{--}65.0\%$), and every non-English representation drops substantially ($10.0\%\text{--}50.0\%$).
2. **Script Alternation Worst-Case in Tamil:** In Tamil (`ta`), `E_MIXED_SCRIPT` collapses to **$10.0\%$** (2/20), reflecting the high orthographic distance between Tamil script and Latin characters.
3. **Cross-Family Robustness:** Both Indo-Aryan languages (Hindi $-28.8\%$, Bengali $-31.3\%$) and Dravidian languages (Telugu $-26.3\%$, Kannada $-35.0\%$, Tamil $-38.8\%$) exhibit parallel performance deficits.

---

## 4. Required Paper Wording

> *"In factorial GEE modeling, no condition-by-language interaction terms reached significance under Holm-Bonferroni family-wise error control (all adjusted p > 0.05). Across all five languages spanning Indo-Aryan and Dravidian families, non-English representations incurred substantial average accuracy penalties (-26% to -39%). However, because each language cell contains N=20 prompts, we do not claim that these languages behave identically, but rather that the representation penalty operates with directional consistency across the evaluated language families."*
