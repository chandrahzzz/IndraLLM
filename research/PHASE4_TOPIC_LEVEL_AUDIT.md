# IndraLLM — Phase 4: Workstream 1 — Topic-Level Generalization & Hierarchical Clustering Audit
## Multi-Level Variance Decomposition, Intra-Class Correlation, and Effective Degrees of Freedom

**Document Version:** 1.0 (Phase 4 Scientific Strengthening)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `69bd848`  
**Primary Source Artifact:** `results/phase4/phase4_statistical_investigation.json`  

---

## 1. Executive Summary

The central methodological concern identified during the Phase 3.5 forensic audit was the **20-topic dependence problem**:
> *"The Authentic Indian Policy Core contains 100 semantic groups evaluated across 5 conditions (500 prompts per model). However, those 100 semantic groups are derived from 20 base statutory propositions replicated across 5 target Indic languages."*

This workstream conducted a formal hierarchical variance decomposition and multi-level regression across all three structural levels:
- **Level 1 (Prompt Level):** $N = 500$ prompt realizations per model.
- **Level 2 (Semantic Group Level):** $N = 100$ semantic clusters.
- **Level 3 (Base Statutory Topic Level):** $N = 20$ independent statutory propositions.

### Master Statistical Finding:
- **Intra-Class Correlation (ICC):** $\mathbf{\rho = 0.2663}$. Approximately $26.6\%$ of the variance in model factuality is attributable to topic-level clustering ($\sigma^2_{\text{topic}} = 0.0588$, $\sigma^2_{\text{residual}} = 0.1619$).
- **The Native, Romanized, and Script-Alternation Penalties are Invariant to Clustering:**
  - `B_NATIVE` (Brahmic script): Level 1 ($p < 0.0001$) $\to$ Level 2 ($p < 0.0001$) $\to$ Level 3 ($\mathbf{p < 0.0001}$).
  - `C_ROMAN` (Romanized Indic): Level 1 ($p < 0.0001$) $\to$ Level 2 ($p < 0.0001$) $\to$ Level 3 ($\mathbf{p = 0.0004}$).
  - `E_MIXED_SCRIPT` (Dual-script): Level 1 ($p < 0.0001$) $\to$ Level 2 ($p < 0.0001$) $\to$ Level 3 ($\mathbf{p = 0.0005}$).
- **The Code-Switching Boundary Effect (`D_CS`):**
  - Level 1 (Naive): $\beta = -0.8572 \pm 0.2902, \mathbf{p = 0.0031}$
  - Level 2 (Semantic): $\beta = -0.8572 \pm 0.2614, \mathbf{p = 0.0010}$
  - Level 3 (Topic): $\beta = -0.8572 \pm 0.4426, \mathbf{p = 0.0528}$
- **Conclusion:** While orthographic disruption and vernacular script penalties are robust to topic-level clustering, the Romanized code-switching deficit sits directly on the boundary of statistical significance ($p = 0.0528$) due to the restricted degrees of freedom ($N=20$).

---

## 2. Structural Decomposition of the Authentic Core

```
[Level 3: Base Statutory Propositions] (N = 20 Independent Topics)
   ├── TF-11: 10 Relational Comparative Statutory Schemas (e.g. PMFBY vs WBCIS, NEFT vs RTGS)
   └── TF-12: 10 Conditional Prerequisite Thresholds (e.g. Patents Act, RTI Third Party, SEBI)
         │
         ▼ Replicated across 5 target Indic languages (hi, ta, te, bn, kn)
[Level 2: Semantic Group Clusters] (N = 100 Semantic Groups, semantic_id)
         │
         ▼ Realized across 5 linguistic representation conditions (A_EN, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT)
[Level 1: Prompt Realizations] (N = 500 Evaluated Prompts per Model)
```

### Table 1: Structural Parameters of the Three Levels
| Hierarchy Level | Grouping Unit | Sample Units ($N$) | Observations per Unit ($m$) | Independence Assumption | Degree of Freedom ($\text{df}$) |
|---|---|---|---|---|---|
| **Level 1** | `prompt_id` | $500$ | $1$ | Mutual independence (Naive) | $495$ |
| **Level 2** | `semantic_id` | $100$ | $5$ (Conditions) | Semantic cluster pairing | $95$ |
| **Level 3** | `base_topic_id` | $20$ | $25$ ($5\text{ Lang} \times 5\text{ Cond}$) | Topic proposition independence | $19$ |

---

## 3. Multi-Level Regression Comparison

To determine how effect estimates and uncertainty intervals behave as clustering becomes coarser, we fitted identical logistic models across all three levels on Qwen-27B:

$$\text{logit}(P(\text{Correct})) = \beta_0 + \sum_{c \in \{B, C, D, E\}} \beta_c \cdot \text{Condition}_c$$

### Table 2: Model Parameter Estimates across Levels
| Condition Term | Level 1: Naive ($N=500$) | Level 2: Semantic ($N=100$) | Level 3: Topic ($N=20$) | Sensitivity Verdict |
|---|---|---|---|---|
| **Intercept (`A_EN`)** | $+0.5754 \pm 0.2083$ ($p = 0.0057$) | $+0.5754 \pm 0.2083$ ($p = 0.0057$) | $+0.5754 \pm 0.4452$ ($p = 0.1962$) | Baseline shift |
| **`B_NATIVE`** | $-1.5198 \pm 0.3050$ (**$p < 0.0001$**) | $-1.5198 \pm 0.2413$ (**$p < 0.0001$**) | $-1.5198 \pm 0.3650$ (**$p < 0.0001$**) | **Invariantly Significant** |
| **`C_ROMAN`** | $-1.2835 \pm 0.2977$ (**$p < 0.0001$**) | $-1.2835 \pm 0.2482$ (**$p < 0.0001$**) | $-1.2835 \pm 0.3604$ (**$p = 0.0004$**) | **Invariantly Significant** |
| **`D_CS`** | $-0.8572 \pm 0.2902$ (**$p = 0.0031$**) | $-0.8572 \pm 0.2614$ (**$p = 0.0010$**) | $-0.8572 \pm 0.4426$ (**$p = 0.0528$**) | **Marginal at Level 3** |
| **`E_MIXED_SCRIPT`** | $-1.7280 \pm 0.3134$ (**$p < 0.0001$**) | $-1.7280 \pm 0.2844$ (**$p < 0.0001$**) | $-1.7280 \pm 0.4936$ (**$p = 0.0005$**) | **Invariantly Significant** |

---

## 4. Methodological Findings & Implications

1. **Parameter Point Estimates are Invariant:**
   Notice that the estimated coefficients ($\beta$) are **strictly identical** across all three levels ($\beta_{D\_CS} = -0.8572, \beta_{E\_MIXED} = -1.7280$). The estimated effect size does not change.
2. **Standard Error Widening:**
   What changes is the standard error. At Level 3, the cluster-robust sandwich covariance estimator is constrained by only $N=20$ clusters, causing the standard error for `D_CS` to widen from $0.2614$ to $0.4426$ ($+69.3\%$ increase).
3. **The Script Disruption Effect (`E_MIXED_SCRIPT`) is Completely Robust:**
   Even with standard errors inflated by $N=20$ topic clustering, the dual-script penalty remains highly statistically significant ($z = -3.50, \mathbf{p = 0.0005}$).
4. **The Code-Switching Deficit (`D_CS`) Requires Power Augmentation:**
   Because $p = 0.0528$ is right at the edge of the 5% alpha threshold under 20-topic clustering, expanding the number of authentic propositions is the single most valuable action to transform this marginal result into an unassailable scientific proof.
