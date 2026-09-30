# IndraLLM — Phase 5: Conference & Journal Venue-Fit Strategy

**Document Version:** 1.0 (Phase 5 Manuscript Construction)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  

---

## 1. Executive Summary

This document evaluates the structural, methodological, and topical fit of the IndraLLM research paper across premier computational linguistics and natural language processing publication venues. Rather than speculating on subjective acceptance probabilities, this analysis assesses how the paper's core contributions—controlled semantic-paired benchmarking, factual reliability evaluation, subword boundary disruption mechanisms, and epidemiological sensitivity analysis—align with the specific review criteria, tracks, and page constraints of target conferences and journals.

---

## 2. Venue Alignment Analysis

### A. EMNLP (Conference on Empirical Methods in Natural Language Processing)
- **Primary Track Fit:** *Multilingual and Cross-Lingual NLP* / *Evaluation Methodologies* / *Factuality & Hallucination*.
- **Contribution Alignment:** **EXCEPTIONALLY HIGH.**
  EMNLP places intense emphasis on empirical rigor, negative result preservation, and forensic statistical modeling. The paper's four-step mediation decomposition (refuting linear fertility), 3-level GEE clustering, and 25-point Rogan–Gladen sensitivity surface strongly resonate with EMNLP's empirical standards.
- **Format Requirements:** 8 pages of content (excluding references and appendices).
- **Manuscript Readiness:** The core paper structure fits cleanly within the 8-page limit, with mathematical derivations, annotation guidelines, and full contrast tables placed in the appendix.

---

### B. ACL (Annual Meeting of the Association for Computational Linguistics)
- **Primary Track Fit:** *Linguistic Diversity and Multilingual NLP* / *Language Model Analysis & Interpretability*.
- **Contribution Alignment:** **HIGH.**
  ACL strongly values linguistic nuance, particularly the principled separation between lexical code-mixing and orthographic script alternation across Indo-Aryan and Dravidian families. The paper's focus on real-world Indian sociolinguistic dynamics under strict semantic pairing matches ACL's commitment to linguistic diversity.
- **Format Requirements:** 8 pages of content (long paper) + unlimited references and appendices.
- **Review Vulnerabilities Addressed:** The explicit disclosure of the Level 3 $p = 0.0528$ borderline result and the prospective labeling of the 45-topic expansion fully immunize the submission against hostile ACL benchmark reviewers.

---

### C. TACL (Transactions of the Association for Computational Linguistics)
- **Primary Focus:** High-depth, exhaustive journal-length research with thorough ablation studies.
- **Contribution Alignment:** **MODERATE TO HIGH.**
  TACL requires extensive cross-architectural exploration. While our manuscript provides exhaustive statistical and sensitivity depth on Qwen-27B and Allam-7B, a TACL submission would benefit from including empirical evaluations on the newly expanded 25 pilot topics once live API execution is authorized.

---

### D. NAACL (North American Chapter of the ACL)
- **Primary Track Fit:** *Evaluation of Language Technologies* / *Low-Resource & Multilingual NLP*.
- **Contribution Alignment:** **HIGH.**
  NAACL frequently highlights practical engineering vulnerabilities and diagnostic evaluation frameworks. The demonstration that automated LLM evaluators exhibit condition-dependent sensitivity differences directly appeals to the NAACL evaluation audience.

---

### E. COLING (International Conference on Computational Linguistics)
- **Primary Track Fit:** *Sociolinguistics & Pragmatics* / *Multilingual Processing*.
- **Contribution Alignment:** **MODERATE.**
  COLING values theoretical sociolinguistic framing. While IndraLLM features strong computational linguistics grounding in the Code-Mixing Index (CMI) and transliteration naturalness, the paper's primary identity is empirical evaluation and statistical modeling.

---

## 3. Recommended Submission Roadmap

1. **Target Submission Venue:** **EMNLP or ACL (Long Paper Track)**.
2. **Submission Files Prepared:**
   - Anonymous Manuscript: `paper/main_anonymous.tex` (8 pages of main text + appendix).
   - De-anonymized Camera-Ready: `paper/main_camera_ready.tex`.
   - Complete Reproducibility Appendix: `paper/supplementary/` and `paper/README.md`.
