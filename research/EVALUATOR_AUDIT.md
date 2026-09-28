# Automated Evaluator Audit & Factuality Labeling Protocol

**Document Version:** 1.0 (Frozen for Phase 2.5)  
**Target Specification:** Part 11 Research Integrity Audit  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Epistemological Grounding: Ground Truth vs. Automated Evaluator

A core vulnerability in contemporary LLM hallucination benchmarks is conflating an LLM-based judge with ground truth. In IndraLLM, we enforce strict epistemological boundaries:

- **Ground Truth:** Derived strictly from verified reference documents (`reference_answer`, `evidence_snippet`, verified `evidence_source_url` from Wikipedia, PubMed, NCERT, RBI, PIB, and OpenStax) audited by human domain experts.
- **Automated Evaluator:** A secondary inference system (specifically, a frozen instruction-tuned frontier judge or high-capacity model) that compares a model's generated output against the ground truth evidence.
- **Human Calibration Set:** A stratified native-speaker human verification panel used to audit, calibrate, and report the precision, recall, and error rates of the automated evaluator.

Under no circumstances will automated evaluator scores be reported as "human ground truth."

---

## 2. Five-Way Labeling Rubric & Decision Rule

Every model response $Y$ generated for prompt $X$ with reference answer $A^*$ and evidence $E$ receives a primary categorical outcome:

$$\text{Label} \in \{\text{FACTUAL}, \text{HALLUCINATED}, \text{PARTIALLY\_CORRECT}, \text{INCORRECT}, \text{REFUSAL}\}$$

### Explicit Definitions
1. **`FACTUAL` (0):**
   - The response directly addresses the question and all substantive factual assertions are verified by, or fully consistent with, the reference evidence $E$.
   - Minor stylistic, linguistic, or conversational remarks do not disqualify the response.
2. **`HALLUCINATED` (1 - Primary Outcome of Interest):**
   - The response contains one or more factual claims that are directly contradicted by the evidence $E$, or fabricates entities, numbers, causal mechanisms, historical events, or scientific facts not grounded in reality.
3. **`PARTIALLY_CORRECT` (2):**
   - The response contains at least one core factual claim that is true and verified, but also includes unverified, inaccurate, or omitted crucial details without direct fabrication of primary entities.
4. **`INCORRECT` (3):**
   - The response is completely wrong or answers a different question, but is a clear misconception or error rather than fluent fabricated pseudo-facts.
5. **`REFUSAL` (4):**
   - The model explicitly declines to answer (e.g., *"I cannot assist with this request"*, *"As an AI..."*, *"Nenu ee prashnaku samadhanam cheppalenu"*), or returns an empty/whitespace string.

### Binary Classification Mapping for Primary Analysis
For primary statistical testing (McNemar test, mixed-effects logistic regression):
- **Hallucinated:** $\text{Label} == \text{HALLUCINATED}$ (Binary 1)
- **Non-Hallucinated:** $\text{Label} \in \{\text{FACTUAL}, \text{PARTIALLY\_CORRECT}\}$ (Binary 0)
- **Refusals:** Handled via pre-specified sensitivity protocols (Protocol S1: Excluded; Protocol S2: Worst-case coded as 1; Protocol S3: Penalized rate).

---

## 3. Judge Architecture & Deterministic Parameters

- **Judge Model:** `Qwen-2.5-72B-Instruct` / `Llama-3.3-70B-Instruct` (via deterministic frozen endpoint).
- **Sampling Parameters:**
  - Temperature: $T = 0.0$ (deterministic greedy decoding).
  - Top-p: $1.0$
  - Max Generation Tokens: 512
  - Deterministic System Prompt & Few-Shot Rubric.
- **Input Payload:**
  ```json
  {
    "question": "<Prompt Text>",
    "language": "<Language>",
    "condition": "<A_EN | B_NATIVE | C_ROMAN | D_CS | E_MIXED_SCRIPT>",
    "reference_answer": "<Gold Answer>",
    "evidence_snippet": "<Verified Ground Truth Evidence>",
    "model_response": "<Model Output to Evaluate>"
  }
  ```

---

## 4. Evaluator Output Schema & Validation Parser

The evaluator must return a strictly validated JSON object conforming to:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "label": {
      "type": "string",
      "enum": ["FACTUAL", "HALLUCINATED", "PARTIALLY_CORRECT", "INCORRECT", "REFUSAL"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "hallucinated_spans": {
      "type": "array",
      "items": { "type": "string" }
    },
    "rationalization": {
      "type": "string",
      "maxLength": 1000
    }
  },
  "required": ["label", "confidence", "hallucinated_spans", "rationalization"]
}
```

### Parser Failure Handling
1. If the evaluator fails JSON parsing, a deterministic regex extraction fallback extracts the enum label.
2. If regex fails, the item is retried up to 3 times with exponential backoff.
3. If still unresolvable, it is flagged as `EVALUATOR_PARSE_ERROR` and submitted to the human audit queue. Under no circumstances will parse failures be silently dropped.
