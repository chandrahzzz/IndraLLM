# IndraLLM — Phase 7: Official Venue Submission Requirements

**Document Version:** 1.0 (Phase 7 Venue Audit)  
**Lead Strategist:** Senior ACL/EMNLP Publication Strategist  
**Author & Sole Contributor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Date:** September 30, 2026  

---

## 1. Scope & Objective

This document analyzes current, official submission guidelines and requirements across the four premier computational linguistics and NLP publication venues:
1. **ACL (Association for Computational Linguistics)**
2. **EMNLP (Empirical Methods in Natural Language Processing)**
3. **NAACL (North American Chapter of the ACL)**
4. **TACL (Transactions of the Association for Computational Linguistics)**

Information is compiled directly from the official ACL Rolling Review (ARR) guidelines, conference calls for papers (CFPs), and TACL author instructions.

---

## 2. Comparative Venue Specification Matrix

| Dimension | ACL (via ARR) | EMNLP (via ARR / Direct) | NAACL (via ARR) | TACL (Journal) |
|---|---|---|---|---|
| **Submission Model** | Rolling monthly via ARR | Rolling via ARR / Direct Track | Rolling monthly via ARR | Year-round rolling submissions |
| **Commitment Cycle** | Fixed commitment deadlines | Fixed commitment deadlines | Fixed commitment deadlines | Post-acceptance conference presentation |
| **Review Platform** | OpenReview | OpenReview | OpenReview | MIT Press / OpenReview |
| **Reviewing Model** | Double-blind (anonymized) | Double-blind (anonymized) | Double-blind (anonymized) | Double-blind (anonymized) |
| **Page Limits (Long Paper)** | **Up to 8 pages** of content | **Up to 8 pages** of content | **Up to 8 pages** of content | **Up to 10 pages** of content |
| **Page Limits (Short Paper)** | **Up to 4 pages** of content | **Up to 4 pages** of content | **Up to 4 pages** of content | N/A (Full articles only) |
| **Exclusions from Page Limit** | Limitations, Ethics, References | Limitations, Ethics, References | Limitations, Ethics, References | References only |
| **Mandatory Sections** | Limitations (required, after body) | Limitations (required, after body) | Limitations (required, after body) | Reproducibility / Replication Details |
| **Ethics Section** | Highly encouraged / optional | Highly encouraged / optional | Highly encouraged / optional | Standard ethical disclosure |
| **Appendix / Supplementary Rules** | Allowed after references in same PDF; reviewers not obligated to read | Allowed after references in same PDF; reviewers not obligated to read | Allowed after references in same PDF; reviewers not obligated to read | Category 1 (Replication $\le 5$ pp), Category 2 (Complementary $\le 3$ pp) |
| **Camera-Ready Expansion** | $+1$ additional page of content | $+1$ additional page of content | $+1$ additional page of content | As authorized by Action Editor |
| **Code & Data Policy** | Encouraged to link anonymized repo or upload zip; mandatory open release upon acceptance | Encouraged to link anonymized repo or upload zip; mandatory open release upon acceptance | Encouraged to link anonymized repo or upload zip; mandatory open release upon acceptance | Mandatory reproducibility archive |
| **Anonymity Window** | Strict double-blind; no preprints within 1 month of submission if direct track | Strict double-blind; preprint policy adheres to ACL guidelines | Strict double-blind; ARR preprint policy | Strict double-blind |
| **Dual Submission Policy** | Prohibited for concurrently under-review works | Prohibited for concurrently under-review works | Prohibited for concurrently under-review works | Prohibited for concurrently under-review works |
| **Archival Status** | Archival (ACL Anthology) | Archival (ACL Anthology) | Archival (ACL Anthology) | Archival (ACL Anthology / MIT Press) |

---

## 3. Granular Analysis by Venue

### A. ACL (Annual Meeting of the Association for Computational Linguistics)
- **Primary Mechanism:** ACL operates primary review intake via **ACL Rolling Review (ARR)**. Authors submit to an ARR review cycle (e.g., bi-monthly or monthly deadlines on the 15th of the cycle). Following reviews and meta-reviews, authors commit their reviewed paper to ACL by the designated conference commitment deadline.
- **Length Constraint:** Long papers: exactly 8 pages for main content. The Limitations section is **mandatory** and must appear after the main text and before the references (does not count against page limits). Ethical Considerations is optional and excluded from page limits. References are unlimited.
- **Appendices:** Appendices must follow the references within the single submission PDF. Reviewers are instructed that papers must be self-contained; appendices are consulted at the reviewer's discretion for verification.
- **Anonymity:** Absolute double-blind. Submissions must not contain author names, affiliations, acknowledgments, links to personal GitHub repositories, project URLs containing user handles, or self-identifying citations.
- **Author Registration:** All co-authors must have verified OpenReview profiles with DBLP and institutional affiliations before the cycle submission deadline.

### B. EMNLP (Conference on Empirical Methods in Natural Language Processing)
- **Primary Mechanism:** Either commitments from ARR or a hybrid dedicated direct submission track following identical ARR formatting and page limits.
- **Focus & Culture:** Strong emphasis on **empirical rigor, statistical discipline, measurement integrity, and failure analysis**. Methodological skepticism towards uncalibrated LLM claims is notably high among EMNLP reviewers.
- **Formatting:** Identical 2-column ACL format. 8 content pages + Limitations + Ethics + References + Appendices.

### C. NAACL (North American Chapter of the ACL)
- **Primary Mechanism:** Coordinated through ARR commitments on the alternate-year cycle.
- **Focus & Culture:** High interest in linguistic diversity, sociolinguistic phenomena (including code-switching, borrowing, and dialectal variations), and computational linguistics fundamentals.
- **Formatting:** Standard ACL ARR guidelines apply.

### D. TACL (Transactions of the Association for Computational Linguistics)
- **Primary Mechanism:** Year-round submission to an open journal track with Action Editor assignment. Authors of accepted TACL papers are entitled to present at an upcoming ACL, EMNLP, or NAACL conference.
- **Length Constraint:** Up to **10 content pages** for original submissions. References are excluded.
- **Appendices (Policy effective 2024):** Stricter appendix categorization:
  - *Category 1 (Replication Details):* Up to 5 pages for hyperparameters, prompt templates, annotator agreements, and derivations.
  - *Category 2 (Complementary Results):* Up to 3 pages for supplemental tables and figures.
- **Turnaround:** Typically 60--90 days for initial decision (Category A: Accept, Category B: Minor Revision, Category C: Major Revision, Category D: Reject).

---

## 4. Key Procedural Checklist for IndraLLM Submission
1. **Long Paper Submission Format:** IndraLLM is designed as an **8-page Long Research Paper** (content pages 1--8), with:
   - Page 1--8: Introduction, Related Work, Research Questions, Benchmark Architecture, Empirical Results, Robustness & Sensitivity, Benchmark Expansion.
   - Excluded Pages: Limitations (Section 8), Ethics (Section 9), References (references.bib).
   - Appendices: Appendix A (Prompts & Annotation), Appendix B (Statistical Derivations), Appendix C (Dataset Taxonomy & Error Breakdown).
2. **Anonymity Audit:** Verified zero leaks of author identity, institutional affiliation, or personal repository URLs in the submission package.
3. **Commitment Strategy:** The paper is formatted for the standard ACL/ARR template, enabling seamless submission to ARR and subsequent commitment to ACL or EMNLP without reformatting.
