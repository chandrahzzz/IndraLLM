# IndraLLM — Phase 6: Clean-Room Reproducibility & Verification Report

**Document Version:** 1.0 (Phase 6 Final Verification)  
**Lead Auditor:** Senior Reproducibility Auditor & Research Software Engineer  
**Author & Sole Contributor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Evaluation Scope:** Fully Local Offline Verification (Zero API Inference Spend)  

---

## 1. System Environment Specifications

| Parameter | Observed System Environment | Requirement / Standard | Status |
|---|---|---|---|
| **Operating System** | Windows 11 Pro (`Windows-10-10.0.26200-SP0`) | Windows / Linux / macOS compatible | **PASS** |
| **Python Version** | Python 3.11.9 (64-bit AMD64) | Python $\ge 3.10$ | **PASS** |
| **NumPy Version** | 2.1.3 | Compatible with SciPy / Pandas | **PASS** |
| **Pandas Version** | 2.2.3 | Standard DataFrame library | **PASS** |
| **SciPy Version** | 1.14.1 | Statistical testing library | **PASS** |
| **Statsmodels Version** | 0.14.4 | GEE & GLM modeling library | **PASS** |
| **Pytest Version** | 9.0.2 | Test execution framework | **PASS** |
| **Cloud/Colab Dependency** | **None** (100% locally runnable offline) | Self-contained local execution | **PASS** |

---

## 2. Test Suite Execution Audit

### Pytest Execution Command
```bash
python -m pytest -q
```

### Execution Output & Results
```
..............x........................................                  [100%]
54 passed, 1 xfailed in 12.99s
```

### Breakdown of Test Modules
- `tests/test_benchmark_split_integrity.py`: 12 passed (entity disjointness, template isolation, CMI enforcement)
- `tests/test_cmi_measurement.py`: 8 passed (Gambäck & Das formula verification, Latin/Indic token boundary parsing)
- `tests/test_phase2_5_integrity.py`: 9 passed, 1 intentional xfail (`test_legacy_v1_0_quarantine_enforcement`)
- `tests/test_phase3_5_forensic_audit.py`: 15 passed (recomputation of all 18 primary metrics against raw logs)
- `tests/test_phase4_audit.py`: 10 passed (GEE convergence, Sobel mediation, Rogan--Gladen inversion, pilot dataset isolation)

**Total Test Count:** 55 tests (54 passing, 1 intentional xfail).  
**Execution Time:** 12.99 seconds.  
**Failures:** 0 unexpected failures.

---

## 3. Data Integrity & SHA-256 Checksum Audit

All benchmark candidate partitions in `data/questions/IndraLLM-CS-v1.1-CANDIDATE/` were verified against `data_manifest.json`:

| File Name | Record Count | SHA-256 Hash Status | Verification |
|---|---|---|---|
| `development.csv` | 5,000 prompts | Verified match against manifest | **PASS** |
| `validation.csv` | 1,000 prompts | Verified match against manifest | **PASS** |
| `test_id.csv` | 1,000 prompts | Verified match against manifest | **PASS** |
| `test_ood.csv` | 500 prompts | Verified match against manifest | **PASS** |
| `condition_prompts_7500.csv` | 7,500 prompts | Verified match against manifest | **PASS** |
| `semantic_questions_full_1500.jsonl` | 1,500 groups | Verified match against manifest | **PASS** |

### Historical Contamination Sentinel Check
The historical contaminated v1.0 dataset (`data/questions/historical_contaminated_v1.0/`) is quarantined. It is physically isolated and cannot accidentally enter any active evaluation or training split.

---

## 4. Pipeline Execution & Output Verification

### Step 1: Statistical Recomputation
Command: `python scripts/verify_phase6_all_numbers.py`
- Raw records parsed: 3,000 predictions from `results/EXP-002/full_predictions.jsonl`.
- Accuracies verified:
  - `A_EN`: 64.0%
  - `D_CS`: 43.0%
  - `C_ROMAN`: 33.0%
  - `B_NATIVE`: 28.0%
  - `E_MIXED`: 24.0%
- GEE Level 3 robust standard errors and $p$-values replicated exactly.
- Execution time: 2.14s.

### Step 2: Figure Generation
Command: `python scripts/generate_phase4_figures.py`
- All 8 publication figures generated into `results/phase4/figures/` and mirrored to `paper/figures/`:
  - `fig1_effect_size_by_clustering_level.png` (114 KB)
  - `fig2_accuracy_by_condition_ci.png` (132 KB)
  - `fig3_tokenization_fragmentation_vs_accuracy.png` (172 KB)
  - `fig4_script_transitions_vs_error.png` (101 KB)
  - `fig5_condition_x_language.png` (289 KB)
  - `fig6_condition_x_model.png` (140 KB)
  - `fig7_error_taxonomy_by_condition.png` (141 KB)
  - `fig8_authentic_proposition_level_effects.png` (180 KB)
- Execution time: 8.61s.
- Hash/content comparison against committed paper figures: 100% identical.

### Step 3: LaTeX Syntax and Asset Integrity
Command: `python scripts/validate_latex_syntax.py`
- Both `paper/main_anonymous.tex` and `paper/main_camera_ready.tex` verified:
  - Braces balance: 0 unclosed braces.
  - Environments balance: 19 begins, 19 ends.
  - Inputs: 8 table files, 3 supplementary files all exist and resolve.
  - Figures: All 5 included figures exist and resolve.
  - Cross-references: All 13 `\ref{}` calls resolve to valid `\label{}` definitions.

---

## 5. Model Inference Status Disclosure

- **Live Model Inference:** Intentionally excluded from Phase 6 execution. Model outputs were generated during EXP-002 and are permanently frozen in `results/EXP-002/full_predictions.jsonl`.
- **Phase 6 API Expenditure:** Exactly **$0.00000 USD**.
- **Cumulative Project Expenditure:** Frozen at **$0.20606 USD** (well below the $5.00 USD target and $10.00 USD ceiling).

---

## 6. Reproducibility Auditor Final Sign-Off

The entire analytical and empirical pipeline reproduces completely, autonomously, and deterministically on a standard consumer laptop running Windows 11 without cloud dependencies or GPU requirements.

**Reproducibility Verdict:** **APPROVED / PASS**
