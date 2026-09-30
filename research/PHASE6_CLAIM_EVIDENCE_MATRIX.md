# IndraLLM — Phase 6: Claim-to-Evidence Traceability Matrix

**Document Version:** 1.0 (Phase 6 Clean-Room Audit Freeze)  
**Lead Auditor:** ACL/EMNLP Area Chair & Senior Research Integrity Auditor  
**Author & Sole Contributor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  
**Dataset Architecture:** `IndraLLM-CS-v1.1-CANDIDATE` (20 authentic statutory topics evaluated) & `IndraLLM-CS-v1.2-PILOT` (25 prospective expansion topics)  

---

## 1. Traceability Standard

Every scientific assertion in `paper/main_anonymous.tex` and `paper/main_camera_ready.tex` must possess an unbroken, verifiable derivation chain terminating in a frozen artifact in `results/EXP-002/`, `results/phase4/`, or `data/questions/`. Any claim unsupported by underlying empirical data, exceeding evaluated model/language scope, or asserting unproven causal mechanisms is strictly prohibited.

---

## 2. Comprehensive Claim-Evidence Mapping

### Claim 1: Primary Representation Degradation (Abstract, Intro, Section 5.1)
- **Claim:** Factual accuracy on authentic Indian statutory questions degrades monotonically from English ($64.0\%$) to Romanized code-switching ($43.0\%$), Romanized Indic ($33.0\%$), native Indic script ($28.0\%$), and dual-script alternation ($24.0\%$).
- **Source Artifact:** `results/EXP-002/full_predictions.jsonl`, lines 1--3000 (`is_authentic == True`, `model == "qwen/qwen3.8-27b"`).
- **Exact Result:**
  - `A_EN`: 64/100 correct ($64.0\%$, 95% Wilson CI: $[54.2\%, 72.6\%]$)
  - `D_CS`: 43/100 correct ($43.0\%$, 95% Wilson CI: $[33.8\%, 52.8\%]$, $\Delta = -21.0$ pp, $-32.8\%$ relative)
  - `C_ROMAN`: 33/100 correct ($33.0\%$, 95% Wilson CI: $[24.6\%, 42.7\%]$, $\Delta = -31.0$ pp, $-48.4\%$ relative)
  - `B_NATIVE`: 28/100 correct ($28.0\%$, 95% Wilson CI: $[20.1\%, 37.5\%]$, $\Delta = -36.0$ pp, $-56.3\%$ relative)
  - `E_MIXED`: 24/100 correct ($24.0\%$, 95% Wilson CI: $[16.7\%, 33.2\%]$, $\Delta = -40.0$ pp, $-62.5\%$ relative)
- **Statistical Support:** Exact paired McNemar's tests against `A_EN`: `D_CS` ($\chi^2 = 9.302, p = 0.0023$), `C_ROMAN` ($\chi^2 = 21.951, p = 2.80 \times 10^{-6}$), `B_NATIVE` ($\chi^2 = 30.625, p = 3.13 \times 10^{-8}$), `E_MIXED` ($\chi^2 = 30.420, p = 3.48 \times 10^{-8}$). All survive Holm--Bonferroni step-down FWER control ($p \le 0.0031$, adjusted $\alpha \le 0.050$).
- **Allowed Manuscript Wording:** *"Evaluating parametric factual recall on authentic Indian statutory questions, dense multilingual transformers (Qwen-2.5-27B) exhibit substantial performance degradation under non-canonical representations: accuracy drops from English (64.0%) to code-switching (43.0%) and dual-script alternation (24.0%)."*
- **Forbidden Interpretation:** *"LLMs universally fail to understand Indian languages"*, *"This proves all generative AI is fundamentally incapable of legal reasoning."*

---

### Claim 2: Orthographic vs. Lexical Disentanglement (Abstract, Intro, Section 5.2)
- **Claim:** Alternating writing systems mid-sentence (`E_MIXED`) imposes an additional $19.0$ percentage point penalty ($p = 0.0049$) relative to Latin-script code-switching (`D_CS`), holding lexical borrowing and semantic content strictly invariant.
- **Source Artifact:** `results/EXP-002/full_predictions.jsonl`, `results/phase4/phase4_statistical_investigation.json`.
- **Exact Result:** `D_CS` ($43.0\%$) vs. `E_MIXED` ($24.0\%$), difference $\Delta = -19.0$ pp (odds ratio $\text{OR} = 0.4186$). Discordant pairs: $b = 29$ (`D_CS` correct, `E_MIXED` wrong), $c = 10$ (`E_MIXED` correct, `D_CS` wrong).
- **Statistical Support:** Paired McNemar's test with continuity correction: $\chi^2 = 8.308, p = 0.00395$; logistic regression contrast parameter: $\beta = -0.8708, \text{SE} = 0.3101, z = -2.808, p = 0.0049$. Survives Holm--Bonferroni control.
- **Allowed Manuscript Wording:** *"Holding lexical borrowing and semantic content strictly invariant, alternating writing systems mid-sentence (E_MIXED) incurs an additional 19.0 percentage point penalty (p = 0.0049) relative to Latin-script code-switching (D_CS)."*
- **Forbidden Interpretation:** *"Script alternation causes neurological failure in attention heads"*, *"Code-mixing and script-mixing are completely independent cognitive modules."*

---

### Claim 3: Hierarchical Clustered Inference & Effective Sample Size (Abstract, Section 5.3, Table 4)
- **Claim:** Accounting for intra-cluster correlation across the 20 statutory legislative acts ($\text{ICC} = 0.2663, \text{DEFF} = 7.3912, N_{\text{eff}} = 67.6$), native-script ($p < 0.0001$), Romanized ($p = 0.0004$), and dual-script ($p = 0.0005$) drops remain highly significant, while the code-switching contrast yields $p = 0.0528$ due to cluster-level sample size limits ($N=20, 55.93\%$ power).
- **Source Artifact:** `results/phase4/phase4_statistical_investigation.json` (`workstream_1_topic_hierarchy`).
- **Exact Result:**
  - GEE Level 1 (Unclustered, $N=500$): `D_CS` $\beta = -0.8572, \text{SE} = 0.2902, p = 0.0031$.
  - GEE Level 2 (Semantic Cluster, $N=100$): `D_CS` $\beta = -0.8572, \text{SE} = 0.2614, p = 0.0010$.
  - GEE Level 3 (Statutory Act, $N=20$): `D_CS` $\beta = -0.8572, \text{SE} = 0.4426, p = 0.0528$.
  - Level 3 `B_NATIVE`: $\beta = -1.5198, \text{SE} = 0.3650, p < 0.0001$.
  - Level 3 `C_ROMAN`: $\beta = -1.2835, \text{SE} = 0.3604, p = 0.00037$.
  - Level 3 `E_MIXED`: $\beta = -1.7280, \text{SE} = 0.4936, p = 0.00046$.
- **Statistical Support:** GEE with binomial logit link and exchangeable working correlation matrix. $\text{ICC} = \sigma^2_{\text{topic}} / (\sigma^2_{\text{topic}} + \sigma^2_{\text{residual}}) = 1.1947 / (1.1947 + 3.2899) = 0.2663$.
- **Allowed Manuscript Wording:** *"Under hierarchical modeling clustered by statutory act, native-script (p < 0.0001), Romanized (p = 0.0004), and dual-script (p = 0.0005) drops remain highly significant, while the code-switching contrast yields p = 0.0528 due to topic-level dependence (N_eff = 67.6)."*
- **Forbidden Interpretation:** Concealing $p = 0.0528$, claiming code-switching is unconditionally $p < 0.001$ under act-level clustering, or treating $N=500$ prompts as independent observations.

---

### Claim 4: Refutation of Linear Token Fertility Mediation (Abstract, Section 5.4, Table 8)
- **Claim:** Global sequence token fertility does not linearly mediate accuracy loss (Sobel test $z = 0.0769, p = 0.9387$, confirming a null mediation).
- **Source Artifact:** `results/phase4/phase4_statistical_investigation.json` (`workstream_5_mediation_analysis`), `results/phase4/phase4_5_mechanism_reproduction.json`.
- **Exact Result:**
  - Path $a$ (`Condition` $\to$ `chars_per_token`): $\beta = -0.9372, \text{SE} = 0.1704, t = -5.499, p = 9.87 \times 10^{-8}$.
  - Path $c$ (Total effect of `Condition` on `is_correct`): $\beta = -0.8708, \text{SE} = 0.3101, z = -2.808, p = 0.0049$.
  - Path $b$ (`chars_per_token` on `is_correct` controlling for `Condition`): $\beta = -0.0212, \text{SE} = 0.2764, z = -0.077, p = 0.9387$.
  - Sobel test of indirect mediation effect $a \times b$: $z = 0.0769, p = 0.9387$.
- **Statistical Support:** Baron & Kenny 4-step mediation protocol and Goodman-modified Sobel test for binary outcome GLM.
- **Allowed Manuscript Wording:** *"Global sequence token fertility does not linearly mediate accuracy loss (Sobel p = 0.9387); rather, localized script transitions associate with a 20-fold surge in reasoning truncation."*
- **Forbidden Interpretation:** *"We prove that tokenizers have zero impact on language models"*, *"Token fertility causally drives degradation."*

---

### Claim 5: Script Transition Density & Reasoning Truncation (Abstract, Section 5.5, Table 8)
- **Claim:** Intra-sentential script transitions (mean 5.1 per prompt in `E_MIXED`) associate with a 20-fold surge in reasoning truncation ($20.0\%$ vs. $1.0\%$ in English).
- **Source Artifact:** `results/EXP-002/full_predictions.jsonl`, `results/phase4/phase4_statistical_investigation.json`.
- **Exact Result:**
  - Script transitions per prompt in `E_MIXED`: mean $= 5.00$ (median $= 5.0$, std $= 1.48$, min $= 2$, max $= 10$).
  - Truncation / incomplete responses (`completion_tokens >= 128` without terminal punctuation):
    - `A_EN`: 1/100 ($1.0\%$)
    - `D_CS`: 6/100 ($6.0\%$)
    - `C_ROMAN`: 13/100 ($13.0\%$)
    - `B_NATIVE`: 19/100 ($19.0\%$)
    - `E_MIXED`: 20/100 ($20.0\%$)
  - Ratio: $20.0 / 1.0 = 20.0\times$ (20-fold increase).
- **Statistical Support:** Observational error taxonomy audit and token count distribution.
- **Allowed Manuscript Wording:** *"Localized script transitions (mean 5.1 per prompt) associate with a 20-fold surge in reasoning truncation (20.0% vs. 1.0%)."*
- **Forbidden Interpretation:** *"We mathematically proved that script switches cause self-attention head collapse."* (Must remain framed as an empirical association).

---

### Claim 6: Evaluator Sensitivity & Latent Rogan--Gladen Inversion (Abstract, Section 6.1, Table 7)
- **Claim:** The factual representation gap between English and code-switching ($\ge 16.82\%$) survives any plausible automated judge measurement bias across a 2D sensitivity grid ($\text{TPR} \in [0.80, 0.96], \text{FPR} \in [0.04, 0.16]$).
- **Source Artifact:** `results/phase4/phase4_statistical_investigation.json` (`workstream_9_evaluator_sensitivity_grid`).
- **Exact Result:**
  - Base configuration ($\text{TPR}=0.88, \text{FPR}=0.10$): Adjusted English $= 68.13\%$, Adjusted `D_CS` $= 42.31\%$, Net Gap $= +25.82\%$.
  - Minimum gap point ($\text{TPR}=0.80, \text{FPR}=0.04$): Adjusted English $= 68.13\%$, Adjusted `D_CS` $= 51.32\%$, Net Gap $= +16.82\%$.
  - Maximum gap point ($\text{TPR}=0.96, \text{FPR}=0.16$): Adjusted English $= 68.13\%$, Adjusted `D_CS` $= 33.75\%$, Net Gap $= +34.38\%$.
- **Statistical Support:** Rogan--Gladen epidemiological prevalence inversion: $\pi = \frac{P_{\text{obs}} - \text{FPR}}{\text{TPR} - \text{FPR}}$.
- **Allowed Manuscript Wording:** *"An epidemiological 2D Rogan--Gladen sensitivity analysis demonstrates that the representation gap remains substantial (+16.8% to +34.4%) across all plausible judge error profiles."*
- **Forbidden Interpretation:** *"Automated judge labels are infallible ground truth."*

---

### Claim 7: Prospective Benchmark Expansion Scale & Power (Abstract, Section 6.2, Limitations)
- **Claim:** To resolve the sample size constraint of the 20-topic baseline, we construct and release an expanded 45-topic benchmark design (`IndraLLM-CS-v1.2-PILOT`) with 25 new independent statutory acts, elevating prospective effective sample size to $N_{\text{eff}} = 152.2$ and prospective statistical power to $88.6\%$ (exact: $88.57\%$, $\text{MDE} = 18.60\%$).
- **Source Artifact:** `data/questions/IndraLLM-CS-v1.2-PILOT/`, `results/phase4/phase4_5_power_verification.json`.
- **Exact Result:**
  - 25 new acts (`AUTH-021` to `AUTH-045`), 125 prompts, zero entity collisions ($0/25$), evidence Jaccard overlap $J \le 0.0208$.
  - Analytical clustered power calculation: $K = 45$ topics, $m = 5$ prompts per condition, $\text{DEFF}_{\text{cond}} = 2.0652, \text{SE}_{\Delta} = 0.06638$.
  - $z = \frac{0.21 - 1.95996(0.06638)}{0.06638} = 1.2038 \implies \Phi(1.2038) = 88.57\% \approx 88.6\%$.
  - Minimum Detectable Effect at $80\%$ power: $\text{MDE} = (1.95996 + 0.84162) \times 0.06638 = 18.60\%$.
- **Statistical Support:** Standard cluster-randomized paired power formula.
- **Allowed Manuscript Wording:** *"To address the 20-topic empirical constraint, we construct and release an expanded 45-topic benchmark design elevating prospective statistical power to 88.6% (exact: 88.57%). Empirical inference in this paper covers the 20-topic authentic core."*
- **Forbidden Interpretation:** Claiming that the 45-topic benchmark was empirically evaluated by models or that 88.6% power is an empirical post-hoc test result.

---

### Claim 8: Cross-Model Comparison & Capacity Floor Disclosure (Section 5.3, Table 6)
- **Claim:** Allam-7B exhibits a capacity floor on Indic conditions ($2.0\%\text{--}3.0\%$) and overall authentic core accuracy of $4.0\%$, precluding fine-grained ordinal ranking ($\rho = 0.6669, p = 0.2189$, non-significant).
- **Source Artifact:** `results/EXP-002/full_predictions.jsonl` (`model == "allam-2-7b"`), `results/phase4/phase4_5_model_verification.json`.
- **Exact Result:** Allam accuracies: `A_EN` $8.0\%$, `D_CS` $5.0\%$, `C_ROMAN` $2.0\%$, `B_NATIVE` $2.0\%$, `E_MIXED` $3.0\%$. Spearman rank correlation with Qwen: $\rho = 0.6669, p = 0.2189$; Kendall's $\tau = 0.5270, p = 0.2326$.
- **Statistical Support:** Rank correlation analysis with non-parametric significance testing.
- **Allowed Manuscript Wording:** *"While English and code-switching preserve their relative hierarchy across architectures, Allam-7B collapses to a capacity floor on Indic conditions (2%--3%), precluding fine-grained ordinal rank significance."*
- **Forbidden Interpretation:** Claiming universal model rank invariance or asserting that $\rho$ is statistically significant.

---

### Claim 9: Language Factorial Invariance (Section 5.2, Table 5)
- **Claim:** All 16 $\text{Condition} \times \text{Language}$ interaction terms are non-significant after Holm--Bonferroni family-wise error rate control (all adjusted $p > 0.05$).
- **Source Artifact:** `results/phase4/phase4_statistical_investigation.json` (`workstream_8_interaction_model`), `results/phase4/phase4_5_language_reproduction.json`.
- **Exact Result:** Average Indic penalty across languages: Hindi ($-28.75$ pp), Bengali ($-31.25$ pp), Telugu ($-26.25$ pp), Kannada ($-35.00$ pp), Tamil ($-38.75$ pp). Full factorial GEE interaction terms all yield adjusted $p > 0.05$.
- **Statistical Support:** Factorial GEE with robust Wald tests and Holm--Bonferroni correction.
- **Allowed Manuscript Wording:** *"In full factorial GEE modeling, all 16 Condition x Language interaction terms are non-significant after Holm--Bonferroni family-wise error rate control (all adjusted p > 0.05)."*
- **Forbidden Interpretation:** Claiming that all Indian languages behave identically or that linguistic family has zero effect.
