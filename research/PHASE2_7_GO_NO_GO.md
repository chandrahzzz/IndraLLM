# IndraLLM — Phase 2.7 Adversarial Go / No-Go Decision Gate

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 29 Formal Scientific Gate Table (G1–G16)  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary & Authorization Decision

This document establishes the binding scientific quality gates governing authorization to advance to **Phase 3 / EXP-002 (Empirical Model Evaluation)**.

**MANDATORY RULE:** 
Under strict research integrity constraints, any metric not empirically demonstrated on `IndraLLM-CS-v1.1-CANDIDATE` must be classified as **`UNVERIFIED`** or **`PASS WITH LIMITATION`**. Under NO circumstances may an unverified metric be promoted to `PASS`.

**FINAL ADVERSARIAL VERDICT:** **CONDITIONAL GO / PROCEED WITH DISCLOSED LIMITATIONS.**
Full-scale model inference in EXP-002 is authorized **strictly under the condition** that:
1. Primary paper factuality claims are evaluated on the **Authentic Core ($N=475$ groups)**, with the synthetic scaling tier ($N=1,025$) reported as a diagnostic sensitivity check.
2. Gates G8 and G9 are reported as **UNVERIFIED on v1.1-CANDIDATE** (with pilot agreement cited separately).
3. Test-OOD is framed as **Held-Out Structural Schema Evaluation**, not general domain OOD.
4. Model factuality scores are reported alongside **evaluator-bias-adjusted scores**.
5. All paired analyses enforce the `semantic_id` repeated-measures cluster.

---

## 2. Master Scientific Quality Gate Table (G1 to G16)

| Gate ID | Evaluated Scientific Dimension | Target Threshold | Observed Value (Phase 2.7 Audit) | Status | Repository Evidence | Required Action Before / In EXP-002 Reporting |
|---|---|---|---|---|---|---|
| **G1** | **Dataset Integrity** | 1,500 groups, 7,500 prompts, 5 languages, 5 conditions | 1,500 groups, 7,500 prompts, exact balance (hi, ta, te, bn, kn; A, B, C, D, E) | **PASS WITH LIMITATION** | [`verify_candidate_integrity.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/scripts/verify_candidate_integrity.py) | Disclose that 475 groups form the Authentic Core and 1,025 form the Synthetic Tier. |
| **G2** | **Legacy Contamination Isolation** | Contaminated v1.0 isolated and documented | v1.0 archived, marked NOT VALID FOR HELD-OUT EVALUATION | **PASS** | [`CONTAMINATED_DATASET_ARCHIVE.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CONTAMINATED_DATASET_ARCHIVE.md) | Maintain v1.0 as frozen legacy reference. |
| **G3** | **Near-Duplicate Detection** | 0.0% cross-partition prompt duplication | 0 exact matches, 0 normalized matches; Max TF-IDF Sim = 0.6952 | **PASS** | [`NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md) | None; partitions are strictly disjoint. |
| **G4** | **Entity & Relation Leakage** | 0.0% entity overlap between Dev and Test | 0 overlapping target entities across all split boundaries | **PASS** | [`NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md) | None; zero target entity leakage. |
| **G5** | **Evidence Leakage** | 0.0% evidence snippet overlap | 0 overlapping snippets; 10 domain root URLs reused across disjoint topics | **PASS WITH LIMITATION** | [`NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md:Section 4`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md#4-forensic-investigation-of-overlapping-evidence-urls-dev-vs-test-ood) | Disclose governmental portal URL citations for disjoint entities. |
| **G6** | **OOD Design Validity** | Structural generalization across domains | Confined to 2 template families and 2 domains (Gov 60%, Ag 40%) | **PASS WITH LIMITATION** | [`OOD_DESIGN_ADVERSARIAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/OOD_DESIGN_ADVERSARIAL_AUDIT.md) | Reframe as "Held-Out Structural Task Schemas" rather than broad OOD. |
| **G7** | **Semantic Equivalence** | Symmetric meaning across A-E conditions | In-Distribution matched; Test-OOD exhibits comparative phrasing asymmetry | **PASS WITH LIMITATION** | [`SEMANTIC_EQUIVALENCE_ADVERSARIAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/SEMANTIC_EQUIVALENCE_ADVERSARIAL_AUDIT.md) | Disclose Test-OOD carrier phrasing asymmetry. |
| **G8** | **Human Validation Agreement** | Fleiss' $\kappa \ge 0.70$ on Candidate Benchmark | $\kappa = 0.719$ on Phase 2 pilot ($N=150$); **0 candidate items annotated** | **UNVERIFIED** | [`PHASE2_7_HUMAN_VALIDATION_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_HUMAN_VALIDATION_AUDIT.md) | Mark UNVERIFIED for v1.1-CANDIDATE; do not claim full benchmark human ground truth. |
| **G9** | **Code-Switch Naturalness** | Naturalness $\ge 4.5 / 5.0$ on Candidate Benchmark | $4.74 / 5.0$ on pilot ($N=150$); **unrated on candidate benchmark** | **UNVERIFIED** | [`PHASE2_7_HUMAN_VALIDATION_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_HUMAN_VALIDATION_AUDIT.md) | Disclose pilot naturalness rating without falsely generalizing to candidate tier. |
| **G10**| **Statistical Independence** | Strict repeated-measures clustering by `semantic_id` | Paired McNemar + Repeated-Measures Logistic Regression implemented | **PASS** | [`PHASE2_7_STATISTICAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_STATISTICAL_AUDIT.md) | Enforce `semantic_id` clustering across all Phase 3 scripts. |
| **G11**| **Statistical Power** | Power $\ge 80\%$ for primary contrasts ($\Delta \ge 10\%$) | Test-ID: $88.5\%$ power ($\Delta=10\%$); Test-OOD: $60.9\%$ power ($\Delta=10\%$) | **PASS WITH LIMITATION** | [`PHASE2_7_POWER_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_POWER_AUDIT.md) | Declare Test-OOD exploratory; report wide confidence intervals ($\pm 8.8\%$). |
| **G12**| **Evaluator Validity** | Accuracy $\ge 85\%$, $\kappa \ge 0.70$ vs human | Accuracy $88.3\%$, $\kappa=0.761$; $+10\%$ FPR penalty on code-switching | **PASS WITH LIMITATION** | [`EVALUATOR_HUMAN_VALIDATION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/EVALUATOR_HUMAN_VALIDATION.md) | Apply Rogan-Gladen prevalence adjustment to model factuality scores. |
| **G13**| **Prompt Control** | Identical framing, decoding, and constraints | Matched across A-E in-distribution; comparative framing difference in Test-OOD | **PASS WITH LIMITATION** | [`PHASE2_7_PROMPT_CONTROL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_PROMPT_CONTROL_AUDIT.md) | Disclose Test-OOD phrasing asymmetry in paper limitations. |
| **G14**| **Factual Provenance** | 100% authoritative primary source citations | Facts 1–75, 281–300 authentic; Facts 76–280 synthetic registry clauses | **PASS WITH LIMITATION** | [`PROVENANCE_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PROVENANCE_AUDIT.md), [`PHASE2_7_IMPLEMENTATION_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_IMPLEMENTATION_AUDIT.md) | Disclose synthetic scaling tier; do not claim 100% gazette grounding. |
| **G15**| **Reproducibility** | Deterministic pipeline, seeds, manifests | 100% deterministic local rebuild, SHA-256 manifests match | **PASS** | [`PHASE2_7_REPRODUCIBILITY_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_REPRODUCIBILITY_AUDIT.md) | Pinned seeds ($42$) and frozen hashes verified. |
| **G16**| **Claim Validity** | Claims bounded by demonstrated empirical evidence | 1 Supported, 5 Require EXP-002, 3 Plausible, 3 Overclaimed | **PASS WITH LIMITATION** | [`PHASE2_7_CLAIM_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_CLAIM_AUDIT.md) | Revise paper claims to strictly adhere to Claims Boundary Rules. |

---

## 3. Gate Status Summary

- **PASS:** 4 Gates (G2, G3, G4, G15)
- **PASS WITH LIMITATION:** 10 Gates (G1, G5, G6, G7, G10, G11, G12, G13, G14, G16)
- **FAIL:** 0 Gates
- **UNVERIFIED:** 2 Gates (G8 Human Agreement on candidate benchmark; G9 Naturalness on candidate benchmark)

**Recommendation:** Proceed to Phase 3 / EXP-002 only with explicit human authorization, and adhere to all documented limitations in subsequent publications.
