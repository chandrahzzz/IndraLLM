# IndraLLM — Ethics, Privacy, and Responsible Research Statement

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Adherence:** ACL Ethics Policy, Belmont Report Principles, FAIR Data Principles  

---

## 1. Human Subject Protection & Annotator Welfare

### 1.1 Fair Compensation & Labor Standards
- **Living Wage Commitment:** All bilingual annotators participating in dataset validation and gold factuality rating are compensated at or above prevailing local professional rates (equivalent to $> 1.5\times$ local minimum wage).
- **Cognitive Load & Ergonomics:** Annotation sessions are strictly capped at 2 hours per sitting to prevent cognitive fatigue and inconsistent evaluation.
- **Informed Consent:** Annotators are briefed on the research purpose, potential model biases, the non-commercial academic release scope, and maintain the right to withdraw at any time without penalty.

### 1.2 Anonymity and Privacy
- Annotator identities are stored under hashed, anonymized tokens (`RATER_01`, `RATER_02`). No personal contact details, demographic identifiers, or private data are committed to the repository or published.

---

## 2. Data Sourcing, Consent, and PII Protection

### 2.1 Authentic and Naturalistic Sourcing Policy
- **Zero Private Data Scraped:** The project strictly prohibits scraping private group chats (e.g., WhatsApp, Telegram, Discord) or non-consensual personal correspondence.
- **Public Domain & Creative Commons:** Naturalistic examples are gathered exclusively from open, public public forums (e.g., public Reddit discussions, open civic portals) in accordance with platform terms of service and robots.txt.
- **PII Scrubbing Pipeline:** All raw and filtered text passes through an automated PII redaction filter removing:
  - Phone numbers (Indian mobile formats `+91-XXXXX-XXXXX`)
  - Aadhaar / PAN / Identification numbers
  - Personal names and email addresses
  - Specific private addresses / home locations

---

## 3. High-Stakes Domain Safety: Healthcare & Legal Advice

### 3.1 Medical Knowledge Safeguards
- Questions categorized under the `public_health` domain query **verifiable biological and public health facts** (e.g., vaccine schedules, disease vectors, nutritional definitions, historical health policies).
- **Prohibited Content:** We strictly exclude:
  - Individualized medical diagnosis or prescription queries ("What dose of X should my child take?").
  - Emergency triage or psychiatric crisis scenarios.
- **Mandatory Safety Disclaimer:** All benchmark releases containing health questions carry a prominent warning:
  > *This dataset contains factual QA pairs designed solely for computational NLP research on language model hallucination. It does NOT provide medical advice, diagnosis, or treatment.*

### 3.2 Civic and Legal Knowledge
- Government scheme queries are verified against official portal guidelines (e.g., PM-Kisan, state welfare criteria). Models are evaluated strictly on whether they state official administrative facts accurately.

---

## 4. Linguistic Equity & Demographic Representation

- **Avoiding False Universalism:** We explicitly declare that 5 languages do not represent the rich linguistic diversity of the Indian subcontinent (over 22 official languages and hundreds of mother tongues).
- **Regional Bias Disclosure:** Our current dataset samples Hindi, Tamil, Telugu, Bengali, and Kannada. We explicitly document this limitation and warn against generalizing our findings to Tibeto-Burman or Austroasiatic Indian languages.
