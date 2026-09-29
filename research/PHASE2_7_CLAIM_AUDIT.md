# IndraLLM — Adversarial Research Claim & Hypothesis Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 22 Scientific Claim Categorization & Scope Audit  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

Scientific rigor requires matching the strength of empirical claims strictly to the strength of demonstrated evidence. Papers that claim "causal mechanisms," "general out-of-distribution robustness," or "universal hallucination reduction" based on correlational observations or narrow synthetic splits are routinely rejected at ACL/EMNLP/TACL.

**Adversarial Verdict:** 
Out of 12 planned scientific claims in the IndraLLM research portfolio:
- **1 claim is SUPPORTED** (Benchmark architectural decoupling and contamination resolution).
- **5 claims REQUIRE EXP-002** (Empirical factuality gaps, model ranking, tokenizer fragmentation).
- **3 claims are PLAUSIBLE BUT UNTESTED** (Mitigation distillation efficacy, evaluator calibration).
- **3 claims are OVERCLAIMED / UNSUPPORTED** (Broad OOD generalization, pure causal script attribution, and synthetic grounding claims).

---

## 2. Systematic Paper Claim Classification

| Claim ID | Planned Research Paper Assertion | Audit Classification | Evidence / Rationale | Mandatory Paper Rephrasing |
|---|---|---|---|---|
| **CLM-01** | *"Code-switching degrades model factuality relative to monolingual English (H1)."* | **REQUIRES EXP-002** | Demonstrated in Phase 2 pilot ($N=500$), but confirmatory test requires multi-model evaluation on held-out Test-ID ($N=200$). | State as a confirmed empirical finding only after EXP-002; until then, refer to as "pilot-supported hypothesis." |
| **CLM-02** | *"Hallucination increases monotonically with Gambäck & Das (2014) CMI (H2)."* | **REQUIRES EXP-002** | Continuous CMI correlation requires full EXP-003 regression analysis across diverse models. | Avoid claiming universal monotonicity until full continuous curve is plotted. |
| **CLM-03** | *"Devanagari and Dravidian scripts suffer higher hallucination rates than Latin-script English due to tokenizer fragmentation (H3 & H5)."* | **REQUIRES EXP-002** | Pilot indicates elevated fertility ($2.8\times$), but causal link between fragmentation and factuality requires EXP-004 ablation. | Frame as a strong correlational hypothesis to be tested in EXP-002/004. |
| **CLM-04** | *"IndraLLM benchmarks out-of-distribution generalization across unseen reasoning domains."* | **OVERCLAIMED** | Test-OOD tests only 2 task families (`TF-11` & `TF-12`) and only 2 domains (Gov, Ag). Science, History, Health are absent. | **Must downgrade:** *"Evaluates generalization to held-out comparative and conditional structural task families."* |
| **CLM-05** | *"All 1,500 semantic units are grounded in verified, authentic Indian statutory gazettes."* | **UNSUPPORTED / OVERCLAIMED** | Facts 76–280 (1,025 groups, 68.3% of the candidate dataset) are synthetic formulas (`National_X_Registry_Unit_idx`). | **Must disclose:** *"Consists of a 475-item authentic gazette core and a 1,025-item formulaically expanded scaling tier."* |
| **CLM-06** | *"The 5 conditions strictly isolate script from language mixing."* | **SUPPORTED** | CMI, script transition counts, and language switch counts empirically demonstrate orthogonal separation between D_CS and E_MIXED_SCRIPT. | Supported by mathematical proof and empirical metric distributions. |
| **CLM-07** | *"Evidence-filtered teacher distillation eliminates hallucinations in Indic LLMs (H8)."* | **PLAUSIBLE BUT UNTESTED** | Not yet executed. Depends entirely on future mitigation experiments EXP-009/010. | Must remain framed as a planned mitigation protocol. |
| **CLM-08** | *"IndraLLM-CS-v1.1 candidate benchmark is human-validated with Fleiss' $\kappa = 0.719$."* | **OVERCLAIMED / FALSE ATTRIBUTION** | $\kappa = 0.719$ was measured on the Phase 2 pilot sample ($N=150$), NOT on the newly generated 1,500 candidate groups. | **Must correct:** Reclassify G8 as UNVERIFIED on v1.1-CANDIDATE until fresh human ratings are conducted. |
| **CLM-09** | *"The automated evaluator provides unbiased factuality judgments across all Indian languages."* | **UNSUPPORTED** | Evaluator exhibits a measured $+10\%$ false-positive elevation in code-switched conditions (`EVALUATOR_HUMAN_VALIDATION.md`). | Must disclose evaluator bias and report Rogan-Gladen adjusted scores alongside raw outputs. |
| **CLM-10** | *"Contamination from question template reuse has been completely eliminated."* | **SUPPORTED** | 13-layer audit verified 0.0% prompt, entity, and evidence leakage across partition boundaries. | Supported with documented caveat on governmental portal URL reuse. |
| **CLM-11** | *"Causal attribution of hallucination to token fertility."* | **OVERCLAIMED** | Observational regression cannot prove causality without synthetic vocab/tokenizer intervention. | Reframe from "causes" to "is strongly correlated with (Spearman $\rho$)." |
| **CLM-12** | *"Test-OOD demonstrates robust statistical power."* | **UNSUPPORTED** | Power recalculation proves Test-OOD ($N=100$) has only $20.1\%$ power for a $5\%$ effect and $60.9\%$ for $10\%$. | Acknowledge Test-OOD as exploratory and report wide confidence intervals ($\pm 8.8\%$). |

---

## 3. Mandatory Paper Claims Boundary Definition

To ensure acceptance at a top-tier venue, the paper must adhere to the following **Claims Boundary Rules**:
1. **No Causal Overreach:** Use *"is associated with,"* *"exhibits degradation under,"* or *"is correlated with,"* rather than *"causes."*
2. **Transparent Generalization Boundaries:** Do not refer to `Test-OOD` as general domain OOD; define it precisely as *"held-out structural schema generalization."*
3. **Dual Metric Reporting:** Report raw model accuracy alongside **evaluator-bias-adjusted accuracy** to insulate against judge model skepticism.
4. **Honest Dataset Composition:** Explicitly distinguish the authentic gazette core from the synthetic scaling tier in the dataset description.
