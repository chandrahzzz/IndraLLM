# IndraLLM — Adversarial Synthetic Data Dependency & Circularity Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 24 Synthetic Data Bias, Provenance & Circularity Analysis  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

A frequent critique at ACL/EMNLP is the **"LLM Mirror Chamber" (Circularity)**: an LLM generates a synthetic benchmark, LLMs answer the benchmark, and another LLM evaluates the outputs. Without authoritative external grounding, the entire experiment risks becoming a self-referential measurement of model alignment rather than real-world linguistic factuality.

**Adversarial Verdict:**
1. **Pipeline Circularity Risk:** Moderate to High if unmitigated.
2. **Authoritative Grounding Anchors Exist:** Facts 1–75 and 281–300 (95 unique factual topics, generating 475 semantic groups / 2,375 prompts) are anchored in **verifiable Indian statutory acts, census data, space missions, and agricultural policies**.
3. **Synthetic Padding Exposure:** Facts 76–280 (205 topics, generating 1,025 semantic groups / 5,125 prompts, ~68.3% of the candidate dataset) were algorithmically generated using synthetic template clauses (`Statutory Clause {idx} of the National {Domain} Framework establishes parameter threshold {idx * 10}`).
4. **Circularity in Automated Judging:** The automated evaluator uses an LLM judge (`llama-3.1-8b` / `gemini-flash`). In Phase 2.5, we discovered this judge exhibits a $+10\%$ false-positive penalty on code-switched answers.

---

## 2. Stage-by-Stage Synthetic Dependency Mapping

| Pipeline Stage | Generation Method | Synthetic vs. Authoritative | Circularity Risk | Mitigation Implemented |
|---|---|---|---|---|
| **1. Factual Knowledge Source** | Curated official Indian gazettes (Facts 1–75, 281–300); Algorithmic loop (Facts 76–280) | **$31.7\%$ Authoritative Ground Truth**, $68.3\%$ Synthetic Pattern | Low for Core; High for Padding | Stratify paper results by authentic core vs synthetic tier. |
| **2. Question Formulation** | Deterministic rule-based template injection (12 Template Families) | **Rule-Based Deterministic** (No LLM hallucinations) | Zero | Templates are fixed programmatic schemas. |
| **3. Condition Translation (B_NATIVE)** | Native carrier translation templates + English proper noun | **Rule-Based Deterministic Grammar** | Zero | Fixed native carriers; no stochastic LLM translation. |
| **4. Romanization (C_ROMAN)** | Deterministic Indic-to-Latin rule mappings | **Algorithmic Transliteration** | Zero | Fully reproducible deterministic script. |
| **5. Code-Switching (D_CS)** | Natural syntactic insertion of English nouns/verbs into matrix frame | **Algorithmic Linguistic Insertion** | Low | Guided by Poplack (1980) equivalence constraints. |
| **6. Mixed Scripting (E_MIXED_SCRIPT)** | Orthographic alternation at word boundaries | **Algorithmic Script Switching** | Zero | Deterministic script alternation. |
| **7. Answering Phase (EXP-002)** | Evaluated Target Models (Llama, Qwen, Sarvam, Airavata, Mistral, Gemma) | **Target Empirical Subject** | N/A | Evaluates 8 diverse model families. |
| **8. Evaluation / Judging Phase** | Automated Tri-Layer Judge (`Llama-3.1-8B` / `Gemini-Flash`) + Exact Match | **LLM Judge + Rule-Based Match** | **HIGH** | Calibrated against human gold standard; Rogan-Gladen adjusted. |

---

## 3. The Three Circularity Hazards & Defensive Proofs

### Hazard 1: "The Model Pre-Trained on the Generator's Prompts"
- **Risk:** If a commercial LLM (e.g. GPT-4) generated the questions, models from the same provider might recognize the generation artifacts.
- **Defensive Proof:** **ZERO LLM BENCHMARK GENERATION.** The entire candidate benchmark `IndraLLM-CS-v1.1-CANDIDATE` was constructed using **deterministic Python procedural generation** (`build_decontaminated_benchmark_v1_1.py`), using explicit grammatical frames. No commercial LLM was used to generate questions or prompts.

### Hazard 2: "The Evaluator is the Same Family as the Answering Model"
- **Risk:** If `Llama-3.1-8B` evaluates `Llama-3.1-8B`, it may systematically rate its own output style higher.
- **Defensive Proof:** 
  1. The automated evaluator combines **deterministic string/number extraction** with model judgment.
  2. For model outputs in EXP-002, the judge will be paired with an independent cross-architecture model (`gemini-flash` or `qwen-2.5-32b`) to prevent intra-family favoritism.
  3. A subset of model responses must be verified by human bilingual raters.

### Hazard 3: "Synthetic Padding Distortion"
- **Risk:** An automated evaluation of synthetic facts (Facts 76–280) tests in-context reading or generic parameter retrieval rather than pre-trained cultural knowledge.
- **Defensive Proof:** 
  In the final analysis, all primary claims regarding real-world multilingual factuality must be validated on the **Authentic Core ($N=475$ semantic groups)**. The synthetic scaling tier ($N=1,025$) must be presented strictly as a diagnostic benchmark for syntactic/orthographic robustness.

---

## 4. Audit Summary & Compliance Status

- **Benchmark Generation Dependency on LLMs:** **0.0%** (100% deterministic programmatic construction).
- **Benchmark Translation Dependency on LLMs:** **0.0%** (Fixed bilingual linguistic carrier frames).
- **Overall Status:** **PASS WITH LIMITATION.**
  The project is completely free of LLM generation circularity, but must transparently disclose the synthetic padding tier and evaluator orthographic bias.
