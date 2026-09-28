# IndraLLM — Novelty Audit & Scientific Differentiation

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Review Standard:** ACL/EMNLP Senior Area Chair Evaluation  

---

## 1. Audit Framework

For every claimed contribution of IndraLLM, we apply a four-question litmus test:
1. *Has this exact claim or artifact been published before?*
2. *Is our implementation substantially different from existing literature?*
3. *Is the difference scientifically meaningful or merely an incremental engineering wrapper?*
4. *Can the contribution be empirically supported through our proposed experiments?*

---

## 2. Granular Novelty Audit of Proposed Contributions

### Contribution 1: Semantically Paired Benchmark across 5 Orthographic Conditions
- **Prior Work:** Parallel corpora exist for machine translation (e.g., FLORES, Samanantar). However, hallucination benchmarks in NLP (HaluEval, TruthfulQA, BHRAM-IL) either test monolingual English or un-paired monolingual target languages.
- **Substantial Difference:** We create $5 \times 1$ paired tuples ($S_{EN}, S_{Native}, S_{Roman}, S_{CS}, S_{Mixed}$) for identical underlying facts with authoritative external ground-truth evidence.
- **Scientific Significance:** High. Enables paired statistical analysis (McNemar's test, GLMM) to isolate representation-induced factuality degradation from entity difficulty confounds.
- **Verdict:** **Validated Primary Novelty Claim.**

### Contribution 2: Continuous Code-Switch Intensity (CMI) and Orthographic Disentanglement
- **Prior Work:** Code-switching in NLP has traditionally been studied through binary labels or categorical classifications. Gambäck & Das (2014) introduced CMI, but no prior work correlates continuous CMI directly with LLM hallucination probability under semantic control.
- **Substantial Difference:** We calculate token-level CMI and script transition frequencies across 5 languages, testing the hypothesis that factuality scales inversely with CMI and subword fragmentation.
- **Scientific Significance:** High. Disentangles script effects (Latin vs. Native script) from lexical mixing effects (Indic vocabulary vs. English vocabulary).
- **Verdict:** **Validated Primary Novelty Claim.**

### Contribution 3: Out-of-Distribution Hallucination Detection Benchmark
- **Prior Work:** Standard hallucination detectors are evaluated on random train/test splits, which inflate performance due to entity and template memorization.
- **Substantial Difference:** We benchmark across 6 disjoint axes: Question-disjoint, Domain-disjoint, Language-disjoint (LOLO), Model-disjoint (LOMO), and Hard-split, explicitly including an artifact-only baseline to prevent spurious feature learning.
- **Scientific Significance:** High. Addresses a critical open vulnerability in hallucination detection literature.
- **Verdict:** **Validated Novelty Claim.**

### Contribution 4: Factuality-Preserving Mitigation under Code-Switch Constraints
- **Prior Work:** Standard distillation and preference optimization frequently induce "style collapse" or "language collapse" (e.g., models responding purely in English or refusing ambiguous queries to minimize hallucination penalty).
- **Substantial Difference:** We formalize a multi-objective optimization criterion requiring high factual accuracy, retention of code-switch fidelity ($|\Delta \text{CMI}| < 10\%$), low refusal rate, and blinded human bilingual naturalness verification.
- **Scientific Significance:** High. Addresses the real-world deployment trade-off of multilingual LLMs.
- **Verdict:** **Validated Novelty Claim.**

---

## 3. Discarded or Weak Claims (Removed from Paper Scope)

The following claims were considered and **explicitly rejected** as weak, unsupported, or deceptive:
1. *CLAIM: "First benchmark for Indian language hallucination"* $\to$ **REJECTED.** BHRAM-IL precedes us for monolingual Indic hallucination. We claim novelty specifically on *code-switching, script variation, and semantic pairing*.
2. *CLAIM: "IndraLLM eliminates hallucinations in Indian languages"* $\to$ **REJECTED.** Scientifically inaccurate and sensationalist. We report *relative error reduction under controlled distillation*.
3. *CLAIM: "Code-switching causes hallucination"* $\to$ **REJECTED.** Unless unmeasured confounders can be completely ruled out, we employ rigorous non-causal language (*"is associated with a statistically significant reduction in factual accuracy under matched conditions"*).
4. *CLAIM: "Surface features alone detect hallucinations"* $\to$ **REJECTED.** As established in Phase 0 audit, boundary entropy and surface heuristics fail (AUC $\le 0.52$). We do not resurrect failed claims.
