# IndraLLM — Phase 4: Workstream 10
# External Validity and Epistemic Scope Specification

**Document Version:** 1.0 (Phase 4 Scientific Hardening)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  

---

## 1. Executive Summary

To prevent hostile reviewer rejections based on overclaiming, this audit establishes a formal **Epistemic Scope Specification**. We catalog permissible vs. impermissible scientific assertions, establishing strict boundaries for the manuscript.

---

## 2. Permissible vs. Impermissible Scientific Claims

### Table 1: Epistemic Boundary Matrix

| Scientific Domain | ❌ Impermissible Overclaim (Forbidden) | ✅ Defensible Scientific Claim (Permissible) |
|---|---|---|
| **Model Scope** | *"LLMs universally suffer factual collapse under code-switching."* | *"Across evaluated open-weight multilingual LLMs (27B dense and 7B architectures), linguistic representation significantly modulates factual retrieval accuracy."* |
| **Linguistic Scope** | *"Indian languages cause LLMs to hallucinate."* | *"On authentic Indian statutory questions, non-canonical representations (code-switching, romanization, dual-script alternation) incur a 21 to 40 percentage-point accuracy penalty relative to semantically equivalent English."* |
| **Domain Scope** | *"Code-switching causes hallucination across all NLP tasks."* | *"In high-precision statutory and policy question answering—where exact numerical thresholds, dates, and legal entities are required—code-switched queries degrade parametric factual precision."* |
| **Mechanism Scope** | *"Subword tokenization fragmentation causally causes all representation failure."* | *"Dual-script alternation induces severe subword fragmentation and script transition boundaries, disrupting self-attention and reasoning continuity, though linear sequence-wide token fertility does not account for the entire gap."* |
| **Evaluator Scope** | *"Automated LLM judges are completely objective and unskewed."* | *"While automated evaluators exhibit measurable condition-dependent sensitivity differences, the representation gap persists ($\Delta \ge 16.8\%$) across all plausible human-calibrated sensitivity and specificity parameters."* |

---

## 3. Threat Model and Boundary Conditions

### A. Boundary 1: Parametric vs. In-Context Retrieval
- **Condition:** IndraLLM evaluates closed-book parametric recall.
- **Boundary:** Findings do *not* automatically extrapolate to Retrieval-Augmented Generation (RAG) settings where verbatim statutory snippets are prepended in-context. Future work must investigate whether gold context buffers mitigate this representation penalty.

### B. Boundary 2: High-Stakes Legal Domain vs. Casual Conversational NLP
- **Condition:** Indian statutory questions demand strict, exact-match numeric and legal criteria (e.g., Section numbers, cut-off dates, penalty limits).
- **Boundary:** Casual dialogue, sentiment analysis, or narrative generation in code-switched Hinglish may tolerate semantic drift without operational failure. The observed penalty is specific to **fact-critical, constraint-sensitive information retrieval**.

### C. Boundary 3: Evaluated Language Set
- **Condition:** 5 major scheduled Indian languages (Hindi, Bengali, Tamil, Telugu, Kannada) spanning Indo-Aryan and Dravidian families.
- **Boundary:** While results demonstrate cross-family consistency across these 5 languages, we make no claims regarding unrepresented language families (e.g., Austroasiatic, Sino-Tibetan) or languages without standardized written corpora.

---

## 4. Manuscript Guidance for Authors

All manuscript sections (Abstract, Introduction, Discussion, Conclusion) must strictly conform to these epistemic boundaries. Framing the contribution as a precise, controlled discovery on high-stakes statutory retrieval makes the work scientifically invulnerable to hostile review.
