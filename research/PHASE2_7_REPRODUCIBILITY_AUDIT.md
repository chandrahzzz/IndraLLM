# IndraLLM — Adversarial Reproducibility & Integrity Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 25 Reproducibility, Determinism & Artifact Audit  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

Top-tier NLP conferences (ACL Reproducibility Badge, EMNLP Artifact Review) require that any third-party researcher can clone the repository, run deterministic offline scripts, and reconstruct the exact benchmark files, hashes, partitions, and baseline statistical estimates without external API access or manual interventions.

**Adversarial Verdict:** **PASS WITH LIMITATION.**
1. **Benchmark Rebuild is 100% Deterministic:** `python -m indrallm.collection.rebuild_benchmark_v1_1` executes completely offline, requiring zero network calls or API keys, and deterministically generates byte-for-byte identical partitions matching `data/questions/IndraLLM-CS-v1.1-CANDIDATE/data_manifest.json`.
2. **Deterministic Random Seeds:** Pinned to `seed = 42` across dataset partitioning, bootstrap resampling, and evaluator calibration.
3. **Limitation Disclosed:** Model inference in EXP-002 depends on remote model APIs or local GPU hardware. Determinism in inference requires pinning temperature to $0.0$ and recording precise model revision hashes.

---

## 2. Reproducibility Checklist & Verification Matrix

| Reproducibility Component | Repository Path / Artifact | Deterministic? | External Dependency? | SHA-256 Verified? | Status |
|---|---|---|---|---|---|
| **Legacy v1.0 Archive** | `data/questions/IndraLLM-CS-v1.0/` | YES | None | Verified in manifest | **FROZEN** |
| **Candidate v1.1 Dataset** | `data/questions/IndraLLM-CS-v1.1-CANDIDATE/` | YES | None | All 6 files match manifest | **VERIFIED** |
| **Benchmark Generator** | `src/indrallm/collection/build_decontaminated_benchmark_v1_1.py` | YES | None (Pure Python) | N/A | **REPRODUCIBLE** |
| **Partition Script** | `src/indrallm/collection/rebuild_benchmark_v1_1.py` | YES | None | N/A | **REPRODUCIBLE** |
| **CMI Engine** | `src/indrallm/collection/cmi.py` | YES | Pure Python | N/A | **REPRODUCIBLE** |
| **Statistical Engine** | `src/indrallm/evaluation/statistical_testing.py` | YES | Scipy, Statsmodels | N/A | **REPRODUCIBLE** |
| **Test Suite** | `tests/test_phase2_6_rebuild.py` | YES | Pytest | N/A | **PASSING (38/38)** |
| **Inference Pipeline** | `src/indrallm/generation/run_inference_pilot.py` | Conditional | API keys or local weights | N/A | **MOCK FALLBACK** |

---

## 3. Cryptographic Hash Verification

All candidate partitions on disk match their declared SHA-256 hashes in `data_manifest.json`:
- `development.csv`: `ae244ef8cc20bf76eecbf3c1264c180860477da09cb57c0e07ae4118f6f6ef42`
- `validation.csv`: `a22505f9629047a06a29ec62b083b4e6d42df790eb21cf897e9d7a2e88a03285`
- `test_id.csv`: `02ea9525d1a7efb28a2a7a9223e7f4460f951e4ceaa098ae8bdf09e259e21971`
- `test_ood.csv`: `166d8f40340b1be9078f44ff53c448bb52b1464b58e6e580e55047b0e14dbdf8`
- `condition_prompts_7500.csv`: `27fd7d30e3f7c9e6bb07a4a984fe7c9f80bf13e90ec54284d7a8d58544d6db53`
- `semantic_questions_full_1500.jsonl`: `e6106786a3148da0c7ce91a58a60ff9e2b102ce06d0426d4090b848dd30eb743`

---

## 4. Software Environment & Dependencies

- **Python Version:** 3.11.x
- **Core Dependencies:**
  - `numpy >= 1.24.0`
  - `pandas >= 2.0.0`
  - `scipy >= 1.10.0`
  - `statsmodels >= 0.14.0`
  - `scikit-learn >= 1.3.0`
  - `pytest >= 7.4.0`
- **Zero Proprietary Hardware Lock-In:** All benchmark construction, partitioning, CMI calculation, and statistical evaluations run on standard CPU architectures without GPU acceleration.
