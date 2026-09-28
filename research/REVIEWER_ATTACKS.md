# IndraLLM — Reviewer Attack Simulation & Methodological Defense

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Reviewer Personas:** Area Chair (ACL/EMNLP), Reviewer 1 (Novelty), Reviewer 2 (Methodology/Statistics), Reviewer 3 (Multilingual NLP), Reviewer 4 (Reproducibility)  

---

## Reviewer 1 (Novelty & Contribution Focus)
> **Critique:** *"How is this different from existing Indian language benchmarks like BHRAM-IL or multilingual factuality datasets? Isn't this just another benchmark?"*
- **Defense Evidence:** BHRAM-IL is strictly monolingual in native scripts. Over 70% of real-world Indian digital text is Romanized and code-switched. IndraLLM is the first benchmark to use **5-condition semantic pairing** ($S_{EN} \leftrightarrow S_{Native} \leftrightarrow S_{Roman} \leftrightarrow S_{CS} \leftrightarrow S_{Mixed}$) to causally isolate whether code-switching and Romanization introduce independent factual reliability degradation when semantic content is held constant.
- **Action Required:** Highlight Section 2 of `research/RELATED_WORK_MATRIX.md` prominently in the paper introduction.

---

## Reviewer 2 (Methodological & Statistical Rigor)
> **Critique:** *"LLM-as-a-judge is known to have position and length biases. How can we trust the reported hallucination rates without human calibration? And why should we believe a 100-item test sample?"*
- **Defense Evidence:** We reject single-model LLM judging as sole ground truth. IndraLLM introduces a **tri-layer evaluation framework** with 1,500 human bilingual expert annotations, reporting multi-rater Fleiss' $\kappa \ge 0.70$ and Krippendorff's $\alpha \ge 0.70$. All empirical claims feature 95% bootstrap confidence intervals, paired McNemar's tests, and Holm-Bonferroni corrections.
- **Action Required:** Ensure every table and figure includes explicit 95% CIs and adjusted p-values.

---

## Reviewer 3 (Multilingual & Code-Switching Linguistics)
> **Critique:** *"Code-switching cannot be treated as a binary variable. Synthetic code-switching is often ungrammatical. Did you measure mixing intensity or validate naturalness?"*
- **Defense Evidence:** We reject binary code-switching. We compute continuous token-level Code-Mixing Index (Gambäck & Das, 2014) and script transition frequencies. Every prompt is reviewed for naturalness and language mixture fidelity by bilingual native speakers (Likert $\ge 4.0$).
- **Action Required:** Present Figure 2 (Factuality vs. Continuous CMI curve) and Figure 4 (Script comparison) in the main paper.

---

## Reviewer 4 (Reproducibility & Artifacts)
> **Critique:** *"Can external researchers independently reproduce these results without spending thousands of dollars on proprietary APIs?"*
- **Defense Evidence:** The repository includes a deterministic reproducibility package (`reproduce/`), frozen seed manifests, config-driven CLI execution (`python -m indrallm.evaluate --config ...`), zero-leakage automated unit tests, and open-source models (Sarvam-2B, IndicBERT, XLM-R).
- **Action Required:** Maintain 100% unit test coverage on data splits and statistical routines.
