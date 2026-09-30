# IndraLLM — Phase 4: Workstream 2 — Clustered Power & Precision Analysis
## Effective Sample Size, Design Effect, and True Statistical Power Under Topic Clustering

**Document Version:** 1.0 (Phase 4 Scientific Strengthening)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `69bd848`  
**Primary Source Artifact:** `results/phase4/phase4_statistical_investigation.json`  

---

## 1. Executive Summary

A critical error in NLP benchmark design is computing statistical power assuming prompt observations are mutually independent ($N=500$). When observations are grouped within semantic clusters and shared underlying statutory topics, intra-cluster correlation reduces the **effective sample size ($N_{\text{eff}}$)**.

This workstream computed the exact Design Effect ($\text{DEFF}$), effective sample size, and statistical power curves under true topic clustering.

### Master Statistical Finding:
- **Intra-Class Correlation (ICC):** $\rho = 0.2663$.
- **Design Effect:** $\text{DEFF} = 1 + (m - 1)\rho = 1 + (25 - 1)(0.2663) = \mathbf{7.3912}$.
- **Effective Sample Size:** $N_{\text{eff}} = \frac{N_{\text{total}}}{\text{DEFF}} = \frac{500}{7.3912} = \mathbf{67.6}$ independent factual observations.
- **Current Power at $N=20$ Topics:**
  - Minimum Detectable Effect (MDE) at $80\%$ power: $\mathbf{27.89\%}$.
  - Statistical power for the observed English vs. Code-Switching gap ($\Delta = 21.0\%$): **$55.93\%$**.
  - Statistical power for the observed Dual-Script penalty ($\Delta = 40.0\%$ vs English): **$98.2\%$**.
- **Conclusion:** At $N=20$ topics, the study is fully powered for large script collapse ($> 30\%$), but only moderately powered ($55.9\%$) for subtle representation deficits ($\sim 20\%$). Expanding the authentic core to **$50$ independent statutory propositions** guarantees $> 91.5\%$ power under topic-level clustering.

---

## 2. Mathematical Framework for Clustered Power

For a cluster-randomized or cluster-evaluated design where $N_{\text{topics}}$ clusters each contain $m = 25$ evaluations ($5\text{ languages} \times 5\text{ conditions}$):

1. **Intra-Cluster Correlation ($\rho$):**
   $$\rho = \frac{\sigma^2_{\text{topic}}}{\sigma^2_{\text{topic}} + \sigma^2_{\text{residual}}} = \frac{0.0588}{0.0588 + 0.1619} = \mathbf{0.2663}$$
2. **Design Effect ($\text{DEFF}$):**
   $$\text{DEFF} = 1 + (m - 1)\rho = 1 + (24 \times 0.2663) = \mathbf{7.3912}$$
3. **Effective Sample Size ($N_{\text{eff}}$):**
   $$N_{\text{eff}} = \frac{500}{7.3912} \approx \mathbf{67.6}$$
4. **Minimum Detectable Effect (MDE at $80\%$ Power, $\alpha = 0.05$):**
   $$\text{MDE}_{80\%} = (z_{0.975} + z_{0.80}) \times \sqrt{\frac{2 \cdot p(1 - p) \cdot \text{DEFF}}{N_{\text{prompts}}}}$$

---

## 3. Power Scenarios across Proposition Scale

### Table 1: Statistical Power and MDE Across Number of Independent Statutory Topics
| Number of Independent Topics ($N_{\text{topics}}$) | Total Evaluated Prompts per Model | Minimum Detectable Effect at 80% Power ($\text{MDE}_{80\%}$) | Statistical Power for $\Delta = 15.0\%$ | Statistical Power for $\Delta = 21.0\%$ (Observed $A\_EN - D\_CS$) | Statistical Power for $\Delta = 40.0\%$ (Observed $A\_EN - E\_MIX$) |
|---|---|---|---|---|---|
| **$10$** | $250$ | $39.45\%$ | $18.4\%$ | $32.0\%$ | $81.5\%$ |
| **$20$ (Current EXP-002)** | **$500$** | **$27.89\%$** | **$31.2\%$** | **$55.9\%$** | **$98.2\%$** |
| **$30$** | $750$ | $22.78\%$ | $44.6\%$ | $73.3\%$ | $99.9\%$ |
| **$50$ (Recommended Target)** | **$1,250$** | **$17.64\%$** | **$68.4\%$** | **$91.5\%$** | **$> 99.9\%$** |
| **$75$** | $1,875$ | $14.40\%$ | $83.5\%$ | $98.3\%$ | $> 99.9\%$ |
| **$100$** | $2,500$ | $12.47\%$ | $91.8\%$ | $99.7\%$ | $> 99.9\%$ |

---

## 4. Key Insights for Peer Review

1. **Why $p = 0.0528$ Occurred:**
   Under 20-topic clustering, statistical power for a $21.0\%$ difference is $55.93\%$. With power near $56\%$, observing a borderline $p$-value ($p \approx 0.05$) is the exact expected theoretical outcome of an under-clustered design.
2. **Why Orthographic Disruption Remained $p = 0.0005$:**
   The difference between English and Dual-Script input is $\Delta = 40.0\%$ ($64\%$ vs $24\%$). For a $40\%$ gap, current power under 20-topic clustering is **$98.2\%$**. The orthographic disruption finding is so large that it easily exceeds the MDE ceiling.
3. **The Clear Prescriptive Path Forward:**
   Expanding the authentic benchmark from 20 to 50 independent statutory propositions reduces MDE from $27.9\%$ to $17.6\%$, elevating power for the $21\%$ code-switching gap to **$91.5\%$**.
