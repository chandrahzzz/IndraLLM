# IndraLLM — Complete Reproduction Guide

**Artifact Type:** Scientific Code, Benchmark Manifests, and Offline Statistical Pipeline  
**Execution Environment:** Standard Local Workstation / Laptop (Windows, Linux, or macOS)  
**Hardware Requirements:** CPU-only (No GPU required for reproduction)  
**Cloud / API Requirements:** Zero (100% offline local reproduction from frozen generation logs)  

---

## 1. Quickstart Reproduction Pipeline

### Step 1: Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install exact requirements
pip install -r requirements.txt
```

### Step 2: Verify Benchmark Integrity & Hashes
```bash
python scripts/validate_latex_syntax.py
```
This verifies that all candidate benchmark CSVs match the SHA-256 hashes recorded in `checksums/data_manifest.json`.

### Step 3: Run Full Statistical Verification Suite
```bash
python scripts/verify_phase6_all_numbers.py
```
This recomputes every single number, confidence interval, odds ratio, GEE clustering parameter, and power estimate directly from the 3,000 raw generation predictions in `results/EXP-002/full_predictions.jsonl`.

### Step 4: Regenerate Publication Figures
```bash
python scripts/generate_phase4_figures.py
```
Regenerates all 8 publication figures at 300 DPI into `results/phase4/figures/`.

### Step 5: Execute Pytest Test Suite
```bash
python -m pytest -q
```
Expected output:
```
54 passed, 1 xfailed in ~12s
```
*(Note: 1 xfail is the intentional contamination quarantine sentinel ensuring historical v1.0 data cannot leak).*

---

## 2. Directory Structure of Reproducibility Package

```
reproducibility/
├── README.md               # This step-by-step guide
├── requirements.txt        # Pinned dependency specifications
├── configs/
│   └── config.yaml         # Complete experiment hyperparameter definitions
├── checksums/
│   └── data_manifest.json  # Cryptographic SHA-256 hashes of all benchmark files
└── scripts/
    ├── verify_phase6_all_numbers.py    # Independent statistical reproduction
    ├── generate_phase4_figures.py      # Publication figure generator
    ├── validate_latex_syntax.py        # LaTeX structural & asset validator
    └── audit_phase6_text_and_claims.py # Anonymity & citation validator
```

---

## 3. Scope of Reproduction & Frozen Model Inference

- **Frozen Generation Outputs:** As documented in the paper, all 3,000 model generation calls and 3,000 factual judge evaluations were executed during EXP-002 under greedy decoding ($T=0.0$) and are permanently frozen in `results/EXP-002/full_predictions.jsonl`.
- **Zero API Spend:** Reproducing the statistical tests, tables, figures, and claims does **not** call any paid external APIs or require API keys.
- **Determinism:** All analytical statistical procedures, GEE fits, and plotting scripts are 100% deterministic and reproduce exact values down to 4 decimal places.
