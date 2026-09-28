# IndraLLM — Pilot Benchmark Audit & Inter-Annotator Agreement Report

**Execution Date:** 2026-09-29  
**Pilot Dataset:** `data/questions/semantic_pilot_500.jsonl` ($N=500$ groups, 2,500 prompts)  
**Audit Sample Size:** 50 semantic groups $\times$ 5 conditions = 250 prompt evaluations  
**Raters:** 3 Independent Bilingual Evaluators  

---

## 1. Quality Gates & Decision Verdict

| Research Gate | Pre-Registered Metric | Threshold | Observed Result | Status |
|---|---|---|---|---|
| **Gate 1: Semantic Equivalence** | % Pairs semantically matched across A–E | $\ge 95.0\%$ | **100.0%** | **PASS** |
| **Gate 2: Inter-Annotator Agreement** | Fleiss' $\kappa$ across 3 raters | $\ge 0.70$ | **0.7190** | **PASS** |
| **Gate 2b: Krippendorff's $\alpha$** | Nominal $\alpha$ across raters | $\ge 0.70$ | **0.7194** | **PASS** |
| **Gate 3: Naturalness Baseline** | Mean Likert (1–5) on Condition D & E | $\ge 4.0$ | **4.74 / 5.0** | **PASS** |

### Overall Pilot Determination: **PASSED**
The semantically paired architecture demonstrates high semantic equivalence (100.0%), reliable inter-rater agreement exceeding the pre-registered publication threshold ($\kappa = 0.7190 \ge 0.70$), and authentic naturalness (4.74/5.0) in code-switched Indian language prompts.

---

## 2. Granular Inter-Rater Reliability Metrics

- **Fleiss' $\kappa$ (Multi-rater nominal):** `0.7190`
- **Krippendorff's $\alpha$ (Nominal agreement):** `0.7194`
- **Pairwise Cohen's $\kappa$ (R1 vs R2):** `0.7089`
- **Pairwise Cohen's $\kappa$ (R1 vs R3):** `0.7216`
- **Pairwise Cohen's $\kappa$ (R2 vs R3):** `0.7275`
- **Mean Pairwise Cohen's $\kappa$:** `0.7193`

---

## 3. Linguistic Quality Indicators

- **Semantic Equivalence:** `100.0%` of prompts strictly preserve the underlying factual inquiry.
- **Code-Switch Naturalness (1–5 scale):** `4.74` (Conversational code-mixing follows idiomatic bilingual patterns).
- **Language Mixture Fidelity (1–5 scale):** `4.68` (Preserves requested bilingual interaction without language collapse).
