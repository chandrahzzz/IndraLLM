# IndraLLM — Representation Fragility in Multilingual LLMs

[![Tests](https://img.shields.io/badge/tests-57%20passed%2C%201%20xfail-success)](tests/)
[![Paper](https://img.shields.io/badge/paper-submission--ready-blue)](paper/)
[![Reproducibility](https://img.shields.io/badge/reproducibility-100%25%20deterministic-brightgreen)](scripts/)
[![Budget](https://img.shields.io/badge/cumulative%20spend-%240.21442%20USD-blueviolet)](research/BUDGET.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Official Repository for:**  
> **"Representation Fragility: Evaluating Factual Reliability under Controlled Semantic Pairing Across Indic Code-Switching and Script Alternation"**  
> **Author:** Chandrahas Reddy ([kurkurrereddy@gmail.com](mailto:kurkurrereddy@gmail.com))  
> **Manuscript:** [paper/main_camera_ready.tex](paper/main_camera_ready.tex) | [CONFINFO.md](CONFINFO.md) | [research/EXP003_MATCHED_EN_REPORT.md](research/EXP003_MATCHED_EN_REPORT.md)

---

## 📌 Executive Summary

Multilingual Large Language Models (LLMs) are widely assumed to share a unified semantic conceptual space across languages. However, standard multilingual benchmarks frequently confound **linguistic representation** with **semantic content** by querying disparate questions across languages or applying noisy translations.

**IndraLLM** resolves this fundamental methodological confound by introducing a **controlled five-way semantic-paired evaluation framework**. Holding underlying factual propositions strictly invariant across authoritative Indian administrative, civic, and statutory law (20 Indian public-policy and regulatory topics, e.g., *Crop Insurance Schemes*, *RTI*, *Consumer Rights*, *Companies Act*, *Arbitration*, *Banking Clearance*), we evaluate parametric factual recall across five scheduled Indian languages (**Hindi**, **Bengali**, **Tamil**, **Telugu**, **Kannada**) under controlled linguistic modalities:

1. **`A_EN` (Original)**: Monolingual English baseline (difference / timeline template).
2. **`A_EN_MATCHED`**: Syntactically matched English control (*"What is the main rule, date or parameter regarding {X}?"*).
3. **`D_CS`**: Romanized Code-Switching (lexical English mixed into Romanized Indic).
4. **`C_ROMAN`**: Romanized Indic (pure transliteration into Latin script).
5. **`B_NATIVE`**: Native Indic Brahmic script (Devanagari, Bengali, Tamil, Telugu, Kannada).
6. **`E_MIXED_SCRIPT`**: Dual-Script Alternation (English technical terms in Latin script embedded within native Brahmic sentences).

Evaluating state-of-the-art dense multilingual transformers (**Qwen-2.5-27B**), we uncover a severe **monotonic degradation in factual reliability** driven solely by surface representation: factual accuracy drops from **60.0%** in matched English down to **24.0%** in dual-script alternation.

---

## 🔬 Core Empirical Results

### 1. Condition Accuracies & Factual Degradation (Qwen-2.5-27B, $N=500$ Empirical Core)

All conditions query the exact same 100 propositions across 20 public-policy and regulatory topics:

| Condition | Phrasing / Modality Description | Factual Accuracy | 95% Wilson Score CI | Contrast vs. `A_EN_MATCHED` ($\Delta$) | Exact Binomial McNemar $p$ | Holm-Bonferroni Adjusted $p$ |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **`A_EN` (Original)** | Specific difference / timeline template | **64.0%** (64/100) | [54.2%, 72.7%] | +4.0 pp | $p = 0.5716$ | $p = 0.5716$ |
| **`A_EN_MATCHED`** | *"What is the main rule, date or parameter...?"* | **60.0%** (60/100) | [50.2%, 69.1%] | — | — | — |
| **`D_CS`** | Romanized Code-Switching (*"...ke regarding main rule..."*) | **43.0%** (43/100) | [33.7%, 52.8%] | **−17.0 pp** | **$p = 0.01372$** | **$p = 0.02744$** |
| **`C_ROMAN`** | Romanized Indic Transliteration | **33.0%** (33/100) | [24.6%, 42.7%] | **−27.0 pp** | **$p = 9.85 \times 10^{-5}$** | **$p = 3.94 \times 10^{-4}$** |
| **`B_NATIVE`** | Native Indic Brahmic Script | **28.0%** (28/100) | [20.1%, 37.5%] | **−32.0 pp** | **$p = 1.83 \times 10^{-6}$** | **$p = 1.10 \times 10^{-5}$** |
| **`E_MIXED`** | Dual-Script Alternation | **24.0%** (24/100) | [16.7%, 33.2%] | **−36.0 pp** | **$p = 2.03 \times 10^{-6}$** | **$p = 1.10 \times 10^{-5}$** |

### 2. Orthographic Disentanglement (`D_CS` vs. `E_MIXED`)
By holding vocabulary invariant between Romanized code-switching (`D_CS`) and dual-script code-switching (`E_MIXED`), we isolate the pure orthographic script-alternation penalty:
$$\Delta = -19.0\text{ percentage points}\quad (43.0\% \to 24.0\%),\quad \text{Discordant } (b=29, c=10),\quad \text{Exact Binomial } p = 0.00338,\quad \text{Holm-adj } p = 0.0101$$
Script alternation alone inflicts a statistically significant collapse in model retrieval performance on identical vocabulary.

### 3. Cross-Model Replication (Allam-2-7B)
- `A_EN_MATCHED`: **10.0%** (10/100) [95% CI: 5.5%, 17.4%]
- `A_EN` (Original): **8.0%** (8/100)
- `D_CS`: **5.0%** | `E_MIXED`: **3.0%** | `B_NATIVE`: **2.0%** | `C_ROMAN`: **2.0%**
- Demonstrates a severe Indic capacity floor (2%–3%), with Spearman rank correlation $\rho = 0.6669$ ($p = 0.2189$, properly reported without inflation).

---

## 📊 Statistical Hardening & Methodological Transparency

IndraLLM subjects all empirical findings to adversarial statistical scrutiny:

1. **Hierarchical Generalized Estimating Equations (GEE)**:
   - **Level 1 (Prompt-level, unclustered, $N=500$):** $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$: $\beta = -0.6873$, $\text{SE} = 0.2872$, **$p = 0.0167$**
   - **Level 2 (Semantic Proposition Clustered, $N=100$):** $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$: $\beta = -0.6873$, $\text{SE} = 0.2635$, **$p = 0.0091$**
   - **Level 3 (Topic Clustered, $N=20$):** $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$: $\beta = -0.6873$, $\text{SE} = 0.4844$, **$p = 0.1559$**  
     *(Disclosed transparently: Intra-cluster correlation $\text{ICC} = 0.2040$, Design Effect $\text{DEFF} = 5.895$, effective sample size $N_{\text{eff}} = 84.8$. Level 3 clustering remains strictly significant for `B_NATIVE` $p = 0.00018$, `C_ROMAN` $p = 0.0031$, and `E_MIXED` $p = 0.00035$.)*

2. **Epidemiological Evaluator Sensitivity (2D Rogan–Gladen Inversion)**:
   - Evaluator error grid across true positive rates $\text{TPR} \in [0.80, 0.96]$ and false positive rates $\text{FPR} \in [0.04, 0.16]$.
   - Across all plausible evaluator profiles, the true adjusted representation penalty between `A_EN_MATCHED` and `D_CS` remains strictly positive: **$+18.48\%$ to $+26.56\%$** (raw observed gap: $+17.0\%$).

3. **Mechanistic Investigation (Negative vs. Positive Findings)**:
   - **Token Fertility Mediation (Strictly Null):** Global subword sequence length does *not* linearly mediate accuracy loss (Sobel test: $z = 1.0161$, **$p = 0.3096$** using the official Qwen BPE tokenizer).
   - **Script Boundary Shock & Reasoning Truncation (Positive Mechanism):** Dual-script alternation introduces a mean of **5.00 script transitions per prompt** (Unicode-block verified), associating directly with a surge in reasoning truncation under an explicit automated rule: **41.0% in `E_MIXED` vs. 0.0% in `A_EN_MATCHED` (and 3.0% in `A_EN`)**.

4. **Prospective Benchmark Expansion (IndraLLM-CS-v1.2-PILOT)**:
   - Formulates and releases 25 additional statutory acts (`AUTH-021` to `AUTH-045`, 125 prompts), expanding the benchmark to 45 topics.
   - Elevates prospective power to **88.6%** (exact: $88.57\%$, $N_{\text{eff}} = 152.2$, $\text{MDE} = 18.60\%$).

---

## 🗂️ Benchmark Datasets & Experiment Artifacts

| Dataset Partition | Path | Description | Evaluation Status |
|---|---|---|:---:|
| **Authentic Empirical Core (v1.1)** | `data/questions/IndraLLM-CS-v1.1-CANDIDATE/` | 20 public-policy topics, 100 semantic groups, 500 prompts across 5 conditions & 5 languages | **Empirically Evaluated** |
| **Matched English Condition (EXP-003)** | `results/EXP-003-matched-en/` | 100 matched English prompts, 200 raw predictions, and complete statistical JSON ledger | **Empirically Evaluated & Frozen** |
| **Prospective Expansion (v1.2 Pilot)** | `data/questions/IndraLLM-CS-v1.2-PILOT/` | 25 additional statutory acts (`AUTH-021` to `AUTH-045`), 125 prompts | **Prospective Benchmark Design** |
| **Raw Predictions Artifact (EXP-002)** | `results/EXP-002/full_predictions.jsonl` | 3,000 raw inference responses with judge labels and token metrics | **Frozen Canonical Artifact** |

### Evaluated Public-Policy Topics (Empirical Core: 20 Topics)
1. PMFBY vs WBCIS (Crop Insurance) | 2. NEFT vs RTGS (Banking Settlements) | 3. Covaxin vs Covishield (Vaccine Approvals) | 4. Kharif vs Rabi Rice (Agricultural Seasons) | 5. ISRO PSLV vs GSLV Mk III (Launch Vehicles) | 6. Lok Sabha vs Rajya Sabha Money Bill (Parliamentary Procedure) | 7. National Park vs Wildlife Sanctuary (Environmental Protection) | 8. Classical Tamil vs Sanskrit Grammar (Linguistics) | 9. PM-KISAN vs Rythu Bandhu (Direct Benefit Transfers) | 10. Supreme Court vs High Court Writ Jurisdiction (Constitutional Law) | 11. Patents Act Compulsory License | 12. RTI Third Party Information | 13. GST Registration Exemption | 14. Companies Act CSR Mandate | 15. Arbitration Act Time Limit | 16. IBC Section 7 Default Threshold | 17. Environment Clearance Public Hearing | 18. Medical Termination of Pregnancy Act | 19. SEBI Insider Trading Pre-Clearance | 20. Citizenship Amendment Act Cut-off.

---

## 🚀 Quickstart & One-Click Reproducibility

IndraLLM is designed for **100% offline, zero-marginal-cost reproduction** using standard Python 3.10+.

### 1. Environment Setup
```bash
git clone https://github.com/chandrahzzz/IndraLLM.git
cd IndraLLM
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Every Number in the Matched Manuscript & Audit
```bash
python scripts/run_exp003_matched_analysis.py
```
This recomputes all condition accuracies, exact Wilson CIs, exact binomial McNemar statistics, GEE clustering values, Qwen BPE token fertility, and automated truncation rates directly from `results/EXP-002/full_predictions.jsonl` and `results/EXP-003-matched-en/matched_predictions.jsonl`.

### 3. Run the Complete Verification Test Suite
```bash
python -m pytest -q
```
*Output: 57 passed, 1 intentional xfailed (`test_allam_capacity_floor_known_issue`), 0 failures.*

---

## 📁 Repository Structure

```
IndraLLM/
├── CONFINFO.md                      # Complete 44-section conference-grade knowledge base
├── research/
│   ├── EXP003_MATCHED_EN_REPORT.md  # Comprehensive report on matched English & mechanisms
│   ├── CONFINFO.md                  # Definitive scientific knowledge base
│   ├── CONFINFO_AUDIT.md            # Forensic audit of artifacts, conflicts, and reviewer risks
│   ├── BUDGET.md                    # Cumulative spend ledger ($0.21442 USD)
│   └── PHASE2_5_RESEARCH_INTEGRITY_AUDIT.md
├── paper/
│   ├── main_camera_ready.tex        # Author-attributed submission manuscript
│   ├── main_anonymous.tex          # Double-blind anonymous submission manuscript
│   ├── CLAIM_LEDGER.md              # Granular verification & claim boundaries
│   ├── figures/                     # High-resolution publication figures (Fig 1 to 8)
│   ├── tables/                      # Standalone LaTeX tables (Table 1 to 8)
│   └── references.bib               # Complete bibliography
├── data/
│   ├── questions/
│   │   ├── IndraLLM-CS-v1.1-CANDIDATE/   # Evaluated 20-topic empirical core (7,500 prompts)
│   │   └── IndraLLM-CS-v1.2-PILOT/       # Prospective 25-topic expansion (125 prompts)
│   └── budget_ledger.json           # Cryptographic budget log
├── results/
│   ├── EXP-002/
│   │   └── full_predictions.jsonl   # Canonical 3,000 raw model prediction records
│   ├── EXP-003-matched-en/          # Matched English prompts, predictions, and summary JSON
│   │   ├── matched_prompts_100.jsonl
│   │   ├── matched_predictions.jsonl
│   │   └── matched_analysis_summary.json
│   └── phase4/
│       └── phase4_statistical_investigation.json
├── scripts/
│   ├── run_exp003_matched_inference.py # Matched English inference & judge runner
│   ├── run_exp003_matched_analysis.py  # Comprehensive re-analysis script
│   ├── verify_phase6_all_numbers.py    # EXP-002 verification script
│   ├── audit_phase6_text_and_claims.py # Reviewer claims and anonymity auditor
│   ├── generate_phase3_5_figures.py
│   └── generate_phase4_figures.py
├── tests/                           # Complete pytest suite (57 passed, 1 intentional xfail)
└── src/indrallm/                    # Core Python package (CMI calculation, filtering, inference)
```

---

## ⚖️ Citation & Research Integrity

All code, data, and manuscripts in this repository are released under open licenses to foster reproducible NLP research.

```bibtex
@inproceedings{reddy2026indrallm,
  title={{Representation Fragility: Evaluating Factual Reliability under Controlled Semantic Pairing Across Indic Code-Switching and Script Alternation}},
  author={Reddy, Chandrahas},
  booktitle={Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year={2026},
  url={https://github.com/chandrahzzz/IndraLLM}
}
```

**Author Contact:** Chandrahas Reddy — [kurkurrereddy@gmail.com](mailto:kurkurrereddy@gmail.com)  
**Project Inquiries & Issues:** Please open an issue on GitHub.
