# IndraLLM — Phase 3.5: Audit 6 — Authentic vs. Synthetic Data Forensic Audit
## Disaggregation of Real-World Statutory Facts vs. Fictitious Scaling Clauses

**Document Version:** 1.0 (Post-Execution Forensic Audit)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `1d4a65c`  

---

## 1. Executive Summary

A critical threat to benchmark credibility identified in Phase 2.7 is **data composition heterogeneity**: `IndraLLM-CS-v1.1-CANDIDATE` contains 475 Authentic Gazette semantic groups and 1,025 Synthetic Scaling groups.

This audit investigated the distribution of authentic vs. synthetic data across the held-out test evaluation splits and conducted a deep qualitative and quantitative audit of model responses on synthetic items.

### Key Forensic Discoveries:
1. **100% Confounding of Partition and Authenticity in Test Splits:**
   - `test_id.csv` ($N = 200$ semantic groups / 1,000 prompts) is **$100.0\%$ Synthetic Scaling Tier**.
   - `test_ood.csv` ($N = 100$ semantic groups / 500 prompts) is **$100.0\%$ Authentic Indian Policy Core**.
   - Consequently, in EXP-002, any comparison between "Test-ID" and "Test-OOD" is identical to comparing "Synthetic Scaling" and "Authentic Core."
2. **The 0% Synthetic Phenomenon is an Epistemic Truthfulness Signal:**
   On the synthetic scaling tier, models scored $\sim 0\%$ not because of catastrophic linguistic failure, but because **the clauses do not exist in real-world Indian law** (e.g. `National Agriculture Framework Clause 241`). In English (`A_EN`), Qwen-27B explicitly denied the existence of the clause in **$99.0\%$ of cases**, which the automated judge marked as "incorrect."
3. **Primary Findings Remain Statistically Robust on Authentic Data:**
   When restricted strictly to authentic Indian statutory acts, the linguistic representation penalty ($A\_EN: 64\% \to D\_CS: 43\% \to E\_MIXED: 24\%$) remains highly statistically significant ($p \le 0.0039$).

---

## 2. Dataset Composition in Held-Out Test Partitions

| Partition Split | File Name | Semantic Groups ($N$) | Prompts per Model | Authenticity Classification | Source Evidence Type | Evaluated Domain |
|---|---|---|---|---|---|---|
| **Test-ID** | `test_id.csv` | **200** | 1,000 | **$100\%$ Synthetic Scaling Tier** | Algorithmic registry generator | Algorithmic clauses (TF-01 to TF-10) |
| **Test-OOD** | `test_ood.csv` | **100** | 500 | **$100\%$ Authentic Policy Core** | Real statutory acts, SEBI, Patents, RTI | Real Indian administrative law (TF-11, TF-12) |
| **Combined** | Both Splits | **300** | 1,500 | **33.3% Authentic / 66.7% Synthetic** | Mixed | Combined benchmark |

---

## 3. Forensic Analysis of the Synthetic Scaling Tier

### Qualitative Response Trace (Prompt: `S001201_A_EN_hi`):
```text
PROMPT: "Under the National Agriculture Framework Clause 241, what is the mandatory benchmark parameter threshold?"
GOLD REFERENCE: "Parameter threshold 2410."
EVIDENCE SNIPPET: "Under the National Agriculture Regulatory Bulletin Clause 241, benchmark standard is set at 2410 units."

QWEN-27B GENERATION:
"There is no such thing as a 'National Agriculture Framework Clause 241' in Indian law or policy.
India does not have a single, unified statute called the 'National Agriculture Framework.' Agricultural policy in India is governed by a combination of:
1. Constitutional Provisions: Agriculture is a State subject under the Seventh Schedule of the Indian Constitution...
2. Central Schemes: PM-KISAN, PMFBY..."

JUDGE VERDICT:
VERDICT: 1 (HALLUCINATED / INCORRECT)
REASON: "Incorrectly denies existence of the specific clause mentioned in the question."
```

### Forensic Diagnosis:
1. **The Model was Factually Right, but Benchmark-Wrong:** In a closed-book parametric setting, `qwen/qwen3.8-27b` correctly determined that no Indian parliamentary act titled "National Agriculture Framework Clause 241" exists.
2. **Language Epistemic Asymmetry:**
   - In English (`A_EN`), the model recognized the fictitious premise and issued a denial in **$99.0\%$** of prompts ($198 / 200$).
   - In Romanized code-switching (`D_CS`), the denial rate dropped to **$2.5\%$** ($5 / 200$).
   - In Native Brahmic script (`B_NATIVE`), the denial rate dropped to **$0.0\%$** ($0 / 200$).
3. **Scientific Implication:** Changing the linguistic representation from English to Indic code-switching impairs the model's **epistemic calibration**, causing it to lose its non-existence rejection threshold and hallucinate plausible-sounding legal jargon.

---

## 4. Authentic Core Performance Separation

Because synthetic items cannot be parametrically recalled without in-context evidence, all primary scientific claims must be grounded in the Authentic Policy Core:

### Table 1: Model Accuracy Disaggregated by Authenticity Tier
| Model | Linguistic Condition | Authentic Policy Core ($N=100$) | Synthetic Scaling Tier ($N=200$) | Full Benchmark ($N=300$) |
|---|---|---|---|---|
| **Qwen-2.5-27B** | `A_EN` (English) | **$64.0\%$** ($64/100$) | **$1.0\%$** ($2/200$) | **$22.00\%$** ($66/300$) |
| | `B_NATIVE` (Brahmic) | **$28.0\%$** ($28/100$) | **$0.0\%$** ($0/200$) | **$9.33\%$** ($28/300$) |
| | `C_ROMAN` (Romanized) | **$33.0\%$** ($33/100$) | **$0.0\%$** ($0/200$) | **$11.00\%$** ($33/300$) |
| | `D_CS` (Code-Switched) | **$43.0\%$** ($43/100$) | **$0.0\%$** ($0/200$) | **$14.33\%$** ($43/300$) |
| | `E_MIXED_SCRIPT` (Dual) | **$24.0\%$** ($24/100$) | **$0.0\%$** ($0/200$) | **$8.00\%$** ($24/300$) |
| **Allam-2-7B** | `A_EN` (English) | **$8.0\%$** ($8/100$) | **$0.0\%$** ($0/200$) | **$2.67\%$** ($8/300$) |
| | `B_NATIVE` (Brahmic) | **$2.0\%$** ($2/100$) | **$0.0\%$** ($0/200$) | **$0.67\%$** ($2/300$) |
| | `C_ROMAN` (Romanized) | **$2.0\%$** ($2/100$) | **$0.0\%$** ($0/200$) | **$0.67\%$** ($2/300$) |
| | `D_CS` (Code-Switched) | **$5.0\%$** ($5/100$) | **$0.0\%$** ($0/200$) | **$1.67\%$** ($5/300$) |
| | `E_MIXED_SCRIPT` (Dual) | **$3.0\%$** ($3/100$) | **$0.0\%$** ($0/200$) | **$1.00\%$** ($3/300$) |

---

## 5. Formal Policy on Reporting Authenticity

1. **Strict Prohibition:** It is strictly prohibited to cite the Full Benchmark accuracy ($12.93\%$) as an indicator of general Indian legal factuality without immediately disclosing that $66.7\%$ of the test items are synthetic non-existent clauses.
2. **Primary Citation Mandate:** In the paper abstract and primary results section, performance must be cited as:
   > *"On the Authentic Indian Policy Core ($N=100$ semantic clusters), factual retrieval accuracy reaches $64.0\%$ in English, but drops to $43.0\%$ under Romanized code-switching ($p = 0.0023$) and $24.0\%$ under mixed-script alternation ($p = 0.0039$). On the synthetic scaling tier, models correctly reject non-existent clauses in English ($99\%$ denial rate) but lose epistemic rejection capabilities under Indic representations."*
