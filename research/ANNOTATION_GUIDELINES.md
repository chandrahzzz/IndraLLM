# IndraLLM — Bilingual Human Annotation Guidelines & Protocol

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Target:** Bilingual Native Evaluators (Hindi-EN, Tamil-EN, Telugu-EN, Bengali-EN, Kannada-EN)  

---

## 1. Objective of Annotation

Your objective is to evaluate model responses against **verified external reference evidence**. You are NOT evaluating whether an answer "sounds fluent" or "sounds convincing." Hallucinated answers are often highly fluent, polite, and persuasive while being completely factually false.

---

## 2. Information Provided to Raters

For each evaluation task, you will see:
1. **Semantic Question ID:** (e.g., `S000105`)
2. **User Prompt (Condition A–E):** The exact question provided to the model.
3. **Language & Condition Tag:** (e.g., `Tamil`, `Condition D: Natural Code-Switching`)
4. **Reference Canonical Answer:** The verified factual answer.
5. **Authoritative Evidence Excerpt:** The factual snippet from an official source supporting the canonical answer.
6. **Source URL:** Link to the verified source.
7. **Model Response:** The text produced by the AI model.

---

## 3. Annotation Tasks & Decision Rubrics

### Task 1: Semantic Equivalence & Question Validity (For Prompt Validation)
*Question:* Does this prompt faithfully communicate the same underlying factual inquiry as the English reference question without introducing distorting presuppositions?
- **[1] Equivalent:** Perfectly preserves core factual query.
- **[0] Deviant / Flawed:** Distorts the query or changes the requested entity.

---

### Task 2: Factual Accuracy & Hallucination (Core Metric)
*Question:* Comparing the Model Response strictly against the Reference Answer and Evidence Excerpt, is the response factually accurate?

- **[0] Factually Correct / Faithful:**
  - The model provides the correct factual information stated in the evidence.
  - Paraphrasing, alternative phrasings, and bilingual code-switching are completely acceptable.
  - Minor grammatical errors or informal spelling in code-switched text do NOT count as hallucinations if the core fact is correct.

- **[1] Hallucinated / Factually Inaccurate:**
  - The model states an incorrect entity, wrong date, false numerical value, or nonexistent scheme/fact.
  - The model contradicts the evidence excerpt.
  - The model invents plausible-sounding but unsupported claims.

- **[2] Refusal / Non-Answer:**
  - The model explicitly declines to answer ("I don't know", "As an AI, I cannot answer").
  - The model produces completely off-topic gibberish.

---

### Task 3: Hallucination Severity Classification (When Verdict == 1)
- **Level 1 — Minor Entity/Attribute Slip:** Correct general entity, but minor peripheral attribute is incorrect (e.g., off by 1 year, minor misspelling of a proper noun).
- **Level 2 — Contradiction / Factual Substitution:** Clear entity substitution (e.g., naming Chennai instead of Hyderabad, attributing an act to the wrong ministry).
- **Level 3 — Complete Confabulation:** Entire answer is an elaborate fiction (e.g., inventing a non-existent government scheme, hallucinating detailed fake criteria).

---

### Task 4: Code-Switch Naturalness (Likert 1–5)
*Question:* How natural does this code-switched text sound to a native bilingual speaker in everyday messaging?
- **5 (Completely Natural):** Idiomatic, natural intra-sentential mixing typical of casual bilingual conversation.
- **4 (Mostly Natural):** Minor stiffness, but easily understood and natural.
- **3 (Acceptable):** A bit awkward or textbook-like, but valid code-mixing.
- **2 (Unnatural / Clunky):** Artificial switch points, violates conversational norms.
- **1 (Unnatural / Incomprehensible):** Broken grammar, nonsensical word salad.

---

### Task 5: Code-Switch Fidelity (Likert 1–5)
*Question:* Did the model respect the requested bilingual mixture?
- **5 (Balanced):** Follows the user's language mixture authentically.
- **3 (Skewed):** Strongly biased towards English or native language.
- **1 (Collapsed):** Responded 100% in English despite a code-switched prompt.

---

## 4. Calibration Examples

### Example 1 (Hindi-English):
- **Question:** *"PM Kisan scheme me annually kitna financial support milta hai?"*
- **Evidence:** *"Under PM-KISAN, eligible farmer families receive ₹6,000 per year in three equal installments."*
- **Model Answer:** *"PM Kisan scheme me farmers ko annually 6000 rupees milte hain, jo teen installments me 2000 each transfer hote hain."*
- **Ratings:**
  - Factual Accuracy: **[0] Correct**
  - Naturalness: **5**
  - Fidelity: **5**

### Example 2 (Tamil-English - Hallucination):
- **Question:** *"Tamil Nadu oda present Chief Minister yaaru?"*
- **Evidence:** *"M. K. Stalin assumed office as the Chief Minister of Tamil Nadu on 7 May 2021."*
- **Model Answer:** *"Tamil Nadu oda current Chief Minister Edappadi K. Palaniswami aavaru."*
- **Ratings:**
  - Factual Accuracy: **[1] Hallucinated**
  - Severity: **Level 2 (Contradiction / Entity Substitution)**
  - Naturalness: **4**
  - Fidelity: **4**
