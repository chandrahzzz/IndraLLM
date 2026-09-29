# 10-Level Contamination Audit of IndraLLM-CS-v1.0

**Document Version:** 2.0 (Phase 2.6 Comprehensive Audit)  
**Target Specification:** Part 2 Research Integrity Audit  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Evaluated Artifacts:** `data/questions/IndraLLM-CS-v1.0/{train.csv, val.csv, test.csv}`  

---

## 1. Methodology & Ten-Level Granularity

Standard NLP audits frequently report a coarse, binary "contamination = yes/no" without characterizing the locus of information leakage. We conduct a structured 10-level forensic audit measuring overlap across train ($N=8,000$), validation ($N=1,000$), and test ($N=1,000$) partitions.

---

## 2. Multi-Level Forensic Overlap Matrix

| Level | Contamination Dimension | Train Unique | Test Unique | Shared (Train $\cap$ Test) | Test Overlap (%) | Detection Method |
|---|---|---|---|---|---|---|
| **L1** | **Exact Prompt-Text** | 126 | 126 | 126 | **100.0%** | Exact case-sensitive string matching |
| **L2** | **Exact Factual Question** | 6 (EN) | 6 (EN) | 6 | **100.0%** | Normalized base English query string |
| **L3** | **Exact Semantic Answer** | 6 | 6 | 6 | **100.0%** | Gold reference answer matching |
| **L4** | **Entity-Pair Overlap** | 6 pairs | 6 pairs | 6 pairs | **100.0%** | Named entity relation graph extraction |
| **L5** | **Near-Duplicate / Paraphrase** | 126 | 126 | 126 | **100.0%** | Cross-lingual embedding cosine $\ge 0.95$ |
| **L6** | **Template-Family Overlap** | 6 | 6 | 6 | **100.0%** | Syntactic frame & question taxonomy |
| **L7** | **Evidence-Source Overlap** | 6 URLs | 6 URLs | 6 URLs | **100.0%** | Canonical URL matching |
| **L8** | **Evidence-Snippet Overlap** | 6 | 6 | 6 | **100.0%** | Token-level text matching of excerpts |
| **L9** | **Claim-Level Overlap** | 6 | 6 | 6 | **100.0%** | Propositional truth condition matching |
| **L10**| **Domain Overlap** | 6 | 6 | 6 | **100.0%** | Categorical topic assignment |

---

## 3. Forensic Breakdown by Level

### Level 1: Exact Prompt-Text Duplication
- **Observed:** Out of 1,000 condition prompts in `test.csv`, all 126 distinct prompt text strings ($25–26$ per language across the 5 conditions) appear verbatim in `train.csv`.
- **False-Positive Analysis:** None. Strings match character-for-character.
- **Example:** `"How much financial support is provided annually under the PM-KISAN scheme?"` appears 107 times in train and 13 times in test.

### Level 2: Exact Factual Question Duplication
- **Observed:** Across the 5 Indian languages and English, only 6 base questions exist in the entire dataset:
  1. *PM-KISAN annual financial support*
  2. *Chandrayaan-3 Moon landing date*
  3. *Soil Health Card parameters tested*
  4. *Keezhadi archaeological site district*
  5. *NIRF launch year*
  6. *Mission Indradhanush launch date*
- **Impact:** Test set evaluates zero unseen questions relative to train.

### Level 3: Semantic Answer Duplication
- **Observed:** Exactly 6 gold answers (`"₹6,000 per year..."`, `"August 23, 2023."`, `"12 parameters."`, `"Sivaganga district..."`, `"2015..."`, `"December 2014..."`) represent 100% of answers in train, val, and test.

### Level 4: Entity-Pair Overlap
- **Observed:** The entity relations (e.g. `(PM-KISAN, Ministry of Agriculture)`, `(Chandrayaan-3, Lunar South Pole)`, `(Keezhadi, Sivaganga)`) are 100% identical between train and test.

### Level 5: Near-Duplicate / Paraphrase Overlap
- **Observed:** Cross-lingual semantic embedding similarity (`paraphrase-multilingual-mpnet-base-v2`) between test items and their train counterparts is $> 0.98$ for all items, representing literal re-instances.

### Level 6: Template-Family Overlap
- **Observed:** All 6 syntactic frames (factual amount, temporal date, count, geographical location, year retrieval, temporal month) exist in train and test with zero out-of-distribution syntactic variation.

### Level 7 & 8: Evidence-Source and Evidence-Snippet Overlap
- **Observed:** All 6 evidence URLs (`https://pmkisan.gov.in`, `https://isro.gov.in/...`, etc.) and their exact excerpts are 100% identical.

### Level 9 & 10: Claim-Level and Domain Overlap
- **Observed:** Complete 100% domain overlap across Governance, Science, Agriculture, History, Education, and Public Health.

---

## 4. Audit Conclusion & Remediation Imperatives

The audit establishes that IndraLLM-CS-v1.0 is **100% contaminated at all 10 analytical levels**. 

### Mandatory Architectural Requirements for IndraLLM-CS-v1.1-CANDIDATE:
1. **Zero L1–L3 Overlap:** Test-ID and Test-OOD must contain $0\%$ exact prompt, question, or answer overlap with Development.
2. **Strict L6 Separation:** Test-OOD must withhold designated template families entirely from Development.
3. **Partition Before Condition Generation:** Semantic questions must be isolated into disjoint partitions prior to multi-condition translation.
