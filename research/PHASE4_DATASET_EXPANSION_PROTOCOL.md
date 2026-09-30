# IndraLLM — Phase 4: Workstream 3 — Authentic Dataset Expansion Protocol
## Standard Operating Procedures for Scaling Authentic Indian Statutory Propositions

**Document Version:** 1.0 (Phase 4 Scientific Strengthening)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `69bd848`  

---

## 1. Executive Summary

To resolve the 20-topic clustering limitation identified in Workstreams 1 and 2, this protocol establishes standard operating procedures to scale the Authentic Indian Policy Core from 20 to **50+ independent statutory propositions**.

Scaling must **not** consist of generating synthetic clauses or paraphrasing existing facts. Every expanded proposition must represent an independently sourced, legally verified parliamentary act, regulatory threshold, or statutory comparison.

---

## 2. Eligibility & Provenance Criteria

### 2.1 Inclusion Criteria
Every candidate factual proposition must satisfy all five criteria:
1. **Primary Legislative Authority:** Must derive directly from an Act of the Indian Parliament, a Central Gazette Notification, a constitutional provision, or a statutory regulatory framework (e.g. SEBI, RBI, TRAI, FSSAI, CCI, RERA, IRDAI).
2. **Deterministic Truth Value:** The target fact must be truth-conditionally closed (e.g. precise numerical timeline, pecuniary threshold, statutory prerequisite, or jurisdictional distinction). Ambiguous, discretionary, or speculative legal matters are strictly excluded.
3. **Verifiable Primary Evidence:** Must include a verbatim evidence snippet from the official legislative text and a verifiable government URL (`.gov.in` or `.nic.in` domain).
4. **Bilingual Natural Usability:** Must represent a concept naturally discussed by bilingual citizens in India (e.g. consumer court limits, real estate RERA registration, PF withdrawal rules, maternity leave, traffic fines).
5. **Entity Independence:** Must introduce novel target statutory entities that do not appear anywhere in existing benchmark partitions.

### 2.2 Exclusion Criteria
- ❌ Fictitious, synthetic, or algorithmically generated clauses (e.g. `National_Agriculture_Registry_Unit_X`).
- ❌ State-level municipal bye-laws with localized, non-generalizable variation.
- ❌ News commentary, opinion pieces, or secondary law firm blog summaries.
- ❌ Transient economic statistics (e.g. quarterly GDP growth, fluctuating interest rates).

---

## 3. Semantic Pairing & Condition Realization Protocol

For each newly accepted statutory proposition $P_k$, exactly **5 parallel condition prompts** must be constructed under strict semantic pairing:

```
[Underlying Statutory Fact: Proposition P_k]
    ├── Condition A_EN:           Standard Indian English formal query
    ├── Condition B_NATIVE:       Monolingual vernacular query in native script (Devanagari, Tamil, Telugu, Bengali, Kannada)
    ├── Condition C_ROMAN:        Full Latin transliteration of the native vernacular query
    ├── Condition D_CS:           Romanized code-switched matrix with English technical statutory terms
    └── Condition E_MIXED_SCRIPT: Dual-script realization (Indic carrier in native script + English statutory terms in Latin)
```

### Invariance Rules across Conditions:
1. **Entity Invariance:** The core statutory entity or compared entities must appear in identical propositional roles across all 5 conditions.
2. **Target Answer Invariance:** The reference answer used by the factual evaluator must be 100% identical for all 5 prompts within the proposition cluster.
3. **Template Family Balance:** New propositions must expand both held-out structural schemas:
   - **`TF-11` (Cross-Entity Relational Comparison):** 50% allocation.
   - **`TF-12` (Conditional Regulatory Thresholds):** 50% allocation.

---

## 4. Quality Control & Decontamination Gates

Before any newly constructed proposition is admitted to the benchmark, it must pass three automated quality gates:
1. **13-gram Jaccard Contamination Gate:** Max 13-gram Jaccard similarity against all existing Development, Validation, and Test splits must be $< 0.35$.
2. **Embedding Semantic Similarity Gate:** Sentence-BERT cosine similarity between `A_EN` and back-translated vernacular prompts must exceed $0.85$.
3. **Gold Extraction Validation:** The gold reference answer must be cleanly extractable from the accompanying evidence snippet.

---

## 5. Versioning & Deprecation Policy

- All new authentic propositions must be saved under a separate, versioned namespace:
  `data/questions/IndraLLM-CS-v1.2-PILOT/`
- Historical benchmarks (`IndraLLM-CS-v1.0` and `IndraLLM-CS-v1.1-CANDIDATE`) must remain **frozen and unaltered** to preserve complete historical reproducibility.
