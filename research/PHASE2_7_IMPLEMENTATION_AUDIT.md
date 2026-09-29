# Phase 2.7 Implementation & Code-Documentation Audit

**Document Version:** 1.0 (Adversarial Pre-EXP-002 Audit)  
**Target Specification:** Part 3 Adversarial Research Integrity Audit  
**Reviewer Role:** Hostile ACL/EMNLP/TACL Meta-Reviewer  
**Author:** Chandrahas Reddy  
**Date:** September 2026  

---

## 1. Executive Summary: Hostile Reviewer Assessment

This audit evaluates whether the actual repository implementation in `src/indrallm/`, `tests/`, and `data/questions/` matches the claims made in research reports. 

**Adversarial Verdict:** While Phase 2.6 successfully achieved mathematical string disjointness across partitions (eliminating the crude literal overlap of v1.0), an adversarial inspection of `build_decontaminated_benchmark_v1_1.py` reveals **three CRITICAL and two MAJOR discrepancies** between the documentation and the underlying code. 

Most notably, the candidate benchmark was padded with synthetic template formulas, human validation metrics from an earlier pilot were conflated with the candidate dataset, and English entity insertion distorted the CMI distribution.

---

## 2. Forensic Discrepancy Matrix

| Discrepancy ID | Severity | File & Location | Documented Behavior | Actual Code Behavior | Required Correction |
|---|---|---|---|---|---|
| **DISC-01** | **CRITICAL** | [`src/indrallm/collection/build_decontaminated_benchmark_v1_1.py:270-290`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/src/indrallm/collection/build_decontaminated_benchmark_v1_1.py#L270-L290) | Claims 300 authentic, independently grounded factual units with verified gazette provenance (`PROVENANCE_AUDIT.md`). | Facts 76 to 280 (205 out of 300 facts, ~68.3% of the catalog) are synthetically generated using a template loop (`National_X_Registry_Unit_idx`, `https://{domain}.gov.in/gazette/clause{idx}`). | Mark G1/G14 as **UNVERIFIED / PASS WITH LIMITATION**; disclose synthetic padding; curate authentic facts or scale down to verified core. |
| **DISC-02** | **CRITICAL** | [`research/PHASE2_6_GO_NO_GO.md:32`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_6_GO_NO_GO.md#L32), [`research/PHASE2_6_REPORT.md:58`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/research/PHASE2_6_REPORT.md#L58) | Reports Gate G8 (Human Agreement: $\kappa = 0.719$) and G9 (Naturalness: $4.74/5.0$) as "PASS" for `IndraLLM-CS-v1.1-CANDIDATE`. | These ratings were historical numbers measured on the Phase 2 pilot sample ($N=150$), NOT on the newly generated 1,500 semantic groups of v1.1-CANDIDATE. | Reclassify Gate G8 and G9 as **UNVERIFIED** for v1.1-CANDIDATE. Prohibit claiming human validation without fresh human annotation. |
| **DISC-03** | **CRITICAL** | [`src/indrallm/collection/build_decontaminated_benchmark_v1_1.py:353-380`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/src/indrallm/collection/build_decontaminated_benchmark_v1_1.py#L353-L380) | `B_NATIVE` is documented as "Monolingual Native Script representation in Brahmic scripts with formal vocabulary" (`DATA_SCHEMA.md`). | English entity names were prepended verbatim into native script prompts (`{name} के संबंध में...`), causing Latin tokens in B_NATIVE and inflating CMI from $0.43\%$ to $16.75\%$. | Transliterate entity names into native scripts for B_NATIVE or document code-mixing of Latin entities in native carrier clauses. |
| **DISC-04** | **MAJOR** | [`src/indrallm/generation/run_inference_pilot.py:134-137`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/src/indrallm/generation/run_inference_pilot.py#L134-L137) | Documents multi-model inference pilot demonstrating "0% parsing failures and 0% refusal" on Llama and Qwen models. | In local/offline runs where API keys or live endpoints are unavailable, the code returns deterministic mock strings (`Answer to: [prompt] [reference_answer]`). | Clearly distinguish between live API inference metrics and offline pipeline test runs. |
| **DISC-05** | **MAJOR** | [`tests/test_phase2_5_integrity.py:152`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/tests/test_phase2_5_integrity.py#L152) | Documented that v1.0 benchmark has 2,000 independent semantic groups. | `test_dataset_contamination_and_exact_duplicates` is marked `@pytest.mark.xfail`, allowing pytest to pass while v1.0 remains 100% contaminated. | Keep v1.0 archived as deprecated; ensure all Phase 3 scripts point strictly to validated, decontaminated partitions. |

---

## 3. Discrepancy Forensic Deep-Dive

### 3.1 DISC-01: The Synthetic Padding Flaw
In `build_decontaminated_benchmark_v1_1.py`, facts 1 to 75 are high-quality, authentic Indian facts (PM-KISAN, MSME, Chandrayaan-3, Keezhadi, NIRF, etc.), and facts 281 to 300 are genuine OOD comparative/regulatory items.
However, to bridge the gap from 75 to 280, the generator ran a synthetic loop:
```python
while len(facts) < 280:
    idx = len(facts) + 1
    dom = domains_cycle[idx % len(domains_cycle)]
    tf_id = f"TF-{(idx % 10) + 1:02d}"
    facts.append({
        "fact_id": idx,
        "entity": f"National_{dom.capitalize()}_Registry_Unit_{idx}",
        "fact": f"Statutory Clause {idx} of the National {dom.capitalize()} Framework establishes parameter threshold {idx * 10} for regulated institutions.",
        "answer": f"Parameter threshold {idx * 10}.",
        "source": f"https://{dom}.gov.in/gazette/clause{idx}",
        ...
    })
```
- **Reviewer Attack:** An EMNLP reviewer would notice that `https://governance.gov.in/gazette/clause76` does not exist, and that `National_Governance_Registry_Unit_76` is not a real Indian institution.
- **Scientific Consequence:** Any claim that all 1,500 groups are "grounded in authentic Indian gazettes" is partially false. Only facts 1–75 and 281–300 (95 unique factual topics, generating 475 semantic groups) are authentically grounded; the remaining 1,025 groups are synthetic formulaic patterns.

### 3.2 DISC-02: Conflating Pilot Human Agreement with Candidate Benchmark
- In Phase 2, three human annotators evaluated $N = 150$ semantic groups (750 prompts) from the pilot/hardening dataset, yielding Fleiss' $\kappa = 0.719$.
- In Phase 2.6, when `IndraLLM-CS-v1.1-CANDIDATE` was synthesized, the report claimed:
  `G8 Human Agreement: Fleiss kappa = 0.719 -> PASS`.
- **Reviewer Attack:** No native speakers annotated `IndraLLM-CS-v1.1-CANDIDATE`. Carrying over an agreement metric from an older pilot dataset to a new, differently generated dataset is methodologically invalid.

### 3.3 DISC-03: Entity Insertion Distorting Condition CMI
In `build_decontaminated_benchmark_v1_1.py`:
```python
b_q = f"{name} के संबंध में मुख्य नियम, तिथि या मापदंड क्या है?"
```
Because `{name}` is in English (e.g. `"Central Rice Research Institute"` or `"National_Agriculture_Registry_Unit_80"`), the `B_NATIVE` condition prompt became a code-mixed prompt containing Latin script!
- Consequently, `B_NATIVE` CMI was measured at **$16.75\%$** (instead of near $0.0\%$), and `C_ROMAN` ($14.55\%$) had *lower* measured CMI than native script!
- This contradicts the benchmark's core operational definition of `B_NATIVE` as monolingual native script.

---

## 4. Required Action Plan Before Phase 3 Authorization

1. **Reclassify Gate Statuses:** Reclassify G8 (Human Agreement) and G9 (Naturalness) on v1.1-CANDIDATE as **UNVERIFIED**.
2. **Transparently Disclose Benchmark Composition:** Formally document that v1.1-CANDIDATE consists of a verified core (95 facts / 475 groups) and a synthetic scaling tier (205 facts / 1,025 groups).
3. **Conduct Dedicated Adversarial Duplicate and OOD Audits:** Quantify exact leakage across both tiers.
