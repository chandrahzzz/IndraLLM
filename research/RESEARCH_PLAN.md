# IndraLLM — Publication-Grade Research & Transformation Plan

**Target Venues:** ACL / EMNLP / NAACL / TACL / Findings of ACL  
**Core Objective:** Establish the first semantically paired, human-grounded causal benchmark and empirical study investigating how code-switching, script choice, and mixing intensity influence LLM factuality across 5 major Indian languages.

---

## 1. Research Architecture & Phase Breakdown

```
Phase 0: Baseline Audit & Pre-Registration (Completed)
   │
   ▼
Phase 1: Controlled Semantic Benchmark & Data Pipeline
   ├── Step 1.1: Semantically Paired Data Schema (Condition A to E)
   ├── Step 1.2: Human Factual Evidence Ingestion (Authoritative Sources)
   ├── Step 1.3: Continuous CMI & Script Transition Instrumentation
   └── Step 1.4: Pilot Benchmark Generation ($N=500$ semantic groups)
   │
   ▼
Phase 2: Multi-Layer Evaluation & Human Gold Standard
   ├── Step 2.1: Formal Annotation Protocol & Interactive Guidelines
   ├── Step 2.2: Bilingual Human Gold Annotation ($N=1,500$ responses)
   ├── Step 2.3: Inter-Annotator Agreement (Fleiss' $\kappa$, Krippendorff's $\alpha$)
   └── Step 2.4: Dual/Triple LLM Judge Calibration vs. Human Ground Truth
   │
   ▼
Phase 3: Large-Scale Empirical Evaluation & Causal Analysis
   ├── Step 3.1: Model Panel Evaluation (6–8 Diverse LLMs)
   ├── Step 3.2: Paired Statistical Tests (McNemar, Mixed-Effects GLMM, Bootstrap CIs)
   ├── Step 3.3: Tokenizer Fragmentation & Orthographic Disentanglement Analysis
   └── Step 3.4: Automated Publication Table and Figure Generation
   │
   ▼
Phase 4: Hallucination Detection Benchmark under Distribution Shift
   ├── Step 4.1: Baselines (TF-IDF, XLM-R, IndicBERT, Dual-Judge)
   ├── Step 4.2: Feature-Augmented Detector (Code-switch & Tokenization aware)
   ├── Step 4.3: Out-of-Distribution Stress Tests (LOLO, LOMO, LODO, Hard Split)
   └── Step 4.4: Artifact-Only Control Verification
   │
   ▼
Phase 5: Factuality Mitigation & Human Preference Evaluation
   ├── Step 5.1: Controlled Ablation Matrix ($M_0$ Base $\to$ $M_4$ DPO/Fact-SFT)
   ├── Step 5.2: Verification and Quality Filtering of Teacher Supervision
   ├── Step 5.3: Dual Evaluation: Factuality vs. Code-Switch Fidelity & Refusal
   └── Step 5.4: Blinded Human Bilingual Pairwise Preference Evaluation
   │
   ▼
Phase 6: Reproducibility Package, Paper Artifacts & Defense Readiness
   ├── Step 6.1: Full Experiment Registry & Config-driven execution
   ├── Step 6.2: Dataset Card, Model Card, and Ethical Impact Documentation
   ├── Step 6.3: Simulated Reviewer Attacks & Methodological Hardening
   └── Step 6.4: LaTeX Paper Draft & Camera-Ready Package
```

---

## 2. Phase 1 Detailed Specifications: Semantic-Paired Dataset Design

### 2.1 Five Controlled Conditions per Semantic Unit
For every semantic question $S_i$ ($i \in \{1, \dots, N\}$):
1. **Condition A — English Baseline (`EN`):** Standard English factual formulation.
   *Example:* *"What is the capital city of Tamil Nadu?"*
2. **Condition B — Native Script Monolingual (`NATIVE`):** Grammatical monolingual sentence in the native Indic script.
   *Example (Tamil):* *"தமிழ்நாட்டின் தலைநகரம் எது?"*
3. **Condition C — Romanized Monolingual (`ROMAN`):** Phonetic transliteration into Latin script without English lexical substitution.
   *Example (Tamil):* *"Tamilnattin thalainagaram ethu?"*
4. **Condition D — Natural Code-Switching (`CS`):** Bilingual intra-sentential code-switching adhering to natural conversational conventions.
   *Example (Tamil):* *"Tamil Nadu oda capital city enna?"*
5. **Condition E — Mixed-Script Code-Switching (`MIXED_SCRIPT`):** Native Indic script mixed with Latin script within the same utterance.
   *Example (Tamil):* *"Tamil Nadu-வின் capital city என்ன?"*

### 2.2 Target Languages ($K=5$)
- **Dravidian Family:** Tamil (`ta`), Telugu (`te`), Kannada (`kn`).
- **Indo-Aryan Family:** Hindi (`hi`), Bengali (`bn`).
- All 5 languages paired with English (`en`).

### 2.3 Domain Taxonomy ($D=6$)
1. **Governance & Civic Rights:** Schemes, constitutional rights, documentation processes.
2. **Agriculture & Climate:** Crops, irrigation, soil health, regional agricultural programs.
3. **Education & Academia:** Admissions, scholarships, historical institutions, curriculum.
4. **History & Heritage:** Architecture, historical dates, dynasties, cultural events.
5. **Science & Technology:** Space missions, geography, basic physical sciences.
6. **Public Health & Wellness:** Preventative health, vaccination facts (strictly non-prescriptive, disclaimed).

---

## 3. Human Grounding & Reference Verification

- **Ground Truth Evidence Ingestion:** Every semantic question must be paired with:
  - An exact canonical answer.
  - An authoritative reference URL / source citation (e.g., government portals, encyclopedic databases, academic records).
  - An extracted ground truth evidence snippet (1–3 sentences).
- **Quality Gates:** Any question whose ground truth cannot be verified through authoritative external evidence is dropped.

---

## 4. Stopping Rules & Gate Checks

| Gate | Check Criteria | Action if Failed |
|---|---|---|
| **Gate 1: Semantic Equivalence** | Pilot bilingual review of Condition A–E semantic equivalence $\ge 95\%$ | Refine transliteration / translation pipeline before generation |
| **Gate 2: Inter-Annotator Agreement** | Fleiss' $\kappa \ge 0.70$ or Krippendorff's $\alpha \ge 0.70$ on human labels | Revise annotation guidelines, conduct adjudicator calibration |
| **Gate 3: CMI Dispersion** | Measured CMI across Condition D spans $\ge 15\%$ to $\le 60\%$ | Re-calibrate prompt constraints to ensure wide intensity spread |
| **Gate 4: Artifact Independence** | Artifact-only detector must achieve $\text{PR-AUC} \le 0.58$ | If artifact detector achieves high score, re-balance length and language tokens |
| **Gate 5: Mitigation Trade-off** | Mitigation must maintain $\Delta \text{Refusal} < 5\%$ and $\Delta \text{CMI} < 10\%$ | Reject mitigation technique if it lowers hallucination via refusal or language collapse |

---

## 5. Execution Strategy & Incremental Milestones

1. **Milestone 1:** Architecture, pre-registered hypotheses, experiment matrix, and data schema.
2. **Milestone 2:** Semantic-paired data generation tools, CMI engine, and verified evidence schema.
3. **Milestone 3:** Pilot benchmark ($N=500$ semantic groups = 2,500 questions across 5 languages).
4. **Milestone 4:** Multi-model generation and tri-layer evaluation harness with statistical testing.
5. **Milestone 5:** Human annotation protocol and inter-rater agreement computation.
6. **Milestone 6:** Detector benchmark with OOD evaluation and artifact control.
7. **Milestone 7:** Controlled mitigation study and human preference evaluation.
8. **Milestone 8:** Publication-ready tables, figures, documentation, and test suite.
