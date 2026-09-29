# IndraLLM — Phase 2.7 Adversarial Pre-EXP-002 Scientific Audit Report

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 28 & Part 30 Comprehensive Synthesis Report  
**Reviewer Role:** Hostile ACL/EMNLP/NAACL/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary

Phase 2.7 conducted an exhaustive, hostile adversarial pre-experiment scientific audit of the IndraLLM research repository, candidate benchmark (`IndraLLM-CS-v1.1-CANDIDATE`), statistical models, and planned claims. 

Under the primary operational directives:
- **EXP-002 WAS NOT RUN.**
- **NO LARGE-SCALE MODEL INFERENCE WAS EXECUTED.**
- **NO PAID API BUDGET WAS SPENT** (Total spend remains frozen at **$0.1040 USD**, well below the $5.00 USD target and $10.00 USD hard ceiling).
- **Sole Contributor / Author:** Strictly preserved as `Chandrahas Reddy <kurkurrereddy@gmail.com>` without third-party or organizational attribution.

---

## 2. Comprehensive 19-Point Audit Synthesis

### 1. Critical Issues Discovered
- **CRIT-01 (Synthetic Padding Exposure):** While facts 1–75 and 281–300 (95 unique topics, generating 475 semantic groups) are authentically sourced, facts 76–280 (205 facts, generating 1,025 semantic groups, ~68.3% of the candidate dataset) were algorithmically generated using synthetic formulaic patterns (`National_{Domain}_Registry_Unit_{idx}`).
- **CRIT-02 (Human Validation Conflation):** Gate G8 (Human Agreement $\kappa=0.719$) and G9 (Naturalness $4.74/5$) were reported as PASS for `IndraLLM-CS-v1.1-CANDIDATE`, but were actually measured on an earlier Phase 2 pilot sample ($N=150$). Zero native human annotators reviewed the 1,500 groups in v1.1-CANDIDATE.
- **CRIT-03 (B_NATIVE Entity Borrowing CMI Distortion):** English proper nouns were prepended in Latin script into native Brahmic carrier sentences (`PM-KISAN के संबंध में...`), artificially inflating `B_NATIVE` CMI from near $0\%$ to $16.75\%$, compressing the contrast between native script and code-switching (`D_CS` at $17.29\%$).

### 2. Major Issues Discovered
- **MAJ-01 (Domain Void in Test-OOD):** `Test-OOD` contains strictly 2 domains (Governance 60%, Agriculture 40%), with 0% representation for Science, History, Education, or Public Health.
- **MAJ-02 (Test-OOD Prompt Asymmetry):** English prompts explicitly direct the model to compare structural differences (`TF-11`), while Indic prompts ask for generic rules, creating an artificial English advantage in Test-OOD.
- **MAJ-03 (Evaluator Orthographic Bias):** The automated judge exhibits a $+10\%$ false-positive rate elevation on code-switched answers compared to English, risking misinterpretation of judge bias as model defect.
- **MAJ-04 (Severe Test-OOD Underpowering):** Test-OOD ($N=100$ semantic groups) has only $20.1\%$ power to detect a $5\%$ effect and $60.9\%$ power for a $10\%$ effect.
- **MAJ-05 (Missing Repeated-Measures GLMM):** The preregistered statistical plan specified a GLMM with logit link, but the codebase lacked this implementation.

### 3. Minor Issues Discovered
- **MIN-01 (Governmental Portal URL Overlap):** 10 root portal URLs (`cbic.gov.in`, `isro.gov.in`, `sebi.gov.in`) appear across both Development and Test-OOD for disjoint statutory entities.
- **MIN-02 (Offline Deterministic Mock Inference):** Offline test runs return deterministic mock strings (`Answer to: [prompt] [reference_answer]`) when API keys are absent, which must be distinguished from live model runs.

### 4. Fixes Applied in Phase 2.7
1. **Implemented Repeated-Measures Logistic Regression:** Added `fit_repeated_measures_logistic_regression` to `src/indrallm/evaluation/statistical_testing.py` using cluster-robust standard errors grouped by `semantic_id`.
2. **Reclassified Quality Gates:** Reclassified Gate G8 and G9 on `IndraLLM-CS-v1.1-CANDIDATE` as **`UNVERIFIED`**.
3. **Reframed Research Claims:** Downgraded "general out-of-distribution generalization" to "held-out structural schema generalization."
4. **Mandated Rogan-Gladen Bias Adjustment:** Formally incorporated evaluator prevalence adjustments into the Phase 3 analysis plan.

### 5. Unresolved Issues (To Be Disclosed in Paper)
- **Authentic vs Synthetic Tier Partitioning:** The candidate dataset contains 475 authentic and 1,025 synthetic semantic groups. Results must be reported disaggregated.
- **Test-OOD Prompt Asymmetry:** The generic Indic carrier phrasing in TF-11/TF-12 must be documented as an experimental limitation.

### 6. Revised Dataset Statistics
- **Total Semantic Units:** 1,500 groups (7,500 condition prompts)
- **Partitions:**
  - `development.csv`: 1,000 groups (5,000 prompts)
  - `validation.csv`: 200 groups (1,000 prompts)
  - `test_id.csv`: 200 groups (1,000 prompts)
  - `test_ood.csv`: 100 groups (500 prompts)
- **Language Balance:** Exactly 20.0% each (Hindi, Tamil, Telugu, Bengali, Kannada) across all partitions.
- **Condition Balance:** Exactly 20.0% each (`A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`) across all partitions.
- **Composition:** 475 Authentic Gazette Groups (31.7%), 1,025 Synthetic Scaling Groups (68.3%).

### 7. Revised Contamination Statistics
- **Exact String Duplicates:** 0 (0.0%) across all partition pairs.
- **Normalized String Duplicates:** 0 (0.0%) across all partition pairs.
- **Target Entity Overlap:** 0 (0.0%) across all partition pairs.
- **Evidence Snippet Overlap:** 0 (0.0%) across all partition pairs.
- **Evidence URL Overlap:** 10 domain root URLs (Dev vs Test-OOD, disjoint facts).
- **Template Family Overlap:** 10 families shared between Dev/Val/Test-ID; **0 overlap** with Test-OOD (`TF-11` and `TF-12` are 100% disjoint).

### 8. Revised OOD Assessment
- **Status:** **PASS WITH LIMITATION.**
- Does NOT measure broad domain OOD.
- Measures generalization to **two held-out structural reasoning schemas**: Cross-Entity Comparison (`TF-11`) and Conditional Regulatory Thresholds (`TF-12`).

### 9. Revised Power Analysis (Cluster Unit = Semantic Group)
- **Test-ID ($N=200$ clusters):**
  - MDE at 80% Power: $8.86\%$ (at $20\%$ discordance)
  - Power for $\Delta = 5\%$: $35.3\%$
  - Power for $\Delta = 10\%$: **$88.5\%$**
  - Power for $\Delta = 15\%$: **$99.7\%$**
  - Expected 95% CI Half-Width: $\pm 6.20\%$
- **Test-OOD ($N=100$ clusters):**
  - MDE at 80% Power: $12.53\%$ (at $20\%$ discordance)
  - Power for $\Delta = 5\%$: $20.1\%$
  - Power for $\Delta = 10\%$: $60.9\%$
  - Power for $\Delta = 15\%$: **$91.8\%$**
  - Expected 95% CI Half-Width: $\pm 8.77\%$
  - **Verdict:** Test-OOD is exploratory for subtle effects ($<12.5\%$).

### 10. CMI Findings
- **B_NATIVE CMI = 16.75%:** Mathematically accurate consequence of Gambäck & Das (2014) applied to Latin entity insertion into Indic scripts.
- **Condition Separation:** Cleanly verified through orthogonal dimensions: `D_CS` has low script transitions ($1.42$) but elevated language switches ($2.60$); `E_MIXED_SCRIPT` has high script transitions ($5.73$) and high language switches ($5.00$).

### 11. Semantic Equivalence Findings
- Automated cosine similarity ($\ge 0.82$) is insensitive to 10x numerical shifts (0.8502 sim) and temporal inversions (0.7026 sim).
- In-Distribution prompt carriers are verified semantically equivalent.
- Test-OOD contains an intentional prompt directive asymmetry between English and Indic carriers.

### 12. Human Validation Findings
- Phase 2 Pilot Sample ($N=150$): Fleiss' $\kappa = 0.719$, Krippendorff's $\alpha = 0.719$, Naturalness $4.74 / 5.0$.
- Candidate Benchmark ($N=1,500$): **0 items annotated by humans**. Status: **UNVERIFIED**.

### 13. Evaluator Findings
- Accuracy vs human gold standard: $88.3\%$, Cohen's $\kappa = 0.761$.
- Evaluator has a $+10\%$ false-positive penalty on code-switched answers.
- Rogan-Gladen prevalence adjustment is required to separate judge bias from model hallucination.

### 14. Synthetic Data Findings
- LLM Benchmark Generation Dependency: **0.0%** (100% programmatic procedural generation).
- Circularity between answering model and benchmark is zero.
- Primary factuality claims must be reported on the Authentic Core ($N=475$).

### 15. Statistical Findings
- Enforcing `semantic_id` as the repeated-measures cluster prevents pseudoreplication.
- Paired McNemar tests and cluster-robust logistic regression protect Type I error rates.

### 16. Reproducibility Findings
- 100% deterministic local generation.
- Random seeds pinned to $42$.
- All 6 candidate dataset files verify against declared SHA-256 hashes.

### 17. Test Suite Result
- Full pytest execution: `python -m pytest -q`
- Result: **38 passed, 1 xfailed (legacy v1.0 stop condition) in 1.91s**.
- Zero regression errors.

### 18. Total Budget Spent
- Phase 2.7 Spend: **$0.0000 USD**
- Cumulative Project Spend: **$0.1040 USD**
- Remaining Spend to Target (<$5.00): **$4.8960 USD**
- Remaining Spend to Ceiling ($10.00): **$9.8960 USD**

### 19. Final GO / NO-GO Recommendation
- **CONDITIONAL GO / PROCEED WITH DISCLOSED LIMITATIONS.**
- Full-scale model inference in EXP-002 may proceed only with explicit human authorization, provided that all documented limitations, gate classifications, and claims boundaries are strictly respected.
