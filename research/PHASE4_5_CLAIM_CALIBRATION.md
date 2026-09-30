# IndraLLM — Phase 4.5: Workstream 6
# Claim Calibration Matrix: Rigorous Verification of Core Manuscript Claims

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  

---

## 1. Executive Summary

This audit subjects every prospective scientific claim intended for the IndraLLM research paper to rigorous evidentiary verification. Each claim is categorized into one of four formal epistemic classes:
- **`SUPPORTED`**: Fully verified by empirical data, appropriate statistical modeling, and sensitivity analysis.
- **`SUPPORTED_WITH_QUALIFICATION`**: Empirically valid, but requires explicit boundary conditions (e.g., disclosure of cluster-level uncertainty or architecture scope).
- **`EXPLORATORY`**: Plausible post-hoc hypothesis requiring further testing.
- **`UNSUPPORTED`**: Lacks sufficient evidentiary support or represents an overgeneralization; strictly forbidden from manuscript claims.

---

## 2. Exhaustive Claim Classification Matrix

### Table 1: Comprehensive Calibration of Core Research Claims

| Ref # | Prospective Paper Claim | Audit Status | Empirical Grounding & Limitations | Strongest Defensible Manuscript Wording |
|---|---|---|---|---|
| **C1** | *"Non-canonical linguistic representations degrade parametric factual reliability under invariant semantics."* | **SUPPORTED_WITH_QUALIFICATION** | On authentic Indian statutory questions ($N=500$), English achieves $64.0\%$, dropping to $43.0\%$ (Code-Switching) and $24.0\%$ (Dual-Script) under strict 5-way semantic control. Bounded to evaluated models. | *"In evaluated open-weight multilingual LLMs, non-canonical representations (code-switching, romanization, dual-script) incur substantial factual degradation relative to semantically equivalent English on authentic statutory questions."* |
| **C2** | *"Code-switching degrades factual accuracy by 21 percentage points relative to English."* | **SUPPORTED_WITH_QUALIFICATION** | $\Delta = -21.0\%$ ($64\%$ vs $43\%$). Significant at Level 1 ($p=0.0031$) and Level 2 ($p=0.0010$); borderline at Level 3 ($p=0.0528$) due to $N=20$ clusters. | *"Romanized code-switching incurs a 21-percentage-point factual penalty (p = 0.0010 at semantic cluster level; p = 0.0528 under conservative 20-topic clustering), driven by metric and date drift."* |
| **C3** | *"Dual-script alternation induces catastrophic degradation beyond code-switching alone."* | **SUPPORTED** | `D_CS` ($43.0\%$) drops to `E_MIXED_SCRIPT` ($24.0\%$), $\Delta = -19.0\%$, GEE $p = 0.0049$. Fully robust across all clustering levels. | *"Intra-sentential script alternation degrades factual accuracy by an additional 19 percentage points beyond code-switching alone (p = 0.0049), demonstrating that orthographic switching impairs generation flow."* |
| **C4** | *"Subword tokenization fragmentation causally mediates factual failure linearly."* | **UNSUPPORTED** | Baron–Kenny Path $a$ and $c$ are significant, but Path $b$ is null ($\beta = -0.0212, p = 0.9387$, Sobel $z = 0.0769$). | **FORBIDDEN CLAIM.** Replaced by C5. |
| **C5** | *"Discrete script transitions disrupt self-attention and induce reasoning truncation."* | **SUPPORTED_WITH_QUALIFICATION** | Dual-script prompts exhibit an average of $5.1$ script switches and a $20\times$ surge in truncated reasoning ($20\%$ vs $1\%$). Direct causal proof of attention head breakage is mechanistic/qualitative, not mathematically isolated. | *"Orthographic script alternation introduces frequent script transition boundaries (mean 5.1 per prompt), which strongly associate with an 18-to-20-fold increase in reasoning truncation and relational failure."* |
| **C6** | *"Representation degradation is uniform across Indic language families."* | **SUPPORTED** | Evaluated 16 $\text{Condition} \times \text{Language}$ interaction terms across Hindi, Bengali, Tamil, Telugu, and Kannada; all $p \ge 0.0504$. | *"Across five major Indian languages spanning Indo-Aryan and Dravidian families, the representation penalty operates with striking uniformity (no significant condition x language interactions, all p >= 0.0504)."* |
| **C7** | *"The observed representation penalty is an invariant law governing all Large Language Models."* | **UNSUPPORTED** | Only Qwen-27B and Allam-7B evaluated. Allam-7B is at a capacity floor. | **FORBIDDEN CLAIM.** Must strictly bound claims to evaluated architectures. |
| **C8** | *"Automated evaluator bias cannot explain away the observed representation deficit."* | **SUPPORTED** | 2D Rogan–Gladen sensitivity surface across $\text{TPR} \in [0.80, 0.96]$ and $\text{FPR} \in [0.04, 0.16]$ preserves an adjusted gap of $+16.82\%$ to $+34.38\%$. | *"Accounting for potential judge bias across a comprehensive 2D sensitivity surface, the adjusted English vs. code-switching performance gap remains substantial (+16.8% to +34.4%) across all plausible evaluator error profiles."* |
| **C9** | *"The 45-topic expansion was empirically evaluated and proved 89.4% power."* | **UNSUPPORTED** | The 25 pilot topics were constructed and frozen, but not live-inferred. Power is a prospective design property. | *"We release an expanded 45-topic benchmark design (IndraLLM-CS-v1.2-PILOT) with a prospective effective sample size of 152.2 and 89.4% statistical power."* |

---

## 3. Disaggregated Condition Profile Summary

| Condition | Absolute Accuracy | 95% Wilson CI | Odds Ratio vs English | Cluster-Robust Level 3 $p$-value | Primary Qualitative Error Signature |
|---|---|---|---|---|---|
| **`A_EN`** | **$64.0\%$** | [$54.2\%$, $72.6\%$] | Baseline ($1.00$) | — | Balanced factual omissions ($18\%$), truncation minimal ($1\%$) |
| **`D_CS`** | **$43.0\%$** | [$33.8\%$, $52.8\%$] | $0.4243$ | $0.0528$ | Associative numeric & calendar date drift ($33\%$) |
| **`C_ROMAN`** | **$32.0\%$** | [$23.7\%$, $41.7\%$] | $0.2771$ | $0.0004$ | Phonetic ambiguity and out-of-date statutory recall ($35\%$) |
| **`B_NATIVE`** | **$28.0\%$** | [$20.1\%$, $37.5\%$] | $0.2188$ | $< 0.0001$ | Subword token fragmentation and reasoning truncation ($19\%$) |
| **`E_MIXED_SCRIPT`** | **$24.0\%$** | [$16.7\%$, $33.2\%$] | $0.1776$ | $0.0005$ | Script-boundary relational disruption & premature termination ($20\%$) |

---

## 4. Manuscript Integration Directives

Every claim in the paper draft must adhere verbatim to the calibrated language in Table 1. Claims flagged as **UNSUPPORTED** must never appear in the title, abstract, introduction, or discussion.
