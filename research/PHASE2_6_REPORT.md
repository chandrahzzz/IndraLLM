# Phase 2.6 Comprehensive Benchmark Rebuild & Decontamination Report

**Document Version:** 1.0 (Phase 2.6 Final Milestone)  
**Target Specification:** Part 26 Comprehensive Execution Report  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**New Candidate Benchmark:** [`data/questions/IndraLLM-CS-v1.1-CANDIDATE/`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.1-CANDIDATE/)  
**Preserved Contaminated Benchmark:** [`data/questions/IndraLLM-CS-v1.0/`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.0/)  

---

## 1. Executive Summary & Core Accomplishment

Phase 2.5 uncovered a fatal scientific defect in the benchmark: **IndraLLM-CS-v1.0** had scaled 6 base question templates across 2,000 numeric IDs, resulting in 100% prompt and question overlap across train, val, and test partitions.

In Phase 2.6, rather than manufacturing artificial paraphrases or silently modifying historical files, we executed a complete, scientifically principled benchmark rebuild:
1. **Preserved v1.0 as an Immutable Artifact:** Documented in [`research/CONTAMINATED_DATASET_ARCHIVE.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CONTAMINATED_DATASET_ARCHIVE.md) with exact SHA-256 manifests.
2. **Formulated a 12-Tier Template Taxonomy:** Established distinct cognitive reasoning frames (`TF-01` to `TF-12`) in [`research/TEMPLATE_TAXONOMY.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/TEMPLATE_TAXONOMY.md).
3. **Built an Authentic Knowledge Base:** Curated 300 distinct factual items from official gazettes, statutory acts, national registries, and science agencies across 6 domains (Governance, Agriculture, Science, History, Education, Public Health).
4. **Enforced Strict Pre-Partitioning:** All 300 factual items were assigned to partitions (`DEVELOPMENT`, `VALIDATION`, `TEST-ID`, `TEST-OOD`) **prior** to condition generation.
5. **Constructed IndraLLM-CS-v1.1-CANDIDATE:** Generated $1,500$ semantic groups ($7,500$ condition prompts) with complete 5-condition pairing (`A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`) across 5 Indian languages.
6. **Achieved 0.0% Cross-Partition Leakage:** Verified that `TEST-ID` and `TEST-OOD` share zero prompt texts, zero questions, zero gold answers, zero evidence snippets, and zero entity pairs with `DEVELOPMENT` or `VALIDATION`.
7. **Quarantined Structural OOD:** Restricted `TF-11` (Cross-Entity Comparison) and `TF-12` (Conditional Regulatory) exclusively to `TEST-OOD`.
8. **Automated Test Validation:** 38 tests passing in `pytest -q`, with 1 xfail specifically capturing the known historical v1.0 flaw.
9. **Budget Discipline:** Rebuild executed via deterministic offline synthesis; project spend remains **$0.1040 USD** ($9.8960 USD remaining of $10.00 ceiling).

---

## 2. Partition Architecture & Zero-Leakage Audit

Across the 7,500 condition prompts in `IndraLLM-CS-v1.1-CANDIDATE`:

| Partition | Unique Facts | Semantic Groups ($N$) | Condition Prompts | Template Families | Overlap with Dev/Val | Status |
|---|---|---|---|---|---|---|
| **DEVELOPMENT** | 200 | 1,000 | 5,000 | `TF-01` to `TF-10` | Baseline training split | Frozen |
| **VALIDATION** | 40 | 200 | 1,000 | `TF-01` to `TF-10` | **0.0%** (0 shared prompts/answers) | **DECONTAMINATED** |
| **TEST-ID** | 40 | 200 | 1,000 | `TF-01` to `TF-10` | **0.0%** (0 shared prompts/answers) | **DECONTAMINATED** |
| **TEST-OOD** | 20 | 100 | 500 | `TF-11` & `TF-12` | **0.0%** (0 shared prompts; 0% TF overlap) | **DECONTAMINATED** |
| **Total** | **300** | **1,500** | **7,500** | **TF-01 to TF-12** | **Zero Cross-Split Contamination** | **VERIFIED** |

---

## 3. Multidimensional Linguistic Metrics

| Condition | Mean CMI (%) | SD | Variance ($\sigma^2$) | Script Transitions | Language Switches | Switch Density | Token Count |
|---|---|---|---|---|---|---|---|
| **A_EN** | 0.03 | 0.48 | 0.23 | $1.41 \pm 0.49$ | $0.01 \pm 0.08$ | $0.00 \pm 0.01$ | $13.75 \pm 2.10$ |
| **B_NATIVE** | 16.75 | 3.20 | 10.25 | $1.73 \pm 0.44$ | $1.00 \pm 0.05$ | $0.04 \pm 0.01$ | $24.01 \pm 3.45$ |
| **C_ROMAN** | 14.55 | 7.90 | 62.35 | $1.42 \pm 0.49$ | $2.40 \pm 0.49$ | $0.20 \pm 0.04$ | $12.61 \pm 1.95$ |
| **D_CS** | 17.29 | 4.79 | 22.91 | $1.42 \pm 0.49$ | $2.60 \pm 0.49$ | $0.23 \pm 0.04$ | $12.21 \pm 1.85$ |
| **E_MIXED_SCRIPT**| 38.90 | 7.90 | 62.38 | $5.73 \pm 0.88$ | $5.00 \pm 0.15$ | $0.38 \pm 0.05$ | $14.41 \pm 2.05$ |

### Scientific Significance
- In `D_CS`, language switching is active ($2.60 \pm 0.49$) while script hopping remains at single-script Latin levels ($1.42 \pm 0.49$).
- In `E_MIXED_SCRIPT`, script transitions surge to $5.73 \pm 0.88$ alongside language switches ($5.00 \pm 0.15$).
- In `B_NATIVE`, subword fragmentation creates a massive tokenization penalty ($24.01$ tokens vs $12.61$ for `C_ROMAN`).
- Non-zero variance exists across conditions, supporting continuous mixed-effects regression.

---

## 4. Recomputed Statistical Power & Precision

| Partition | Semantic Units ($N$) | True Difference ($\Delta$) | Intra-Unit Correlation ($\rho$) | Standard Error ($SE$) | 95% CI Half-Width | Statistical Power |
|---|---|---|---|---|---|---|
| **TEST-ID** | 200 | $+7.5\%$ | 0.50 | 0.0276 | $\pm 5.42\%$ | **$77.5\%$** |
| **TEST-ID** | 200 | $+10.0\%$ | 0.50 | 0.0283 | $\pm 5.55\%$ | **$94.2\%$** |
| **TEST-ID** | 200 | $+15.0\%$ | 0.50 | 0.0295 | $\pm 5.78\%$ | **$99.9\%$** |
| **TEST-OOD** | 100 | $+10.0\%$ | 0.50 | 0.0400 | $\pm 7.85\%$ | **$70.4\%$** |
| **TEST-OOD** | 100 | $+15.0\%$ | 0.50 | 0.0417 | $\pm 8.17\%$ | **$94.9\%$** |

- **TEST-ID:** Achieves $>94\%$ power for detecting $\Delta \ge 10\%$ effect sizes with a precision of $\pm 5.5\%$.
- **TEST-OOD:** Detects larger structural shifts ($\Delta \ge 15\%$) at $\approx 95\%$ power with a precision of $\pm 8.2\%$.

---

## 5. Artifact Audit Trail (All Required Deliverables Created)

The following 12 Phase 2.6 research deliverables are complete, verified, and frozen in [`research/`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/):

1. [`research/CONTAMINATED_DATASET_ARCHIVE.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CONTAMINATED_DATASET_ARCHIVE.md)
2. [`research/CONTAMINATION_AUDIT_V2.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CONTAMINATION_AUDIT_V2.md)
3. [`research/TEMPLATE_TAXONOMY.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/TEMPLATE_TAXONOMY.md)
4. [`research/PROVENANCE_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PROVENANCE_AUDIT.md)
5. [`research/DATASET_REBUILD_PROTOCOL.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/DATASET_REBUILD_PROTOCOL.md)
6. [`research/DATASET_PARTITION_PROTOCOL.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/DATASET_PARTITION_PROTOCOL.md)
7. [`research/TEST_ID_SPECIFICATION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/TEST_ID_SPECIFICATION.md)
8. [`research/TEST_OOD_SPECIFICATION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/TEST_OOD_SPECIFICATION.md)
9. [`research/OOD_VALIDATION_REPORT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/OOD_VALIDATION_REPORT.md)
10. [`research/NEW_DATASET_STATISTICS.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NEW_DATASET_STATISTICS.md)
11. [`research/PHASE2_6_REPORT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_6_REPORT.md)
12. [`research/PHASE2_6_GO_NO_GO.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_6_GO_NO_GO.md)

---

## 6. Execution Rule Conformance

In strict compliance with **PART 29 — DO NOT RUN FULL EXP-002**, no evaluation inference was launched against `IndraLLM-CS-v1.1-CANDIDATE`. 

Execution is halted pending human review and formal Go/No-Go approval.
