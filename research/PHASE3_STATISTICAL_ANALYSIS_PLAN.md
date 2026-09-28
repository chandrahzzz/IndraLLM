# IndraLLM — Phase 3 Pre-Registered Statistical Analysis Plan (SAP)

**Document Version:** 1.0 (Frozen Pre-Registration)  
**Date:** 2026-09-29  
**Registration Status:** FROZEN PRIOR TO EXP-002 EXECUTION  
**Primary Unit of Analysis:** `semantic_id` ($N = 200$ clusters in held-out test split, 1,000 paired condition prompts)  

---

## 1. Primary Objective & Research Endpoints

### 1.1 Primary Outcome Variable
The primary outcome variable is **Binary Factual Correctness** ($Y_{i,c,m} \in \{0, 1\}$) for semantic question $i$, condition $c$, and model $m$:
- **$Y = 1$ (Factually Correct / Faithful):** The model response correctly asserts the factual claim substantiated by the authoritative reference evidence excerpt. Paraphrase and code-mixing are permitted.
- **$Y = 0$ (Hallucinated / Factual Error):** The response states an erroneous entity, contradictory date, fabricated number, or ungrounded assertion.
- **Hallucination Rate:** $\text{Hallucination Rate} = 1.0 - \text{Accuracy}$.

### 1.2 Missing Outputs and Refusal Policy
- **Refusals ($Y_{\text{refusal}} = 1$):** Explicit refusal to answer ("I don't know", "As an AI...") is tracked as a distinct categorical state. In the primary analysis, refusals are treated as $Y = 0$ (failure to provide the correct fact). In pre-specified Sensitivity Analysis 1, models are re-evaluated with refusals censored.
- **Parser / API Failures:** Any network timeout or JSON parse failure will be retried up to 3 times with exponential backoff. If unresolved, the item is retained as `missing_eval` and reported in the completion table. Dropping missing data without audit is prohibited.

---

## 2. Pre-Specified Primary Contrasts (Family of Confirmatory Hypotheses)

To control the Family-Wise Error Rate (FWER at $\alpha = 0.05$), we pre-specify exactly **7 orthogonal and semi-orthogonal pairwise contrasts** per model:

| Contrast ID | Comparison | Null Hypothesis ($H_0$) | Scientific Question Addressed |
|---|---|---|---|
| **C1** | $A\_EN \text{ vs } B\_NATIVE$ | $\theta_{A\_EN} = \theta_{B\_NATIVE}$ | Baseline English vs. native script Indic accuracy. |
| **C2** | $A\_EN \text{ vs } C\_ROMAN$ | $\theta_{A\_EN} = \theta_{C\_ROMAN}$ | Baseline English vs. Romanized monolingual Indic. |
| **C3** | $A\_EN \text{ vs } D\_CS$ | $\theta_{A\_EN} = \theta_{D\_CS}$ | Baseline English vs. natural code-switching. |
| **C4** | $A\_EN \text{ vs } E\_MIXED\_SCRIPT$ | $\theta_{A\_EN} = \theta_{E\_MIXED}$ | Baseline English vs. mixed-script intra-sentential mixing. |
| **C5** | $B\_NATIVE \text{ vs } C\_ROMAN$ | $\theta_{B\_NATIVE} = \theta_{C\_ROMAN}$ | **Pure Orthographic Effect:** Holding language constant, what is the effect of Latin transliteration? |
| **C6** | $B\_NATIVE \text{ vs } D\_CS$ | $\theta_{B\_NATIVE} = \theta_{D\_CS}$ | **Code-Switching from Native Base:** What is the effect of introducing English code-mixing into an Indic base? |
| **C7** | $C\_ROMAN \text{ vs } D\_CS$ | $\theta_{C\_ROMAN} = \theta_{D\_CS}$ | **Pure Lexical Mixing Effect:** Holding Latin script constant, what is the effect of code-switching? |

---

## 3. Confirmatory Statistical Tests

### 3.1 Paired Binary Test: McNemar's Test
For each contrast $C_j$ on $N = 200$ matched semantic units:
$$\chi^2 = \frac{(|b_{01} - b_{10}| - 1)^2}{b_{01} + b_{10}}, \quad \text{df} = 1$$
Where:
- $b_{01}$: Number of semantic units where Condition 1 is Correct and Condition 2 is Incorrect.
- $b_{10}$: Number of semantic units where Condition 1 is Incorrect and Condition 2 is Correct.
- Continuity correction (Edwards, 1948) is mandatory.

### 3.2 Paired Bootstrap Confidence Intervals
- Resampling unit: `semantic_id` (resampling the entire 5-condition tuple together).
- Number of bootstrap replicates: $B = 2,000$.
- Confidence interval: 95% Percentile / BCa bootstrap interval on $\Delta \text{Accuracy} = \theta_{\text{Condition\_2}} - \theta_{\text{Condition\_1}}$.

### 3.3 Multiple Testing Correction: Holm-Bonferroni
- Applied to the family of 7 primary contrasts ($C_1 \dots C_7$).
- P-values sorted in ascending order: $p_{(1)} \le p_{(2)} \le \dots \le p_{(7)}$.
- Significance threshold at rank $k$: $\alpha_k = \frac{0.05}{7 - k + 1}$.

---

## 4. Hierarchical Mixed-Effects Model Specification

To evaluate simultaneous multivariate predictors and interactions without pseudo-replication:

$$\text{logit}(P(Y_{i,c,m,l} = 0)) = \beta_0 + \beta_{\text{cond}}[c] + \beta_{\text{lang}}[l] + \beta_{\text{model}}[m] + \beta_{\text{fertility}} \cdot \text{Fertility}_{i,c,m} + \beta_{\text{cmi}} \cdot \text{CMI}_{i,c} + u_i$$

Where:
- $Y = 0$: Binary indicator of hallucination / factual error.
- $\beta_{\text{cond}}[c]$: Fixed effect of condition ($c \in \{A\_EN, B\_NATIVE, C\_ROMAN, D\_CS, E\_MIXED\_SCRIPT\}$) with $A\_EN$ as reference.
- $\beta_{\text{lang}}[l]$: Fixed effect of language ($l \in \{hi, ta, te, bn, kn\}$).
- $\beta_{\text{model}}[m]$: Fixed effect of model family.
- $\text{Fertility}_{i,c,m}$: Subword token fertility ($\text{tokens}/\text{word}$) for the specific model's tokenizer.
- $\text{CMI}_{i,c}$: Measured continuous Code-Mixing Index.
- $u_i \sim \mathcal{N}(0, \sigma_u^2)$: Random intercept for `semantic_id` $i$, accounting for item-level baseline difficulty.

---

## 5. Pre-Specified Secondary and Exploratory Endpoints

### 5.1 Secondary Endpoints:
1. **Within-Model Representation Gap:**
   $$\text{RepGap}(M_k, c) = \text{Accuracy}(M_k, A\_EN) - \text{Accuracy}(M_k, c)$$
2. **Cross-Condition Factual Consistency (CCFC):**
   For semantic unit $S_i$, the fraction of pairs $(c_j, c_k)$ where model $M$ gives identical factual assertions:
   $$\text{CCFC}_i(M) = \frac{1}{\binom{5}{2}} \sum_{j < k} \mathbb{I}(\hat{y}_{i, c_j} = \hat{y}_{i, c_k})$$

### 5.2 Exploratory Analyses:
- Non-linear spline regression of hallucination probability against continuous CMI ($0\% \to 50\%$).
- Interaction between token fertility and condition error rate.
- Cross-domain stability: Evaluating whether the representation gap expands in technical domains (`science`, `public_health`) compared to civic domains (`governance`).

---

## 6. Sensitivity Analyses

1. **SA-1 (Refusal Handling):** Re-compute all primary contrasts with explicit refusals censored rather than coded as errors.
2. **SA-2 (Difficulty Stratification):** Compare primary contrasts separately for Level 1–2 (Direct factual) versus Level 4–5 (Multi-hop and ambiguous entities).
3. **SA-3 (Evaluator Confidence Filtering):** Re-run primary contrasts restricting analysis to cases where automated evaluator confidence is $\ge 0.85$ or validated by human raters.

---

## 7. Preregistration Freeze Declaration

This Statistical Analysis Plan is formally frozen. No comparisons or model formulas may be altered post-hoc after inspecting main Phase 3 experimental tables. Any subsequent exploratory analyses will be explicitly designated as such in the paper.
