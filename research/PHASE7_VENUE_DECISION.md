# IndraLLM — Phase 7: Primary and Backup Venue Decision

**Document Version:** 1.0 (Phase 7 Strategic Venue Decision)  
**Lead Strategist:** Senior ACL/EMNLP Publication Strategist & Area Chair  
**Author & Sole Contributor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Date:** September 30, 2026  

---

## 1. Venue Hierarchy Decision Summary

Based on rigorous comparative evaluation of submission requirements, topical focus, empirical methodology, paper length, and community review culture, the publication roadmap for IndraLLM is formally established:

| Priority | Target Venue | Submission Route | Primary Subject Track | Rationale Summary |
|---|---|---|---|---|
| **PRIMARY VENUE** | **EMNLP (via ARR)** | ACL Rolling Review (ARR) $\to$ Commitment | *Evaluation Methodologies / Multilingual NLP* | Optimal alignment with empirical benchmark methodology, conservative statistical modeling, null result disclosure, and evaluator sensitivity analysis. |
| **BACKUP VENUE 1** | **ACL (via ARR)** | ACL Rolling Review (ARR) $\to$ Commitment | *Multilingualism and Language Diversity* | Premier general venue; high visibility for controlled semantic-paired framework and non-canonical linguistic representation findings. |
| **BACKUP VENUE 2** | **TACL** | Direct Journal Submission | Full Archival Track | Comprehensive archival venue allowing expansion to 10 content pages with full mathematical and linguistic replication appendices. |

---

## 2. Technical Justification for Primary Venue Selection: EMNLP (via ARR)

### Reason 1: Methodological Symmetry with EMNLP Culture
EMNLP reviewers are notoriously rigorous regarding empirical controls and statistical validity. The strengths of IndraLLM directly target the standard expectations of an EMNLP paper:
1. **Confound Elimination:** By enforcing strict semantic pairing across identical statutory propositions, IndraLLM removes the knowledge-vs-language confound that plagues prior multilingual benchmarks (e.g., MEGA, IndicLLMSuite).
2. **Conservative Statistical Discipline:** Rather than relying on naive unclustered significance, the paper leads with Generalized Estimating Equations (GEE) clustered by base statutory act ($\text{ICC} = 0.2663, \text{DEFF} = 7.3912, N_{\text{eff}} = 67.6$) and transparently discloses that the code-switching contrast yields $p = 0.0528$ under act-level clustering. EMNLP reviewers reward this honesty far more than generalist conferences that might penalize any $p > 0.05$.
3. **Forensic Evaluator Audit:** Automated LLM judge evaluation is audited using an epidemiological 2D Rogan--Gladen latent prevalence inversion ($\text{TPR} \in [0.80, 0.96], \text{FPR} \in [0.04, 0.16]$), proving the $+16.82\%$ to $+34.38\%$ gap survives judge bias. This level of measurement modeling is ideally suited for EMNLP's *Evaluation Methodologies* track.
4. **Honest Negative Results:** The refutation of the continuous token fertility mediation hypothesis (Sobel $p = 0.9387$) is treated as a major scientific finding rather than swept under the rug.

### Reason 2: Submission Route Optimization (ACL Rolling Review)
Submitting through **ACL Rolling Review (ARR)** provides maximum strategic flexibility:
- A single submission to ARR is reviewed by a specialized panel of computational linguistics and NLP reviewers.
- Once reviews and meta-reviews are finalized, the paper can be directly committed to **EMNLP** or **ACL** during their respective commitment windows without reformatting or restarting the review cycle.
- If reviewers request minor textual clarifications or additional descriptive analyses, revisions can be incorporated directly in ARR before conference commitment.

---

## 3. Backup Venue Strategies

### Backup 1: ACL (via ARR Commitment)
- **Trigger Condition:** If the ARR meta-review highlights the broad sociolinguistic importance of code-switching across 5 Indian scheduled languages and emphasizes the general interest to the global NLP community.
- **Action:** Commit the reviewed paper directly to the *Multilingualism and Language Diversity* track of ACL.

### Backup 2: TACL (Transactions of the ACL)
- **Trigger Condition:** If ARR reviewers suggest that the paper would benefit from a longer, journal-style treatment integrating the 25 pilot topic data cards, full prompt rubrics, and extended mathematical derivations directly into the main text.
- **Action:** Transition the manuscript into the 10-page TACL format, incorporating the supplementary materials into TACL Category 1 (Replication) and Category 2 (Complementary Results) appendices.

---

## 4. Operational Next Steps
1. Package the manuscript into a pristine, fully anonymized ARR submission bundle (`submission/anonymous/`).
2. Package the complete offline local reproduction pipeline (`submission/reproducibility/`).
3. Maintain the camera-ready version (`submission/camera_ready/`) with author attribution strictly reserved for Chandrahas Reddy (`kurkurrereddy@gmail.com`).
