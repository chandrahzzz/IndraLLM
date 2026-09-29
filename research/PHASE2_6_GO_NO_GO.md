# Phase 2.6 Formal Go / No-Go Decision Gate

**Document Version:** 1.0 (Phase 2.6 Decision Matrix)  
**Target Specification:** Part 27 Formal Quality Gate Evaluation  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Evaluated Candidate:** `IndraLLM-CS-v1.1-CANDIDATE`  

---

## 1. Executive Summary & Verdict

| Final Gate Evaluation | **PASS (READY FOR PHASE 3 EXP-002 REVIEW)** |
|---|---|
| **Contamination Status** | **0.0% Overlap across Level 1–10 Leakage Dimensions** |
| **Dataset Scale** | **1,500 Semantic Groups (7,500 Condition Prompts)** |
| **Partitions Established** | **Development (5,000), Validation (1,000), Test-ID (1,000), Test-OOD (500)** |
| **Structural OOD Isolation** | **TF-11 & TF-12 strictly quarantined to Test-OOD (0% Dev presence)** |
| **Cumulative Project Spend** | **$0.1040 USD** (Target ceiling: $5.00, Hard ceiling: $10.00) |
| **Test Suite Verification** | **38 passed, 1 xfailed (documenting legacy v1.0 stop condition)** |
| **Execution Directive** | **STOPPING AT PHASE 2.6. Awaiting human approval before Phase 3.** |

---

## 2. Comprehensive 15-Gate Decision Table

| Gate | Metric / Dimension | Defined Threshold | Observed Value | Status | Evidence File |
|---|---|---|---|---|---|
| **G1** | Exact Prompt Duplication | $0.0\%$ between Dev and Test | **$0.0\%$ (0 / 1,500 shared prompts)** | **PASS** | [`NEW_DATASET_STATISTICS.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NEW_DATASET_STATISTICS.md) |
| **G2** | Semantic Question Duplication | $0.0\%$ between Dev and Test | **$0.0\%$ (0 / 300 shared base queries)** | **PASS** | [`DATASET_PARTITION_PROTOCOL.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/DATASET_PARTITION_PROTOCOL.md) |
| **G3** | Near-Duplicate / Paraphrase Leakage | Cosine Sim $< 0.85$ cross-split | **All pairs disjoint facts; max $r < 0.62$** | **PASS** | [`CONTAMINATION_AUDIT_V2.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CONTAMINATION_AUDIT_V2.md) |
| **G4** | Critical Entity-Pair Leakage | $\le 5.0\%$ Test-ID, $0.0\%$ Test-OOD | **$0.0\%$ Test-ID, $0.0\%$ Test-OOD** | **PASS** | [`TEST_ID_SPECIFICATION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/TEST_ID_SPECIFICATION.md) |
| **G5** | TEST-OOD Template Separation | $0.0\%$ TF-11 & TF-12 in Dev/Val | **$0.0\%$ presence in Dev, Val, Test-ID** | **PASS** | [`OOD_VALIDATION_REPORT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/OOD_VALIDATION_REPORT.md) |
| **G6** | Evidence / Claim Leakage | $0.0\%$ snippet overlap | **$0.0\%$ (0 / 300 shared snippets)** | **PASS** | [`PROVENANCE_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PROVENANCE_AUDIT.md) |
| **G7** | Semantic Equivalence Gate | Multilingual Embedding Cosine $\ge 0.82$ | **Mean Cosine $= 0.854 \pm 0.04$** | **PASS** | [`SEMANTIC_EQUIVALENCE_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/SEMANTIC_EQUIVALENCE_AUDIT.md) |
| **G8** | Human Inter-Rater Agreement | Fleiss' $\kappa \ge 0.70$ | **Fleiss' $\kappa = 0.719$, Cohen's $\kappa = 0.761$** | **PASS** | [`EVALUATOR_HUMAN_VALIDATION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/EVALUATOR_HUMAN_VALIDATION.md) |
| **G9** | Naturalness Rating | Likert Score $\ge 4.0 / 5.0$ | **$4.74 \pm 0.38 / 5.0$** | **PASS** | [`PHASE2_REPORT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_REPORT.md) |
| **G10**| CMI Within-Condition Variance | $\sigma^2 > 10.0$ in D_CS & E_MIXED | **D_CS $\sigma^2 = 22.91$, E_MIXED $\sigma^2 = 62.38$** | **PASS** | [`NEW_DATASET_STATISTICS.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NEW_DATASET_STATISTICS.md) |
| **G11**| 5-Condition Completeness | Exactly 5 conditions per semantic unit | **100% complete ($1,500 \times 5 = 7,500$)** | **PASS** | [`tests/test_phase2_6_rebuild.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/tests/test_phase2_6_rebuild.py) |
| **G12**| Provenance Validity | $100\%$ valid HTTPS official URLs | **$100\%$ verified ($0$ missing URLs)** | **PASS** | [`PROVENANCE_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PROVENANCE_AUDIT.md) |
| **G13**| Pre-Partitioning Enforcement | Partition assigned before condition gen | **Verified pre-partitioned factual allocation** | **PASS** | [`DATASET_REBUILD_PROTOCOL.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/DATASET_REBUILD_PROTOCOL.md) |
| **G14**| SHA-256 Manifest Verification | Exact disk hash matches manifest | **100% match across all partition files** | **PASS** | [`data_manifest.json`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.1-CANDIDATE/data_manifest.json) |
| **G15**| Automated Reproduction Suite | `python -m pytest -q` passes | **38 passed, 1 xfailed in 2.74s** | **PASS** | [`tests/test_phase2_6_rebuild.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/tests/test_phase2_6_rebuild.py) |

---

## 3. Explanatory Note on Statuses

1. **Gate G1–G15 Status: PASS**
   - The candidate benchmark `IndraLLM-CS-v1.1-CANDIDATE` resolves the cross-partition contamination discovered in Phase 2.5.
   - Test-ID and Test-OOD contain zero shared prompts, zero shared questions, and zero shared entity pairs with Development.
   - Structural OOD generalization is rigorously isolated via template families `TF-11` and `TF-12`.
2. **Phase 2.5 Stop Condition Cleared:**
   - The stop condition triggered in Phase 2.5 applied specifically to `IndraLLM-CS-v1.0`. With the construction of `IndraLLM-CS-v1.1-CANDIDATE`, the benchmark is methodologically clean and defensible for top-tier peer review.
3. **Execution Stop Enforced:**
   - In accordance with non-negotiable instruction **PART 29 — DO NOT RUN FULL EXP-002**, execution is stopped now. No full-scale inference evaluation will be performed until human review and approval.
