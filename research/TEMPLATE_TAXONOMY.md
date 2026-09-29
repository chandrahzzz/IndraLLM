# Benchmark Template Family Taxonomy & Reasoning Framework

**Document Version:** 1.0 (Frozen for Phase 2.6 Rebuild)  
**Target Specification:** Part 3 & 4 Research Integrity Plan  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Design Rationale: Anti-Trivialization & Authentic Diversity

A fatal shortcut in multilingual dataset creation is "slot-filling trivialization" (e.g., repeating *"What is the capital of [Country]?"* 500 times). While the entities change, the syntactic frame, reasoning path, cognitive load, and token boundaries remain identical.

To prevent fake diversity, the IndraLLM-CS-v1.1 rebuild establishes an explicit **12-Family Multi-Tier Taxonomy**. Each template family defines:
1. A unique **epistemic question type** (numerical threshold, structural mechanism, regulatory condition, comparative contrast, etc.).
2. A distinct **reasoning type** (direct fact retrieval, constraint satisfaction, relational inference, multi-hop lookup, temporal anchor).
3. Explicit **linguistic construction rules** across English, native Indic scripts, Romanized Indic, and code-switching patterns.

---

## 2. Master Template Family Matrix

The taxonomy partitions into **In-Distribution (ID)** families (shared across Development, Validation, and Test-ID) and **Out-of-Distribution (OOD)** families (strictly quarantined to Test-OOD):

| Family ID | Family Name | Primary Domain(s) | Reasoning Type | Question Type | Partition Eligibility |
|---|---|---|---|---|---|
| **TF-01** | `NUMERICAL_THRESHOLD` | Governance / Welfare | Constraint Lookup | Quantitative Threshold | In-Distribution (Dev / Val / Test-ID) |
| **TF-02** | `TEMPORAL_MILESTONE` | History / Science | Temporal Anchoring | Date / Chronology | In-Distribution (Dev / Val / Test-ID) |
| **TF-03** | `SCIENTIFIC_COMPOSITION` | Science / Medicine | Structural Decomposition | Component / Count | In-Distribution (Dev / Val / Test-ID) |
| **TF-04** | `GEOGRAPHICAL_LOCATION` | Geography / Heritage | Spatial Mapping | District / Basin / Site | In-Distribution (Dev / Val / Test-ID) |
| **TF-05** | `INSTITUTIONAL_FRAMEWORK` | Education / Law | Regulatory Mapping | Body / Statutory Basis | In-Distribution (Dev / Val / Test-ID) |
| **TF-06** | `PUBLIC_HEALTH_TARGET` | Public Health / Policy | Target Specification | Beneficiary / Schedule | In-Distribution (Dev / Val / Test-ID) |
| **TF-07** | `AGRO_ECOLOGICAL_PRACTICE`| Agriculture / Environment | Ecological Fact | Soil / Crop Requirement | In-Distribution (Dev / Val / Test-ID) |
| **TF-08** | `BIOLOGICAL_MECHANISM` | Medicine / Biology | Functional Process | Physiological Role | In-Distribution (Dev / Val / Test-ID) |
| **TF-09** | `CULTURAL_LITERARY_ORIGIN`| Culture / History | Provenance Lookup | Author / Era / Dynastic Root | In-Distribution (Dev / Val / Test-ID) |
| **TF-10** | `MULTI_HOP_RELATIONAL` | History / Governance | Relational Chain | Transitive Association | In-Distribution (Dev / Val / Test-ID) |
| **TF-11** | `CROSS_ENTITY_COMPARISON` | Economy / Governance | Contrastive Evaluation | Comparative Difference | **STRICTLY TEST-OOD** |
| **TF-12** | `CONDITIONAL_REGULATORY` | Law / Administration | Rule-Based Exception | Prerequisite Condition | **STRICTLY TEST-OOD** |

---

## 3. Detailed Specifications per Template Family

### In-Distribution Families (TF-01 to TF-10)

#### TF-01: `NUMERICAL_THRESHOLD`
- **Subfamily:** `TF-01-A` (Financial allocations), `TF-01-B` (Quantity/area quotas).
- **Core Reasoning:** Model must accurately retrieve exact numerical constants, units, and temporal frequencies without arithmetic rounding hallucinations.
- **Example (EN):** *"What is the maximum annual turnover limit for an enterprise to be categorized as a Micro Enterprise under the MSME definition?"*
- **Gold Answer:** *₹5 Crore (with investment in plant & machinery not exceeding ₹1 Crore).*
- **Provenance:** Ministry of Micro, Small and Medium Enterprises (MSME Gazette Notification 2020).

#### TF-02: `TEMPORAL_MILESTONE`
- **Subfamily:** `TF-02-A` (Statutory enactment), `TF-02-B` (Technological mission launch).
- **Core Reasoning:** Exact calendar dates, years, or sequential temporal precedence.
- **Example (EN):** *"On which date was the Goods and Services Tax (GST) formally rolled out across India?"*
- **Gold Answer:** *1 July 2017.*
- **Provenance:** Central Board of Indirect Taxes and Customs (CBIC).

#### TF-03: `SCIENTIFIC_COMPOSITION`
- **Subfamily:** `TF-03-A` (Chemical / Biochemical components), `TF-03-B` (Atmospheric / Physical factors).
- **Core Reasoning:** Multi-element listing, atomic ratios, or standardized composition indices.
- **Example (EN):** *"Which major chemical compound is used as the active ingredient in oral rehydration solutions to stimulate water absorption in the small intestine?"*
- **Gold Answer:** *Sodium chloride and anhydrous glucose (in WHO-standard osmolarity of 245 mOsm/L).*
- **Provenance:** World Health Organization / AIIMS Guidelines.

#### TF-04: `GEOGRAPHICAL_LOCATION`
- **Subfamily:** `TF-04-A` (Archaeological sites), `TF-04-B` (Protected biosphere reserves).
- **Core Reasoning:** Spatial granularity (district, state, geographical formation, river basin).
- **Example (EN):** *"In which Indian state and mountain range is the Silent Valley National Park situated?"*
- **Gold Answer:** *Palakkad district, Kerala, in the Nilgiri Hills of the Western Ghats.*
- **Provenance:** Kerala Forest and Wildlife Department / National Parks Registry.

#### TF-05: `INSTITUTIONAL_FRAMEWORK`
- **Subfamily:** `TF-05-A` (Apex regulatory councils), `TF-05-B` (Statutory commissions).
- **Core Reasoning:** Identifying the constitutionally or legislatively mandated apex agency governing a national domain.
- **Example (EN):** *"Which statutory body serves as the apex regulator for telecommunications and tariff fixation in India?"*
- **Gold Answer:** *Telecom Regulatory Authority of India (TRAI), established under the TRAI Act 1997.*
- **Provenance:** TRAI Act 1997 / Department of Telecommunications.

#### TF-06: `PUBLIC_HEALTH_TARGET`
- **Subfamily:** `TF-06-A` (Immunization schedules), `TF-06-B` (Disease eradication thresholds).
- **Core Reasoning:** Clinical protocols, target population age windows, vaccine dosages.
- **Example (EN):** *"Under the National Vector Borne Disease Control Programme, which parasite species is the primary causative agent for cerebral malaria in India?"*
- **Gold Answer:** *Plasmodium falciparum.*
- **Provenance:** National Centre for Vector Borne Diseases Control (NCVBDC / MoHFW).

#### TF-07: `AGRO_ECOLOGICAL_PRACTICE`
- **Subfamily:** `TF-07-A` (Kharif / Rabi cropping systems), `TF-07-B` (Soil nutrient management).
- **Core Reasoning:** Environmental thresholds (rainfall, temperature, soil pH, photoperiod).
- **Example (EN):** *"What is the optimal soil pH range required for high-yield cultivation of black gram (urad) in peninsular India?"*
- **Gold Answer:** *pH 6.5 to 7.8 (neutral to slightly alkaline).*
- **Provenance:** Indian Council of Agricultural Research (ICAR-IIPR).

#### TF-08: `BIOLOGICAL_MECHANISM`
- **Subfamily:** `TF-08-A` (Cellular respiration / transport), `TF-08-B` (Enzymatic catalysis).
- **Core Reasoning:** Biological causation and mechanism without generic hand-waving.
- **Example (EN):** *"During the light reaction of photosynthesis in plant thylakoid membranes, which enzyme synthesizes ATP by utilizing the trans-membrane proton gradient?"*
- **Gold Answer:** *ATP synthase ($CF_0-CF_1$ complex).*
- **Provenance:** NCERT Class 11 Biology / National Institute of Plant Genome Research.

#### TF-09: `CULTURAL_LITERARY_ORIGIN`
- **Subfamily:** `TF-09-A` (Classical epigraphy / literature), `TF-09-B` (Architectural patron dynasties).
- **Core Reasoning:** Authorship, patron dynasty, script evolution, linguistic century.
- **Example (EN):** *"Which Sangam-era poet compiled the classical Tamil poetic work Kuruntokai?"*
- **Gold Answer:** *Compiled by Purikko (consisting of 401 love poems).*
- **Provenance:** Central Institute of Classical Tamil (CICT).

#### TF-10: `MULTI_HOP_RELATIONAL`
- **Subfamily:** `TF-10-A` (Dynastic successor lineage), `TF-10-B` (Agency $\to$ Parent Ministry $\to$ Act).
- **Core Reasoning:** Requires linking entity $A \to B$ and $B \to C$ to arrive at the gold factual answer.
- **Example (EN):** *"Who was the immediate successor to King Rajaraja Chola I under whose reign the Chola empire extended naval expeditions to Srivijaya?"*
- **Gold Answer:** *Rajendra Chola I.*
- **Provenance:** Archaeological Survey of India (ASI Epigraphia Indica).

---

### Out-of-Distribution Families (Strictly Quarantined to TEST-OOD)

#### TF-11: `CROSS_ENTITY_COMPARISON` (TEST-OOD ONLY)
- **Scientific Purpose:** Evaluates whether models can maintain factual precision across linguistic conditions when comparing two related entities, schemes, or institutions without hallucinating conflated attributes.
- **Constraint:** Zero instances of `TF-11` are permitted in Development or Validation sets.
- **Example (EN):** *"What is the key structural difference between the Pradhan Mantri Fasal Bima Yojana (PMFBY) and the Weather Based Crop Insurance Scheme (WBCIS) regarding claim assessment?"*
- **Gold Answer:** *PMFBY assesses claims based on actual crop yield loss (via Crop Cutting Experiments), whereas WBCIS triggers payouts based on weather parametric indices (rainfall, temperature deviation) irrespective of harvested yield.*
- **Provenance:** Ministry of Agriculture & Farmers Welfare Operational Guidelines.

#### TF-12: `CONDITIONAL_REGULATORY` (TEST-OOD ONLY)
- **Scientific Purpose:** Tests conditional legal/administrative logic (if conditions $X$ and $Y$ are met, then $Z$). Models prone to hallucination routinely ignore negative conditions or prerequisites.
- **Constraint:** Zero instances of `TF-12` are permitted in Development or Validation sets.
- **Example (EN):** *"Under the Indian Patent Act 1970, under what specific statutory condition can an applicant apply for a compulsory license on an active pharmaceutical patent?"*
- **Gold Answer:** *Only after the expiration of 3 years from the date of patent grant, if reasonable requirements of the public have not been satisfied, the patent is not available at a reasonably affordable price, or the patented invention is not worked in India.*
- **Provenance:** Intellectual Property India (Patents Act Section 84).

---

## 4. Anti-Leakage Verification Protocol

Before finalizing splits:
1. `template_family_id` must be recorded as a first-class column in every prompt record.
2. In validation suites, an automated check must verify:
   $$\text{TemplateFamilies}(\text{Development}) \cap \{\text{TF-11}, \text{TF-12}\} = \emptyset$$
   $$\text{TemplateFamilies}(\text{Validation}) \cap \{\text{TF-11}, \text{TF-12}\} = \emptyset$$
   $$\text{TemplateFamilies}(\text{Test-ID}) \cap \{\text{TF-11}, \text{TF-12}\} = \emptyset$$
   $$\text{TemplateFamilies}(\text{Test-OOD}) \subseteq \{\text{TF-11}, \text{TF-12}\}$$
