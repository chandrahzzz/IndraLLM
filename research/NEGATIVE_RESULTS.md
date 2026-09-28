# IndraLLM — Negative Results & Failed Experiment Registry

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Policy:** Preservation of negative results to prevent publication bias and confirmation bias.

---

## 1. Documented Negative Empirical Findings

### NEG-001: Surface-Linguistic Boundary Entropy and Alignment Probes
- **Hypothesis Tested:** Fluency and boundary switch-point entropy features (CLSC, LES, BCS, Cross-Lingual Alignment) can reliably classify hallucinated code-switched answers.
- **Empirical Outcome:** ROC-AUC $\le 0.51$ (CLSC/LES/BCS) and ROC-AUC $0.52$ (Cross-Lingual Alignment).
- **Scientific Interpretation:** Real hallucinations in multilingual code-switched outputs are **fluent, grammatical factual confabulations**. Surface-level lexical transition entropy correlates with stylistic variability, not factual veracity.
- **Action Taken:** Surface-only heuristic detectors were permanently deprecated from the primary detector benchmark.

### NEG-002: Monolingual English BERTScore as a Code-Switched Hallucination Proxy
- **Hypothesis Tested:** BERTScore similarity against an English gold reference can serve as an automated ground truth label for code-switched Indian language responses.
- **Empirical Outcome:** High correlation with Indic script fraction ($r = +0.52, p < 0.001$).
- **Scientific Interpretation:** The metric measured whether the model answered in English vs. Indic languages rather than whether the factual assertion was true. Correct Indic answers received low scores and were mislabeled as hallucinations.
- **Action Taken:** BERTScore labeling was rejected as a ground-truth supervision source; replaced by multi-layer factual judging and human gold standards.

### NEG-003: Unweighted Loss Optimization under Class Imbalance
- **Hypothesis Tested:** Standard unweighted cross-entropy loss can train an IndicBERT sequence classifier on code-switched hallucination detection.
- **Empirical Outcome:** Classifier collapsed to trivial majority-class prediction (predicting 100% "Faithful", yielding F1 = 0.00).
- **Scientific Interpretation:** In natural model responses, hallucination incidence is sparse (~10%). Class-weighted cross-entropy ($w_{\text{hallu}} \approx 9.8$) or focal loss is mandatory.
