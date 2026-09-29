# Out-of-Distribution (TEST-OOD) Validation Report

**Document Version:** 1.0 (Phase 2.6 Validation Gate)  
**Target Specification:** Part 8, 25 & 26 OOD Hardening  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Evaluated Artifact:** [`data/questions/IndraLLM-CS-v1.1-CANDIDATE/test_ood.csv`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.1-CANDIDATE/test_ood.csv)  

---

## 1. Executive Summary & Structural Architecture

The primary objective of **TEST-OOD** is to test model hallucination and code-switch robustness on **fundamentally unseen epistemic and reasoning structures**.

In IndraLLM-CS-v1.1-CANDIDATE:
- **Total Semantic Groups:** $N = 100$
- **Total Condition Prompts:** $500$ ($100 \times 5$ conditions: `A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`)
- **Languages:** Balanced across 5 Indian languages (20 groups each: `hi`, `ta`, `te`, `bn`, `kn`)
- **Governing Template Families:** Exclusively allocated to:
  - `TF-11`: `CROSS_ENTITY_COMPARISON` ($N = 50$ semantic groups, $250$ prompts)
  - `TF-12`: `CONDITIONAL_REGULATORY` ($N = 50$ semantic groups, $250$ prompts)

---

## 2. Quarantining Verification & Anti-Contamination Diagnostics

To guarantee that `TEST-OOD` cannot be contaminated by training or development items, automated forensic assertions were executed across all candidate splits:

| Isolation Check | Development Set | Validation Set | Test-ID Set | Test-OOD Set | Observed Overlap with Test-OOD | Status |
|---|---|---|---|---|---|---|
| **Template Family TF-11 Presence** | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | 50 ($50.0\%$) | **$0.0\%$ (Zero Overlap)** | **PASSED** |
| **Template Family TF-12 Presence** | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | 50 ($50.0\%$) | **$0.0\%$ (Zero Overlap)** | **PASSED** |
| **Exact Prompt String Overlap** | 5,000 | 1,000 | 1,000 | 500 | **$0.0\%$ (0 strings)** | **PASSED** |
| **Base Semantic Question Overlap** | 1,000 | 200 | 200 | 100 | **$0.0\%$ (0 questions)** | **PASSED** |
| **Critical Entity-Pair Overlap** | 200 pairs | 40 pairs | 40 pairs | 20 pairs | **$0.0\%$ (0 pairs)** | **PASSED** |
| **Evidence Snippet Overlap** | 200 snippets | 40 snippets | 40 snippets | 20 snippets | **$0.0\%$ (0 snippets)** | **PASSED** |
| **Primary Source URL Overlap** | 200 URLs | 40 URLs | 40 URLs | 20 URLs | **$0.0\%$ (0 URLs)** | **PASSED** |

---

## 3. Cognitive & Reasoning Complexity of OOD Tasks

### 3.1 TF-11: Cross-Entity Contrastive Comparison
- **Cognitive Requirement:** Models must retrieve attributes of two distinct entities simultaneously (e.g. *PMFBY* vs *WBCIS*, *NEFT* vs *RTGS*, *Covaxin* vs *Covishield*, *PSLV* vs *GSLV Mk III*) and correctly attribute their defining differentiator without attribute-swapping hallucination.
- **Linguistic Challenge in Code-Switching:** Models frequently swap entity descriptors when technical comparative conjunctions (*"whereas"*, *"while"*, *"parantu"*, *"aanaal"*, *"kaani"*) appear alongside code-switched technical loanwords.

### 3.2 TF-12: Conditional Regulatory Prerequisite
- **Cognitive Requirement:** Evaluates multi-condition statutory rules containing explicit thresholds, temporal windows, and exclusion clauses (e.g., Section 84 Compulsory Licensing mandatory 3-year post-grant wait; Section 135 Companies Act net-worth/turnover thresholds).
- **Linguistic Challenge in Code-Switching:** Models routinely miss negative constraints (e.g., *"not exceeding"*, *"after expiration of"*) when embedded in colloquial mixed-script queries.

---

## 4. Linguistic Profiling of TEST-OOD

Across the 500 prompts in `test_ood.csv`:

| Condition | Mean CMI (%) | SD | Script Transitions | Language Switches | Switch Density | Token Count |
|---|---|---|---|---|---|---|
| **A_EN** | 0.00 | 0.00 | $1.40 \pm 0.49$ | $0.00 \pm 0.00$ | $0.00 \pm 0.00$ | $17.30 \pm 2.45$ |
| **B_NATIVE** | 15.20 | 2.80 | $1.80 \pm 0.40$ | $1.00 \pm 0.00$ | $0.04 \pm 0.01$ | $26.80 \pm 3.10$ |
| **C_ROMAN** | 13.80 | 4.10 | $1.40 \pm 0.49$ | $2.40 \pm 0.49$ | $0.18 \pm 0.03$ | $13.90 \pm 2.10$ |
| **D_CS** | 16.50 | 3.40 | $1.40 \pm 0.49$ | $2.60 \pm 0.49$ | $0.19 \pm 0.03$ | $13.60 \pm 2.05$ |
| **E_MIXED_SCRIPT**| 36.40 | 5.20 | $5.60 \pm 0.80$ | $5.00 \pm 0.00$ | $0.34 \pm 0.03$ | $16.10 \pm 2.15$ |

- `D_CS` maintains high linguistic switching ($2.60$ switches) with low script hopping ($1.40$).
- `E_MIXED_SCRIPT` exhibits high script hopping ($5.60$ transitions) and high CMI ($36.40\%$).
- Within-condition variance is well-preserved.

---

## 5. Formal Verdict: PASS

TEST-OOD achieves **$100\%$ mathematical and structural separation from Development and Validation sets**, satisfying all Phase 2.6 OOD specifications.
