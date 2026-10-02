# IndraLLM — Representation Fragility in Multilingual LLMs

[![Tests](https://img.shields.io/badge/tests-54%20passed%2C%201%20xfail-success)](tests/)
[![Paper](https://img.shields.io/badge/paper-submission--ready-blue)](paper/)
[![Reproducibility](https://img.shields.io/badge/reproducibility-100%25%20deterministic-brightgreen)](scripts/)
[![Budget](https://img.shields.io/badge/cumulative%20spend-%240.20606%20USD-blueviolet)](research/BUDGET.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Official Repository for:**  
> **"Representation Fragility: Evaluating Factual Reliability under Controlled Semantic Pairing Across Indic Code-Switching and Script Alternation"**  
> **Author:** Chandrahas Reddy ([kurkurrereddy@gmail.com](mailto:kurkurrereddy@gmail.com))  
> **Manuscript:** [paper/main_camera_ready.tex](paper/main_camera_ready.tex) | [CONFINFO.md](CONFINFO.md) | [paper/CLAIM_LEDGER.md](paper/CLAIM_LEDGER.md)

---

## 📌 Executive Summary

Multilingual Large Language Models (LLMs) are widely assumed to share a unified semantic conceptual space across languages. However, standard multilingual benchmarks frequently confound **linguistic representation** with **semantic content** by querying disparate questions across languages or applying noisy translations.

**IndraLLM** resolves this fundamental methodological confound by introducing a **controlled five-way semantic-paired evaluation framework**. Holding underlying factual propositions strictly invariant across authoritative Indian administrative, civic, and statutory law (20 parliamentary acts, *Right to Information*, *Consumer Protection*, *Digital Personal Data Protection*, etc.), we evaluate parametric factual recall across five scheduled Indian languages (**Hindi**, **Bengali**, **Tamil**, **Telugu**, **Kannada**) under five parallel linguistic modalities:

1. **`A_EN`**: Monolingual English control baseline.
2. **`B_NATIVE`**: Native Indic Brahmic script (Devanagari, Bengali, Tamil, Telugu, Kannada).
3. **`C_ROMAN`**: Romanized Indic (pure transliteration into Latin script).
4. **`D_CS`**: Romanized Code-Switching (lexical English mixed into Romanized Indic).
5. **`E_MIXED_SCRIPT`**: Dual-Script Alternation (English technical terms in Latin script embedded within native Brahmic sentences).

Evaluating state-of-the-art dense multilingual transformers (**Qwen-2.5-27B**), we uncover a severe **monotonic degradation in factual reliability** driven solely by surface representation: factual accuracy plummets from **64.0%** in English down to **24.0%** in dual-script alternation.

---

## 🔬 Core Empirical Results

### 1. Condition Accuracies & Factual Degradation (Qwen-2.5-27B, $N=500$)

All five conditions query the exact same 100 statutory propositions across 20 parliamentary acts:

| Condition | Modality Description | Factual Accuracy | 95% Wilson Score CI | Contrast vs. `A_EN` ($\Delta$) | Odds Ratio | McNemar Test ($p$-value) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **`A_EN`** | Monolingual English Baseline | **64.0%** (64/100) | [54.2%, 72.6%] | — | 1.000 | — |
| **`D_CS`** | Romanized Code-Switching | **43.0%** (43/100) | [33.8%, 52.8%] | **−21.0 pp** | 0.4243 | $\chi^2 = 9.30$, **$p = 0.00229$** |
| **`C_ROMAN`** | Romanized Indic Transliteration | **33.0%** (33/100) | [24.6%, 42.7%] | **−31.0 pp** | 0.2771 | $\chi^2 = 21.95$, **$p = 2.80 \times 10^{-6}$** |
| **`B_NATIVE`** | Native Indic Brahmic Script | **28.0%** (28/100) | [20.1%, 37.5%] | **−36.0 pp** | 0.2188 | $\chi^2 = 30.63$, **$p = 3.13 \times 10^{-8}$** |
| **`E_MIXED`** | Dual-Script Alternation | **24.0%** (24/100) | [16.7%, 33.2%] | **−40.0 pp** | 0.1776 | $\chi^2 = 30.42$, **$p = 3.48 \times 10^{-8}$** |

### 2. Orthographic Disentanglement (`D_CS` vs. `E_MIXED`)
By holding vocabulary invariant between Romanized code-switching (`D_CS`) and dual-script code-switching (`E_MIXED`), we isolate the pure orthographic penalty:
$$\Delta = -19.0\text{ percentage points}\quad (43.0\% \to 24.0\%),\quad \text{OR} = 0.4186,\quad \text{McNemar } p = 0.00395$$
Script alternation alone inflicts a statistically significant collapse in model retrieval performance.

### 3. Cross-Model Replication (Allam-2-7B, $N=500$)
- Overall Authentic Accuracy: **4.0%** (`A_EN`: 8.0%, `D_CS`: 5.0%, `E_MIXED`: 3.0%, `B_NATIVE`: 2.0%, `C_ROMAN`: 2.0%).
- Demonstrates a severe Indic capacity floor (2%–3%), with Spearman rank correlation $\rho = 0.6669$ ($p = 0.2189$, properly reported without inflation).

---

## 📊 Statistical Hardening & Methodological Transparency

IndraLLM subjects all empirical findings to adversarial statistical scrutiny:

1. **Hierarchical Generalized Estimating Equations (GEE)**:
   - **Level 1 (Prompt-level, unclustered, $N=500$):** $\beta = -0.8572$, $\text{SE} = 0.2902$, **$p = 0.0031$**
   - **Level 2 (Semantic Proposition Clustered, $N=100$):** $\beta = -0.8572$, $\text{SE} = 0.2614$, **$p = 0.0010$**
   - **Level 3 (Statutory Act Clustered, $N=20$):** $\beta = -0.8572$, $\text{SE} = 0.4426$, **$p = 0.0528$**  
     *(Disclosed transparently: Intra-cluster correlation $\text{ICC} = 0.2663$, Design Effect $\text{DEFF} = 7.39$, effective sample size $N_{\text{eff}} = 67.6$, power $= 55.93\%$. Level 3 clustering remains strictly significant for `B_NATIVE` $p < 0.0001$, `C_ROMAN` $p = 0.0004$, and `E_MIXED` $p = 0.0005$.)*

2. **Epidemiological Evaluator Sensitivity (2D Rogan–Gladen Inversion)**:
   - Evaluator error grid across true positive rates $\text{TPR} \in [0.80, 0.96]$ and false positive rates $\text{FPR} \in [0.04, 0.16]$.
   - Across all plausible evaluator profiles, the true adjusted representation penalty remains strictly positive: **$+16.82\%$ to $+34.38\%$** (baseline raw gap: $+25.82\%$).

3. **Mechanistic Investigation (Negative vs. Positive Findings)**:
   - **Token Fertility Mediation (Strictly Null):** Global subword sequence length does *not* linearly mediate accuracy loss (Baron–Kenny Path $b$: $\beta = -0.0212$, $p = 0.9387$; Sobel test: $z = 0.0769$, **$p = 0.9387$**).
   - **Script Boundary Shock (Positive Mechanism):** Dual-script alternation introduces a mean of **5.0–5.1 script transitions per prompt**, associating directly with a **20-fold surge in reasoning truncation** (20.0% in `E_MIXED` vs. 1.0% in `A_EN`).

4. **Prospective Benchmark Expansion (IndraLLM-CS-v1.2-PILOT)**:
   - Formulates and releases 25 additional statutory acts (`AUTH-021` to `AUTH-045`, 125 prompts), expanding the benchmark to 45 topics.
   - Increases prospective power to **88.6%** (exact: $88.57\%$, $N_{\text{eff}} = 152.2$, $\text{MDE} = 18.60\%$).

---

## 🗂️ Benchmark Datasets

| Dataset Partition | Path | Description | Evaluation Status |
|---|---|---|:---:|
| **Authentic Empirical Core (v1.1)** | `data/questions/IndraLLM-CS-v1.1-CANDIDATE/` | 20 statutory acts, 100 semantic groups, 500 prompts across 5 conditions & 5 languages | **Empirically Evaluated** |
| **Prospective Expansion (v1.2 Pilot)** | `data/questions/IndraLLM-CS-v1.2-PILOT/` | 25 additional statutory acts (`AUTH-021` to `AUTH-045`), 125 prompts | **Prospective Benchmark Design** |
| **Raw Predictions Artifact** | `results/EXP-002/full_predictions.jsonl` | 3,000 raw inference responses with judge labels and token metrics | **Frozen Canonical Artifact** |

### Evaluated Statutory Acts (Empirical Core: AUTH-001 to AUTH-020)
`AUTH-001`: Right to Information Act, 2005 | `AUTH-002`: Consumer Protection Act, 2019 | `AUTH-003`: Digital Personal Data Protection Act, 2023 | `AUTH-004`: Information Technology Act, 2000 | `AUTH-005`: Motor Vehicles (Amendment) Act, 2019 | `AUTH-006`: Rights of Persons with Disabilities Act, 2016 | `AUTH-007`: Real Estate (RERA) Act, 2016 | `AUTH-008`: Aadhaar Act, 2016 | `AUTH-009`: Food Safety and Standards Act, 2006 | `AUTH-010`: National Food Security Act, 2013 | `AUTH-011`: Payment and Settlement Systems Act, 2007 | `AUTH-012`: Insolvency and Bankruptcy Code, 2016 | `AUTH-013`: Negotiable Instruments Act, 1881 | `AUTH-014`: Companies Act, 2013 | `AUTH-015`: Competition Act, 2002 | `AUTH-016`: Micro, Small and Medium Enterprises Act, 2006 | `AUTH-017`: Arbitration and Conciliation Act, 1996 | `AUTH-018`: Legal Services Authorities Act, 1987 | `AUTH-019`: Protection of Women from Domestic Violence Act, 2005 | `AUTH-020`: Maintenance and Welfare of Parents and Senior Citizens Act, 2007.

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

### 2. Verify Every Number in the Manuscript (0.5s)
```bash
python scripts/verify_phase6_all_numbers.py
```
This recalculates all condition accuracies, Wilson CIs, odds ratios, McNemar test statistics, GEE clustering values, Allam replication numbers, and prospective power curves directly from `results/EXP-002/full_predictions.jsonl`.

### 3. Run the Research-Integrity Test Suite
```bash
python -m pytest -q
```
*Output: 54 passed, 1 intentional xfailed (`test_allam_capacity_floor_known_issue`), 0 failures.*

### 4. Regenerate Publication Figures & Tables
```bash
python scripts/generate_phase3_5_figures.py
python scripts/generate_phase4_figures.py
```
Outputs publication-ready figures to `paper/figures/` (Figures 1–8) and LaTeX tables to `paper/tables/` (Tables 1–8).

---

## 📁 Repository Structure

```
IndraLLM/
├── CONFINFO.md                      # Complete 44-section conference-grade knowledge base
├── research/
│   ├── CONFINFO.md                  # 40-part definitive scientific knowledge base
│   ├── CONFINFO_AUDIT.md            # Forensic audit of artifacts, conflicts, and reviewer risks
│   ├── BUDGET.md                    # Cumulative spend ledger ($0.20606 USD)
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
│   └── phase4/
│       └── phase4_statistical_investigation.json
├── scripts/
│   ├── verify_phase6_all_numbers.py # Standalone verification of all paper numbers
│   ├── audit_phase6_text_and_claims.py # Hostile reviewer claims and anonymity auditor
│   ├── generate_phase3_5_figures.py
│   └── generate_phase4_figures.py
├── tests/                           # Complete pytest suite (54 passed, 1 intentional xfail)
└── src/indrallm/                    # Core Python package (CMI calculation, filtering, inference)
```

---

## 📜 Historical Retrospective (Phase 0 Evolution)

An early prototype explored heuristic hallucination detection (IndicBERT) and distillation (Sarvam-2B) on informal social media text. During audit, we discovered that automated BERTScore evaluation against English reference answers yielded a massive linguistic confound ($r = +0.52$ with Indic character fraction), mistakenly labeling non-English answers as "hallucinated." 

Rather than tolerating this flaw, the project underwent a complete **Phase 0 Research Redesign**: discarding confounded heuristic metrics in favor of an **invariant semantic-paired statutory benchmark** with exact, checkable ground truths and hierarchical statistical modeling.

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
