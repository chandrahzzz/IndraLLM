# IndraLLM — Inter-Annotator Agreement & Reliability Protocol

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Adherence Standard:** Artstein & Poesio (2008) Inter-Coder Agreement in NLP  

---

## 1. Selected Reliability Statistics

To prevent superficial agreement reporting, we use three distinct agreement statistics tailored to our specific annotation schema:

### 1.1 Pairwise Agreement: Cohen's $\kappa$
Used for pairwise rater comparisons on binary factual accuracy ($0 = \text{Correct}, 1 = \text{Hallucinated}$):
$$\kappa = \frac{P_o - P_e}{1 - P_e}$$
where $P_o$ is observed agreement and $P_e$ is chance agreement under marginal distributions.

### 1.2 Multi-Rater Nominal Agreement: Fleiss' $\kappa$
Used when 3 independent bilingual raters annotate each item without an absolute 1-to-1 pairing guarantee:
$$\kappa_{\text{Fleiss}} = \frac{\bar{P} - \bar{P}_e}{1 - \bar{P}_e}$$

### 1.3 Ordinal & Incomplete Annotation: Krippendorff's $\alpha$
Used for:
- Ordinal Likert ratings (Code-Switch Naturalness 1–5, Language Fidelity 1–5) using the ordinal difference metric $\delta^2(v_g, v_h)$.
- Robustness against missing ratings or variable annotator workloads.
$$\alpha = 1 - \frac{D_o}{D_e}$$

---

## 2. Pre-Determined Acceptance Thresholds

| Annotation Task | Metric Used | Minimum Acceptable Threshold | Target Publication Standard |
|---|---|---|---|
| **Factual Accuracy (Binary)** | Fleiss' $\kappa$ / Cohen's $\kappa$ | $\kappa \ge 0.70$ | $\kappa \ge 0.80$ |
| **Hallucination Severity (Nominal)** | Fleiss' $\kappa$ | $\kappa \ge 0.65$ | $\kappa \ge 0.75$ |
| **Code-Switch Naturalness (Ordinal)** | Krippendorff's $\alpha_{\text{ordinal}}$ | $\alpha \ge 0.65$ | $\alpha \ge 0.75$ |
| **Language Fidelity (Ordinal)** | Krippendorff's $\alpha_{\text{ordinal}}$ | $\alpha \ge 0.70$ | $\alpha \ge 0.80$ |

---

## 3. Disagreement Resolution & Adjudication Protocol

1. **Majority Voting ($2/3$):** If 2 of 3 annotators agree on the binary factual correctness label, the majority label is adopted for benchmark evaluation.
2. **Senior Adjudicator Escalation ($1/3$ split or severe conflict):**
   - If raters are fundamentally split or report conflicting interpretations of the evidence snippet, the sample is escalated to a Senior Bilingual NLP Researcher.
   - The adjudicator writes a documented resolution note (`adjudication_rationale`) explaining the final verdict.
3. **Disagreement Analysis:** Instances of persistent annotator disagreement will not be deleted or hidden. They will be analyzed in `research/FAILURE_ANALYSIS.md` as "ambiguous or contested factual claims," which is an established finding in human factuality evaluation.
