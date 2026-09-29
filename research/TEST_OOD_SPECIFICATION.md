# TEST-OOD Specification: Structural Out-of-Distribution Partition

**Document Version:** 1.0 (Frozen Specification)  
**Target Specification:** Part 8 & 26 Out-of-Distribution Specification  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Scientific Purpose

A major critique of LLM benchmarking is that models often succeed on "in-distribution" tests by exploiting spurious syntactic template cues.

The **TEST-OOD** partition evaluates **structural and epistemic robustness**. It determines whether the linguistic representation effects observed in TEST-ID generalize to **fundamentally unseen question constructions and reasoning structures**:
- Multi-parameter cross-entity comparative contrasts (`TF-11`).
- Multi-condition statutory prerequisite rules (`TF-12`).

Under no circumstances may models, detectors, or prompting techniques be tuned or selected against TEST-OOD.

---

## 2. Partition Parameters

- **Number of Semantic Groups:** $N = 100$
- **Total Condition Prompts:** $500$ ($100 \times 5$ conditions)
- **Repeated-Measures Experimental Unit:** `semantic_id` ($N = 100$ clusters)
- **Language Distribution:** Balanced across 5 Indian languages (20 groups each: Hindi, Tamil, Telugu, Bengali, Kannada)
- **Condition Distribution:** Exactly 100 prompts each for `A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`
- **Template Families:** Strictly allocated to:
  - `TF-11`: `CROSS_ENTITY_COMPARISON` ($N = 50$ groups)
  - `TF-12`: `CONDITIONAL_REGULATORY` ($N = 50$ groups)

---

## 3. Strict Quarantining & Anti-Contamination Mandates

1. **Zero Template-Family Leakage:** Families `TF-11` and `TF-12` are completely absent from `DEVELOPMENT`, `VALIDATION`, and `TEST-ID`.
2. **Zero Critical Entity-Pair Overlap:** Evaluated entity pairs are unique to TEST-OOD ($0.0\%$ relational overlap with Development).
3. **Distinct Evidence Sources:** Evidence snippets and primary source URLs are drawn from distinct regulatory sections and statutory codes not cited in Development.
4. **Independent Evaluation Only:** Performance on TEST-OOD is analyzed strictly as a secondary out-of-distribution benchmark to test hypothesis robustness under domain and structural shifts.
