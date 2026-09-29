# IndraLLM-CS-v1.1 Dataset Rebuild Protocol

**Document Version:** 1.0 (Frozen Specification)  
**Target Specification:** Part 5, 6, 7 & 19 Quality Engineering  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Candidate Identifier:** `IndraLLM-CS-v1.1-CANDIDATE`  

---

## 1. The Rebuild Imperative & Philosophy

Phase 2.5 proved that expanding a small template bank into thousands of numeric IDs creates synthetic pseudoscaling and total partition contamination.

The Phase 2.6 rebuild replaces the 6 recycled seeds with a **curated, high-diversity knowledge corpus of authentic Indian factual queries**, designed according to three non-negotiable principles:

1. **Epistemic Authenticity:** Every fact is independently verifiable through public gazettes, statutory acts, national ministries, scientific agencies (ISRO, ICAR, AIIMS), or authoritative classical registries. No synthetic or hallucinated pseudo-facts.
2. **Structural Pre-Partitioning:** All semantic questions are assigned to partitions (`DEVELOPMENT`, `VALIDATION`, `TEST-ID`, `TEST-OOD`) **prior** to the generation of linguistic condition prompts. Under no circumstances are prompts split post-generation.
3. **Strict Structural OOD Isolation:** The benchmark formally introduces an Out-of-Distribution partition (`TEST-OOD`) governed by unseen template families (`TF-11` and `TF-12`), evaluating generalization beyond training templates.

---

## 2. Rebuild Execution Pipeline

```
[Authentic Factual Knowledge Base (1,500 Unique Facts)]
                         │
                         ▼
           [Quality & Provenance Gate]
     (Source verification, schema audit, deduplication)
                         │
                         ▼
        [Pre-Partitioning by Semantic ID]
   ┌─────────────────────┼─────────────────────┬──────────────────┐
   ▼                     ▼                     ▼                  ▼
DEVELOPMENT          VALIDATION             TEST-ID            TEST-OOD
(1,000 groups)       (200 groups)         (200 groups)        (100 groups)
(TF-01 to TF-10)     (TF-01 to TF-10)     (TF-01 to TF-10)    (TF-11 to TF-12)
   │                     │                     │                  │
   └─────────────────────┼─────────────────────┴──────────────────┘
                         ▼
           [Controlled Condition Generation]
  (Produce A_EN, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT)
                         │
                         ▼
        [Multidimensional Linguistic Profiling]
    (CMI, switches, script transitions, token fertility)
                         │
                         ▼
        [15-Gate Statistical & Quality Validation]
                         │
                         ▼
            [IndraLLM-CS-v1.1 Freeze & SHA256]
```

---

## 3. Provenance & Metadata Standards per Semantic Group

Each semantic unit records 12 core metadata fields:
1. `semantic_id`: Unique persistent identifier (`S000001` to `S001500`).
2. `domain`: Categorical domain (Governance, Agriculture, Public Health, History, Science, Education).
3. `subdomain`: Fine-grained topical classification.
4. `template_family_id`: Structural reasoning family (`TF-01` to `TF-12`).
5. `difficulty_level`: Calibrated scale (1 = elementary fact, 2 = standard statutory, 3 = multi-parameter, 4 = fine-grained historical/technical, 5 = cross-domain constraint).
6. `canonical_fact`: Full declarative statement of truth.
7. `reference_answer`: Concise, unambiguous gold answer string.
8. `evidence_snippet`: Verbatim factual excerpt supporting the answer.
9. `evidence_source_url`: Verifiable web archive or official portal URL.
10. `evidence_source_type`: Type (`govt_portal`, `official_archive`, `statutory_act`, `academic_registry`).
11. `target_entity_pair`: Critical entity tuple `(Subject, Object)` to track relational leakage.
12. `partition`: Explicit partition (`DEVELOPMENT`, `VALIDATION`, `TEST-ID`, `TEST-OOD`).

---

## 4. Linguistic Condition Generation Protocol

For each semantic group in language $L \in \{\text{hi}, \text{ta}, \text{te}, \text{bn}, \text{kn}\}$, five condition prompts are synthesized and validated:

- **A_EN (Monolingual English Baseline):** Standard grammatical English interrogative.
- **B_NATIVE (Monolingual Native Script):** Vernacular query written strictly in the corresponding Brahmic script (Devanagari, Tamil, Telugu, Bengali, Kannada) with formal vocabulary.
- **C_ROMAN (Romanized Indic):** Pure Latin-script transcription of the native Indic sentence using frequency-standardized orthography.
- **D_CS (Natural Code-Switched Latin):** Natural intra-sentential code-switching embedding English technical nouns, verbal roots, or phrases in an Indic matrix clause, fully written in Latin script.
- **E_MIXED_SCRIPT (Orthographic Mixed Script):** Intra-sentential code-switching featuring orthographic script alternation between Latin (for English vocabulary) and native Brahmic script (for Indic matrix clauses).

---

## 5. Cost & Budget Safety Guard

- The rebuild utilizes deterministic offline generation and local linguistic rules, incurring **$0.0000 USD** in API expenditure.
- The project spend remains frozen at **$0.1040 USD**, preserving $9.8960 USD of usable budget for approved downstream pilots.
