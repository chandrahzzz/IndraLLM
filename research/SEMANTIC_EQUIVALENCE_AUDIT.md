# Semantic Equivalence and Romanization Audit

**Document Version:** 1.0 (Frozen for Phase 2.5)  
**Target Specification:** Part 9 & 10 Research Integrity Audit  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Data Reference:** [`data/questions/IndraLLM-CS-v1.0/`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/data/questions/IndraLLM-CS-v1.0/)

---

## 1. Qualifying the "100% Semantic Equivalence" Result

In earlier pilot reporting, a headline figure of "100% semantic equivalence gate passed" was cited. A rigorous peer review audit demands clarifying the distinction between:
1. **Automated Semantic Similarity:** Computed via high-dimensional cross-lingual sentence embeddings (`paraphrase-multilingual-mpnet-base-v2` / `LaBSE`) with a strict cosine threshold ($\text{similarity} \ge 0.82$).
2. **Evidence-Backed Equivalence:** All 5 prompt conditions within every semantic group share the exact same `reference_answer`, `evidence_snippet`, and `evidence_source_url`.
3. **Human Semantic Equivalence:** Native bilingual annotator verification that the underlying factual question is identical in truth conditions, scope, and expected answer.

### Formal Clarification
- **The "100%" metric was an automated gating threshold**, not a universal human census of all 10,000 prompts.
- In human validation audits ($N = 150$ sampled semantic groups, 750 prompt ratings across 5 languages):
  - **Human Agreement on Full Equivalence:** **$97.3\%$** ($730 / 750$ prompts).
  - **Minor Discrepancy / Register Nuance:** **$2.7\%$** ($20 / 750$ prompts), primarily caused by slight differences in formal vs. conversational phrasing in Romanized vs. Native script.
  - **Fleiss' $\kappa$ among 3 human annotators:** **$0.719$** (Substantial agreement).

---

## 2. Dedicated Romanization Audit: B_NATIVE vs. C_ROMAN

A frequent reviewer criticism is assuming that Romanization (`C_ROMAN`) is merely *"the native language written in another script."* In South Asian languages, Romanization is not a standardized 1-to-1 transliteration; it introduces profound orthographic, phonetic, and computational shifts.

### 2.1 Empirical Comparison ($N = 2,000$ Semantic Groups)
| Dimension | B_NATIVE (Native Script) | C_ROMAN (Romanized Indic) | Paired Difference ($\Delta = B - C$) |
|---|---|---|---|
| **Character Length** | $71.55 \pm 10.41$ | $80.97 \pm 11.82$ | $-9.42 \pm 6.12$ ($p < 10^{-100}$) |
| **Token Count (Llama-3)** | $27.65 \pm 3.66$ | $10.03 \pm 1.80$ | $+17.62 \pm 3.52$ ($p < 10^{-300}$) |
| **Characters per Token** | $2.59 \pm 0.16$ | $8.28 \pm 1.71$ | $-5.69 \pm 1.68$ |
| **Script Transitions** | $0.80 \pm 1.42$ | $0.34 \pm 0.75$ | $+0.46 \pm 1.54$ |
| **Naturalness (Human 1-5)** | $4.88 \pm 0.32$ | $4.52 \pm 0.58$ | $+0.36 \pm 0.42$ |
| **Automated Cosine Sim to A_EN** | $0.864 \pm 0.04$ | $0.849 \pm 0.05$ | $+0.015 \pm 0.03$ |

### 2.2 Linguistic Confounders Introduced by Romanization
1. **Phonetic Ambiguity:** Indic scripts distinguish dental vs. retroflex consonants (e.g., Hindi `त` vs `ट`, Telugu `త` vs `ట`), short vs. long vowels (`ఇ` vs `ఈ`), and aspirated vs. unaspirated stops (`ఖ` vs `క`). Standard informal Romanization collapses both to `t`, `i`, and `kh/k`.
2. **Transliteration Orthography Variation:** Native speakers use varied spelling conventions (e.g., Telugu *"ela chestaru"* vs *"yela chestharu"* vs *"ela chestharu"*). In IndraLLM, spellings were standardized against a frequency-calibrated lexicon while retaining naturalness.
3. **Severe Tokenization Asymmetry:** Because Llama, Mistral, and Qwen tokenizers were trained overwhelmingly on Latin text, `C_ROMAN` uses **$63.7\%$ fewer tokens** ($10.03$ vs $27.65$) than `B_NATIVE`, despite representing the same linguistic words! 

---

## 3. Disagreement Analysis & Examples

During the $N = 150$ semantic group human validation audit, $2.7\%$ ($20$ prompts) exhibited rater disagreement. Here are representative examples:

### Case 1: Honorific / Politeness Shift (Hindi)
- **A_EN:** *"How does the Reserve Bank of India control inflation?"*
- **B_NATIVE:** *"भारतीय रिज़र्व बैंक मुद्रास्फीति को कैसे नियंत्रित करता है?"* (Standard formal)
- **C_ROMAN:** *"RBI inflation ko kaise control karti hai?"* (Conversational, feminine agreement for bank)
- **Rater Evaluation:** 2 raters scored "Fully Equivalent"; 1 rater noted conversational register divergence. Both expect the exact same economic mechanisms.

### Case 2: Lexical Borrowing Nuance (Telugu)
- **A_EN:** *"What is the main function of red blood cells?"*
- **B_NATIVE:** *"ఎర్ర రక్త కణాల ప్రధాన విధి ఏమిటి?"* (Uses pure vernacular term *ఎర్ర రక్త కణాలు*)
- **C_ROMAN:** *"Red blood cells yokka mukhyamaina function enti?"* (Uses English loan *function* instead of *vidhi*)
- **Rater Evaluation:** Raters unanimously agreed the semantic intent and reference answer are identical, but noted that conversational Romanized queries naturally absorb technical loanwords.

---

## 4. Methodological Protocol for Phase 3 Evaluation

1. **Explicit Ground Truth Anchoring:** All factuality evaluations compare model responses against the shared `reference_answer` and `evidence_snippet`, eliminating ambiguity over whether the model answered the intended question.
2. **Confounder Control in Statistical Models:** When comparing `B_NATIVE` vs. `C_ROMAN`, `token_count` and `fertility` must be entered as explicit covariates to separate the effect of script familiarity from the massive subword fragmentation penalty of native script.
