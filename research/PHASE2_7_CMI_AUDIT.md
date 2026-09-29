# IndraLLM — Adversarial Code-Mixing Index (CMI) & Orthographic Mixing Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Parts 12 & 13 CMI Calculation, B_NATIVE Anomaly, & Script vs. Language Separation  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

In the Phase 2.6 candidate dataset statistics, the measured Gambäck & Das (2014) CMI across the 5 conditions was reported as:
- **`A_EN`:** Mean $0.03\%$ (SD $0.48\%$)
- **`B_NATIVE`:** Mean **$16.75\%$** (SD $3.20\%$)
- **`C_ROMAN`:** Mean **$14.55\%$** (SD $7.90\%$)
- **`D_CS`:** Mean **$17.29\%$** (SD $4.79\%$)
- **`E_MIXED_SCRIPT`:** Mean **$38.90\%$** (SD $7.90\%$)

**Adversarial Challenge:**
An EMNLP reviewer would immediately identify two alarming anomalies:
1. **The B_NATIVE Paradox:** Why does `B_NATIVE` (defined as "Monolingual Native Script representation") have a mean CMI of **$16.75\%$**, which is categorized as *moderate code-mixing* and is actually *higher* than Romanized Indic (`C_ROMAN` at $14.55\%$)?
2. **Condition Compression:** If `B_NATIVE` ($16.75\%$) and `D_CS` ($17.29\%$) have almost identical CMI, how can the benchmark claim that `D_CS` isolates code-switching?

---

## 2. Forensic Investigation of the 16.75% B_NATIVE Anomaly

We inspected 20 raw samples of `B_NATIVE` prompts and traced tokenization, language identification (`token_lid`), and CMI calculation:

### 2.1 Representative Sample Traces
1. **Sample S000001 (Hindi):**
   - *Prompt:* `PM-KISAN के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?`
   - *Token LID:* `PM-KISAN` (2 English tokens), `के संबंध में...` (19 Indic tokens).
   - *Gambäck & Das CMI:* $100 \times (1 - 19 / (19 + 2)) = \mathbf{9.52\%}$.
2. **Sample S000006 (Hindi):**
   - *Prompt:* `Ayushman Bharat PM-JAY के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?`
   - *Token LID:* `Ayushman Bharat PM-JAY` (4 English tokens), native carrier (19 Indic tokens).
   - *Gambäck & Das CMI:* $100 \times (1 - 19 / (19 + 4)) = \mathbf{17.39\%}$.
3. **Sample S000381 (Kannada):**
   - *Prompt:* `National_Agriculture_Registry_Unit_77 ಗೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಮುಖ ನಿಯಮ...`
   - *Token LID:* 4 Latin tokens, 21 Kannada tokens.
   - *Gambäck & Das CMI:* $100 \times (1 - 21 / 25) = \mathbf{16.00\%}$.

### 2.2 Root Cause Adjudication
- **Is it a code bug in `compute_cmi`?** **NO.** The Gambäck & Das (2014) formula:
  $$\text{CMI} = 100 \cdot \left(1 - \frac{\max(w_{\text{lang}})}{n - u}\right)$$
  is implemented with mathematical precision.
- **What caused it?** It is a **benchmark design artifact of entity insertion**. In `build_decontaminated_benchmark_v1_1.py`, target entities (e.g. `PM-KISAN`, `Ayushman Bharat`, `National_Science_Registry_Unit_85`) were inserted in Latin script into native Brahmic carrier sentences without transliteration.
- **Sociolinguistic Reality vs. Benchmark Cleanliness:** In colloquial Indian discourse, administrative scheme acronyms and proper names are frequently written in Latin script even in vernacular publications. However, strictly speaking, this introduces **noun-phrase borrowing / code-mixing** into what was labeled a "monolingual" condition.

---

## 3. Disentangling Script Transitions from Language Switches

To determine whether the 5 experimental conditions are genuinely distinct, we analyze two orthogonal dimensions:
1. **Script Transitions:** Physical orthographic transitions between Latin script and Brahmic scripts.
2. **Language Switches:** Lexical transitions between English vocabulary and Indic vocabulary.

### Multidimensional Condition Matrix (Full Benchmark $N=7,500$)

| Condition | Intended Representation | Mean CMI (%) | Mean Script Transitions | Mean Language Switches | English Token Ratio | Indic Token Ratio | Orthographic State | Lexical State |
|---|---|---|---|---|---|---|---|---|
| **A_EN** | Monolingual English | **$0.03\%$** | $1.41$ | $0.01$ | $0.950$ | $0.000$ | Pure Latin | Pure English |
| **B_NATIVE** | Vernacular Script + Latin Entity | **$16.75\%$** | $1.73$ | $1.00$ | $0.163$ | $0.809$ | Predominantly Brahmic | Predominantly Indic (Borrowed Entity) |
| **C_ROMAN** | Romanized Indic | **$14.55\%$** | $1.42$ | $2.40$ | $0.808$ | $0.138$ | **Pure Latin** | Romanized Indic Grammatical Structure |
| **D_CS** | Code-Switched (Hinglish, etc.) | **$17.29\%$** | $1.42$ | $2.60$ | $0.781$ | $0.164$ | **Pure Latin** | High Intra-Sentential Code-Mixing |
| **E_MIXED_SCRIPT**| Mixed Brahmic + Latin | **$38.90\%$** | **$5.73$** | **$5.00$** | $0.580$ | $0.373$ | **Highly Alternating** | High Lexical + Orthographic Mixing |

---

## 4. Key Scientific Distinctions Proven

1. **D_CS vs. E_MIXED_SCRIPT:**
   - Both represent code-switching, but `D_CS` is written entirely in Latin characters (script transitions = $1.42$, representing sentence boundary punctuation transitions), whereas `E_MIXED_SCRIPT` has **$5.73$ orthographic shifts per prompt** across Devanagari/Tamil/Telugu/Bengali/Kannada and Latin scripts.
   - This cleanly isolates **orthographic disruption** from **lexical code-switching**.
2. **B_NATIVE vs. C_ROMAN:**
   - `B_NATIVE` is written in authentic Brahmic orthography ($80.9\%$ Indic characters).
   - `C_ROMAN` is written in Latin characters ($100\%$ Latin orthography).
   - Comparing `B_NATIVE` vs `C_ROMAN` isolates the **transliteration / script penalty** on models.

---

## 5. Reviewer-Facing Protocol for the Paper

1. **Transparent Entity Disclosure:** In Section 3 of the paper, explicitly state: *"In condition `B_NATIVE`, target entity names and statutory acronyms (e.g., PM-KISAN, SEBI) are preserved in standard Latin script as commonly practiced in official publications, resulting in a baseline entity-borrowing CMI of $16.75\%$."*
2. **Use Multi-Dimensional Metrics:** Do not rely on CMI in isolation. Always report CMI alongside **Script Transition Count** and **Language Switch Count** to demonstrate condition separation.
