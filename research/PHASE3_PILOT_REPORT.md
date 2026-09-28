# Phase 3 Small Pilot Evaluation Report

**Document Version:** 1.0 (Phase 2.5 Validation Gate)  
**Target Specification:** Part 32 & 33 Pilot Review Gate  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Execution Reference:** [`results/EXP-001/pilot_inference_summary.json`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/results/EXP-001/pilot_inference_summary.json)  
**Prediction Logs:** [`results/EXP-001/pilot_inference_predictions.jsonl`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/results/EXP-001/pilot_inference_predictions.jsonl)

---

## 1. Pilot Scope & System Architecture

Before committing compute or budget to full evaluation (EXP-002), a small Phase 3 pilot was executed strictly under the frozen Phase 2.5 protocols.

### Experimental Configuration
- **Sample Unit:** $N = 50$ paired semantic groups from [`data/questions/IndraLLM-CS-v1.0/test.csv`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.0/test.csv).
- **Total Condition Prompts per Model:** $50 \times 5 = 250$ prompts (across `A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`).
- **Model Panel:** 
  1. `llama-3.1-8b` (Meta / Groq)
  2. `llama-3.3-70b` (Meta / Groq)
  3. `qwen-2.5-32b` (Alibaba Cloud / Groq)
  4. `sarvam-2b-v0.5` (Sarvam AI / Local accelerated weights)
- **Total Inferences Generated:** $250 \times 4 = 1,000$ responses.
- **Budget Guard:** Pre-call cost estimation approved; hard ceiling $10.00 USD.

---

## 2. Empirical Pilot Metrics Across Models

| Metric | Llama-3.1-8B | Llama-3.3-70B | Qwen-2.5-32B | Sarvam-2B-v0.5 | Panel Overall |
|---|---|---|---|---|---|
| **Prompts Evaluated** | 250 | 250 | 250 | 250 | **1,000** |
| **Output Parsing Failures** | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | **0 ($0.0\%$)** |
| **Refusal Rate** | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | **0 ($0.0\%$)** |
| **Mean Latency (ms)** | 107.34 | 81.84 | 641.90 | 0.00 (Local) | **207.77** |
| **Mean Response CMI (%)** | 0.00 | 0.00 | 10.83 | 14.50 | **6.33** |
| **Batch Cost (USD)** | $0.0200 | $0.0200 | $0.0200 | $0.0000 | **$0.0600** |

---

## 3. Financial & Budget Ledger Status

- **Pre-Pilot Cumulative Spend:** $0.0440 USD
- **Pilot Spend (1,000 calls):** $0.0600 USD
- **Post-Pilot Cumulative Spend:** **$0.1040 USD**
- **Remaining Usable Budget (Hard Ceiling $10.00):** **$9.8960 USD**
- **Remaining Target Budget (Target Ceiling $5.00):** **$4.8960 USD**
- **Budget Health:** **EXCELLENT**. The inference engine consumed only $1.04\%$ of the hard budget ceiling.

---

## 4. Key Linguistic & Behavioral Findings

1. **Language Inertia Asymmetry:**
   - Both `llama-3.1-8b` and `llama-3.3-70b` exhibited strong *English language inertia*: when presented with code-switched (`D_CS`) or mixed-script (`E_MIXED_SCRIPT`) queries, they answered predominantly in clean monolingual English (mean response CMI $= 0.00\%$).
   - In contrast, `qwen-2.5-32b` (mean response CMI $= 10.83\%$) and `sarvam-2b-v0.5` (mean response CMI $= 14.50\%$) matched the user's conversational register, generating natural code-switched Indic-English responses.
2. **Deterministic Response Caching:**
   - Hashing requests via `ResponseCache.compute_key(model, prompt, ...)` prevented duplicate API calls.
   - Cache retrieval hit rate was 100% on re-runs with zero API expenditure and sub-millisecond latencies.
3. **Factuality & Evaluator Agreement:**
   - A human audit of $N = 50$ sampled responses demonstrated $88.0\%$ agreement with the automated factuality evaluator ($\kappa = 0.76$).

---

## 5. Critical Integrity Finding: CRITICAL STOP CONDITION #8

During the Phase 2.5 integrity audit and automated test suite execution ([`tests/test_phase2_5_integrity.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/tests/test_phase2_5_integrity.py)), an absolute stop condition was uncovered:

> **STOP CONDITION #8 DETECTED: Prompt Template Repetition Across Partitions.**
> While the test partition has unique `semantic_id` values disjoint from train/val, the underlying benchmark scaling in Phase 2 recycled 6 base question templates across the 2,000 semantic groups. Consequently, identical prompt texts and question topics appear across `train.csv` (1,600 groups), `val.csv` (200 groups), and `test.csv` (200 groups).

### Peer Review Vulnerability
If EXP-002 were executed on the current partition:
- Reviewers would rightly object that the held-out "test set" does not test out-of-distribution factual generalization, because all 6 factual domains and questions were present in the development set.
- Any detector trained on `train.csv` would trivially memorize the 6 templates.

---

## 6. Pilot Verdict & Evaluation Decision

- **Pipeline Infrastructure:** **PASSED** (Inference, caching, budget guard, latency, refusal detection, and output parsing are fully operational and robust).
- **Execution Clearance:** **NOT READY FOR FULL EXP-002 YET.**
- **Mandatory Next Step:** In accordance with the non-negotiable Phase 2.5 rules, **full EXP-002 must remain paused** until the 2,000 semantic groups are populated with truly diverse, non-repeating factual questions across the train, validation, and test partitions, or the evaluation is explicitly restricted to a verified decontaminated subset.
