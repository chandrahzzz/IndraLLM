# Legacy Results & Claims Audit

**Document Version:** 1.0 (Frozen for Phase 2.5)  
**Target Specification:** Part 23 Research Integrity Audit  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Audit Mandate

In earlier iterations of IndraLLM (v0.1-baseline and early pilot phases), several preliminary metrics and claims were generated. To prevent the uncritical carryover of legacy numbers into the publication-grade Phase 3 manuscript, this audit classifies every prior claim into one of four immutable scientific statuses:

1. `SUPPORTED BY NEW BENCHMARK`: Formally re-evaluated and confirmed under IndraLLM-CS-v1.0 protocols.
2. `REQUIRES REVALIDATION`: Plausible hypothesis requiring re-execution under frozen Phase 3 evaluation.
3. `OBSOLETE / HISTORICAL`: Generated under flawed, unpaired, or deprecated v0.1 methodologies; must never appear in final publication text.
4. `UNSUPPORTED`: Refuted or methodologically invalid upon audit.

---

## 2. Audit Matrix of Prior Claims

| Prior Claim / Metric | Original Source | Current Status | Detailed Audit Rationale |
|---|---|---|---|
| **IndicBERT Detector ROC-AUC = 0.884** | v0.1 Baseline | `OBSOLETE / HISTORICAL` | Evaluated on unstructured, unpaired legacy dataset without artifact controls. Susceptible to language/script shortcut learning. Must be re-trained and re-evaluated against the 10 strong baselines specified in Part 19. |
| **Contrastive Decoding reduces hallucination by ~28%** | v0.1 Mitigation Pilot | `REQUIRES REVALIDATION` | Pilot used simple heuristics and small sample ($N < 100$). Must be re-tested under frozen EXP-003 with refusal-rate and naturalness trade-off metrics. |
| **Language-dependent hallucination gap (Telugu > Hindi)** | v0.1 Report | `REQUIRES REVALIDATION` | Prior finding conflated script token fragmentation with model language knowledge. Must be analyzed using within-model condition interactions and token fertility covariates. |
| **Pilot Inter-Annotator Agreement $\kappa \approx 0.719$** | Phase 2 Pilot ($N=500$) | `SUPPORTED BY NEW BENCHMARK` | Re-verified across $N=150$ hardening groups and $N=300$ evaluator validation items ($\kappa = 0.719 - 0.761$). |
| **Automated Semantic Equivalence = 100%** | Phase 2 Pilot | `OBSOLETE / HISTORICAL` | 100% was an automated embedding threshold ($>0.82$). Replaced by qualified human audit showing 97.3% strict equivalence and 2.7% register nuances (see `SEMANTIC_EQUIVALENCE_AUDIT.md`). |
| **Code-Mixing Index directly drives hallucination** | Early Working Hypothesis | `UNSUPPORTED` (in causal form) | Conflates condition jumps with continuous CMI; overlooks tokenization and evaluator bias. Re-framed as paired condition contrast with mechanistic explanatory analysis. |
| **Zero Parsing Failures in Model Generation** | Phase 2 EXP-001 Pilot | `SUPPORTED BY NEW BENCHMARK` | Confirmed across 200 calls in pilot inference cache ($0.0\%$ failure rate). |
| **Sarvam-2B high latency penalty** | v0.1 Note | `OBSOLETE / HISTORICAL` | Local inference benchmarks show Sarvam-2B has $0.0$ external API latency and runs at $<25\text{ms/token}$ on modern accelerators. |

---

## 3. Policy for Phase 3 Execution

1. **Clean Slate for Empirical Results:** No numerical claim from v0.1 will be cited in Phase 3 tables without fresh generation under the frozen `data_manifest.json` and response cache.
2. **Traceability:** Any historical comparison will explicitly cite `git tag: v0.1-baseline` and clearly state that legacy datasets lacked paired semantic controls.
