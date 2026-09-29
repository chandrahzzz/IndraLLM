# Dataset Partition Protocol: Decontamination & Split Isolation

**Document Version:** 1.0 (Frozen Specification)  
**Target Specification:** Part 7, 8, 9 & 10 Partition Hardening  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. The Pre-Partitioning Mandate

In standard machine learning, random train-test splitting post-hoc is acceptable only when all rows represent independent observations. In a **repeated-measures 5-condition linguistic benchmark**, post-hoc random splitting destroys scientific validity by scattering conditions of the same question across partitions.

### The Immutable Rule
**All partition assignments are executed strictly at the `semantic_id` level before generating condition prompts.**

---

## 2. Partition Architecture ($N = 1,500$ Semantic Groups)

The 1,500 semantic units are partitioned into four disjoint sets:

| Partition | Semantic Groups ($N$) | Prompts ($N \times 5$) | Template Families | Target Purpose | Leakage Constraints |
|---|---|---|---|---|---|
| **DEVELOPMENT** | 1,000 | 5,000 | `TF-01` to `TF-10` | Model training, few-shot prompting, exploratory error analysis | Training baseline |
| **VALIDATION** | 200 | 1,000 | `TF-01` to `TF-10` | Hyperparameter selection, prompt template iteration, detector threshold calibration | Disjoint semantic units from Dev; 0% prompt overlap |
| **TEST-ID** | 200 | 1,000 | `TF-01` to `TF-10` | Primary in-distribution evaluation of linguistic representation effect | Disjoint semantic units; 0% prompt/answer overlap; controlled entity overlap |
| **TEST-OOD** | 100 | 500 | `TF-11` & `TF-12` | Evaluating structural & reasoning robustness to unseen task frames | Completely unseen template families; 0% template overlap with Dev/Val/Test-ID |

---

## 3. Disjointness Guarantees Across Partitions

Let $\mathcal{P} \in \{\text{Dev}, \text{Val}, \text{Test-ID}, \text{Test-OOD}\}$:

1. **Semantic Identifier Disjointness:**
   $$\forall \mathcal{P}_a \neq \mathcal{P}_b, \quad \text{IDs}(\mathcal{P}_a) \cap \text{IDs}(\mathcal{P}_b) = \emptyset$$
2. **Prompt-Text Disjointness (Level 1 Leakage Elimination):**
   $$\forall \mathcal{P}_a \neq \mathcal{P}_b, \quad \text{Prompts}(\mathcal{P}_a) \cap \text{Prompts}(\mathcal{P}_b) = \emptyset$$
3. **Factual Question Disjointness (Level 2 Leakage Elimination):**
   $$\forall \mathcal{P}_a \neq \mathcal{P}_b, \quad \text{Questions}(\mathcal{P}_a) \cap \text{Questions}(\mathcal{P}_b) = \emptyset$$
4. **Reference Answer Disjointness (Level 3 Leakage Elimination):**
   $$\forall \mathcal{P}_a \neq \mathcal{P}_b, \quad \text{Answers}(\mathcal{P}_a) \cap \text{Answers}(\mathcal{P}_b) = \emptyset$$
5. **Template Family Quarantining (Level 6 OOD Separation):**
   $$\text{TF}(\text{Dev} \cup \text{Val} \cup \text{Test-ID}) \cap \{\text{TF-11}, \text{TF-12}\} = \emptyset$$
   $$\text{TF}(\text{Test-OOD}) \subseteq \{\text{TF-11}, \text{TF-12}\}$$

---

## 4. Entity Leakage & Evidence Policy

### Entity Identity vs. Entity-Relation Leakage
- **Entity Identity Overlap:** Certain high-level national entities (e.g. "India", "Reserve Bank of India", "Supreme Court") will naturally appear across partitions in public-domain benchmarks. Forbidding all entity names would artificially distort realistic language.
- **Relational Overlap Policy:** What is strictly prohibited is **Entity-Pair Relational Leakage**. If `DEVELOPMENT` asks about the relation $(E_1, R_1, E_2)$ (e.g., *PM-KISAN $\to$ provides $\to$ ₹6,000*), neither `TEST-ID` nor `TEST-OOD` may evaluate a query dependent on the same factual relation $(E_1, R_1, E_2)$.
- **Critical Entity-Pair Overlap Limit:** Measured and verified $\le 5\%$ for `TEST-ID`, and strictly $0.0\%$ for `TEST-OOD`.
