# IndraLLM — Adversarial Meta-Reviewer Attack & Defense Dossier

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 23 Hostile Reviewer Simulation (16 Orthogonal Dimensions)  
**Reviewer Role:** Skeptical Senior Area Chair / Meta-Reviewer (ACL/EMNLP/TACL)  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Meta-Reviewer Assessment

This dossier compiles the strongest, most cynical attacks an expert NLP reviewer could raise against the IndraLLM research project. For each attack, we assess its severity, document the exact repository evidence, and prescribe the required fix or paper defense.

---

## 2. The 16-Dimensional Adversarial Reviewer Attack Matrix

### A. Dataset Validity
- **Reviewer Attack:** *"Two-thirds of your dataset (facts 76–280) consists of formulaic synthetic entities like `National_Governance_Registry_Unit_76` with non-existent URLs. This is not a real benchmark of Indian legal/policy factuality; it is a synthetic template test."*
- **Severity:** **CRITICAL**
- **Evidence:** [`src/indrallm/collection/build_decontaminated_benchmark_v1_1.py:270-290`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/src/indrallm/collection/build_decontaminated_benchmark_v1_1.py#L270-L290).
- **Required Fix:** **Must address in paper.** Transparently partition empirical reporting: present primary factuality results on the Authentic Core ($N=475$ groups), and use the synthetic tier ($N=1,025$) strictly as a structural/syntactic diagnostic benchmark.

### B. Contamination
- **Reviewer Attack:** *"Your original v1.0 benchmark had 100% template overlap between train and test. How do I know v1.1 is truly decontaminated?"*
- **Severity:** **MAJOR**
- **Evidence:** [`research/CONTAMINATED_DATASET_ARCHIVE.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/CONTAMINATED_DATASET_ARCHIVE.md), [`research/NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NEAR_DUPLICATE_ADVERSARIAL_AUDIT.md).
- **Required Fix:** **Can address in paper.** Show the 13-layer audit matrix proving 0.0% exact string, normalized string, entity, and evidence snippet overlap. Report the legacy v1.0 failure openly as a methodological lesson in benchmark decontamination.

### C. OOD Validity
- **Reviewer Attack:** *"You claim 'Out-of-Distribution Generalization', but your Test-OOD split contains ONLY two domains (Governance and Agriculture) and only two question families. This is held-out task evaluation, not general OOD."*
- **Severity:** **CRITICAL**
- **Evidence:** [`research/OOD_DESIGN_ADVERSARIAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/OOD_DESIGN_ADVERSARIAL_AUDIT.md).
- **Required Fix:** **Must address in paper.** Completely remove the term "broad OOD generalization" from the paper. Reframe strictly as "Generalization to Held-Out Structural Schemas (Comparative and Conditional Tasks)."

### D. CMI Validity
- **Reviewer Attack:** *"Why does your monolingual native script condition (`B_NATIVE`) have a CMI of 16.75%, which is higher than Romanized Indic (`C_ROMAN` at 14.55%)? Your CMI metric is either broken or your conditions are mislabeled."*
- **Severity:** **MAJOR**
- **Evidence:** [`research/PHASE2_7_CMI_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_CMI_AUDIT.md).
- **Required Fix:** **Can address in paper.** Demonstrate that CMI calculation strictly follows Gambäck & Das (2014) and explain that prepending English statutory acronyms (PM-KISAN, SEBI) into Indic scripts creates noun-phrase borrowing. Show that Script Transition Count ($1.73$ vs $5.73$) and Language Switches ($1.0$ vs $5.0$) cleanly separate the conditions.

### E. Semantic Equivalence
- **Reviewer Attack:** *"You rely on an embedding cosine similarity threshold ($\ge 0.82$) to claim semantic equivalence, but sentence embeddings are notoriously insensitive to negation and numbers. A 10x numerical change still gets 0.85 similarity!"*
- **Severity:** **MAJOR**
- **Evidence:** [`research/SEMANTIC_EQUIVALENCE_ADVERSARIAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/SEMANTIC_EQUIVALENCE_ADVERSARIAL_AUDIT.md).
- **Required Fix:** **Must fix in protocol.** Implement explicit rule-based checks for numerical constants, dates, and negation tokens across condition prompts in addition to embedding similarity.

### F. Human Validation
- **Reviewer Attack:** *"You reported Fleiss' $\kappa = 0.719$ and naturalness $4.74/5$ for your candidate benchmark, but not a single human annotator reviewed the 1,500 groups in v1.1-CANDIDATE. You carried over numbers from an older pilot."*
- **Severity:** **CRITICAL**
- **Evidence:** [`research/PHASE2_7_HUMAN_VALIDATION_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_HUMAN_VALIDATION_AUDIT.md).
- **Required Fix:** **Must fix before EXP-002 reporting.** Reclassify Gates G8 and G9 as UNVERIFIED for v1.1-CANDIDATE. In the paper, clearly differentiate between the pilot human agreement study ($N=150$) and the programmatic candidate benchmark ($N=1500$).

### G. Statistical Power
- **Reviewer Attack:** *"Test-OOD has only 100 semantic groups. With a realistic discordant rate, you have only 20% power to detect a 5% effect and 60% power for a 10% effect. You cannot make confirmatory claims on Test-OOD."*
- **Severity:** **MAJOR**
- **Evidence:** [`research/PHASE2_7_POWER_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_POWER_AUDIT.md).
- **Required Fix:** **Can address in paper.** Acknowledge Test-OOD as exploratory; report exact 95% confidence intervals ($\pm 8.8\%$) and avoid claiming null results on subtle shifts.

### H. Statistical Independence & Pseudoreplication
- **Reviewer Attack:** *"Did you pool the 5 condition prompts per group into an unclustered test of 1,000 independent samples? That is blatant pseudoreplication."*
- **Severity:** **CRITICAL**
- **Evidence:** [`research/PHASE2_7_STATISTICAL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_STATISTICAL_AUDIT.md).
- **Required Fix:** **Already fixed in code.** `src/indrallm/evaluation/statistical_testing.py` now enforces paired McNemar testing and repeated-measures logistic regression with cluster-robust standard errors grouped by `semantic_id`.

### I. Evaluator Bias
- **Reviewer Attack:** *"Your automated judge model penalizes code-switched answers by +10% FPR simply because of script transitions. Your reported factuality drop on Hinglish is just judge bias."*
- **Severity:** **MAJOR**
- **Evidence:** [`research/EVALUATOR_HUMAN_VALIDATION.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/EVALUATOR_HUMAN_VALIDATION.md).
- **Required Fix:** **Must address in paper.** Apply Rogan-Gladen prevalence adjustment to all model factuality scores. Any observed effect smaller than the 10% judge bias margin must be flagged as unconfirmed.

### J. Model Selection
- **Reviewer Attack:** *"Did you hand-pick models that show big drops in Indian languages while omitting models that handle code-switching well?"*
- **Severity:** **MINOR**
- **Evidence:** [`research/EXPERIMENT_MATRIX.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/EXPERIMENT_MATRIX.md).
- **Required Fix:** **Can address in paper.** The preregistered model panel includes 8 diverse open models across 5 architectural families (Llama-3.1, Llama-3.3, Qwen-2.5-32B, Qwen-2.5-7B, Sarvam-2B, Airavata, Mistral-24B, Gemma-2-9B), spanning parameters from 2B to 70B.

### K. Prompt Confounding
- **Reviewer Attack:** *"In Test-OOD, your English prompt explicitly instructs the model to compare entities, while your Indic prompts just ask for general rules. You gave English a prompt engineering advantage."*
- **Severity:** **MAJOR**
- **Evidence:** [`research/PHASE2_7_PROMPT_CONTROL_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_PROMPT_CONTROL_AUDIT.md).
- **Required Fix:** **Can address in paper.** Disclose this prompt phrasing asymmetry in the limitations section and conduct an ablation showing the effect of aligned comparative phrasing.

### L. Reproducibility
- **Reviewer Attack:** *"Can an external researcher reproduce this entire benchmark and analysis from a clean clone without paid API keys?"*
- **Severity:** **MINOR**
- **Evidence:** [`research/PHASE2_7_REPRODUCIBILITY_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_REPRODUCIBILITY_AUDIT.md).
- **Required Fix:** **Can address in paper.** The benchmark generation script (`build_decontaminated_benchmark_v1_1.py`) runs 100% locally and deterministically, and SHA-256 manifests verify exact file integrity.

### M. Synthetic-Data Bias
- **Reviewer Attack:** *"Your benchmark was generated by an LLM, answered by an LLM, and evaluated by an LLM. It is an ungrounded circular sandbox."*
- **Severity:** **MAJOR**
- **Evidence:** [`research/SYNTHETIC_DATA_BIAS_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/SYNTHETIC_DATA_BIAS_AUDIT.md).
- **Required Fix:** **Can address in paper.** Refute the claim: show that the benchmark generation was 100% programmatic (rule-based Python), NOT generated by an LLM. Disclose that facts 1–75 and 281–300 are anchored in verifiable Indian legal/scientific sources.

### N. Generalization
- **Reviewer Attack:** *"Can findings on 5 Indian languages be generalized to all multilingual LLMs or code-switching in general?"*
- **Severity:** **MINOR**
- **Evidence:** [`research/HYPOTHESES.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/HYPOTHESES.md).
- **Required Fix:** **Can address in paper.** Scope claims explicitly to the Indo-Aryan and Dravidian language families and avoid claiming universal typological generalization.

### O. Novelty
- **Reviewer Attack:** *"People have evaluated multilingual LLMs before. What is actually new here?"*
- **Severity:** **MINOR**
- **Evidence:** [`research/NOVELTY_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/NOVELTY_AUDIT.md), [`research/RELATED_WORK_MATRIX.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/RELATED_WORK_MATRIX.md).
- **Required Fix:** **Can address in paper.** Emphasize the unique 5-condition semantic-paired design that orthogonalizes script alternation from lexical code-mixing with exact evidence provenance.

### P. Scope of Claims
- **Reviewer Attack:** *"You make causal assertions about tokenizer fertility causing hallucinations, but your study is observational."*
- **Severity:** **MAJOR**
- **Evidence:** [`research/PHASE2_7_CLAIM_AUDIT.md`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_7_CLAIM_AUDIT.md).
- **Required Fix:** **Must fix in paper text.** Change all causal claims to correlational statements (e.g. *"Spearman correlation between tokenizer fertility and hallucination frequency"*).

---

## 3. Pre-EXP-002 Checklist of Defenses

Every critical and major reviewer attack has now been assigned an explicit defense:
1. Disclose authentic core ($N=475$) vs synthetic scaling tier ($N=1,025$).
2. Reclassify candidate human agreement as UNVERIFIED.
3. Replace "broad OOD" with "held-out structural schema generalization."
4. Report Rogan-Gladen adjusted scores for evaluator bias.
5. Report cluster-robust standard errors and paired McNemar statistics strictly at the `semantic_id` level.
