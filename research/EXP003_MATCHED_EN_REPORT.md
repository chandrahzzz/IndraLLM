# EXP-003: Matched English Condition & Mechanism Verification Report

**Author:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Date of Execution:** October 5, 2026  
**Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Experiment ID:** `EXP-003`  
**Output Artifacts:**
- `results/EXP-003-matched-en/matched_prompts_100.jsonl`
- `results/EXP-003-matched-en/matched_predictions.jsonl`
- `results/EXP-003-matched-en/matched_analysis_summary.json`

---

## 1. Executive Verdict on Key Research Questions

| Question | Verdict Based on Data | Exact Supporting Metric |
|---|:---:|---|
| **1. Does the English advantage survive when prompt phrasing is matched?** | **YES** | Factual accuracy drops from **60.0%** in `A_EN_MATCHED` to **43.0%** in `D_CS` ($\Delta = -17.0$ pp, exact binomial McNemar $p = 0.0137$, Holm-adjusted $p = \mathbf{0.0274}$). Contrasts vs. $C$ (33.0%), $B$ (28.0%), and $E$ (24.0%) remain extreme ($p < 0.0004$). |
| **2. Does the $D_{\text{CS}} \to E_{\text{MIXED}}$ script alternation penalty still hold?** | **YES** | Accuracy plummets from **43.0%** to **24.0%** ($\Delta = -19.0$ pp). Discordant pairs: $b=29, c=10$. Exact binomial McNemar $p = \mathbf{0.00338}$ (Holm-adj $p = 0.0101$). Clustered Level 3 Topic GEE $p = \mathbf{0.00035}$. |
| **3. Does topic-level clustering affect English vs. Code-Switching?** | **YES (Disclosed)** | Due to high topic clustering across the 20 public-policy topics ($\text{ICC} = 0.2040, \text{DEFF} = 5.895, N_{\text{eff}} = 84.8$), the cluster-robust SE at Level 3 yields $p = 0.1559$ for $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$ (down from unclustered $p = 0.0167$). Level 3 clustering remains strictly significant for Native ($p = 0.00018$), Romanized ($p = 0.0031$), and Dual-Script ($p = 0.00035$). |
| **4. Are truncation and script-transition claims reproducible from raw data?** | **CALIBRATED** | Script transitions directly computed via Unicode block changes yield **5.00 transitions/prompt in $E_{\text{MIXED}}$ vs 0.00 in $D_{\text{CS}}$ and $A_{\text{EN}}$**. Automated reasoning truncation (`completion_tokens==128` + ends mid-sentence + judge cites incomplete) yields **41.0% in $E_{\text{MIXED}}$ vs 0.0% in $A_{\text{EN\_MATCHED}}$ (and 3.0% in $A_{\text{EN}}$)**. |
| **5. Does subword token fertility mediate the accuracy collapse?** | **STRICTLY NULL** | Sobel mediation test with the official Qwen tokenizer yields $z = 1.0161, p = \mathbf{0.3096}$. Sequence length does *not* linearly mediate the representation penalty. |

---

## 2. Experimental Setup & Configuration

- **Inference Models:** `qwen/qwen3.8-27b` and `allam-2-7b` on Groq API.
- **Decoding Configuration:** Greedy decoding (`temperature = 0.0`, `top_p = 1.0`, `max_tokens = 128`).
- **Inference System Prompt:**
  ```text
  You are a helpful assistant answering questions from Indian users. Questions may mix an Indian language with English. Answer factually, accurately, and concisely.
  ```
- **Judge Configuration:** `qwen/qwen3.8-27b` on Groq API (`temperature = 0.0`, `max_tokens = 256`).
- **Judge Rubric:**
  ```text
  You are grading whether a model's ANSWER to a user QUESTION is factually correct.
  You are given a trusted GOLD answer. The answer may mix an Indian language with English
  (code-switching) and may be phrased very differently from the gold — that is fine.
  Judge ONLY factual correctness and whether it actually addresses the question.

  Reply on a single line in exactly this format:
  VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>

  QUESTION: {question}
  GOLD ANSWER: {gold}
  MODEL ANSWER: {answer}
  ```
- **Execution Cost:** $0.00836 USD for 200 model inferences + 200 judge evaluations. Total project spend is now **$0.21442 USD** (well below the $10.00 cap).

---

## 3. Master Table: Six Conditions (Qwen-2.5-27B, Authentic Policy Core)

| Condition | Phrasing / Modality Template | Correct (k/100) | Accuracy (%) | 95% Wilson Score CI | Mean Script Switches | Chars / Token (Qwen) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **`A_EN` (Original)** | Specific difference / timeline template | 64/100 | **64.0%** | [54.2%, 72.7%] | 0.00 | 5.822 |
| **`A_EN_MATCHED`** | *"What is the main rule, date or parameter regarding {X}?"* | 60/100 | **60.0%** | [50.2%, 69.1%] | 0.00 | 4.638 |
| **`D_CS`** | Romanized code-switching (*"...ke regarding main rule, date..."*) | 43/100 | **43.0%** | [33.7%, 52.8%] | 0.00 | 4.021 |
| **`C_ROMAN`** | Pure Romanized Indic transliteration | 33/100 | **33.0%** | [24.6%, 42.7%] | 0.00 | 2.903 |
| **`B_NATIVE`** | Pure native Indic Brahmic script | 28/100 | **28.0%** | [20.1%, 37.5%] | 1.00 | 1.237 |
| **`E_MIXED_SCRIPT`** | Dual-script alternation (Latin terms in Brahmic syntax) | 24/100 | **24.0%** | [16.7%, 33.2%] | 5.00 | 2.492 |

*Cross-model comparison on `A_EN_MATCHED`: Allam-2-7B achieves **10.0%** (10/100, 95% CI: [5.5%, 17.4%]), compared to 8.0% on original `A_EN`, confirming its severe cross-lingual capacity floor.*

---

## 4. Paired Hypothesis Tests & Family-Wise Error Rate Control

All comparisons paired per semantic proposition ($N=100$). Family-wise error rate across all 6 contrasts controlled via Holm-Bonferroni:

| Contrast | Accuracy Difference ($\Delta$) | Discordant $(b, c)$ | Exact Binomial $p$-value | Holm-Bonferroni Adjusted $p$ | Continuity-Corrected $\chi^2$ $p$ |
|---|:---:|:---:|:---:|:---:|:---:|
| **`A_EN_MATCHED` vs `B_NATIVE`** | **−32.0 pp** | (39, 7) | $1.83 \times 10^{-6}$ | **$1.10 \times 10^{-5}$** | $4.86 \times 10^{-6}$ |
| **`A_EN_MATCHED` vs `C_ROMAN`** | **−27.0 pp** | (37, 10) | $9.85 \times 10^{-5}$ | **$3.94 \times 10^{-4}$** | $1.49 \times 10^{-4}$ |
| **`A_EN_MATCHED` vs `D_CS`** | **−17.0 pp** | (30, 13) | $0.01372$ | **$0.02744$** | $0.01469$ |
| **`A_EN_MATCHED` vs `E_MIXED`** | **−36.0 pp** | (47, 11) | $2.03 \times 10^{-6}$ | **$1.10 \times 10^{-5}$** | $4.31 \times 10^{-6}$ |
| **`D_CS` vs `E_MIXED_SCRIPT`** | **−19.0 pp** | (29, 10) | $0.00338$ | **$0.01013$** | $0.00395$ |
| **`A_EN` vs `A_EN_MATCHED`** | **−4.0 pp** | (16, 12) | $0.57159$ | **$0.57159$** | $0.57075$ |

**Key Takeaways:**
1. The difference between original `A_EN` and matched `A_EN_MATCHED` is small (−4.0 pp) and statistically non-significant ($p = 0.572$).
2. The contrast between `A_EN_MATCHED` and `D_CS` remains statistically significant ($p = 0.0274$ after Holm-Bonferroni correction).
3. The orthographic disentanglement contrast (`D_CS` vs `E_MIXED_SCRIPT`) remains highly significant ($p = 0.0101$).

---

## 5. Hierarchical Clustered GEE Analysis

Exchangeable correlation structure on the 5-condition matched set ($N=500$ prompts across 20 topics, with $m=25$ observations per topic):

| Level | Cluster Unit | Number of Clusters | Predictor | $\beta$ | Robust SE | $p$-value |
|---|---|:---:|---|:---:|:---:|:---:|
| **Level 1** | Unclustered Prompts | $N=500$ | $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$ | −0.6873 | 0.2872 | **$0.0167$** |
| | | | $E_{\text{MIXED}}$ vs. $A_{\text{MATCHED}}$ | −1.5581 | 0.3087 | **$< 0.0001$** |
| **Level 2** | Semantic Propositions | $N=100$ | $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$ | −0.6873 | 0.2635 | **$0.0091$** |
| | | | $E_{\text{MIXED}}$ vs. $A_{\text{MATCHED}}$ | −1.5581 | 0.2842 | **$< 0.0001$** |
| **Level 3** | Target Topics (Public Policy) | $N=20$ | $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$ | −0.6873 | 0.4844 | **$0.1559$** |
| | | | $E_{\text{MIXED}}$ vs. $A_{\text{MATCHED}}$ | −1.5581 | 0.4357 | **$0.00035$** |
| | | | $B_{\text{NATIVE}}$ vs. $A_{\text{MATCHED}}$ | −1.3651 | 0.3644 | **$0.00018$** |
| | | | $C_{\text{ROMAN}}$ vs. $A_{\text{MATCHED}}$ | −1.1278 | 0.3813 | **$0.0031$** |

### Intra-Cluster Correlation (ICC) & Effective Sample Size
- **Topic-Level $\text{ICC}$:** $0.2040$
- **Design Effect ($\text{DEFF}$ for $m=25$):** $\text{DEFF} = 1 + (25 - 1) \times 0.2040 = \mathbf{5.895}$
- **Effective Sample Size ($N_{\text{eff}}$):** $500 / 5.895 = \mathbf{84.8}$
- **Topic Distribution in `A_EN_MATCHED`:** Across the 20 distinct topics, 12 topics had 5/5 correct answers, while 8 topics had 0/5 correct answers. Because prompts within a topic are semantically related, topic clustering inflates the standard error for the borderline $D_{\text{CS}}$ contrast ($p = 0.1559$), while the more pronounced penalties for $B, C, E$ remain resiliently significant ($p \le 0.0031$).

---

## 6. Epidemiological Sensitivity Analysis (2D Rogan–Gladen Inversion)

Re-evaluating the true factual gap between `A_EN_MATCHED` (observed 60.0%) and `D_CS` (observed 43.0%):

$$\pi_{\text{true}} = \frac{y_{\text{obs}} - \text{FPR}}{\text{TPR} - \text{FPR}}$$

| Evaluator Sensitivity (TPR) | FPR = 0.04 | FPR = 0.08 | FPR = 0.12 | FPR = 0.16 |
|:---:|:---:|:---:|:---:|:---:|
| **0.80** | +22.37% | +23.61% | +25.00% | +26.56% |
| **0.84** | +21.25% | +22.37% | +23.61% | +25.00% |
| **0.88** | +20.24% | +21.25% | +22.37% | +23.61% |
| **0.92** | +19.32% | +20.24% | +21.25% | +22.37% |
| **0.96** | +18.48% | +19.32% | +20.24% | +21.25% |

**Verdict:** The true adjusted representation gap remains positive and substantial (**+18.48% to +26.56%**) across all plausible evaluator performance characteristics.

---

## 7. Mechanistic Analysis & Truncation Reproducibility

### A. Subword Token Fertility Mediation (Baron–Kenny & Sobel Test)
- **Mediator:** Characters per token (CPT) computed via official Qwen BPE tokenizer (`Qwen/Qwen2.5-7B`).
- **Path $a$ ($E_{\text{MIXED}}$ vs $D_{\text{CS}} \to \text{CPT}$):** $\beta = -1.5289, \text{SE} = 0.076, p = 2.91 \times 10^{-40}$ (Dual-script prompts have fewer characters per subword token).
- **Path $b$ ($\text{CPT} \to \text{Accuracy}$ controlling for script):** $\beta = -0.2479, \text{SE} = 0.243, p = \mathbf{0.3087}$ (Non-significant).
- **Sobel Test:** $z = 1.0161, p = \mathbf{0.3096}$.
- **Scientific Conclusion:** Sequence token length does **not** linearly explain the accuracy gap.

### B. Explicit Automated Reasoning Truncation Rule
- **Automated Rule Definition:**
  $$\text{Truncation} = (\text{completion\_tokens} == 128) \land (\text{response ends mid-sentence}) \land (\text{judge\_label} == 1) \land (\text{judge\_reason cites incomplete/missing})$$
- **Reproducible Rates:**
  - `A_EN_MATCHED`: **0/100 (0.0%)**
  - `A_EN` (Original): **3/100 (3.0%)**
  - `D_CS`: **15/100 (15.0%)**
  - `C_ROMAN`: **24/100 (24.0%)**
  - `B_NATIVE`: **42/100 (42.0%)**
  - `E_MIXED_SCRIPT`: **41/100 (41.0%)**

Script alternation and native Brahmic representations cause a dramatic increase in **reasoning derailment and incomplete responses (over 40%)**, while matched English completes concise, well-formed answers within the 128-token cap.

---

## 8. Summary of Changes vs. EXP-002

1. **A New, Unconfounded Condition (`A_EN_MATCHED`):** Created 100 prompts using the exact English translation of the generic B–E template (*"What is the main rule, date or parameter regarding {X}?"*). Original `A_EN` remains fully preserved.
2. **True Exact Statistics:** Replaced continuity-corrected approximations with exact two-sided binomial McNemar tests and applied Holm-Bonferroni correction.
3. **Reproducible Mechanism Code:** Script transitions and subword fertility are now computed directly via explicit Unicode block parsing and the official Qwen tokenizer.
4. **Transparent Cluster Reporting:** Disclosed topic-level clustering ($p = 0.1559$ for $D_{\text{CS}}$ vs. $A_{\text{MATCHED}}$ at Level 3, while $B, C, E$ remain $p \le 0.0031$).
