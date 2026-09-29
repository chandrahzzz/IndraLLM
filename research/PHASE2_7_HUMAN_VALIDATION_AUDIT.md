# IndraLLM — Adversarial Human Validation & Naturalness Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Parts 15 & 16 Forensic Human Annotation Verification  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

In the Phase 2.6 Report (`PHASE2_6_REPORT.md:58`) and Go/No-Go Gate Table (`PHASE2_6_GO_NO_GO.md:32`), the candidate dataset `IndraLLM-CS-v1.1-CANDIDATE` was reported as:
- `Gate G8 (Human Agreement): Fleiss' kappa = 0.719 -> PASS`
- `Gate G9 (Code-Switch Naturalness): Mean = 4.74 / 5.0 -> PASS`

**Adversarial Verdict:** **CRITICAL MISATTRIBUTION / UNVERIFIED.**
A forensic repository audit reveals that **zero native human annotators evaluated the newly generated 1,500 semantic groups of `IndraLLM-CS-v1.1-CANDIDATE`**. 
The numbers reported ($\kappa = 0.719$ and naturalness $4.74/5$) were measured exclusively on an earlier Phase 2 pilot subset ($N=150$ semantic groups, 750 prompts from `semantic_hardening_150.jsonl`). 

Carrying over validation statistics from an older pilot dataset to a completely rebuilt candidate benchmark without re-annotation is methodologically invalid under ACL/EMNLP standards. 

**Required Action:** Reclassify Gate G8 and Gate G9 for `IndraLLM-CS-v1.1-CANDIDATE` as **UNVERIFIED**.

---

## 2. Forensic Audit of Historical vs. Candidate Human Annotation

| Dimension | Phase 2 Pilot Hardening Sample | IndraLLM-CS-v1.1-CANDIDATE (Rebuilt) | Discrepancy Status |
|---|---|---|---|
| **Artifact File** | `data/questions/semantic_hardening_150.jsonl` | `data/questions/IndraLLM-CS-v1.1-CANDIDATE/` | Different Data Pool |
| **Semantic Groups Evaluated** | 150 groups | **0 groups** | **NOT VERIFIED** |
| **Total Prompts Annotated** | 750 prompts | **0 prompts** | **NOT VERIFIED** |
| **Number of Annotators** | 3 independent bilingual raters | None | Missing |
| **Languages Represented** | 30 groups per language (hi, ta, te, bn, kn) | None | Missing |
| **Conditions Represented** | 150 prompts per condition (A, B, C, D, E) | None | Missing |
| **Test-ID Items Annotated** | 0 items (Pre-partition dataset) | **0 items** | **NOT VERIFIED** |
| **Test-OOD Items Annotated** | 0 items (Pre-partition dataset) | **0 items** | **NOT VERIFIED** |
| **Observed Fleiss' $\kappa$** | $0.719$ (Substantial Agreement) | **UNTESTED** | False Attribution |
| **Observed Krippendorff's $\alpha$**| $0.719$ | **UNTESTED** | False Attribution |
| **Observed Naturalness (1–5)** | $4.74 \pm 0.38$ | **UNTESTED** | False Attribution |
| **Adjudication Recorded** | Majority voting (2/3) + senior resolver | None | Missing |

---

## 3. Naturalness Evaluation Audit

### 3.1 Pilot Protocol (Phase 2)
- Evaluated on a 5-point Likert scale (1 = completely unnatural/unintelligible, 5 = native/idiomatic colloquial code-switching).
- Stratification: 30 examples per language across conditions `C_ROMAN`, `D_CS`, and `E_MIXED_SCRIPT`.
- Independence: Naturalness was rated on an independent rubric from semantic equivalence, ensuring grammatical naturalness was not conflated with factual truth.
- Result: Mean $4.74 / 5.0$, with `D_CS` averaging $4.82$ and `E_MIXED_SCRIPT` averaging $4.61$.

### 3.2 Candidate Benchmark Vulnerability
- In `IndraLLM-CS-v1.1-CANDIDATE`, facts 76–280 were generated using synthetic carrier frames (`National_{Domain}_Registry_Unit_{idx}`).
- Because these synthetic phrases were generated algorithmically without native human review, their naturalness and colloquial authenticity are **unknown**.
- Claiming that the entire candidate benchmark achieves $4.74 / 5.0$ naturalness is **unsupported by empirical data**.

---

## 4. Preregistration & Gate Classification

1. **Gate G8 (Human Semantic Agreement on Candidate Benchmark):** **UNVERIFIED.**
   - The pilot study demonstrated that the prompt-generation protocol is *capable* of achieving $\kappa = 0.719$, but the candidate benchmark itself has not been annotated.
2. **Gate G9 (Code-Switch Naturalness on Candidate Benchmark):** **UNVERIFIED.**
   - Pilot naturalness of $4.74/5$ cannot be generalized to the synthetic padding tier without fresh human rating.
3. **Pre-EXP-002 Authorization Constraint:**
   - EXP-002 cannot claim "Human-Validated Ground Truth" for the full candidate benchmark.
   - The paper must clearly state: *"Pilot prompt construction was validated by three bilingual raters on 750 prompts ($\kappa = 0.719$), while full benchmark expansion relied on algorithmic scaling verified against formal grammatical schemas."*
