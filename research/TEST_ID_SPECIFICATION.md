# TEST-ID Specification: Primary In-Distribution Held-Out Split

**Document Version:** 1.0 (Frozen Specification)  
**Target Specification:** Part 8 In-Distribution Specification  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Scientific Purpose

The **TEST-ID** partition serves as the primary held-out empirical evaluation set for testing the central pre-registered hypotheses (H1 to H8):

> *When semantic content is held constant within paired units, how does linguistic representation (English vs. Native vs. Romanized vs. Code-Switched vs. Mixed-Script) affect factual hallucination rates in Indian languages?*

TEST-ID evaluates generalization to **new semantic questions, new facts, and new entities** within the familiar syntactic and epistemic distribution of In-Distribution template families (`TF-01` to `TF-10`).

---

## 2. Partition Parameters

- **Number of Semantic Groups:** $N = 200$
- **Total Condition Prompts:** $1,000$ ($200 \times 5$ conditions)
- **Repeated-Measures Experimental Unit:** `semantic_id` ($N = 200$ clusters)
- **Language Distribution:** Balanced across 5 Indian languages (40 groups each: Hindi, Tamil, Telugu, Bengali, Kannada)
- **Condition Distribution:** Exactly 200 prompts each for `A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`
- **Template Families:** Uniform coverage across `TF-01` through `TF-10` (20 groups per family)

---

## 3. Strict Inclusion & Exclusion Criteria

### Inclusion Criteria
1. Factually verified against official gazettes or authoritative institutional archives.
2. Complete semantic pairing across all 5 conditions with identical reference answers and evidence.
3. Automated semantic equivalence cosine similarity $\ge 0.82$.

### Exclusion / Anti-Leakage Criteria
1. **Zero Prompt Overlap:** Must not contain any prompt text present in `DEVELOPMENT` or `VALIDATION`.
2. **Zero Question Overlap:** Must not contain any base question present in `DEVELOPMENT` or `VALIDATION`.
3. **Controlled Entity-Pair Overlap:** No critical relation tuple $(E_1, R, E_2)$ may duplicate a relation tested in the training partition.
4. **Prohibition of Template Overlap with OOD:** Zero instances of `TF-11` (Cross-Entity Comparison) or `TF-12` (Conditional Regulatory) are permitted in TEST-ID.
