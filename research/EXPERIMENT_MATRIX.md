# IndraLLM — Experiment Matrix & Registry

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Registry Policy:** Every empirical run receives a permanent identifier (`EXP-xxx`), pinned configuration file, git commit hash, random seed, raw output log, and machine-readable output summary (`metrics.json`). No results may be edited manually.

---

## 1. Master Experiment Catalog

| Experiment ID | Primary Objective | Hypotheses Tested | Dataset Slice | Models Evaluated | Target Output | Status |
|---|---|---|---|---|---|---|
| **EXP-001** | Pilot Semantic Benchmark Validation | H1, H3 | Pilot $N=500$ ($2,500$ queries) | Llama-3-8B, Llama-3-70B, Qwen-2.5-32B, Sarvam-2B | `results/EXP-001/` | Scheduled |
| **EXP-002** | Main Cross-Lingual & Condition Evaluation | H1, H3, H4 | Full Benchmark $N=2,000$ | 8 Models (Llama, Qwen, Sarvam, Airavata, Mistral, Gemma) | `results/EXP-002/` | Planned |
| **EXP-003** | Continuous Code-Switch Intensity Curve | H2 | Intensity Stratified $N=1,000$ | Top 4 Answering Models | `results/EXP-003/` | Planned |
| **EXP-004** | Tokenizer Fragmentation Correlate | H5 | Full Benchmark | All Model Tokenizers | `results/EXP-004/` | Planned |
| **EXP-005** | Tri-Layer Judge Calibration & Human Agreement | H1 | Human Gold Subset $N=1,500$ | Human Panel vs. Llama-3.1-8B, Gemini-1.5, Claude-3.5 | `results/EXP-005/` | Planned |
| **EXP-006** | Detector In-Distribution Benchmarking | H6, H7 | Random & QID Split ($N=10,000$ pairs) | TF-IDF, IndicBERT, XLM-R, Feature-Augmented | `results/EXP-006/` | Planned |
| **EXP-007** | Detector OOD Generalization (LOLO / LOMO / LODO) | H6, H7 | Disjoint Language/Model/Domain Splits | IndicBERT vs. Proposed Feature Detector | `results/EXP-007/` | Planned |
| **EXP-008** | Detector Artifact Control Ablation | H7 | Shuffled / Surface-only feature set | Logistic Regression vs. Full Detector | `results/EXP-008/` | Planned |
| **EXP-009** | Mitigation: Teacher Quality Filtering | H8 | Distillation Pool ($N=2,000$) | Llama-3-70B Teacher $\to$ Verification Filter | `results/EXP-009/` | Planned |
| **EXP-010** | Mitigation: Controlled Ablation ($M_0 \to M_4$) | H8 | Test Split ($N=400$ QIDs $\times$ 5 conditions) | Sarvam-2B (Base, SFT, Distill, Filtered Distill, DPO) | `results/EXP-010/` | Planned |
| **EXP-011** | Mitigation: Human Bilingual Preference Eval | H8 | Blinded Pairwise ($N=500$ pairs) | Base Sarvam vs. Proposed Mitigation | `results/EXP-011/` | Planned |

---

## 2. Detailed Experiment Protocols

### EXP-001: Pilot Semantic Benchmark Validation
- **Objective:** Verify feasibility of semantically matched 5-condition generation, inspect quality of natural code-switching across the 5 languages, measure initial factuality spread, and validate automated judging.
- **Sample:** 500 semantic units $\times$ 5 conditions = 2,500 prompts.
  - 100 semantic groups per language (Hindi, Tamil, Telugu, Bengali, Kannada).
  - 6 domains represented proportionally.
- **Models:**
  - Answering: `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, `qwen-2.5-32b`, `sarvam-2b-v0.5`.
  - Judging: Dual LLM judge (`llama-3.1-8b-instant` and `gemini-2.5-flash`).
- **Success Criteria:**
  - Semantic equivalence rate $\ge 95\%$ on human sample inspection.
  - Condition variance $\Delta \text{Factuality} > 0$ observable across at least 3 models.
  - Zero fatal rate-limiting errors or parsing failures.

### EXP-002: Main Empirical Factuality Experiment
- **Objective:** Execute full-scale confirmatory testing of H1, H3, and H4.
- **Model Panel (Diversity Specification):**
  1. `meta-llama/Llama-3.1-8B-Instruct` (Open multilingual generalist, 8B)
  2. `meta-llama/Llama-3.3-70B-Instruct` (High-capacity multilingual, 70B)
  3. `Qwen/Qwen2.5-32B-Instruct` (Strong multilingual reasoning, 32B)
  4. `Qwen/Qwen2.5-7B-Instruct` (Compact multilingual baseline, 7B)
  5. `sarvamai/sarvam-2b-v0.5` (Indic-specialized foundational, 2B)
  6. `ai4bharat/Airavata` (Indic instruction-tuned, 7B)
  7. `google/gemma-2-9b-it` (Independent multilingual architecture, 9B)
  8. `mistralai/Mistral-Small-24B-Instruct-2501` (Independent European multilingual, 24B)
- **Metrics Computed:**
  - Strict Factual Accuracy (% correct against evidence)
  - Hallucination Rate (% containing factual fabrications)
  - Refusal Rate (% refusing to answer or providing evasive statements)
  - Code-Switch Fidelity (% maintaining requested language mixing)
  - Token Fertility ($\text{subwords} / \text{word}$)

### EXP-006 & EXP-007: Detector Benchmark & Out-of-Distribution Stress Test
- **Detector Architectures Evaluated:**
  1. `Baseline-1`: TF-IDF (word + char n-grams) + Logistic Regression
  2. `Baseline-2`: Multilingual Transformer (`xlm-roberta-base`) sequence classifier
  3. `Baseline-3`: Indic-specialized Transformer (`ai4bharat/IndicBERTv2-MLM-only`)
  4. `Baseline-4`: Zero-shot NLI Judge (`microsoft/deberta-v3-large` MNLI)
  5. `Baseline-5`: Dual LLM Ensemble Judge (`llama-3.1-70b` + `gemini-flash`)
  6. `Proposed`: Multi-Modal Feature-Augmented Detector (`IndicBERTv2` + CMI + Script Transition Ratio + Token Fertility + Language Entropy)
- **Evaluation Splits:**
  - **Random Split:** Standard 80/10/10 stratified split by QID.
  - **LOLO (Leave-One-Language-Out):** Train on 4 languages, test on held-out 5th language.
  - **LOMO (Leave-One-Model-Out):** Train on answers from 3 model families, test on unseen model family.
  - **LODO (Leave-One-Domain-Out):** Train on 5 domains, test on held-out 6th domain.
  - **Hard Set:** Subsets with verified high entity ambiguity or multi-hop requirements.

### EXP-010: Factuality Mitigation Ablation Matrix
- **Ablation Configurations:**
  - **$M_0$ (Baseline):** Unmodified `sarvamai/sarvam-2b-v0.5` base model.
  - **$M_1$ (Naive SFT):** Supervised fine-tuning on raw model answers labeled correct.
  - **$M_2$ (Standard Distillation):** Fine-tuning on raw teacher (`llama-3.3-70b`) outputs without evidence verification.
  - **$M_3$ (Evidence-Filtered Distillation):** Fine-tuning strictly on teacher outputs verified against authoritative external evidence.
  - **$M_4$ (Preference Optimization - DPO):** Direct Preference Optimization pairing evidence-verified teacher outputs (chosen) against self-generated hallucinations (rejected).
- **Evaluation Requirements:**
  - Report mean $\pm$ std across 3 random training seeds ($s \in \{42, 123, 999\}$).
  - Measure Factuality, Hallucination, CMI Retention, and Refusal Rate.
