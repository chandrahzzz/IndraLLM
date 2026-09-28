# IndraLLM — Data Contamination & Leakage Prevention Protocol

**Document Version:** 1.0  
**Date:** 2026-09-29  

---

## 1. Contamination Vectors in Multilingual & Code-Switched Benchmarks

Evaluating factuality in LLMs involves severe contamination risks:
1. **Verbatim Question Leakage:** The evaluation query appears identically in model pre-training corpora (Common Crawl, Wikipedia, Reddit).
2. **Cross-Condition Leakage:** The model memorizes the English version of a question and transfers it across splits if questions are split row-by-row.
3. **Train-Test Semantic Leakage:** Similar syntactic structures, identical entities, or multi-question generation clusters leaking across splits.
4. **Benchmark Memorization:** Pre-existing benchmarks (e.g., TruthfulQA, TriviaQA, Samanantar) accidentally ingested into the benchmark.

---

## 2. Leakage Mitigation Architecture

```
                    Raw Candidate QA Pool
                              │
                              ▼
          [Stage 1: Semantic Unit Canonicalization]
            Assign immutable semantic_id (S000001)
                              │
                              ▼
        [Stage 2: Entity & N-gram Overlap Filtering]
          Drop near-duplicate questions (Jaccard > 0.6)
                              │
                              ▼
        [Stage 3: Grouped Semantic Splitting (MANDATORY)]
        All conditions (A, B, C, D, E) for S_i assigned
               STRICTLY to the same partition
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
         Train (80%)      Val (10%)        Test (10%)
        (Zero overlap of entities or questions)
```

---

## 3. Strict Pre-Commit Data Quality Gates

To enforce zero leakage, automatic pipeline checks are integrated into test suites (`tests/test_leakage.py`):
1. **Rule 1 — Zero Semantic ID Overlap:**
   $$\text{Train}_{\text{semantic\_ids}} \cap \text{Test}_{\text{semantic\_ids}} = \emptyset$$
   $$\text{Train}_{\text{semantic\_ids}} \cap \text{Val}_{\text{semantic\_ids}} = \emptyset$$
2. **Rule 2 — Min-Hash / Jaccard Semantic Distance:**
   No question in the Test set may share 8-gram Jaccard similarity $> 0.40$ with any question in the Train set.
3. **Rule 3 — Entity Isolation in Domain Splits:**
   In `split_domain_disjoint`, all entities and subdomains in the evaluation slice are entirely absent from the training partition.
4. **Rule 4 — Known Benchmark Contamination Check:**
   Questions are checked against standard Indic benchmarks (IndicGLUE, BHRAM-IL, Samanantar) using fuzzy string matching to ensure no verbatim copying.
