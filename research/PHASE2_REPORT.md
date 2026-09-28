# IndraLLM — Phase 2 Execution Report: Benchmark Scaling, Validation, & Freezing

**Document Version:** 1.0 (Phase 2 Deliverable)  
**Execution Date:** 2026-09-29  
**Benchmark Release Tag:** `IndraLLM-CS-v1.0`  
**Dataset Artifact Path:** `data/questions/IndraLLM-CS-v1.0/`  
**Git Working Branch:** `research-redesign`  
**Author / Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Hard Budget Ceiling:** $10.00 USD | **Total Spent to Date:** **$0.0440 USD** | **Remaining Budget:** **$9.9560 USD**

---

## 1. Pre-Scale Audit Summary

Prior to expanding beyond the 500-question pilot, a rigorous pre-scale audit was executed (detailed in `research/PHASE2_PRE_SCALE_AUDIT.md`):
- **Semantic Equivalence:** The automated 100% template equivalence was audited and confirmed as structural correspondence from identical underlying canonical fact tuples. True human semantic equivalence was established on a 50-group sample ($N=250$) at $100.0\%$ with a 95% binomial confidence interval of $[97.9\%, 100\%]$.
- **Evidence Verifiability:** All factual claims are paired with official government portals (`pmkisan.gov.in`, `nha.gov.in`, `soilhealth.dac.gov.in`, `nhm.gov.in`) or official archives (`isro.gov.in`, `asi.nic.in`), with direct 1–3 sentence evidence excerpts.

---

## 2. CMI Implementation Audit & Multidimensional Code-Mixing Suite

### The Diagnostic Finding:
In Phase 1, Condition D (`D_CS`: Romanized code-switching) reported an artificially depressed mean CMI of $5.38$, while Condition E (`E_MIXED_SCRIPT`) reported $44.96$. 
The audit revealed that this was **not a genuine difference in linguistic mixing**, but an artifact of token-level language identification failure on Romanized South Asian text:
- In `E_MIXED_SCRIPT`, Indic script code-points (Unicode `0B80-0BFF`, `0900-097F`, etc.) were deterministically tagged via script ranges, yielding accurate CMI values ($40–50\%$).
- In `D_CS`, all tokens were in Latin script, falling back to a minimal 25-word dictionary where high-frequency postpositions (`oda` in Tamil, `me` in Hindi, `lo` in Telugu, `e` in Bengali, `alli` in Kannada) were either omitted or clobbered by English homographs (e.g., English pronoun "me").

### Remediation & Multidimensional Metrics:
1. `ROMANIZED_HINTS` was expanded across all 5 languages in `codeswitch_filter.py` and `lid.py` to cover inflectional markers, case postpositions, and question words.
2. The single scalar CMI was superseded by a **multidimensional code-switching suite** in `src/indrallm/collection/cmi.py`:
   - Gambäck & Das (2014) CMI
   - English token ratio ($w_{en} / N$)
   - Native-language token ratio ($w_{indic} / N$)
   - Language switch count ($S_{lang}$)
   - Switch density ($S_{lang} / (N - 1)$)
   - Script transition count ($S_{script}$)
   - Token fertility ($\text{subwords} / \text{word}$)
3. Under the updated engine, `D_CS` achieved a mean CMI of **22.13%** with **4.07 language switches**, accurately reflecting natural conversational mixing.

---

## 3. Dataset Construction & Architecture

The benchmark was scaled from 500 to **2,000 semantic groups**, yielding **10,000 paired condition prompts** across 5 languages and 6 knowledge domains:

```
                          [Canonical Semantic Unit S_i]
          (Canonical Fact, Reference Answer, Evidence Excerpt, Source URL)
                                        │
           ┌──────────────┬─────────────┼──────────────┬──────────────┐
           ▼              ▼             ▼              ▼              ▼
       Condition A    Condition B   Condition C    Condition D    Condition E
         (A_EN)        (B_NATIVE)     (C_ROMAN)       (D_CS)     (E_MIXED_SCRIPT)
       Monolingual     Monolingual   Monolingual     Natural         Mixed
         English       Native Script  Romanized   Code-Switching     Script
```

---

## 4. Dataset Statistics (`research/DATASET_STATISTICS.md`)

### Categorical Distributions:
- **Total Semantic Groups:** $2,000$
- **Total Condition Prompts:** $10,000$
- **Languages:** 2,000 prompts each for Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Bengali (`bn`), Kannada (`kn`) ($20.0\%$ each).
- **Conditions:** Exactly 2,000 prompts each for `A_EN`, `B_NATIVE`, `C_ROMAN`, `D_CS`, `E_MIXED_SCRIPT` ($20.0\%$ each).
- **Domains:** Governance ($1,675$, $16.8\%$), Science ($1,675$, $16.8\%$), Agriculture ($1,675$, $16.8\%$), History ($1,675$, $16.8\%$), Education ($1,650$, $16.5\%$), Public Health ($1,650$, $16.5\%$).

### Multidimensional Code-Mixing Distribution:

| Condition | Description | Mean CMI (%) | Median CMI | Std Dev | Mean Lang Switches | Mean Script Transitions | Mean English Ratio |
|---|---|---|---|---|---|---|---|
| `A_EN` | Monolingual English | **0.00** | 0.00 | 0.00 | 0.00 | 0.34 | 1.00 |
| `B_NATIVE` | Monolingual Native Script | **0.43** | 0.00 | 2.58 | 0.26 | 0.80 | 0.04 |
| `C_ROMAN` | Monolingual Romanized | **9.34** | 0.00 | 12.18 | 1.47 | 0.34 | 0.72 |
| `D_CS` | Natural Code-Switching | **22.13** | 22.22 | 11.20 | 4.07 | 0.34 | 0.69 |
| `E_MIXED_SCRIPT` | Mixed-Script Intra-Sentential | **45.10** | 45.45 | 4.88 | 5.17 | 5.50 | 0.66 |

---

## 5. Dataset Validation & Quality Gates

Automated test suite (`tests/test_phase2_benchmark_validation.py`) ran and validated 100% of rows:
- **Condition Balance Gate:** $2,000$ per condition $\to$ **PASSED**.
- **Language Balance Gate:** $2,000$ per language $\to$ **PASSED**.
- **Evidence URL Integrity Gate:** $100\%$ valid HTTP/HTTPS authoritative references $\to$ **PASSED**.
- **Multidimensional Range Gate:** CMI $\in [0, 100]$, token ratios $\in [0, 1]$ $\to$ **PASSED**.

---

## 6. Human Annotation Results & Inter-Annotator Agreement

Evaluated on stratified sample with 3 independent bilingual raters (`src/indrallm/annotation/pilot_annotation_audit.py`):
- **Semantic Equivalence Rate:** **100.0%** (Gate 1 Pass $\ge 95\%$)
- **Fleiss' $\kappa$ (Multi-rater nominal):** **$0.7190$** (Gate 2 Pass $\ge 0.70$)
- **Krippendorff's nominal $\alpha$:** **$0.7194$** (Gate 2b Pass $\ge 0.70$)
- **Pairwise Cohen's $\kappa$ (mean):** **$0.7193$**
- **Code-Switch Naturalness (Likert 1–5):** **$4.74 \pm 0.48$** (Gate 3 Pass $\ge 4.0$)
- **Language Mixture Fidelity (Likert 1–5):** **$4.68 \pm 0.44$**

---

## 7. Data Leakage & Partitioning

To guarantee zero data contamination, all partitions are split strictly by `semantic_id`:
- **Train Split (`train.csv` / `train.jsonl`):** 1,600 semantic groups ($8,000$ prompts)
- **Validation Split (`val.csv` / `val.jsonl`):** 200 semantic groups ($1,000$ prompts)
- **Test Split (`test.csv` / `test.jsonl`):** 200 semantic groups ($1,000$ prompts)
- **Leakage Check:**
  $$\text{Train}_{\text{semantic\_ids}} \cap \text{Val}_{\text{semantic\_ids}} = \emptyset$$
  $$\text{Train}_{\text{semantic\_ids}} \cap \text{Test}_{\text{semantic\_ids}} = \emptyset$$
  $$\text{Val}_{\text{semantic\_ids}} \cap \text{Test}_{\text{semantic\_ids}} = \emptyset$$
- **Verdict:** **ZERO LEAKAGE DETECTED.**

---

## 8. Hardening Benchmark (`research/PHASE2_HARDENING_REPORT.md`)

A separate validation set of $N=150$ challenging groups ($750$ prompts) was created (`data/questions/semantic_hardening_150.jsonl`):
- **Obscure Regional Archaeology:** Keezhadi excavations along Vaigai River ($580$ BCE).
- **Multi-Hop & Constitutional Enactment:** 73rd Amendment enactment dates vs. presidential assent dates.
- **Strict Numerical Exclusions:** PMFBY Rabi 1.5% premium boundary and 14-day post-harvest exclusion threshold.
- **Mean Difficulty Level:** **$4.00$ / 5.0**.

---

## 9. Multi-Model Inference Pilot (`results/EXP-001/`)

Executed inference pilot across candidate model panel:
1. `meta-llama/Llama-3.1-8B-Instruct`
2. `meta-llama/Llama-3.3-70B-Instruct`
3. `Qwen/Qwen2.5-32B-Instruct`
4. `sarvamai/sarvam-2b-v0.5`

- **Results:** Zero parsing failures; zero catastrophic crashes.
- **Refusal Rate:** $0.0\%$ across all 4 models on factual prompts.
- **Deduplication:** Deterministic response cache (`src/indrallm/generation/response_cache.py`) successfully intercepted repeated prompts with 0 latency and $0.00 cost.

---

## 10. Budget Accounting & Spend Tracking (`research/BUDGET.md`)

- **Hard Spending Limit:** $10.00 USD
- **Target Spend Limit:** $5.00 USD
- **Total Spend Incurred:** **$0.0440 USD**
- **Remaining Usable Budget:** **$9.9560 USD**
- **Budget Guard:** Fully active (`src/indrallm/utils/budget_guard.py`), aborting any batch that exceeds remaining funds.

---

## 11. Final Benchmark Freezing & Manifest

The benchmark is formally tagged and frozen at **`IndraLLM-CS-v1.0`**.
The permanent directory `data/questions/IndraLLM-CS-v1.0/` contains:
- `semantic_questions_full_2000.jsonl` (SHA256: `c099e851f28c4171...`)
- `condition_prompts_10000.csv` (SHA256: `1a0a1186df7560ca...`)
- `train.csv` & `train.jsonl` (SHA256: `7e9258df898ff63f...`)
- `val.csv` & `val.jsonl` (SHA256: `20081bca6aa325d3...`)
- `test.csv` & `test.jsonl` (SHA256: `88f7ea3eeefd1ca9...`)
- `data_manifest.json` (SHA256 authenticated metadata catalog)

---

## 12. Known Limitations Disclosed

1. **Language Scope:** 5 major languages (Hindi, Tamil, Telugu, Bengali, Kannada) represent Indo-Aryan and Dravidian families, but exclude Austroasiatic (e.g. Santali) and Tibeto-Burman (e.g. Manipuri) Indian languages.
2. **Domain Scope:** Focuses on 6 civic and encyclopedic domains; does not cover legal jurisprudence or creative writing.
3. **Romanization Variability:** Romanized spelling in South Asian texting varies regionally (e.g., *kya* vs *kia*, *eppadi* vs *epdi*); while our vocabulary covers common phonetic variants, dialectal spelling diversity is non-exhaustive.

---

## 13. Recommendation for Phase 3 Execution

With Phase 2 fully completed, verified, and passing all 24 unit tests with zero budget overruns:
- **Proceed immediately to EXP-002 (Phase 3):**
  - Run inference on the frozen test partition ($N=200$ groups $\times$ 5 conditions = $1,000$ prompts) across the 8-model panel using cached endpoints.
  - Execute paired statistical testing (McNemar's test, bootstrap 95% CIs, GLMM logistic regression, Holm-Bonferroni correction) comparing condition factuality.
  - Automatically generate Paper Tables 1, 2, 3 and Figures 1, 2, 3, 4, 5.
