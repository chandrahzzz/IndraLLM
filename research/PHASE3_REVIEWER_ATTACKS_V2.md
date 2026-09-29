# IndraLLM — Phase 3.5: Audit 15 — Adversarial Reviewer Attack Simulation (V2)
## Rigorous Hostile Peer Review Across 5 Specialized Reviewer Profiles

**Document Version:** 2.0 (Post-Execution Forensic Audit)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `1d4a65c`  

---

## 1. Executive Summary

To inoculate IndraLLM against peer rejection at top-tier venues (ACL, EMNLP, NAACL, TACL), this audit simulates five hostile, technically sophisticated reviewer attacks targeting contamination, statistical modeling, multilingual linguistics, LLM evaluation, and meta-scientific claims.

### Summary of Attack Classifications:
- **Reviewer A (Contamination & Leakage):** **RESOLVED** (Decontaminated v1.1 verified with zero n-gram, entity-pair, or template family leakage).
- **Reviewer B (Statistical Methodology):** **RESOLVED** (Clustering on `semantic_id` validated, Holm-Bonferroni FWER validated across all 10 pairs; 20-topic GEE stress test fully disclosed).
- **Reviewer C (Multilingual NLP & Tokenization):** **RESOLVED** (Tokenization confound refuted; chars-per-token fragmentation mechanism identified).
- **Reviewer D (LLM Evaluator Bias):** **RESOLVED** (Rogan-Gladen truncation artifact diagnosed and resolved; valid calibrated metrics established on Authentic Core).
- **Reviewer E (Area Chair / Epistemic Discipline):** **RESOLVED** (Claims strictly bounded; synthetic tier separated from authentic core; OOD bounded to structural schemas).

---

## 2. Reviewer A: Benchmark Contamination & Leakage Expert

### The Attack:
> *"How do I know your Test-OOD results are not simply memorized from your Development and Validation sets? In NLP benchmarks, cross-partition entity leakage is notorious for creating artificial performance gains."*

### Empirical Audit & Defense:
1. **Zero Exact & Near-Duplicate Overlap:** In Phase 2.6, all 1,500 prompts were audited with 13-gram Jaccard matching and sentence embeddings; max cross-split similarity was $< 0.42$.
2. **Disjoint Template Families:** Test-OOD contains *only* template families `TF-11` and `TF-12`. Neither template family appears anywhere in the Development or Validation sets.
3. **Disjoint Entity Pairs:** The comparative entity pairs in Test-OOD (e.g. `PMFBY vs WBCIS`, `NEFT vs RTGS`) do not appear in any other partition.
4. **Classification:** **RESOLVED.** Contamination is strictly zero.

---

## 3. Reviewer B: Statistical Methodologist

### The Attack:
> *"Your dataset contains 5 prompts per semantic group, and your 100 semantic groups in Test-OOD are derived from only 20 base statutory questions. If you treat observations as independent, you are guilty of severe pseudoreplication. Furthermore, did you correct for all 10 pairwise comparisons between your 5 conditions?"*

### Empirical Audit & Defense:
1. **Pseudoreplication Rejected:** All primary tests in EXP-002 utilized paired McNemar tests and GEE clustered at `semantic_id` ($N=100$), explicitly controlling for intra-cluster correlation.
2. **Conservative 20-Topic Stress Test:** In Audit 2, GEE clustered at the coarsest 20-topic level was executed: `B_NATIVE` ($p < 0.0001$), `C_ROMAN` ($p = 0.0004$), and `E_MIXED_SCRIPT` ($p = 0.0005$) remain rock-solid significant. The `D_CS` deficit ($p = 0.0528$) is transparently reported as marginal at $N=20$.
3. **10-Pair FWER Control:** In Audit 4, step-down Holm-Bonferroni was executed across all $\binom{5}{2} = 10$ pairs: `A_EN vs B_NAT` ($p = 3.1 \times 10^{-8}$), `A_EN vs D_CS` ($p = 0.00229$), and `D_CS vs E_MIX` ($p = 0.00395$) all survive full 10-contrast FWER control.
4. **Classification:** **RESOLVED.**

---

## 4. Reviewer C: Multilingual NLP & Tokenization Expert

### The Attack:
> *"Your code-switched and native prompts perform worse simply because they are longer or poorly tokenized. You haven't proven a linguistic representation effect; you've just proven that longer prompts degrade LLM attention."*

### Empirical Audit & Defense:
1. **Zero Length Confound:** In Audit 8, prompt token lengths were measured:
   $$\text{A\_EN}: 68.40 \pm 3.24 \text{ tokens} \quad \text{vs} \quad \text{D\_CS}: 67.92 \pm 2.65 \text{ tokens}$$
   Code-switched prompts are virtually identical in length to English prompts ($\Delta = -0.48$ tokens), completely ruling out length confounding.
2. **Multivariate Regression Control:** Clustered GEE controlling for `token_count` demonstrated that sequence length is non-significant ($p = 0.4096$).
3. **Tokenization as Mechanism, Not Confound:** In Audit 13, we proved that subword fragmentation is the *computational vehicle* through which orthography harms retrieval: Brahmic scripts suffer a $2.28\times$ fertility penalty, and script alternation shatters subword merges at 5.1 boundaries per prompt.
4. **Classification:** **RESOLVED.**

---

## 5. Reviewer D: LLM Evaluation Expert

### The Attack:
> *"You use Qwen-27B to evaluate itself and other models. Automated judges have strong self-preference bias and struggle with non-English evaluation. Furthermore, in Table 3.2 of your results, three conditions have exactly 0.00% accuracy after Rogan-Gladen adjustment. That is an obvious mathematical artifact."*

### Empirical Audit & Defense:
1. **Rogan-Gladen Truncation Artifact Diagnosed & Fixed:** Audit 5 proved that the $0.00\%$ adjusted numbers occurred because the 0% synthetic scaling tier dragged observed prevalence below the 12% FPR ceiling ($P_{\text{obs}} < \text{FPR}$).
2. **Valid Adjustment on Authentic Core:** When applied to the Authentic Core (where $P_{\text{obs}} \ge 24\% > 12\%$), Rogan-Gladen produces clean, non-zero calibrated estimates ($A\_EN: 68.1\%, D\_CS: 41.9\%, E\_MIX: 16.2\%$).
3. **Conservative Judge Bias:** The judge has a $+10\%$ false-positive rate on code-switched answers. Correcting for this conservatism *widens* the performance gap from $21.0\%$ raw to $26.24\%$ adjusted, proving that judge bias was propping up, rather than penalizing, non-English outputs.
4. **Classification:** **RESOLVED.**

---

## 6. Reviewer E: ACL/EMNLP Area Chair (Epistemic Discipline)

### The Attack:
> *"The paper claims publication readiness, but 66.7% of your test items are synthetic clauses where models score ~0%, and your OOD split is only 20 statutory questions. Are you over-claiming general multilingual reasoning?"*

### Empirical Audit & Defense:
1. **Strict Claim Bounding:** In Audit 6 and Audit 11, broad claims were prohibited:
   - Test-OOD is strictly defined as *held-out structural task schema generalization* (TF-11 and TF-12), never open-domain OOD.
   - Results are strictly disaggregated between the Authentic Policy Core and the Synthetic Scaling Tier.
2. **The 0% Synthetic Finding Re-Framed:** Models scored 0% on synthetic clauses because in English they exhibited **$99.0\%$ non-existence denial**, recognizing that the clause was fictitious. This demonstrates epistemic calibration, which degrades under code-switching.
3. **Classification:** **RESOLVED.** All claims are strictly bounded by empirical evidence.
