# Factual Provenance & Ground Truth Evidence Audit

**Document Version:** 1.0 (Frozen Specification)  
**Target Specification:** Part 6 Research Integrity Plan  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Candidate Identifier:** `IndraLLM-CS-v1.1-CANDIDATE`  

---

## 1. Epistemic Standard for Factual Ground Truth

In IndraLLM-CS-v1.1, factual ground truth is anchored strictly in **independently verifiable primary and secondary institutional records**. Models or LLM judges are strictly prohibited from generating ground truth.

Every single semantic item requires four verified evidentiary anchors:
1. `canonical_fact`: A self-contained, unambiguous factual assertion.
2. `reference_answer`: The exact gold answer string.
3. `evidence_snippet`: A verbatim supporting excerpt from the authoritative source.
4. `evidence_source_url`: A permanent, public, verifiable institutional URL or official citation.

---

## 2. Institutional Source Taxonomy & Representation

The knowledge base draws from six categories of authoritative sources:

| Source Category | Code | Representative Institutions & Portals | Verification Protocol |
|---|---|---|---|
| **National Government Portals** | `govt_portal` | `pmkisan.gov.in`, `nhm.gov.in`, `soilhealth.dac.gov.in`, `msme.gov.in`, `cbic.gov.in`, `mhrd.gov.in` | Verified against official gazette notifications and ministry operational guidelines. |
| **National Science Agencies** | `science_agency` | `isro.gov.in`, `icar.org.in`, `csir.res.in`, `drdo.gov.in`, `dbtindia.gov.in` | Verified against mission technical archives and research bulletins. |
| **Statutory Authorities & Acts** | `statutory_act` | `trai.gov.in`, `rbi.org.in`, `sebi.gov.in`, `indiacode.nic.in` | Anchored in Section/Clause references of enacted Parliament Acts. |
| **Public Health Institutions** | `health_registry` | `mohfw.gov.in`, `aiims.edu`, `ncvbdc.mohfw.gov.in`, `who.int` | Anchored in National Health Mission clinical management protocols. |
| **Archaeological & Classical** | `academic_archive` | `asi.nic.in`, `tnarch.gov.in`, `cict.in`, `epigraphia-indica` | Verified against ASI excavation reports and CICT classical concordances. |
| **Educational & Statistical** | `edu_registry` | `nirfindia.org`, `ugc.ac.in`, `censusindia.gov.in`, `mospi.gov.in` | Verified against published ranking frameworks and Census tables. |

---

## 3. Provenance Verification Checklist per Semantic Item

An automated provenance validator audits every record prior to dataset freezing:
- [x] **URL Format:** Valid HTTPS scheme and authentic institutional domain (`.gov.in`, `.nic.in`, `.org.in`, `.edu`, `.who.int`).
- [x] **Snippet Grounding:** `evidence_snippet` must contain the exact key entities and numerical constants present in `reference_answer`.
- [x] **Temporal Scope:** `source_access_date` recorded for all web-retrieved statutory sources.
- [x] **Independent Factuality:** Answers do not rely on subjective opinions, fluid market prices, or transient election polling data.
