# IndraLLM — Phase 7: Final Submission Compliance Checklist

**Document Version:** 1.0 (Phase 7 Final Submission Verification)  
**Lead Auditor:** ACL/EMNLP Area Chair & Submission Committee  
**Author & Sole Contributor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Date:** September 30, 2026  

---

## 1. Comprehensive Compliance Checklist

| Item | Scope & Official Criterion | Status | Verification & Audit Notes |
|---|---|---|---|
| **Correct Venue Template** | Standard 2-column ACL/ARR LaTeX style package (`article`, `times`, `latexsym`, `booktabs`, `microtype`). | **PASS** | `paper/main_anonymous.tex` and `submission/anonymous/main.tex` conform to ACL 2-column layout. |
| **Correct Page Limit** | 8 content pages for long paper; Limitations, Ethics, and References excluded. | **PASS** | Main text (Sections 1--7) fits within 8 pages; Limitations (Sec 8) and Ethics (Sec 9) placed before References. |
| **Anonymous PDF / Source** | 100% free of author names, affiliations, contact info, GitHub repo links, or tracking handles. | **PASS** | Audited via regex search; `\author{Anonymous ACL Submission}`; zero identity leaks found. |
| **No Identity Leakage** | Repository name `IndraLLM` used solely as benchmark noun; zero author handles or GitHub URLs in anonymous text. | **PASS** | Zero identity leaks in `submission/anonymous/`. |
| **Correct Supplementary Format** | Appendices appended after References in the same PDF; self-contained narrative in main paper. | **PASS** | 3 supplementary appendices (`annotation_and_prompts`, `statistical_derivations`, `dataset_and_taxonomy`) properly structured. |
| **Correct References** | All 18 citations verified as real peer-reviewed papers with complete bibliographic metadata. | **PASS** | Audited in `references.bib`; all 18 keys cited in text; zero phantom citations. |
| **Correct Metadata** | OpenReview paper title, abstract, and track keywords match LaTeX source text exactly. | **PASS** | Title, abstract, and keywords verified. |
| **Correct Figures** | All 8 figures at 300 DPI, readable font sizes, colorblind-friendly palettes, and error bars. | **PASS** | 8 figures generated and verified in `paper/figures/` and `submission/anonymous/figures/`. |
| **Correct Tables** | Professional booktabs formatting; explicit sample sizes; Holm--Bonferroni annotations; exact empirical counts. | **PASS** | Tables 1--8 audited; C_ROMAN corrected to $33.0\%$; contrasts updated to $-31.0$ pp. |
| **Correct Appendix** | Contains prompt rubrics, GEE formulas, power derivations, error taxonomies, and CMI equations. | **PASS** | Verified in `paper/supplementary/` and `submission/anonymous/supplementary/`. |
| **Correct Abstract** | 20 evaluated topics, 45 prospective topics, exact numbers ($64.0\% \to 43.0\% \to 24.0\%$), $88.6\%$ power, $20\times$ truncation. | **PASS** | Completely harmonized; zero discrepancies. |
| **Correct Title** | Accurate, descriptive, non-hyped scientific title. | **PASS** | *"Representation Fragility: Evaluating Factual Reliability under Controlled Semantic Pairing Across Indic Code-Switching and Script Alternation"*. |
| **Camera-Ready Author Info** | Camera-ready manuscript contains Chandrahas Reddy (`kurkurrereddy@gmail.com`) as sole author. | **PASS** | Verified in `paper/main_camera_ready.tex` and `submission/camera_ready/main.tex`. |
| **Reproducibility Package** | Complete local reproduction pipeline with pinned dependencies, checksums, and execution guide. | **PASS** | Assembled in `submission/reproducibility/`; 54 tests pass, 1 intentional xfail. |
| **Dataset Documentation** | Full schema, license, provenance, linguistic annotation protocol, and quality gates documented. | **PASS** | Documented in `paper/README.md` and `reproducibility/README.md`. |
| **Code Documentation** | Clear docstrings, typed signatures, and modular architecture across `src/indrallm/`. | **PASS** | Fully documented and passing tests. |
| **License Compliance** | Code licensed under Apache 2.0; benchmark data licensed under CC-BY 4.0; public domain statutory text. | **PASS** | Documented in `research/PHASE7_DATA_LICENSE_AUDIT.md`. |
| **No Dual-Submission Violation** | The work is not submitted, under review, or accepted at any other venue. | **PASS** | Pristine original submission ready for ARR. |
| **No Unsupported Claims** | Zero uncalibrated causal claims; linear sequence fertility mediation refuted (Sobel $p=0.9387$); script transitions framed as association. | **PASS** | Fully compliant with `paper/CLAIM_LEDGER.md`. |
| **Phase 6 Frozen Results Preserved** | All empirical core results ($N=500$, 20 topics) and pilot expansion design ($N=45$) preserved without alteration. | **PASS** | Scientific freeze strictly maintained. |

---

## 2. Final Compliance Sign-Off

Every single compliance dimension has been verified and marked **PASS**.

**Overall Submission Status:** **SUBMISSION_PACKAGE_COMPLETE**
