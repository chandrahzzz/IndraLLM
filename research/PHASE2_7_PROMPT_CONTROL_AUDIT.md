# IndraLLM — Adversarial Prompt Control & Evaluation Confound Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 19 Experimental Prompt Control Verification  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

In cross-lingual and code-switching evaluation, a frequent methodological confound occurs when prompt templates inadvertently supply extra instructions, formatting cues, or reasoning chain scaffolds to one language or condition, confounding linguistic difficulty with prompt engineering.

**Adversarial Verdict:**
1. **Core Pipeline Control is Excellent:** Across all 5 experimental conditions, system prompts, inference parameters (temperature, max tokens, top-p, seed), and output formats are strictly matched. No condition receives special few-shot exemplars or chain-of-thought scaffolds.
2. **Identified Asymmetry in Test-OOD:** In `Test-OOD` (`TF-11` and `TF-12`), English prompts (`A_EN`) explicitly provide relational and temporal directives (*"What is the key structural or operational difference between..."*), whereas Indic conditions (`B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT`) default to generic inquiries (*"{name} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?"*). This gives English a structural advantage on Test-OOD.

---

## 2. Forensic Parameter-Level Prompt Control Audit

| Parameter | Condition A_EN | Condition B_NATIVE | Condition C_ROMAN | Condition D_CS | Condition E_MIXED_SCRIPT | Status |
|---|---|---|---|---|---|---|
| **System Prompt** | Standard Zero-Shot | Identical | Identical | Identical | Identical | **MATCHED** |
| **Few-Shot Examples** | None (Zero-Shot) | None | None | None | None | **MATCHED** |
| **Instruction Prefix** | None | None | None | None | None | **MATCHED** |
| **Formatting Demands** | Direct concise answer | Direct concise answer | Direct concise answer | Direct concise answer | Direct concise answer | **MATCHED** |
| **Decoding Temperature**| $0.0$ (Greedy) / $0.2$ | $0.0$ (Greedy) / $0.2$ | $0.0$ (Greedy) / $0.2$ | $0.0$ (Greedy) / $0.2$ | $0.0$ (Greedy) / $0.2$ | **MATCHED** |
| **Max Output Tokens** | 256 tokens | 256 tokens | 256 tokens | 256 tokens | 256 tokens | **MATCHED** |
| **Top-p / Top-k** | Default ($1.0$) | Default ($1.0$) | Default ($1.0$) | Default ($1.0$) | Default ($1.0$) | **MATCHED** |
| **Special Tokens** | Standard tokenizer BOS/EOS | Standard tokenizer BOS/EOS | Standard tokenizer BOS/EOS | Standard tokenizer BOS/EOS | Standard tokenizer BOS/EOS | **MATCHED** |
| **Random Seed** | Fixed ($42$) | Fixed ($42$) | Fixed ($42$) | Fixed ($42$) | Fixed ($42$) | **MATCHED** |

---

## 3. Discrepancy Breakdown: Test-OOD Task Directive Asymmetry

In `src/indrallm/collection/build_decontaminated_benchmark_v1_1.py`:
- `TF-11` (Cross-Entity Comparison):
  - `A_EN`: *"What is the key structural or operational difference between {entity1} vs {entity2}?"*
  - `B_NATIVE` (hi): *"{entity1} vs {entity2} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?"*
- **Confound Mechanism:** 
  The English prompt explicitly signals that a comparative contrast is expected. A multilingual model answering in English knows to compare the two entities. The Hindi prompt merely asks for "the main rule, date, or parameter regarding X vs Y", which may lead the model to describe only one entity, triggering an automated evaluation penalty.
- **Severity:** **MAJOR.** This introduces an artificial deficit for vernacular conditions in Test-OOD.

---

## 4. Required Action Plan

1. **Gate G13 (Prompt Control):** Classified as **PASS WITH LIMITATION**.
2. **Paper Reporting:** When presenting EXP-002 results on Test-OOD, the paper must explicitly document this prompt framing asymmetry and report an ablation showing whether providing translated comparative phrasing in Indic languages closes the gap.
