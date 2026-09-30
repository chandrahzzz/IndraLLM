# IndraLLM — Phase 4.5: Workstream 12
# Test Suite Integrity & Coverage Audit

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  

---

## 1. Executive Summary

This audit evaluates the substantive test coverage across the repository, determining what the 55 test items actually verify, why one test is intentionally marked `xfail`, and whether the test suite provides true regression protection against benchmark leakage, statistical corruption, and data tampering.

```text
======================== 54 passed, 1 xfailed in 2.68s ========================
```

---

## 2. Exhaustive Test Suite Breakdown

### Table 1: Test Module Coverage and Protection Mapping

| Test File | Tests | Status | Substantive Verification Focus & Invariants Protected |
|---|---|---|---|
| `test_phase4_audit.py` | 9 | **9 Passed** | Verifies 3-level hierarchy (500 $\to$ 100 $\to$ 20), Level 3 GEE standard error scaling, Design Effect ($\text{DEFF} = 7.391$), effective sample size ($N_{\text{eff}} = 67.6$), pilot proposition uniqueness ($25/25$), pilot prompt balance ($125$ prompts), mediation Path $a, b, c$ and Sobel null, factorial language invariance ($p \ge 0.0504$), and Rogan–Gladen sensitivity bounds ($+16.8\%$ to $+34.4\%$). |
| `test_phase3_5_forensic_audit.py` | 7 | **7 Passed** | Verifies exact recomputation of experiment metrics from `full_predictions.jsonl`, sample size balance across models ($1,500$ each), conditions ($600$ each), and languages ($600$ each), McNemar test execution, Rogan–Gladen variance estimation, and Holm–Bonferroni step-down correction. |
| `test_phase2_6_rebuild.py` | 7 | **7 Passed** | Verifies decontaminated partition disjointness in `IndraLLM-CS-v1.1-CANDIDATE`, zero template family leakage between Dev/Val/Test, and exact 5-way condition balance across partitions. |
| `test_phase2_5_integrity.py` | 8 | **7 Passed, 1 xfailed** | Verifies budget ledger enforcement, hard ceiling abortion ($10.00$), prompt length balance across conditions, CMI distribution bounds, and evaluator refusal detection. |
| `test_phase2_benchmark_validation.py` | 7 | **7 Passed** | Verifies semantic pairing integrity, CMI thresholds, and transliteration consistency. |
| `test_cmi.py` | 5 | **5 Passed** | Verifies Code-Mixing Index (CMI) mathematical bounds ($0 \le \text{CMI} \le 100$) and language identification tagging. |
| `test_semantic_paired.py` | 3 | **3 Passed** | Verifies semantic pairing constraints and entity identity across all 5 linguistic condition realizations. |
| `test_leakage_and_quality_gates.py` | 2 | **2 Passed** | Verifies cross-split n-gram overlap gates and quality thresholds. |
| `test_statistical_testing.py` | 7 | **7 Passed** | Verifies exact contingency matrix construction, McNemar test parity, and Holm–Bonferroni adjustment logic. |

---

## 3. Forensic Investigation of the Expected Failure (`xfail`)

- **Failing Test:** `tests/test_phase2_5_integrity.py::test_dataset_contamination_and_exact_duplicates`
- **Decorator:** `@pytest.mark.xfail(reason="CRITICAL STOP CONDITION #8: Benchmark scaling in v1.0 recycled 6 core question templates across 2,000 semantic groups, causing 100% template overlap between train, val, and test splits. Discovered during Phase 2.5 integrity audit.")`
- **Audit Assessment:** **LEGITIMATE AND ESSENTIAL SCIENTIFIC GUARD.**
  This test was created during Phase 2.5 to explicitly fail against the contaminated `IndraLLM-CS-v1.0` benchmark. It serves as a permanent regression sentinel ensuring that the contaminated legacy dataset is never accidentally un-flagged or repurposed. In contrast, `test_phase2_6_rebuild.py` tests `IndraLLM-CS-v1.1-CANDIDATE` and passes $100\%$ green.

---

## 4. Test Suite Conclusion

The test suite is fast ($2.68\text{s}$), fully deterministic, executes entirely offline, and rigorously protects every critical invariant of the research pipeline.
