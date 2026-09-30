# IndraLLM Reproducibility Package & Artifact Guide

This repository contains the complete dataset, evaluation pipeline, statistical investigation engines, and manuscript generation assets for the paper:

> **Representation Fragility: Evaluating Factual Reliability under Controlled Semantic Pairing Across Indic Code-Switching and Script Alternation**

All empirical tables, statistical models, and publication figures in the paper are **100% computationally reproducible** from frozen local outputs in $< 10$ seconds without requiring paid external API calls.

---

## 1. System Requirements & Environment Setup

- **Python Version:** 3.10+ (Tested on Python 3.11.9, Windows x86_64)
- **Core Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
  Key pinned packages: `statsmodels>=0.14.0`, `scipy>=1.11.0`, `pandas>=2.0.0`, `numpy>=1.24.0`, `matplotlib>=3.8.0`, `pytest>=8.0.0`.

---

## 2. Directory Layout & Key Artifacts

```text
├── data/
│   └── questions/
│       ├── IndraLLM-CS-v1.1-CANDIDATE/   # Frozen evaluation benchmark (7,500 prompts)
│       └── IndraLLM-CS-v1.2-PILOT/       # Released 25-topic expansion (125 prompts)
├── results/
│   ├── EXP-002/
│   │   └── full_predictions.jsonl        # Raw model completions (3,000 evaluated records)
│   └── phase4/
│       ├── phase4_statistical_investigation.json  # Hierarchical GEE, mediation, sensitivity logs
│       └── figures/                      # 8 publication-quality figures (PNG, 300 DPI)
├── scripts/
│   ├── run_phase4_statistical_investigation.py   # Complete statistical modeling pipeline
│   ├── generate_phase4_figures.py                # Publication figure generation script
│   └── generate_phase4_pilot_data.py             # Deterministic expansion dataset builder
├── paper/
│   ├── main_anonymous.tex                # Anonymous submission manuscript
│   ├── main_camera_ready.tex             # De-anonymized camera-ready manuscript
│   ├── references.bib                    # 18 verified peer-reviewed BibTeX citations
│   ├── figures/                          # Verified figures linked by LaTeX
│   ├── tables/                           # 8 publication LaTeX tables
│   ├── supplementary/                    # Complete supplementary sections
│   └── CLAIM_LEDGER.md                   # Strict claim guardrail and allowed wording
└── tests/
    └── test_phase4_audit.py              # Automated regression test suite
```

---

## 3. Step-by-Step Reproduction Instructions

### A. Run Automated Verification Test Suite
Execute the deterministic pytest suite:
```bash
python -m pytest -q
```
**Expected Output:**
```text
54 passed, 1 xfailed in ~2.7s
```
*(The single `xfail` is an intentional scientific regression sentinel in `test_phase2_5_integrity.py` preserving the historical quarantine of legacy contaminated v1.0 data).*

### B. Regenerate Complete Statistical Investigation
Recompute all hierarchical variance components, 3-level GEE models, mediation paths, interaction models, and 25-point Rogan--Gladen sensitivity grids:
```bash
python scripts/run_phase4_statistical_investigation.py
```
**Output File:** `results/phase4/phase4_statistical_investigation.json`

### C. Regenerate All 8 Publication Figures
Re-render all publication figures from underlying experimental predictions:
```bash
python scripts/generate_phase4_figures.py
```
**Output Directory:** `results/phase4/figures/` (copied to `paper/figures/`)

---

## 4. Hardware Requirements & Cost Accounting

- **Execution Cost:** **$0.00 USD** (All analyses operate offline over frozen raw predictions in `results/EXP-002/full_predictions.jsonl`).
- **Compute Time:** $< 10$ seconds on any modern laptop or workstation (zero GPU requirement for analysis and plotting).
- **Cumulative Project Spend to Date:** `$0.20606 USD`.

---

## 5. Author Attribution & Contact

- **Lead Author & System Architect:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)
- **Repository:** `https://github.com/chandrahzzz/IndraLLM`
