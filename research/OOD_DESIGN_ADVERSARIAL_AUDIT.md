# IndraLLM — Adversarial Out-of-Distribution (OOD) Design & Distribution Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Parts 8 & 9 OOD Validity & Distributional Confound Analysis  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

The Phase 2.6 benchmark partitions designate 10 template families (`TF-01` to `TF-10`) as In-Distribution (Development, Validation, Test-ID) and reserve 2 template families (`TF-11` Cross-Entity Comparison and `TF-12` Conditional Regulatory Rules) exclusively for `Test-OOD` ($N=100$ semantic groups, 500 prompts).

**Hostile Reviewer Verdict:**
1. **Scope Overclaim:** The current design **DOES NOT** test "general out-of-distribution generalization" across domains or linguistic styles. It tests strictly **held-out task-family generalization** across two specific structural schema families. Calling this "broad OOD robustness" is an unscientific overclaim that an EMNLP reviewer will immediately reject.
2. **Severe Domain Confounding:** While In-Distribution partitions span 6 domains uniformly (Governance, Agriculture, Science, History, Education, Public Health), **`Test-OOD` contains ONLY 2 domains**: Governance (60%) and Agriculture (40%). Science, History, Education, and Public Health have **0.0% representation**. Any observed performance drop on Test-OOD is heavily confounded with domain-specific legal/regulatory reasoning difficulty.
3. **Difficulty and Length Discrepancy:** The average difficulty of Test-OOD items is $4.05 / 5.0$ compared to $2.50 / 5.0$ in Test-ID, and prompt/answer token length is $\sim 45\%$ longer.

---

## 2. Multi-Dimensional Distributional Comparison

| Dimension | Development ($N=1000$) | Validation ($N=200$) | Test-ID ($N=200$) | Test-OOD ($N=100$) | Confound Status |
|---|---|---|---|---|---|
| **Language Balance** | 20% each (hi, ta, te, bn, kn) | 20% each | 20% each | 20% each | **BALANCED** (Intentional control) |
| **Condition Balance** | 20% each (A, B, C, D, E) | 20% each | 20% each | 20% each | **BALANCED** (Intentional control) |
| **Template Families** | 10 families (`TF-01` to `TF-10`) | 10 families (10% each) | 10 families (10% each) | **Only 2 families (`TF-11`, `TF-12`)** | **HELD-OUT TASK TYPE** |
| **Domain Coverage** | 6 Domains (Gov, Ag, Sci, Hist, Edu, Health) | 6 Domains (Balanced) | 6 Domains (Balanced) | **2 Domains (Gov 60%, Ag 40%)** | **ACCIDENTAL SEVERE CONFOUND** |
| **Science Representation** | 16.0% (800 rows) | 15.0% (150 rows) | 17.5% (175 rows) | **0.0% (0 rows)** | Uncontrolled Domain Void |
| **History Representation** | 15.5% (775 rows) | 17.5% (175 rows) | 17.5% (175 rows) | **0.0% (0 rows)** | Uncontrolled Domain Void |
| **Public Health Representation** | 12.0% (600 rows) | 17.5% (175 rows) | 15.0% (150 rows) | **0.0% (0 rows)** | Uncontrolled Domain Void |
| **Mean Difficulty (1–5)** | 2.50 $\pm$ 1.12 | 2.50 $\pm$ 1.12 | 2.50 $\pm$ 1.12 | **4.05 $\pm$ 0.49** | **DIFFICULTY CONFOUND** |
| **Mean Reference Length** | 18.4 tokens | 18.2 tokens | 18.5 tokens | **29.8 tokens** | Multi-fact / comparative elongation |
| **Mean CMI (Condition D_CS)** | 17.29% | 17.29% | 17.29% | 17.29% | Matched |

---

## 3. Structural Generalization vs. Specific Question Types

### 3.1 What TF-11 and TF-12 Actually Test
- **`TF-11` (Cross-Entity Comparison):** Requires recalling two distinct statutory/institutional entities (e.g. `PMFBY` and `WBCIS`, or `NEFT` and `RTGS`) and articulating the functional contrast.
- **`TF-12` (Conditional Regulatory Thresholds):** Requires retrieving multi-variable qualifying conditions (e.g. CSR mandate requiring $\ge ₹500\text{ Cr net worth}$ OR $\ge ₹1000\text{ Cr turnover}$ OR $\ge ₹5\text{ Cr profit}$).

### 3.2 Reviewer Attack: Confounding Reasoning Type with OOD
If a model performs worse on `Test-OOD`:
- Is it because it fails to generalize its factual grounding to unseen structures?
- OR is it simply because comparing two entities or reciting multi-clause financial criteria is intrinsically harder than looking up a single scheme date?
- **Answer:** The current design cannot isolate these factors because difficulty, multi-entity reasoning, and OOD status are collinear.

---

## 4. Prompt Asymmetry in Test-OOD

As uncovered in the implementation audit:
- In English (`A_EN`), Test-OOD prompts specify:
  - `TF-11`: *"What is the key structural or operational difference between {name}?"*
  - `TF-12`: *"Under Indian statutory regulations, what specific prerequisite condition or timeline applies to {name}?"*
- But in conditions `B_NATIVE`, `C_ROMAN`, `D_CS`, and `E_MIXED_SCRIPT`:
  - The prompt defaults to: *"{name} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?"*
- **Consequence:** For Indian languages, the model is asked a generic rule question about a pair of entities (`PMFBY vs WBCIS के संबंध में...`), while in English it is explicitly directed to compare them. This creates an artificial English advantage in Test-OOD!

---

## 5. Mandatory Mitigations for EXP-002 & Paper Framing

1. **Reframe Claim:** In the paper, replace all instances of *"Out-of-Distribution Generalization"* with **"Held-Out Structural Schema Evaluation (Comparative & Conditional Schemas)"**.
2. **Disclose Domain Absence:** Explicitly state in the Limitations section: *"Test-OOD is restricted to regulatory governance and agricultural policy, and does not evaluate historical or scientific comparative reasoning."*
3. **Control for Task Difficulty:** When reporting OOD degradation, compare Test-OOD strictly against In-Distribution items of matching difficulty (Difficulty Level 4 & 5 items in Test-ID), rather than against the overall Test-ID average.
4. **Symmetric Carrier Prompts:** For future benchmark iterations, carrier prompts for B, C, D, and E in TF-11/TF-12 must be aligned with comparative and conditional syntax.
