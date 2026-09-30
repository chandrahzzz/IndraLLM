# IndraLLM — Phase 4.5: Workstream 2
# Topic Independence & Expansion Verification Audit

**Document Version:** 1.0 (Phase 4.5 Independent Verification Audit)  
**Execution Date:** September 2026  
**Auditor:** Chandrahas Reddy (`kurkurrereddy@gmail.com`)  
**Target Repository:** `https://github.com/chandrahzzz/IndraLLM`  
**Git Branch:** `phase4-5-verification`  
**Artifacts Audited:**  
- `data/questions/IndraLLM-CS-v1.2-PILOT/pilot_propositions_25.jsonl`
- `data/questions/IndraLLM-CS-v1.2-PILOT/pilot_prompts_125.csv`
- `data/questions/IndraLLM-CS-v1.2-PILOT/data_manifest.json`
- `results/phase4/phase4_5_topic_audit.json`

---

## 1. Executive Summary

A primary vulnerability raised by hostile peer review was whether the 25 new statutory propositions in `IndraLLM-CS-v1.2-PILOT` (`AUTH-021` to `AUTH-045`) were genuinely independent legal facts or merely superficial paraphrases and re-templatings of the original 20 authentic topics (`AUTH-001` to `AUTH-020`).

This audit conducted an automated, multi-tiered lexical, semantic, entity, evidence, and source overlap investigation comparing all 25 pilot propositions against the frozen authentic core.

### Final Verification Classification:
# **`VERIFIED_INDEPENDENT`**

All 25 new propositions represent genuinely distinct, legally enacted Indian statutory frameworks with zero entity overlap, zero source duplication, and negligible n-gram overlap ($J \le 0.0208$ on evidence snippets).

---

## 2. Item-by-Item Verification Matrix (A through M)

| Audit Criterion | Verification Method | Empirical Finding | Status |
|---|---|---|---|
| **A. Exactly 25 New Propositions?** | Direct JSONL count | Exactly 25 lines in `pilot_propositions_25.jsonl`. | **VERIFIED** |
| **B. Unique Topic Identifiers?** | Regex & Set Disjointness | `AUTH-021` through `AUTH-045` strictly sequential and non-overlapping. | **VERIFIED** |
| **C. Distinct Factual Claims?** | Canonical Fact Set Uniqueness | 25 distinct statutory parameters (e.g., DPDP penalty caps, RERA exemption areas, POSH committee thresholds). | **VERIFIED** |
| **D. Not Mere Paraphrases of AUTH-001–020?** | Proposition Semantic Mapping | Zero topical overlap with original 20 acts (PMFBY, CAA, Maternity Benefit, etc.). | **VERIFIED** |
| **E. New Entities Introduced?** | Target Entity Set Intersection | Exactly 25 new entities; intersection with original 20 entities is `set()` (Zero overlap). | **VERIFIED** |
| **F. New Evidence Snippets?** | 3-gram Jaccard Similarity | Max evidence 3-gram Jaccard similarity is $0.0208$ (essentially zero). | **VERIFIED** |
| **G. New Statutory Acts?** | Legislative Title Check | 25 distinct statutes spanning Consumer Law, Privacy, Competition, Labor, IP, Insolvency, etc. | **VERIFIED** |
| **H. Independent Evidence Sources?** | Source URL & Authority Audit | 25 unique official URLs (meity.gov.in, cci.gov.in, ibbi.gov.in, rera, etc.). | **VERIFIED** |
| **I. Entity Overlap?** | Cross-Split String Match | Zero entity collision ($0 / 25$). | **VERIFIED** |
| **J. Evidence Overlap?** | Normalized Substring Search | Zero verbatim evidence overlap ($0 / 25$). | **VERIFIED** |
| **K. Semantic Duplication?** | Sentence-level Semantic Search | All 25 govern separate regulatory domains and thresholds. | **VERIFIED** |
| **L. Near-Duplicate Leakage?** | Cross-Dataset MinHash / N-gram | Max prompt 3-gram Jaccard is $0.2609$ (restricted solely to generic query framing). | **VERIFIED** |
| **M. Template Leakage?** | Template Family IDs | Assigned to new orthogonal structural templates (`TF-12`, etc.). | **VERIFIED** |

---

## 3. Disaggregated Catalog of the 25 Independent Statutory Acts

| Topic ID | Statutory Act Title | Target Entity & Legal Parameter | Regulatory Domain | Provenance URL |
|---|---|---|---|---|
| `AUTH-021` | Consumer Protection Act 2019 | District Commission Pecuniary Jurisdiction (Rs 50 Lakh) | Consumer Protection | `consumeraffairs.nic.in` |
| `AUTH-022` | Digital Personal Data Protection Act 2023 | Maximum Breach Financial Penalty (Rs 250 Crore) | Data Privacy | `meity.gov.in` |
| `AUTH-023` | Competition Act 2002 (Amendment 2023) | Deal Value Threshold for Merger Review (Rs 2,000 Crore) | Corporate / Anti-trust | `cci.gov.in` |
| `AUTH-024` | POSH Act 2013 | Internal Complaints Committee Mandate Threshold (10 Employees) | Labor / Workplace Safety | `wcd.nic.in` |
| `AUTH-025` | Patents Act 1970 | Statutory Term of Patent Protection (20 Years) | Intellectual Property | `ipindia.gov.in` |
| `AUTH-026` | Insolvency and Bankruptcy Code 2016 | Corporate Insolvency Resolution Threshold (Rs 1 Crore) | Corporate Insolvency | `ibbi.gov.in` |
| `AUTH-027` | Forest Rights Act 2006 | Maximum Land Title Recognition Cap (4 Hectares) | Environmental / Tribal | `tribal.nic.in` |
| `AUTH-028` | Mines and Minerals (MMDR) Act 2015 | District Mineral Foundation Trust Levy (10% to 30%) | Mining / Resources | `mines.gov.in` |
| `AUTH-029` | Real Estate (RERA) Act 2016 | Mandatory Project Registration Exemption Threshold (500 sq m / 8 apts) | Housing / Urban | `mohua.gov.in` |
| `AUTH-030` | Electricity Act 2003 | Open Access Threshold Mandate (1 Megawatt) | Energy / Power | `powermin.gov.in` |
| `AUTH-031` | Aadhaar Act 2016 | Core Biometric Information Retention Prohibition Period | Digital Identity | `uidai.gov.in` |
| `AUTH-032` | Motor Vehicles (Amendment) Act 2019 | Juvenile Driving Offence Guardian Penalty (Rs 25,000 & 3 Yrs) | Transport / Safety | `morth.nic.in` |
| `AUTH-033` | Environment Protection Act 1986 | National Green Tribunal Appeal Limitation Window (30 Days) | Environmental Law | `moef.gov.in` |
| `AUTH-034` | RTI Act 2005 | Third Party Information Response Timeline (40 Days) | Transparency / RTI | `persmin.gov.in` |
| `AUTH-035` | Prevention of Money Laundering Act 2002 | ED Provisional Attachment Validity Window (180 Days) | Financial Crimes | `enforcementdirectorate.gov.in` |
| `AUTH-036` | Seeds Act 1966 | Central Seed Committee Term of Office (2 Years) | Agriculture / Farming | `agricoop.nic.in` |
| `AUTH-037` | Warehousing (Development & Reg) Act 2007 | Negotiable Warehouse Receipt Mandatory Net Worth | Logistics / Agri-trade | `wdra.gov.in` |
| `AUTH-038` | Telecommunications Act 2023 | Interception Order Review Committee Validation (60 Days) | Telecom / Defense | `dot.gov.in` |
| `AUTH-039` | National Food Security Act 2013 | Antyodaya Anna Yojana Monthly Grain Allocation (35 kg) | Food Security | `dfpd.gov.in` |
| `AUTH-040` | Street Vendors Act 2014 | Town Vending Committee Vendor Representation (40%) | Urban Governance | `mohua.gov.in` |
| `AUTH-041` | Transgender Persons Act 2019 | District Magistrate Certificate of Identity Timeline (30 Days) | Civil Rights | `socialjustice.gov.in` |
| `AUTH-042` | Biological Diversity Act 2002 | State Biodiversity Board Benefit Sharing Fee Cap (2%) | Biodiversity | `nbaindia.org` |
| `AUTH-043` | Disaster Management Act 2005 | National Disaster Management Authority Maximum Members (9) | Disaster Management | `ndma.gov.in` |
| `AUTH-044` | Micro, Small & Medium Enterprises Act 2006 | Delayed Payment Interest Penalty (3x RBI Bank Rate) | MSME / Industry | `msme.gov.in` |
| `AUTH-045` | Clinical Establishments Act 2010 | Provisional Registration Validity Duration (1 Year) | Public Health | `mohfw.gov.in` |

---

## 4. Quantitative Leakage Metrics

- **Total Proposition Count:** 25
- **Total Condition Prompts:** 125 ($25 \times 5$ conditions)
- **Entity Overlap with `AUTH-001..020`:** **0** ($0.0\%$)
- **Exact Prompt Overlap with `AUTH-001..020`:** **0** ($0.0\%$)
- **Max Evidence 3-gram Jaccard:** **$0.0208$**
- **Max Prompt 3-gram Jaccard:** **$0.2609$** (Shared query frames: *"under indian statutory regulations what specific prerequisite..."*)

---

## 5. Final Audit Conclusion

The 25 new statutory propositions in `IndraLLM-CS-v1.2-PILOT` represent genuine, authoritative, and structurally independent statutory legal units. They completely eliminate the concern that expansion was achieved via paraphrase or synthetic cloning.
