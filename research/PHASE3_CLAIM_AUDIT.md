# IndraLLM — Phase 3.5: Master Claim & Epistemic Boundary Audit
## Post-Forensic Adjudication of Experimental Hypotheses, Boundaries, and Limitations

**Document Version:** 2.0 (Post-Forensic Audit Hardening)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `1d4a65c`  

---

## 1. Executive Claim Audit Framework

Following the Phase 3.5 forensic audit across all 15 audit dimensions, every scientific claim considered for inclusion in manuscripts or dissemination is formally audited and categorized under six epistemic statuses:
- **`SUPPORTED`:** Statistically confirmed with rigorous repeated-measures clustering, multiple testing FWER control, and zero confound vulnerability.
- **`SUPPORTED WITH QUALIFICATION`:** Statistically verified, but restricted to explicitly disclosed population boundaries (e.g. Authentic Policy Core, specific model architectures).
- **`EXPLORATORY`:** Directionally supported by empirical trends, but underpowered to establish formal statistical significance.
- **`UNSUPPORTED`:** Lacks empirical evidence in the recorded data.
- **`CONTRADICTED BY DATA`:** Refuted by empirical observations.
- **`REQUIRES MORE DATA`:** Needs expanded sample collection before drawing scientific conclusions.

---

## 2. Master Claim Adjudication Matrix

### Claim 1: The Linguistic Representation Penalty (Hypothesis H1)
- **Claim:** Holding factual query semantics constant, representing queries in Romanized Code-Switching (`D_CS`) significantly degrades factual retrieval accuracy relative to standard English (`A_EN`).
- **Evidence:** Qwen-27B achieves $64.0\%$ accuracy in English vs. $43.0\%$ in Code-Switching ($\Delta = -21.0\%$).
- **Dataset:** Authentic Policy Core (`test_ood.csv`, $N=100$ semantic groups).
- **Statistical Test:** Paired McNemar $\chi^2 = 9.30, p = 0.002289$, Odds Ratio $= 2.91$. Significant under 10-contrast Holm-Bonferroni ($p < 0.00714$). GEE clustered on `semantic_id`: $\beta = -0.8572, p = 0.0010$.
- **Limitation:** Under ultra-conservative 20-topic cluster aggregation, GEE $p = 0.0528$ (marginal).
- **STATUS:** **`SUPPORTED WITH QUALIFICATION`** (Established on Authentic Core at $N=100$ semantic cluster level).

---

### Claim 2: The Orthographic Disruption Penalty (Hypothesis H3)
- **Claim:** Intra-sentential dual-script alternation (`E_MIXED_SCRIPT`) significantly degrades factual reliability beyond lexical code-switching alone (`D_CS`).
- **Evidence:** Qwen-27B drops from $43.0\%$ in `D_CS` to $24.0\%$ in `E_MIXED_SCRIPT` ($\Delta = -19.0\%$).
- **Dataset:** Authentic Policy Core (`test_ood.csv`, $N=100$ semantic groups).
- **Statistical Test:** Paired McNemar $\chi^2 = 8.31, p = 0.003948$, Odds Ratio $= 2.90$. Significant under 10-contrast Holm-Bonferroni ($p < 0.00833$). GEE clustered on 20 topics: $\beta = -1.7280, p = 0.0005$.
- **Limitation:** Evaluated on Latin-Brahmic script alternations across 5 Indic languages.
- **STATUS:** **`SUPPORTED`** (Survives all clustering levels, multiple-testing corrections, and confound controls).

---

### Claim 3: Representation Dominance over Language (Hypothesis H2 & H4)
- **Claim:** Condition variation explains significantly greater variance in factual reliability than language identity.
- **Evidence:** Condition accuracy spans $24.0\%$ to $64.0\%$ ($\Delta = 40.0\%$), whereas language accuracy ranges narrowly from $35.0\%$ to $44.0\%$ ($\Delta = 9.0\%$).
- **Dataset:** Authentic Policy Core (`test_ood.csv`, $N=100$ semantic groups).
- **Statistical Test:** Clustered Wald Test on language dummies: $\chi^2(4) = 2.41, p = 0.6608$. Clustered condition terms: $p < 0.001$.
- **Limitation:** Statistical power to detect subtle language differences ($\Delta = 5\%$) is limited ($24.8\%$). Non-significance cannot be claimed as proof of cross-lingual identity.
- **STATUS:** **`SUPPORTED WITH QUALIFICATION`** (Condition dominance confirmed; language invariance bounded to lack of detected difference at MDE $= 21.4\%$).

---

### Claim 4: Subword Token Fragmentation Mechanism
- **Claim:** Script alternation and native Brahmic representation impair factual retrieval by shattering BPE subword merges and inflating token fertility.
- **Evidence:** Characters-per-token drops from $1.57$ (English) to $1.10$ (Code-Switching), $0.91$ (Dual-Script), and $0.69$ (Native Brahmic). Native script requires $2.28\times$ more tokens for the same length. Script transitions average $5.1$ per prompt in Dual-Script.
- **Dataset:** Authentic Policy Core ($N=500$ prompt tokenizations).
- **Statistical Test:** Token fertility and script transition counts correlated with prompt fragmentation ($r = 0.78$).
- **Limitation:** Observed on Qwen-2.5 byte-level BPE tokenizer.
- **STATUS:** **`SUPPORTED`**.

---

### Claim 5: Evaluator Bias Conservatism
- **Claim:** Automated factual judges exhibit a $+10\%$ false-positive rate on code-switched answers, causing raw evaluator metrics to underestimate the true representation penalty.
- **Evidence:** Rogan-Gladen bias adjustment widens the English vs. Code-Switching gap from $21.0\%$ (raw) to $26.24\%$ (calibrated), and the Dual-Script gap from $19.0\%$ (raw) to $25.67\%$ (calibrated).
- **Dataset:** Authentic Policy Core calibrated against $N=150$ human gold annotations.
- **Statistical Test:** Rogan-Gladen epidemiological prevalence adjustment with Delta-method SE propagation.
- **Limitation:** Requires $P_{\text{obs}} > \text{FPR}$; invalid on zero-accuracy synthetic data.
- **STATUS:** **`SUPPORTED`**.

---

### Claim 6: Cross-Model Universality across All LLMs
- **Claim:** All large language models universally exhibit identical representation failure in code-switched environments.
- **Evidence:** Qwen-27B demonstrates robust condition degradation. Allam-7B replicates directional condition ranking ($8\% \to 5\% \to 3\% \to 2\%$), but suffers from an acute floor effect ($4.0\%$ overall).
- **Dataset:** EXP-002 model panel (2 models).
- **Statistical Test:** Model interaction test non-significant, but Allam-7B is compressed near zero.
- **Limitation:** Only two open-weight models evaluated.
- **STATUS:** **`CONTRADICTED BY DATA / OVER-GENERALIZATION`** (Must be restricted to *"the evaluated open-weight models"*).

---

### Claim 7: Broad Out-of-Distribution Generalization
- **Claim:** IndraLLM proves broad open-world out-of-distribution reasoning across all Indian domains.
- **Evidence:** Test-OOD tests two structural task schemas: Cross-Entity Comparison (`TF-11`) and Conditional Thresholds (`TF-12`), all restricted to Indian administrative law.
- **Dataset:** `test_ood.csv` ($N=100$ semantic groups).
- **Statistical Test:** Performance in TF-11 ($42.0\%$) and TF-12 ($34.8\%$).
- **Limitation:** Domain is strictly statutory law; task structures are exactly two schemas.
- **STATUS:** **`UNSUPPORTED AS BROAD CLAIM; SUPPORTED AS STRUCTURAL SCHEMA GENERALIZATION`**.

---

### Claim 8: Human-Validated Candidate Benchmark
- **Claim:** The 1,500-group candidate benchmark is human-validated.
- **Evidence:** Pilot benchmark ($N=150$) received human validation ($\kappa = 0.719$), but the expanded candidate pool ($N=1,500$) received $0$ new human annotations.
- **Dataset:** Candidate benchmark v1.1.
- **Statistical Test:** N/A (Computational verification gates only).
- **Limitation:** Candidate benchmark pool is computationally verified.
- **STATUS:** **`CONTRADICTED BY DATA / FALSE ATTRIBUTION`** (Strictly disallowed; must declare pilot human validation vs candidate computational verification).

---

## 3. Summary of Binding Scientific Boundaries

| Topic | Disallowed Over-Claim | Authorized Empirical Fact |
|---|---|---|
| **Primary Effect** | "Code-switching destroys all LLM reasoning." | "Code-switching degrades factual retrieval by $21.0\%$ ($26.2\%$ adjusted) on authentic Indian statutory law." |
| **Orthography** | "Scripts don't matter, only tokens do." | "Dual-script alternation incurs an additional $19.0\%$ factual penalty ($p = 0.0039$) due to script-boundary subword shattering." |
| **Model Scope** | "Universal across all LLMs." | "Established on Qwen-2.5-27B; replicated in directional ranking on Allam-2-7B." |
| **OOD Scope** | "Broad domain OOD generalization." | "Held-out structural schema generalization across relational comparisons and statutory thresholds." |
| **Benchmark Composition** | "1,500 authentic Indian legal facts." | "475 Authentic Gazette groups (evaluated on Test-OOD) and 1,025 Synthetic Scaling groups (evaluated on Test-ID)." |
| **Validation** | "Human-validated 1,500-item benchmark." | "Generation rules calibrated on $N=150$ human pilot ($\kappa = 0.719$); candidate expanded pool computationally verified." |
