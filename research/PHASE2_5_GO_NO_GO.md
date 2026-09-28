# Phase 2.5 Formal Go / No-Go Research Integrity Decision

**Document Version:** 1.0 (Frozen Final Milestone)  
**Target Specification:** Part 35 Research Integrity Audit  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Decision Summary

| Overall Verdict | **PAUSE FULL EXP-002 (ABSOLUTE STOP CONDITION #8 TRIGGERED)** |
|---|---|
| **Pipeline & Statistical Readiness** | **PASSED & FROZEN** |
| **Statistical Analysis Plan** | **PRE-REGISTERED & FROZEN** (`PHASE3_STATISTICAL_ANALYSIS_PLAN.md`) |
| **Budget & Financial Status** | **PASSED** ($0.104 Spent of $10.00 Ceiling, $9.896 Usable) |
| **Critical Blocker** | **Gate G9 (Leakage / Contamination): 100% template overlap between train/val/test** |

In strict accordance with the non-negotiable research integrity principles of Phase 2.5, **full-scale EXP-002 evaluation must NOT proceed until Gate G9 is resolved**.

---

## 2. Comprehensive 12-Gate Audit Matrix

| Gate | Focus Area | Status | Critical Empirical Finding / Rationale |
|---|---|---|---|
| **G1** | Dataset Integrity | **PASS WITH LIMITATION** | All 10,000 condition prompts conform to the 23-column master schema with verified SHA-256 manifests. Limitation: Underlying question diversity is constrained to 6 core question prototypes scaled across IDs. |
| **G2** | Semantic Equivalence | **PASS WITH LIMITATION** | Replaced unverified "100%" claim with qualified evidence: 97.3% strict human agreement, 2.7% register nuances. Massive tokenization asymmetry between B_NATIVE and C_ROMAN ($17.62$ token gap) documented. |
| **G3** | CMI Validity | **PASS** | Implementation matches Gambäck & Das (2014). Non-zero within-condition variance confirmed in `D_CS` ($\sigma^2 = 59.13$) and `E_MIXED_SCRIPT` ($\sigma^2 = 19.03$). ANOVA confirms residual variance ($SS_{\text{within}} = 346,942.26$). |
| **G4** | Script / Language Disentanglement | **PASS** | Empirically proven: In `D_CS`, script transitions are $0.34 \pm 0.75$ while language switches are $4.07 \pm 1.31$ ($r = -0.0917$). Comparing `D_CS` vs `E_MIXED_SCRIPT` cleanly isolates script transitions. |
| **G5** | Annotation Reliability | **PASS** | Fleiss' $\kappa = 0.719$, Krippendorff's $\alpha = 0.719$, code-switch naturalness $= 4.74 / 5.0$. |
| **G6** | Evaluator Validity | **PASS** | Evaluator labeled as "automated evaluator", not ground truth. Calibrated against $N=300$ stratified human judgements: Accuracy $= 88.3\%$, Cohen's $\kappa = 0.761$, Precision $= 89.2\%$, Recall $= 86.4\%$. |
| **G7** | Evaluator Language Bias | **PASS WITH LIMITATION** | Quantified a $+10.0\%$ false positive elevation on code-switched/mixed-script queries. Rogan-Gladen prevalence adjustment pre-registered to correct for judge bias. |
| **G8** | Statistical Design | **PASS** | Primary repeated-measures unit frozen as `semantic_id` ($N=200$ clusters in test set). McNemar paired tests, bootstrap 95% CIs, and mixed-effects logistic regression `(1 \| semantic_id)` pre-registered. Pseudoreplication prohibited. |
| **G9** | Leakage / Contamination | **FAIL (STOP)** | **CRITICAL STOP CONDITION #8 TRIGGERED**: Test set prompt texts overlap 100% with train/val prompt texts due to scaling from 6 question prototypes. Test partition is not out-of-distribution with respect to development items. |
| **G10** | Reproducibility | **PASS** | Deterministic SHA256 response caching implemented. Request hash uniqueness verified. Code, data manifest, and generation parameters frozen. |
| **G11** | Budget Safety | **PASS** | Total cumulative spend to date is **$0.1040 USD** (Target ceiling: $5.00, Hard ceiling: $10.00). Pre-call budget guard strictly enforced. |
| **G12** | Phase-3 Pilot Validity | **PASS** | Small Phase 3 pilot completed across 50 groups (1,000 inferences across 4 models). Zero parsing failures, 0% refusal, robust cache hits, cost $0.060 USD. |

---

## 3. The Stop Condition Explained

### What Happened?
During Phase 2, the benchmark was scaled from 500 to 2,000 semantic groups by generating prompts for 6 core factual questions across 5 languages and repeating them with distinct `semantic_id`s ($S000001$ to $S002000$).
When the dataset was split into:
- Development/Train: 1,600 semantic groups (8,000 prompts)
- Validation: 200 semantic groups (1,000 prompts)
- Test: 200 semantic groups (1,000 prompts)

Because only 6 unique question templates existed in total, **all 6 questions appeared in Train, all 6 in Validation, and all 6 in Test**.

### Why This Is Fatal for ACL/EMNLP Review
If an NLP paper reports: *"We trained a hallucination detector on our train set and evaluated it on our held-out test set"*, but the test set contains the exact same questions as the train set, reviewers will immediately reject the submission for data leakage and overfitting to template artifacts.

---

## 4. Required Action Plan Before Running Full EXP-002

To transition Gate G9 from **FAIL** to **PASS**:
1. **Decontaminate Benchmark Items:** Populate the benchmark partitions with distinct, non-overlapping factual questions so that no semantic question in `test.csv` shares the same underlying question text, entity pair, or template with `train.csv`.
2. **Re-run Gate G9 Test:** Confirm that `test_dataset_contamination_and_exact_duplicates` passes with zero xfails.
3. **Execute Full EXP-002:** Only after G9 passes will the response cache and inference harness be triggered for the complete evaluation run.

---

## 5. Artifact Audit Trail (All Required Deliverables Created)

The following 12 research-integrity audit documents are fully written, empirical, and frozen in [`research/`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/):

1. [`research/PHASE2_5_RESEARCH_INTEGRITY_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_5_RESEARCH_INTEGRITY_AUDIT.md)
2. [`research/PHASE3_STATISTICAL_ANALYSIS_PLAN.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE3_STATISTICAL_ANALYSIS_PLAN.md)
3. [`research/CMI_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CMI_AUDIT.md)
4. [`research/CMI_DISTRIBUTION_REPORT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CMI_DISTRIBUTION_REPORT.md)
5. [`research/SCRIPT_VS_LANGUAGE_MIXING.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/SCRIPT_VS_LANGUAGE_MIXING.md)
6. [`research/SEMANTIC_EQUIVALENCE_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/SEMANTIC_EQUIVALENCE_AUDIT.md)
7. [`research/EVALUATOR_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/EVALUATOR_AUDIT.md)
8. [`research/EVALUATOR_HUMAN_VALIDATION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/EVALUATOR_HUMAN_VALIDATION.md)
9. [`research/LEGACY_RESULTS_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/LEGACY_RESULTS_AUDIT.md)
10. [`research/PHASE3_POWER_AND_PRECISION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE3_POWER_AND_PRECISION.md)
11. [`research/PHASE3_PILOT_REPORT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE3_PILOT_REPORT.md)
12. [`research/PHASE2_5_GO_NO_GO.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_5_GO_NO_GO.md)
