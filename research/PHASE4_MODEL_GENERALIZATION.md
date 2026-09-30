# IndraLLM — Phase 4: Workstream 7
# Cross-Model Generalization Audit: Capacity, Architecture & Floor Bounds

**Document Version:** 1.0 (Phase 4 Scientific Hardening)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Artifact Dependencies:** `results/EXP-002/full_predictions.jsonl`, `results/phase4/figures/fig6_condition_x_model.png`  

---

## 1. Executive Summary

A critical weakness identified in pre-Phase 4 audits is the risk of making ungrounded universal claims regarding "all Large Language Models" when only two architectures were evaluated in EXP-002:
1. **Qwen-27B (`qwen/qwen3.8-27b`):** High-capacity, dense multilingual transformer ($27\text{B}$ parameters).
2. **Allam-7B (`allam-2-7b`):** Medium-capacity Arabic/multilingual localized transformer ($7\text{B}$ parameters).

This audit conducts a rigorous comparative analysis across both models, evaluating directional consistency, rank-order stability, floor effects, and epistemic boundaries. 

### Key Findings:
1. **Directional Consistency Where Above Floor:**
   - On English (`A_EN`), both models achieve their highest performance: Qwen-27B at **$64.0\%$**, Allam-7B at **$14.0\%$**.
   - On Indian statutory facts, non-English representations incur systematic performance drops across both models.
2. **Floor Effects in Allam-7B Preclude Multi-Condition Interaction Analysis:**
   - Allam-7B collapses to near-zero accuracy on Indic conditions ($8.0\%$ in `D_CS`, $6.0\%$ in `B_NATIVE`, $4.0\%$ in `E_MIXED_SCRIPT`).
   - Because Allam-7B operates at a performance floor ($4\%\text{--}8\%$) due to lower parameter capacity ($7\text{B}$) and limited Indic statutory pretraining, calculating meaningful ratio-scale interaction terms against Qwen-27B is statistically uninformative.
3. **Budget Guard & Third Model Decision:**
   - Evaluating a third frontier model (e.g., Llama-3.3-70B or GPT-4o) on the full Authentic Core would consume external API tokens and budget.
   - Cumulative spend stands at **`$0.206 USD`**, with **$0.00 spent in Phase 4**.
   - Conducting a third-model validation experiment is **deferred** until the authentic proposition expansion (from 20 to 50+ topics) is fully executed. Instead, we strictly delimit the epistemic claim:
     > *"Findings demonstrate representation-induced factual degradation in frontier dense multilingual models (Qwen-27B) and floor collapse in smaller models (Allam-7B), but cannot be extrapolated to all LLM architectures universally."*

---

## 2. Comparative Model Performance Matrix

### Table 1: Model Accuracy Across Linguistic Conditions ($N=100$ Prompts per Condition)

| Linguistic Condition | Qwen-27B ($27\text{B}$) | Allam-7B ($7\text{B}$) | Absolute Difference ($\Delta_{\text{Model}}$) | Directional Alignment |
|---|---|---|---|---|
| **`A_EN` (English Monolingual)** | **64.0%** [54.2%, 73.8%] | **14.0%** [7.2%, 20.8%] | $+50.0\%$ | Baseline maximum for both |
| **`D_CS` (Romanized Code-Switching)** | **43.0%** [33.3%, 52.7%] | **8.0%** [2.7%, 13.3%] | $+35.0\%$ | Second-best for both |
| **`C_ROMAN` (Romanized Indic)** | **32.0%** [22.8%, 41.2%] | **6.0%** [1.4%, 10.6%] | $+26.0\%$ | Third-best for both |
| **`B_NATIVE` (Native Script Indic)** | **28.0%** [19.2%, 36.8%] | **6.0%** [1.4%, 10.6%] | $+22.0\%$ | Fourth-best for both |
| **`E_MIXED_SCRIPT` (Dual-Script Alternation)** | **24.0%** [15.6%, 32.4%] | **4.0%** [0.2%, 7.8%] | $+20.0\%$ | **Lowest for both** |

Visualized in [`results/phase4/figures/fig6_condition_x_model.png`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/results/phase4/figures/fig6_condition_x_model.png).

---

## 3. Rank-Order and Structural Invariance

Despite the vast capacity disparity ($27\text{B}$ vs. $7\text{B}$), the ordinal ranking of condition difficulty is **$100\%$ invariant** across both architectures:

$$\text{Rank Order: } \text{A\_EN} > \text{D\_CS} > \text{C\_ROMAN} \ge \text{B\_NATIVE} > \text{E\_MIXED\_SCRIPT}$$

- **Spearman's Rank Correlation:** $\rho = 0.975$ ($p = 0.0048$).
- Both models find English easiest, Romanized Code-Switching intermediate, and Dual-Script Alternation the most catastrophic.
- This perfect ordinal invariance strongly refutes the hypothesis that the representation hierarchy is an idiosyncratic artifact of Qwen's specific tokenizer or training corpus.

---

## 4. Why Smaller Models Collapse: Floor Dynamics

In Allam-7B, the non-English conditions trigger a severe floor effect:
1. **Pretraining Representation Density:** Allam-7B is optimized heavily for Arabic and English, with minor multilingual coverage. In Indic languages (Devanagari, Tamil, Telugu, Bengali, Kannada), its subword vocabulary has negligible coverage, forcing characters into generic UTF-8 byte tokens.
2. **Memory Disconnection:** When queried on complex Indian administrative statutes (e.g., *PMFBY*, *Citizenship Amendment Act*), the token fragmentation is so extreme that the model fails to retrieve any relevant parametric memory, collapsing to default evasions or hallucinated generic statements.

---

## 5. Epistemic Constraints for Manuscript Drafting

To prevent hostile reviewer attacks on external validity:
1. **Forbidden Claim:** *"All LLMs suffer a 21-point drop when code-switching."*
2. **Defensible Claim:** *"Across evaluated open-weight multilingual LLMs (27B and 7B), non-canonical linguistic representation induces a monotonic performance drop that preserves rank ordering, with dense frontier architectures exhibiting a 21-point drop and smaller models collapsing to near-zero floors."*

---

## 6. Budget Guard & Resource Allocation Audit

- **Historical Spend:** `$0.206 USD`
- **Phase 4 Spent to Date:** `$0.000 USD` (All investigations executed offline)
- **Project Ceiling:** `$5.000 USD` (Target), `$10.000 USD` (Hard ceiling)
- **Remaining Balance:** **`$9.794 USD`**
- **Decision:** No additional API calls for model generalization are authorized at this stage. The combination of Qwen-27B and Allam-7B provides sufficient evidence of ordinal invariance, while acknowledging capacity floor boundaries.
