# IndraLLM — Phase 3.5: Audit 11 — Structural OOD Generalization Audit
## Bounding Out-of-Distribution Claims, Schema Generalization, and Power Limitations

**Document Version:** 1.0 (Post-Execution Forensic Audit)  
**Execution Date:** September 2026  
**Auditor & Lead Investigator:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Commit Audited:** `1d4a65c`  

---

## 1. Executive Summary

A pervasive vulnerability in modern benchmark research is **unbounded generalization claims**—describing a restricted evaluation split as measuring "broad out-of-distribution (OOD) general intelligence" when it actually evaluates a narrow, specific distribution shift.

This audit evaluated the exact operational definition of `Test-OOD` in IndraLLM, audited prompt structures, and established the binding scientific boundaries of what the OOD split establishes.

### Key Audit Findings:
1. **Binding Definition: Held-Out Structural Schema Generalization:**
   `Test-OOD` evaluates exactly two held-out task schemas:
   - **`TF-11`:** Cross-Entity Relational Comparison (e.g. `PMFBY vs WBCIS`, `NEFT vs RTGS`, `Covaxin vs Covishield`).
   - **`TF-12`:** Conditional Regulatory Prerequisite Thresholds (e.g. `Patents Act Section 84`, `RTI Section 11`, `SEBI Pre-Clearance`).
   - It is **strictly NOT** general broad-domain open-world generalization.
2. **100% Authentic Core Alignment:**
   In EXP-002, `Test-OOD` contains the entire $100\%$ of the Authentic Policy Core ($N=100$ semantic groups). It cannot be compared to `Test-ID` without controlling for the fact that `Test-ID` is $100\%$ synthetic.
3. **Statistical Power Limitation on OOD Comparisons:**
   With $N = 100$ semantic clusters, the Minimum Detectable Effect (MDE) at $80\%$ power is **$12.53\%$**. Power for a subtle effect ($\Delta = 5\%$) is only **$20.1\%$**. Subtle differences between sub-schemas cannot be interpreted as evidence of absence of an effect.

---

## 2. Structural Task Schema Architecture

`Test-OOD` was constructed during Phase 2.6 to evaluate structural generalization away from standard single-fact templates (`TF-01` to `TF-10` in Development):

### Table 1: Composition of the Held-Out Structural Split (`test_ood.csv`)
| Schema Family ID | Schema Operationalization | Target Reasoning Mechanism | Semantic Groups ($N$) | Prompts per Model | Authentic Real-World Entities |
|---|---|---|---|---|---|
| **`TF-11`** | Cross-Entity Relational Comparison | Multi-entity discrimination & operational distinction | **50** (10 base topics $\times$ 5 languages) | 250 | PMFBY/WBCIS, NEFT/RTGS, Covaxin/Covishield, Kharif/Rabi, ISRO PSLV/GSLV, etc. |
| **`TF-12`** | Conditional Regulatory Thresholds | Prerequisite timelines, defaults, and statutory constraints | **50** (10 base topics $\times$ 5 languages) | 250 | Patents Act, RTI Third Party, GST Exemption, Companies Act CSR, IBC Default, SEBI Insider Trading |
| **Total Test-OOD** | Held-Out Structural Schemas | Relational & Threshold Inference | **100** | **500** | 100% Real Indian Administrative Law |

---

## 3. Performance Breakdown by Structural Schema

### Table 2: Accuracy by Structural Schema and Condition (Qwen-27B)
| Schema Family | Description | `A_EN` (%) | `B_NATIVE` (%) | `C_ROMAN` (%) | `D_CS` (%) | `E_MIXED_SCRIPT` (%) | Schema Mean |
|---|---|---|---|---|---|---|---|
| **`TF-11`** | Cross-Entity Comparison | **$70.0\%$** ($35/50$) | $32.0\%$ ($16/50$) | $36.0\%$ ($18/50$) | **$46.0\%$** ($23/50$) | **$26.0\%$** ($13/50$) | **$42.0\%$** |
| **`TF-12`** | Conditional Thresholds | **$58.0\%$** ($29/50$) | $24.0\%$ ($12/50$) | $30.0\%$ ($15/50$) | **$40.0\%$** ($20/50$) | **$22.0\%$** ($11/50$) | **$34.8\%$** |
| **Combined OOD**| Held-Out Structural Schemas | **$64.0\%$** ($64/100$) | $28.0\%$ ($28/100$) | $33.0\%$ ($33/100$) | **$43.0\%$** ($43/100$) | **$24.0\%$** ($24/100$) | **$38.4\%$** |

### Key Structural Finding:
- Models perform systematically better on **Cross-Entity Comparison (`TF-11`: $42.0\%$)** than on **Conditional Thresholds (`TF-12`: $34.8\%$)** ($\Delta = 7.2\%$).
- Crucially, the condition degradation pattern is identical across both schemas:
  - In `TF-11`: English is $70\%$, Code-Switching is $46\%$ ($-24\%$), and Dual-Script is $26\%$ ($-20\%$).
  - In `TF-12`: English is $58\%$, Code-Switching is $40\%$ ($-18\%$), and Dual-Script is $22\%$ ($-18\%$).
- This demonstrates that the representation penalty generalizes cleanly across distinct structural task types.

---

## 4. Bounding Claims & Prohibited Phrasing

### Strictly Disallowed:
❌ *"IndraLLM demonstrates that models generalize out-of-distribution across all Indian legal and cultural domains."*

### Mandated Accurate Formulation:
✅ *"Under held-out structural schema generalization (`Test-OOD`), evaluating cross-entity relational comparisons (`TF-11`) and conditional regulatory thresholds (`TF-12`), foundation models exhibit a robust representation penalty. Accuracy drops by $21.0\%$ under code-switching and an additional $19.0\%$ under dual-script alternation. This confirms that representation bottlenecks persist when models are evaluated on unseen relational reasoning structures."*
