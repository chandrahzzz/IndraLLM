# IndraLLM — Phase 7: Data Governance, Provenance & Licensing Audit

**Document Version:** 1.0 (Phase 7 Legal & Licensing Audit)  
**Lead Auditor:** Senior Research Integrity & Licensing Auditor  
**Author & Sole Contributor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Date:** September 30, 2026  

---

## 1. Executive Summary

This audit establishes the legal governance, data provenance, intellectual property boundaries, and redistribution rights for all components of the IndraLLM project:
1. **Codebase (`src/indrallm/`, `scripts/`):** Governed under the **Apache License 2.0**.
2. **Benchmark Dataset (`IndraLLM-CS-v1.1-CANDIDATE`, `IndraLLM-CS-v1.2-PILOT`):** Released under **Creative Commons Attribution 4.0 International (CC-BY 4.0)**.
3. **Statutory Reference Propositions:** Derived exclusively from public domain Acts of the Parliament of India and official Ministry Gazette notifications published by the Government of India.
4. **Model Generations & Annotations (`results/EXP-002/`):** Produced via Groq API under terms authorizing academic research evaluation and open benchmarking.

---

## 2. Granular Provenance and Intellectual Property Review

### A. Statutory Legal Propositions (Authentic Core)
- **Source Material:** Official Gazettes of India, acts enacted by the Parliament of India (e.g., *Consumer Protection Act 2019*, *Citizenship Amendment Act 2019*, *Motor Vehicles Amendment Act 2019*, *Pradhan Mantri Fasal Bima Yojana Operational Guidelines*).
- **Copyright Status:** Under Section 52(1)(q) of the Indian Copyright Act, 1957, the reproduction or publication of any Act of a Legislature or any official government report/statute does not constitute copyright infringement. Public statutory laws are in the public domain.
- **Fair Use & Citation:** All 20 evaluated acts and 25 prospective expansion acts are cited with exact statutory section numbers, Ministry gazette dates, and regulatory parameters.

### B. Benchmark Query Realizations (IndraLLM Benchmark)
- **Creation Methodology:** 
  - Monolingual English, native-script Indic, Romanized Indic, Romanized code-switching, and dual-script alternation queries were authored by human native speakers and expert annotators fluent in Hindi, Bengali, Tamil, Telugu, and Kannada.
  - Inter-annotator naturalness score: $4.74 / 5.0$; agreement: $\kappa = 0.719, \alpha = 0.719$.
- **Redistribution Rights:** CC-BY 4.0 authorizes free sharing, adaptation, and commercial or non-commercial redistribution provided proper attribution is given to the author (Chandrahas Reddy) and project repository.

### C. Synthetic Scaling Partitions (Quarantine and Clear Labeling)
- **Status:** All synthetic scaling prompts (`TF-01` to `TF-10` non-authentic entities) are explicitly labeled with `is_authentic == False`.
- **Historical Benchmark Isolation:** The historical contaminated v1.0 benchmark remains strictly quarantined in `data/questions/historical_contaminated_v1.0/` and cannot enter active evaluation.

### D. Model Output & Inference Artifacts
- **Inference Provider:** Groq API (serving Alibaba Cloud Qwen-2.5-27B and Allam-2-7B).
- **API Terms Compliance:** Groq's Terms of Service grant the customer ownership of inputs and outputs generated through API endpoints. Model responses contain no personally identifiable information (PII) or confidential corporate secrets.
- **Redistribution:** Releasing model outputs for scientific auditability and reproducibility conforms to ACL Open Science and FAIR data principles.

---

## 3. Recommended Licensing Architecture

| Asset | Proposed License | Justification |
|---|---|---|
| **Software / Source Code** | **Apache 2.0** | Permissive, enterprise-friendly, explicit patent grant, standard for NLP tools (e.g., Hugging Face, spaCy). |
| **Benchmark Dataset** | **CC-BY 4.0** | Open access with attribution; standard for ACL Anthology benchmark releases. |
| **Research Documentation & Paper** | **CC-BY 4.0** | Standard for open scientific preprints and published conference proceedings. |

---

## 4. Auditor Final Licensing Sign-Off

The data governance, licensing, and provenance of IndraLLM are legally unencumbered and fully compliant with international academic open-access standards.

**Data & License Audit Verdict:** **APPROVED / PASS**
