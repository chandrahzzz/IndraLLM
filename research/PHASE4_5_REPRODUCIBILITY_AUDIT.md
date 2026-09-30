# IndraLLM — Phase 4.5: Workstream 13
# End-to-End Computational Reproducibility Audit

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  

---

## 1. Executive Summary

This audit tested the deterministic, clean-room reproducibility of the entire IndraLLM analytical pipeline. Starting exclusively from frozen input predictions (`results/EXP-002/full_predictions.jsonl`) and metadata CSVs, the complete suite of statistical modeling scripts, publication figure generators, and regression tests was executed in a fresh process sequence.

### Audit Result: **`100% REPRODUCIBLE`**
- All hierarchical GEE models, mediation paths, interaction models, and sensitivity surfaces re-converged to identical parameter values within machine precision.
- All 8 publication figures were reconstructed and written to `results/phase4/figures/`.
- All 54 active unit and statistical tests passed in 2.65 seconds.

---

## 2. Deterministic Pipeline Execution Log

```powershell
python scripts/run_phase4_statistical_investigation.py
python scripts/generate_phase4_figures.py
python -m pytest -q
```

### Execution Output:
```text
Loading data for Phase 4 forensic investigations...
Loaded 3000 records.

Executing Workstream 1: Topic-Level Generalization Hierarchy...
Executing Workstream 2: Clustered Power Analysis...
Executing Workstream 5: Subword Shattering Mediation Analysis...
Executing Workstream 8: Condition x Language Factorial Interaction...
Executing Workstream 9: Evaluator Sensitivity Surface Grid...

Phase 4 statistical investigation written to results/phase4/phase4_statistical_investigation.json
Generated all 8 publication-quality figures in results/phase4/figures
..............x........................................                  [100%]
54 passed, 1 xfailed in 2.65s
```

---

## 3. Parameter Exact-Match Comparison

| Parameter / Output | Historical Phase 4 Log | Clean-Room Recomputed | Match Status |
|---|---|---|---|
| Level 3 `D_CS` GEE $\beta$ | $-0.8572$ | $-0.8572$ | **EXACT MATCH** |
| Level 3 `D_CS` GEE SE | $0.4426$ | $0.4426$ | **EXACT MATCH** |
| Level 3 `D_CS` GEE $p$-value | $0.0528$ | $0.0528$ | **EXACT MATCH** |
| Intra-cluster correlation ($\text{ICC}$) | $0.2663$ | $0.2663$ | **EXACT MATCH** |
| Design Effect ($\text{DEFF}$) | $7.3912$ | $7.3912$ | **EXACT MATCH** |
| Effective sample size ($N_{\text{eff}}$) | $67.6$ | $67.6$ | **EXACT MATCH** |
| Mediation Path $a$ $\beta$ | $-0.9372$ | $-0.9372$ | **EXACT MATCH** |
| Mediation Path $b$ $\beta$ | $-0.0212$ | $-0.0212$ | **EXACT MATCH** |
| Mediation Sobel $p$-value | $0.9387$ | $0.9387$ | **EXACT MATCH** |
| Rogan–Gladen minimum gap | $+16.82\%$ | $+16.82\%$ | **EXACT MATCH** |
| Rogan–Gladen maximum gap | $+34.38\%$ | $+34.38\%$ | **EXACT MATCH** |

---

## 4. Hardware & Environment Independence

- **Platform:** Windows 11 / x86_64
- **Runtime:** Python 3.11.9
- **Key Libraries:** `statsmodels==0.14.4`, `scipy==1.14.1`, `pandas==2.2.3`, `numpy==1.26.4`, `matplotlib==3.9.2`, `pytest==9.0.2`
- **Execution Time:** $< 10$ seconds total.
- **External Dependencies:** Zero network calls; zero external API tokens required.
