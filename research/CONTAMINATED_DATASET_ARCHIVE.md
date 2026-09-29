# Contaminated Dataset Archive & Deprecation Notice: IndraLLM-CS-v1.0

**Archival Status:** DEPRECATED / CONTAMINATED — NOT VALID FOR PRIMARY HELD-OUT EVALUATION  
**Document Version:** 1.0  
**Date:** September 2026  
**Author:** Chandrahas Reddy  
**Preserved Location:** [`data/questions/IndraLLM-CS-v1.0/`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.0/)  
**Git Commit at Freezing:** `1093da7600d90ca545c943903307129551d4350f`  
**Data Manifest Checksum:** [`data/questions/IndraLLM-CS-v1.0/data_manifest.json`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.0/data_manifest.json)

---

## 1. Executive Summary of Contamination Discovery

During the Phase 2.5 research-integrity audit, an automated partition-leakage test ([`tests/test_phase2_5_integrity.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/tests/test_phase2_5_integrity.py)) discovered that the full-scale benchmark **IndraLLM-CS-v1.0** suffers from severe **template-level data contamination**:

- **Stated Benchmark Scale:** 2,000 semantic groups ($S000001$ to $S002000$), yielding 10,000 condition prompts across 5 languages (Hindi, Tamil, Telugu, Bengali, Kannada).
- **Actual Question Diversity:** Only **6 unique factual questions** were used as base templates and repeated across the 2,000 numeric IDs.
- **Cross-Partition Contamination:** Because semantic groups were assigned to partitions (`train.csv`: 1,600 groups; `val.csv`: 200 groups; `test.csv`: 200 groups) based solely on numeric `semantic_id` ranges, **all 6 base factual questions appear across every single partition**.
- **Contamination Rate:** Exactly **100% of prompt texts and factual claims in `test.csv` are identical duplicates of prompts in `train.csv` and `val.csv`**.

---

## 2. Preserved Manifest & Checksums (Immutability Guarantee)

In accordance with Phase 2.6 Rule 3 and Rule 4, **IndraLLM-CS-v1.0 is preserved in its entirety without modification or deletion** for historical traceability and scientific auditability:

| File Name | Row Count | Semantic Groups | SHA-256 Checksum |
|---|---|---|---|
| `condition_prompts_10000.csv` | 10,000 | 2,000 | `1a0a1186df7560ca60428c6b4838105c11acfa7d55d4658d11f1c1f8d43da36b` |
| `semantic_questions_full_2000.jsonl` | 2,000 | 2,000 | `c099e851f28c41718a820ce3edb240be34b64b2d9ad26072f17bed6a096694fb` |
| `train.csv` | 8,000 | 1,600 | `7e9258df898ff63fb9d76ee31a7ece18e1cece8a3481b24acf2ac5b8e0030940` |
| `val.csv` | 1,000 | 200 | `20081bca6aa325d3aff84dbc84640f8aceccf63b1896ba3775825dd4e7aa5757` |
| `test.csv` | 1,000 | 200 | `88f7ea3eeefd1ca9f54a67716b4c0d53b57bc8ddefe779f8b34ddb254aa3992a` |

---

## 3. Root Cause Analysis: Why Numeric Disjointness Was Insufficient

The scaling script ([`src/indrallm/collection/scale_benchmark_2000.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/src/indrallm/collection/scale_benchmark_2000.py)) defined a seed catalog of 6 hand-verified factual questions (`SEEDS_CATALOG`). To achieve $N = 2,000$ groups, it assigned incremented IDs ($S000001, S000002, \dots$) in a modular loop:

```python
seed = SEEDS_CATALOG[i % len(SEEDS_CATALOG)]  # Cycles through 6 templates 334 times
```

When validation logic checked for leakage:
```python
assert train_ids.isdisjoint(test_ids)  # PASSED: {'S000001', ...} is disjoint from {'S001601', ...}
```
The test passed because the string identifiers were disjoint. However, $S000001$ and $S001601$ contained the **exact same prompt text, entity set, evidence snippet, and gold answer** (PM-KISAN scheme annual financial support).

---

## 4. Scientific Consequences & Reviewer Attack Exposure

If an empirical paper were submitted with this test set:
1. **Pseudoscaling:** Reviewers would identify that the 10,000-prompt benchmark evaluates only 6 facts repeated 334 times.
2. **Data Leakage:** Any supervised hallucination detector or fine-tuned model trained on `train.csv` would memorize the 6 questions, achieving inflated evaluation accuracy on `test.csv` through template memorization rather than generalized reasoning.
3. **Desk Rejection:** At top-tier venues (ACL, EMNLP, NAACL, TACL), evaluating a test set that shares identical questions with the training set violates core benchmarking standards.

---

## 5. Approved vs. Prohibited Uses of IndraLLM-CS-v1.0

### Strictly Prohibited Uses
- **DO NOT** use `data/questions/IndraLLM-CS-v1.0/test.csv` for primary EXP-002 evaluation.
- **DO NOT** report model accuracy, hallucination rates, or detector ROC-AUC on this split in the main conference paper.
- **DO NOT** cite performance on this split as evidence of out-of-distribution generalization.

### Permitted Uses
- Unit testing and CI verification of pipeline throughput (latency, memory, batching).
- Verification of deterministic response caching and hashing routines.
- Educational demonstration of pseudo-scaling in benchmark engineering audits.
