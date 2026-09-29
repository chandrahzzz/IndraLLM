# IndraLLM — Adversarial Semantic Equivalence & Semantic Inversion Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 14 Semantic Equivalence & Contrastive Inversion Stress Test  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

In Phase 2 and Phase 2.6, semantic equivalence across conditions was reported as passing an automated threshold of mean cosine similarity $\ge 0.82$ ($0.854 \pm 0.04$).

**Adversarial Challenge:**
Treating high cosine similarity as proof of semantic equivalence is an established methodological error in NLP. Dense embedding models and TF-IDF representations frequently assign high cosine similarity ($\ge 0.85$) to sentence pairs with **inverted polarity, swapped numeric magnitudes, or opposite temporal constraints**.

Furthermore, forensic analysis of `IndraLLM-CS-v1.1-CANDIDATE` reveals an actual semantic divergence between English and Indic prompts in Test-OOD (`TF-11` and `TF-12`).

---

## 2. Empirical Sensitivity Analysis: Contrastive Inversion Tests

We constructed controlled contrastive sentence pairs where a single token completely inverts or alters the factual meaning, and measured the resulting similarity:

| Perturbation Category | Sentence A (Base) | Sentence B (Perturbed Inversion) | TF-IDF Cosine Sim | Neural Embedding Sim (Typical) | Meaning Inverted? | Passes $\ge 0.82$ Similarity Gate? |
|---|---|---|---|---|---|---|
| **Numeric Magnitude** | *Annual assistance is 6,000 rupees.* | *Annual assistance is 60,000 rupees.* | **0.8502** | $\sim 0.94$ | **YES (10x Error)** | **FALSE PASS (CRITICAL)** |
| **Temporal Scope** | *Completed before March 31, 2023.* | *Completed after March 31, 2023.* | **0.7026** | $\sim 0.89$ | **YES (Opposite Window)** | **FALSE PASS (Neural)** |
| **Quantifier (Bound)** | *Must own at least 2 hectares.* | *Must own at most 2 hectares.* | **0.7297** | $\sim 0.88$ | **YES (Floor vs Ceiling)** | **FALSE PASS (Neural)** |
| **Comparator** | *Threshold requires more than 50 units.*| *Threshold requires less than 50 units.* | **0.7297** | $\sim 0.87$ | **YES (Inverted Criteria)** | **FALSE PASS (Neural)** |
| **Exclusivity** | *Only rural accounts are eligible.* | *Rural and urban accounts are eligible.* | **0.6418** | $\sim 0.82$ | **YES (Strict Scope)** | Borderline |
| **Polarity (Negation)** | *Scheme provides a subsidy.* | *Scheme does not provide a subsidy.* | **0.5577** | $\sim 0.86$ | **YES (Complete Negation)**| **FALSE PASS (Neural)** |

### Finding
An automated cosine similarity threshold ($\ge 0.82$) is **fundamentally blind** to 10x numerical errors, date directionality (`before` vs `after`), and quantifiers (`at least` vs `at most`). Cosine similarity alone is **insufficient evidence** of semantic equivalence.

---

## 3. Forensic Semantic Audit of Candidate Prompts (v1.1-CANDIDATE)

### 3.1 Facts 1 to 280 (In-Distribution)
- In-Distribution prompt carriers across all 5 conditions translate the exact same conceptual query:
  - `A_EN`: *"What is the statutory provision, date, or target for {entity}?"*
  - `B_NATIVE` (hi): *"{entity} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?"*
  - `C_ROMAN` (hi): *"{entity} ke sambandh mein mukhya niyam, tareekh ya mapdand kya hai?"*
  - `D_CS` (hi): *"{entity} ke regarding main rule, date ya parameter kya hai?"*
  - `E_MIXED_SCRIPT` (hi): *"{entity} के regarding main rule, date या parameter क्या है?"*
- **Audit Adjudication:** **SEMANTICALLY EQUIVALENT.** The target entity, required information, and factual answer constraints are identical across all 5 conditions.

### 3.2 Facts 281 to 300 (Test-OOD TF-11 & TF-12 Divergence)
- In Test-OOD, `A_EN` was customized with task-specific question phrasing:
  - `TF-11` (A_EN): *"What is the key structural or operational difference between {entity1} vs {entity2}?"*
  - `TF-12` (A_EN): *"Under Indian statutory regulations, what specific prerequisite condition or timeline applies to {entity}?"*
- BUT conditions `B_NATIVE`, `C_ROMAN`, `D_CS`, and `E_MIXED_SCRIPT` retained the generic template:
  - `TF-11` (B_NATIVE): *"{entity1} vs {entity2} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?"*
  - `TF-12` (B_NATIVE): *"{entity} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?"*
- **Audit Adjudication:** **PARTIAL ASYMMETRY.** In English, the model is asked specifically to articulate the *structural difference*, whereas in vernacular conditions it is asked for the *main rule or parameter*. While both answers converge on the same reference fact, the task directive is less explicit in Indic languages.

---

## 4. Multi-Layer Semantic Validation Requirements

To defend semantic equivalence before reviewers, the benchmark must implement a **3-stage verification pipeline**:
1. **Rule-Based Entity & Number Match:** Exact string matching of numerical constants, dates, and proper entities across condition prompt pairs.
2. **Polarity Check:** Strict checking that negation particles (`not`, `never`, `nahi`, `illai`, `kaadu`, `na`, `alla`) are symmetrically present or absent across all paired representations.
3. **Targeted Human Adjudication:** Human bilingual verification of any pair with cosine similarity between $0.75$ and $0.85$.

---

## 5. Audit Status: PASS WITH LIMITATION

- For In-Distribution (`development`, `validation`, `test_id`), semantic equivalence is confirmed.
- For Out-of-Distribution (`test_ood`), a prompt asymmetry exists between English and Indic carriers that must be disclosed in the paper.
