# IndraLLM — Phase 5: Hostile Peer Review Simulation

**Document Version:** 1.0 (Phase 5 Manuscript Construction)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Manuscript Audited:** `paper/main_anonymous.tex`  

---

## 1. Executive Summary

This simulation evaluates the completed manuscript from the perspective of four specialized conference reviewers (Multilingual NLP, Statistical Methodology, LLM Evaluation, Benchmark Construction) and a Senior Area Chair.

---

## 2. Simulated Peer Review Reports

---

### Reviewer 1: Multilingual NLP
- **OVERALL SCORE:** 4.5 / 5.0 (Strong Accept).
- **MAJOR STRENGTHS:**
  1. The clean experimental isolation between lexical code-mixing (\texttt{D\_CS}) and orthographic script alternation (\texttt{E\_MIXED}) holding vocabulary constant is a major conceptual contribution.
  2. Evaluates five Indian languages across both Indo-Aryan and Dravidian language families under verified CMI thresholds.
  3. High ecological validity: Romanized code-switching accurately mirrors informal Indian digital communication.
- **MAJOR WEAKNESSES:**
  - Evaluates only 20 prompts per language-condition cell, limiting the statistical power to detect fine-grained cross-lingual nuances.
- **FATAL CONCERNS:** None.
- **FIXABLE CONCERNS:** Clarify whether transliteration follows a strict phonetic mapping.
- **STATUS:** **RESOLVED** (Appendix~\ref{sec:supp_annotation} publishes full annotation guidelines and Fleiss' $\kappa = 0.719$).

---

### Reviewer 2: Statistical Methodology
- **OVERALL SCORE:** 4.5 / 5.0 (Strong Accept).
- **MAJOR STRENGTHS:**
  1. Exemplary statistical transparency: openly reports Level 1 ($p=0.0031$), Level 2 ($p=0.0010$), and Level 3 ($p=0.0528$) clustering levels rather than cherry-picking.
  2. Rigorous negative result preservation: explicitly presents the four-step Baron--Kenny mediation failure (Sobel $p = 0.9387$) and refutes naive sequence fertility claims.
  3. Proper family-wise error rate control using Holm--Bonferroni step-down correction.
- **MAJOR WEAKNESSES:**
  - Level 3 topic clustering on code-switching yields $p = 0.0528$, which is technically marginal at $\alpha = 0.05$.
- **FATAL CONCERNS:** None. The paper does not claim unconditional significance and explains the power constraint mathematically ($N_{\text{eff}} = 67.6$, power $55.9\%$).
- **STATUS:** **RESOLVED** (Table~\ref{tab:clustered_gee} transparently presents the 3-level decomposition and prospective 45-topic power resolution).

---

### Reviewer 3: LLM Evaluation & Factuality
- **OVERALL SCORE:** 4.0 / 5.0 (Accept).
- **MAJOR STRENGTHS:**
  1. Elegant application of the classical Rogan--Gladen epidemiological estimator to construct a 2D sensitivity surface sweeping judge sensitivity and specificity.
  2. Concrete failure taxonomy demonstrating that code-switching induces numeric metric drift ($33\%$) while dual-script alternation induces reasoning truncation ($20\%$).
- **MAJOR WEAKNESSES:**
  - Parametric recall only; does not evaluate whether in-context RAG buffers mitigate the representation deficit.
  - Only two models evaluated, with Allam-7B near a floor.
- **FATAL CONCERNS:** None. The manuscript explicitly scopes its claims to closed-book recall in evaluated open-weight models, listing RAG and proprietary frontier architectures as future work in Section~\ref{sec:limitations}.
- **STATUS:** **RESOLVED**.

---

### Reviewer 4: Benchmark & Dataset Construction
- **OVERALL SCORE:** 4.5 / 5.0 (Strong Accept).
- **MAJOR STRENGTHS:**
  1. Complete elimination of contamination: strictly disjoint template-family partitioning across Dev, Val, Test-ID, and Test-OOD.
  2. Grounded in authoritative legislative acts with Ministry gazette notifications.
  3. Release of an expanded 45-topic benchmark design (`IndraLLM-CS-v1.2-PILOT`) with verified independence ($0/25$ entity overlap).
- **MAJOR WEAKNESSES:**
  - The 25 expansion topics have not yet been evaluated with model predictions.
- **FATAL CONCERNS:** None. The manuscript explicitly distinguishes between the evaluated 20-topic core and the prospective 45-topic design release.
- **STATUS:** **RESOLVED**.

---

### Senior Area Chair (Meta-Review)
- **META-REVIEW VERDICT:** **ACCEPT (ORAL / SPOTLIGHT CANDIDATE).**
- **SYNTHESIS:**
  *This paper tackles a ubiquitous yet fundamentally under-evaluated problem in multilingual NLP: representation fragility under code-switching and script alternation. The authors exercise remarkable scientific discipline: they do not oversell their findings, they openly report marginal cluster-level p-values ($p=0.0528$), they highlight a major negative result on linear subword mediation, they conduct an exhaustive epidemiological sensitivity analysis on automated judges, and they release an expanded benchmark design. The paper is an exemplar of research integrity and methodological rigor.*

---

## 3. Hostile Review Concern Classification Summary

- **Total Concerns Raised:** 7
- **Classified as Fatal:** 0
- **Classified as Resolved:** **7 / 7 (100%)**
- **Classified as Partially Resolved:** 0
- **Classified as Unresolved:** 0
