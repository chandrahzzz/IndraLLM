# IndraLLM — Phase 2A: Pre-Scale Scientific & Methodological Audit

**Date:** 2026-09-29  
**Branch:** `research-redesign`  
**Review Standard:** ACL/EMNLP Reviewer & Factuality Experimentalist  
**Purpose:** Rigorous pre-scale verification of Phase 1 artifacts before expanding benchmark data generation.

---

## 1. Semantic Equivalence Audit: Automated vs. Human Grounding

### Finding:
In Phase 1, the preliminary pilot report logged an automated semantic equivalence gate of `100.0%`. 

### Critical Methodological Distinction:
1. **Automated Semantic Similarity ($100\%$):** This metric was derived from paired prompt generation templates seeded from identical canonical fact tuples. Because all five condition prompts ($A\_EN, B\_NATIVE, C\_ROMAN, D\_CS, E\_MIXED\_SCRIPT$) were generated simultaneously from a single underlying factual context, syntactic equivalence was nominally preserved.
2. **Human Bilingual Verification:** In the sample audit ($N=50$ groups, 250 condition prompts), native speakers verified that the query entity was identical across conditions. However, nuanced pragmatics differed:
   - For example, Romanized Condition C (*"PM-Kisan yojana ke antargat saalana kitni vittiya sahayata di jaati hai?"*) carries formal register, whereas Condition D (*"PM-Kisan scheme me annually kitna financial support milta hai?"*) uses conversational loanwords.
3. **Evidence-Based Grounding:** For $100\%$ of the pilot seeds, an authoritative source URL (`pmkisan.gov.in`, `isro.gov.in`, `nha.gov.in`) and exact excerpt were present and verified.

### Action for Phase 2 Scale:
- Do NOT conflate structural template equivalence with human semantic equivalence.
- Report automated template equivalence as **100% structural correspondence**, and report human-verified semantic fidelity as an independent metric with binomial confidence intervals ($\pm 2.1\%$).

---

## 2. CMI Implementation Audit & The "D_CS vs. E_MIXED_SCRIPT" Discrepancy

### The Phenomenon:
In the Phase 1 pilot:
- **Condition D (Romanized Code-Switching):** $\text{Mean CMI} \approx 5.38$ (Bengali: $2.00$, Tamil: $1.75$, Telugu: $2.92$, Hindi: $9.87$, Kannada: $10.38$)
- **Condition E (Mixed-Script Code-Switching):** $\text{Mean CMI} \approx 44.96$

### Root-Cause Diagnostic Analysis:
A deep inspection of `src/indrallm/collection/cmi.py` and `src/indrallm/detection/lidar/lid.py` reveals the exact mechanism:

```
Condition E (Mixed Script):
"Tamil Nadu-வின் capital city என்ன?"
    Tokens: [Tamil (Latin), Nadu (Latin), வின் (Tamil Script), capital (Latin), city (Latin), என்ன (Tamil Script)]
    Script Detector: Checks Unicode block (0B80-0BFF) -> 100% accurate classification.
    Result: 4 Latin tokens, 2 Tamil tokens -> CMI = 100 * (1 - 4/6) = 33.3% - 50.0%.

Condition D (Romanized Script):
"Tamil Nadu oda capital city enna?"
    Tokens: [Tamil, Nadu, oda, capital, city, enna]
    Script Detector: ALL tokens are Latin script!
    Fallback LID: Relies on ROMANIZED_HINTS dictionary (~25 words per language).
    Failure 1: "oda" was MISSING from ROMANIZED_HINTS["ta"]. It fell back to _is_latin() -> labeled "en"!
    Failure 2: "me" in Hindi ("scheme me") was labeled "en" because "me" is an English pronoun!
    Failure 3: Named entities ("Tamil", "Nadu", "Kisan") labeled "en".
    Result: Only 1 token ("enna") recognized as Tamil -> 5 "en" vs 1 "ta" -> CMI = 16.6%, or 0% if no dictionary hit.
```

### Diagnostic Comparison Table:

| Linguistic Dimension | Condition D (`D_CS`: Romanized CS) | Condition E (`E_MIXED_SCRIPT`) | Why the Measured CMI Diverged |
|---|---|---|---|
| **Underlying Language Mix** | 40–50% Indic words, 50–60% English | 40–50% Indic words, 50–60% English | Both conditions have **comparable lexical mixing**; semantic intent is identical. |
| **Orthography** | 100% Latin Alphabet | Unicode Indic Script + Latin Alphabet | Orthography triggers distinct code paths in the classifier. |
| **Token LID Mechanism** | Small dictionary lookup + fastText fallback | Exact Unicode Code-Point Script Ranges | Script range is deterministic; dictionary lookup suffers extreme false-negative rate on Romanized morphology. |
| **Cross-Lingual Homographs** | Severe collision (`me`, `to`, `is`, `in`, `no`) | Zero collision (Indic scripts are unique) | English pronouns/prepositions clobber Romanized Indic markers. |
| **Empirical CMI Result** | $\mathbf{5.38}$ (Artificially Depressed) | $\mathbf{44.96}$ (Accurate Script-Level CMI) | **The divergence is an artifact of token LID failure on Romanized text, not genuine linguistic composition.** |

### Methodological Remediation:
1. **Multi-Dimensional Code-Mixing Suite:** Replace the single CMI scalar with a comprehensive profile:
   - Gambäck & Das CMI (calibrated)
   - English token ratio ($w_{en} / N$)
   - Native-language token ratio ($w_{indic} / N$)
   - Language switch count ($S_{lang}$)
   - Switch point density ($S_{lang} / (N - 1)$)
   - Script transition count ($S_{script}$)
   - Token fertility ($\text{subwords} / \text{word}$)
2. **Expanded Phonetic Lexicons & Suffix Stripping:** Expand `ROMANIZED_HINTS` across all 5 languages to include case markers and postpositions (`oda`, `la`, `kku`, `lo`, `ki`, `er`, `te`, `alli`, `ge`, `mein`, `se`, `ko`).

---

## 3. Annotation Agreement Audit: What Does $\kappa \approx 0.719$ Mean?

### Deconstruction:
- **Task:** 3 independent bilingual raters evaluated binary factual accuracy ($0 = \text{Hallucinated}, 1 = \text{Correct}$) against verified reference evidence snippets.
- **Sample:** $N = 250$ prompt evaluations across 5 languages.
- **Label Distribution:** 81.2% Correct, 18.8% Hallucinated/Error.
- **Observed Metrics:**
  - Fleiss' $\kappa = 0.7190$
  - Krippendorff's nominal $\alpha = 0.7194$
  - Mean pairwise Cohen's $\kappa = 0.7193$

### Disagreement Case Inspection:
Manual audit of the discordant evaluations reveals two primary failure modes:
1. **Granularity Disagreement (Partial vs. Complete Error):**
   - *Query:* "During which century and dynasty was ancient Nalanda University founded?"
   - *Model Answer:* "5th century by Gupta rulers, specifically Chandragupta II."
   - *Conflict:* Rater 1 marked [1] Hallucinated (Gupta dynasty and 5th century are correct, but founder was Kumaragupta I, not Chandragupta II). Rater 2 marked [0] Correct (focused on 5th century Gupta empire).
   - *Protocol Fix:* Guidelines must explicitly state: **Any factual entity substitution (e.g. naming the wrong emperor) constitutes a factual error, even if the dynasty is correct.**
2. **Numerical Rounding / Format Variation:**
   - *Query:* Annual financial support under PM-KISAN.
   - *Model Answer:* "₹2000 thrice a year (6000 total)."
   - *All raters agreed: [0] Correct.*

---

## 4. Naturalness & Code-Switch Fidelity Audit

### Distribution & Confidence Intervals:
- **Sample:** 50 semantic groups $\times$ 5 conditions = 250 items.
- **Ratings:** 5-point Likert scale (1 = completely unnatural, 5 = fully natural bilingual conversational flow).
- **Observed Mean:** $4.74 \pm 0.48$ ($95\% \text{ CI } [4.68, 4.80]$).
- **Condition Breakdown:**
  - Condition A (English): $5.00$
  - Condition B (Native Monolingual): $4.96$
  - Condition C (Romanized Monolingual): $4.18 \pm 0.62$ (Some raters penalize formal Romanized text as awkward compared to code-mixing).
  - Condition D (Natural Code-Switching): $4.78 \pm 0.42$ (High naturalness; matches real texting behavior).
  - Condition E (Mixed-Script): $4.42 \pm 0.58$ (Accepted in digital signage/social media, but slightly less common in everyday typing than pure Latin Romanization).

---

## 5. Evidence Quality Audit

Every factual item in the pilot was inspected against four criteria:
1. **Source Verifiability:** $100\%$ of items map to verified domains (`pmkisan.gov.in`, `nha.gov.in`, `soilhealth.dac.gov.in`, `isro.gov.in`, `asi.nic.in`, `nirfindia.org`, `nhm.gov.in`).
2. **Temporal Validity:** Temporal markers (e.g. Chandrayaan-3 landing date "August 23, 2023", NIRF launch "September 29, 2015") are explicit and immutable.
3. **Answer Groundedness:** Every canonical answer is directly entailed by the 1–3 sentence evidence excerpt without requiring unstated assumptions.
4. **Source Type Classification:** All sources are classified as `govt_portal` ($66.7\%$) or `official_archive` ($33.3\%$).

---

## Conclusion & Pre-Scale Verdict

- **Pre-Scale Audit Verdict:** **PASSED WITH METHODOLOGICAL CORRECTIONS REQUIRED.**
- **Remediations to execute before scaling to 2,000 groups:**
  1. Upgrade `src/indrallm/collection/cmi.py` with expanded romanized postposition lexicons and multi-dimensional metrics (CMI, EN ratio, Native ratio, switch count, switch density, script transitions, fertility).
  2. Implement hardening set (Phase 2B) with obscure entities, temporal nuance, and multi-hop questions before large-scale freezing.
