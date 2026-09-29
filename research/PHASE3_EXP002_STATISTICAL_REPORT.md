# IndraLLM — Phase 3: EXP-002 Confirmatory Statistical Report
## Paired Repeated-Measures Analysis, McNemar Tests, and Clustered Logistic Regression

**Document Version:** 1.0 (Post-Execution Synthesis)  
**Execution Date:** September 2026  
**Experiment Identifier:** `EXP-002`  
**Author & Sole Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Statistical Anchor Unit:** `semantic_id` ($N = 100$ independent clusters on Authentic Core)  
**Software Environment:** Python 3.11 | Scipy 1.14 | Statsmodels 0.14 | NumPy 1.26  

---

## 1. Executive Summary & Methodological Defense

To avoid pseudoreplication, this report treats the **`semantic_id`** as the repeated-measures clustering unit. Individual condition prompts belonging to the same factual unit are **NOT** assumed to be independent.

### Key Inferential Conclusions:
1. **Hypothesis H1 (Condition Difference):** **CONFIRMED.** Code-switched text (`D_CS`) suffers a statistically significant **$21.0\%$ factual accuracy degradation** relative to English ($p = 0.0023$, $OR = 2.91$, Holm-Bonferroni adjusted).
2. **Hypothesis H3 (Orthographic Disruption):** **CONFIRMED.** Dual-script alternating text (`E_MIXED_SCRIPT`) suffers an additional **$19.0\%$ degradation** beyond Romanized code-switching ($p = 0.0039$, $OR = 2.90$, Holm-Bonferroni adjusted), proving that intra-sentential script shifting disrupts factual recall beyond lexical mixing.
3. **Hypothesis H4 (Condition vs. Language Dominance):** **CONFIRMED.** Clustered logistic regression demonstrates that condition fixed effects are massive ($p < 0.0006$, Odds Ratios $0.18 - 0.42$), whereas language effects are non-significant ($p > 0.25$), proving that orthographic and lexical representation format dominates over language family identity.

---

## 2. Primary Planned Contrasts: Paired McNemar Tests (Authentic Core $N=100$)

Evaluated on `qwen/qwen3.8-27b` across $N = 100$ paired semantic clusters (500 condition prompts).

| Contrast ID | Comparison (Control vs. Treatment) | Observed Accuracy Diff (%) | 95% Percentile Bootstrap CI | Discordant Pairs ($b_{01}, b_{10}$) | Odds Ratio | Edwards $\chi^2$ | Exact $p$-value | Holm-Bonferroni Adjusted $\alpha$ | Statistically Significant? |
|---|---|---|---|---|---|---|---|---|---|
| **$C_1$** | **English (`A_EN`) vs. Native (`B_NATIVE`)** | **$-36.00\%$** | $[-46.0\%, -26.0\%]$ | $(38, 2)$ | **$19.00$** | $30.62$ | **$< 0.000001$** | $\alpha / 4 = 0.0125$ | **YES (CONFIRMED)** |
| **$C_2$** | **Native (`B_NATIVE`) vs. Roman (`C_ROMAN`)** | **$+5.00\%$** | $[-6.0\%, +16.0\%]$ | $(13, 18)$ | **$0.72$** | $0.52$ | $0.472498$ | $\alpha / 1 = 0.0500$ | **NO (Inconclusive)** |
| **$C_3$** | **English (`A_EN`) vs. Code-Switch (`D_CS`)** | **$-21.00\%$** | $[-33.0\%, -8.98\%]$ | $(32, 11)$ | **$2.91$** | $9.30$ | **$0.002289$** | $\alpha / 3 = 0.0167$ | **YES (CONFIRMED)** |
| **$C_4$** | **Single Script (`D_CS`) vs. Mixed Script (`E`)** | **$-19.00\%$** | $[-31.0\%, -8.00\%]$ | $(29, 10)$ | **$2.90$** | $8.31$ | **$0.003948$** | $\alpha / 2 = 0.0250$ | **YES (CONFIRMED)** |

### Contrast Forensic Analysis:
- In $C_1$, there were **38 cases** where Qwen answered correctly in English but hallucinated/failed in Native script, compared to only **2 cases** where it succeeded in Native script but failed in English ($OR = 19.0$, $\chi^2 = 30.62$).
- In $C_3$, English outperformed Code-Switching by 32 to 11 discordant cases ($OR = 2.91$), establishing the statistical reality of the code-switching factuality gap.
- In $C_4$, Romanized code-switching outperformed mixed-script code-switching by 29 to 10 discordant cases ($OR = 2.90$), validating that intra-sentential script transitions create severe attention and tokenization penalties.

---

## 3. Repeated-Measures Logistic Regression (Cluster-Robust GEE)

Model Specification:
$$\text{logit}(P(y_{ij} = 1)) = \beta_0 + \sum_{k} \beta_k \cdot \text{Condition}_{kij} + \sum_{m} \gamma_m \cdot \text{Language}_{mij} + u_i$$
where observations are clustered by `semantic_id` ($N = 100$ clusters, 500 observations) with cluster-robust variance estimation.

Reference Categories: `Condition = A_EN`, `Language = bn (Bengali)`.

| Parameter | Coefficient ($\beta$) | Robust Std. Error | $z$-statistic | $p$-value ($P > |z|$) | Odds Ratio ($e^\beta$) | 95% Confidence Interval for Odds Ratio |
|---|---|---|---|---|---|---|
| **Intercept** | $+0.4230$ | $0.3138$ | $1.348$ | $0.1774$ | $1.5266$ | $[0.825, 2.823]$ |
| **`Condition: B_NATIVE`** | **$-1.5316$** | $0.3082$ | $-4.970$ | **$< 0.0001$** | **$0.2162$** | **$[0.118, 0.395]$** |
| **`Condition: C_ROMAN`** | **$-1.2938$** | $0.2905$ | $-4.453$ | **$< 0.0001$** | **$0.2742$** | **$[0.155, 0.485]$** |
| **`Condition: D_CS`** | **$-0.8641$** | $0.2505$ | $-3.450$ | **$0.0006$** | **$0.4214$** | **$[0.258, 0.689]$** |
| **`Condition: E_MIXED_SCRIPT`**| **$-1.7410$** | $0.3223$ | $-5.402$ | **$< 0.0001$** | **$0.1753$** | **$[0.093, 0.329]$** |
| `Language: Hindi (hi)` | $+0.3246$ | $0.3592$ | $0.904$ | $0.3662$ | $1.3835$ | $[0.685, 2.795]$ |
| `Language: Kannada (kn)` | $+0.0952$ | $0.3627$ | $0.262$ | $0.7929$ | $1.0998$ | $[0.540, 2.240]$ |
| `Language: Tamil (ta)` | $-0.0485$ | $0.3789$ | $-0.128$ | $0.8981$ | $0.9527$ | $[0.453, 2.001]$ |
| `Language: Telugu (te)` | $+0.4140$ | $0.3622$ | $1.143$ | $0.2530$ | $1.5129$ | $[0.744, 3.078]$ |

### Regression Takeaways:
1. **Odds of Factual Correctness:**
   - Under `B_NATIVE`, the odds of answering factually are **$78.4\%$ lower** than in English ($OR = 0.216$, $p < 0.0001$).
   - Under `D_CS`, the odds of answering factually are **$57.9\%$ lower** than in English ($OR = 0.421$, $p = 0.0006$).
   - Under `E_MIXED_SCRIPT`, the odds of answering factually are **$82.5\%$ lower** than in English ($OR = 0.175$, $p < 0.0001$).
2. **Language Invariance:** None of the language dummy variables achieve significance ($p = 0.25$ to $0.90$), confirming that the failure mode is fundamentally driven by **orthography, script mixing, and code-switching**, not specific regional language vocabulary.

---

## 4. Test-OOD Power Qualification

As pre-registered in the Phase 2.7 Power Audit:
- With $N = 100$ clusters, the minimum detectable effect at $80\%$ power is $12.53\%$.
- The observed effect sizes for $C_1$ ($-36\%$), $C_3$ ($-21\%$), and $C_4$ ($-19\%$) all **substantially exceed the $12.53\%$ MDE threshold**.
- Therefore, despite the smaller sample size of Test-OOD, these three primary contrasts are **fully statistically powered and robust against Type II error**.
- Contrast $C_2$ ($+5.0\%$) falls below the $12.5\%$ MDE threshold; as pre-registered, we report its 95% confidence interval ($[-6\%, +16\%]$) and classify it as **exploratory / inconclusive**.
