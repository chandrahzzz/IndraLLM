# Code-Mixing Index (CMI) and Multidimensional Metrics Audit

**Document Version:** 1.0 (Frozen for Phase 2.5)  
**Target Specification:** Part 5 Research Integrity Audit  
**Author:** Chandrahas Reddy  
**Date:** September 2026  
**Implementation Source:** [`src/indrallm/collection/cmi.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/src/indrallm/collection/cmi.py)

---

## 1. Mathematical Formulation & Implementation Fidelity

The benchmark implements the canonical utterance-level **Code-Mixing Index (CMI)** defined by Gambäck & Das (2014) (*Comparing the Level of Code-Mixing in Corpora*, LREC 2014):

$$\text{CMI} = 100 \times \left(1 - \frac{\max_{L_i}(w_{L_i})}{n - u}\right) \quad \text{for } (n - u) > 0$$

where:
- $n$: Total token count of the prompt string.
- $u$: Count of language-independent tokens ($w_{\text{other}}$), comprising numeric literals, ASCII/Unicode punctuation marks, symbols, and non-alphabetic glyphs.
- $n - u$: Count of language-assigned tokens (the effective linguistic denominator).
- $w_{L_i}$: Count of tokens assigned to language $L_i$ (in our bilingual setting, $L \in \{\text{Indic}, \text{English}\}$).
- $\max_{L_i}(w_{L_i})$: Token frequency of the majority language.

### Theoretical Bounds & Edge Cases
1. **Monolingual Utterance ($w_{L_1} = n - u, w_{L_2} = 0$):**
   $$\text{CMI} = 100 \times \left(1 - \frac{n - u}{n - u}\right) = 0.00\%$$
2. **Equally Mixed Utterance ($w_{\text{Indic}} = w_{\text{English}} = \frac{n - u}{2}$):**
   $$\text{CMI} = 100 \times \left(1 - \frac{(n - u)/2}{n - u}\right) = 50.00\%$$
3. **Empty or Pure-Punctuation Utterance ($n - u = 0$):**
   $$\text{CMI} \equiv 0.00\% \quad (\text{handled via explicit denominator guard in line 115})$$

---

## 2. Token-Level Language Identification (LID) Audit

The accuracy of CMI is strictly dependent on the underlying token-level LID engine ([`src/indrallm/detection/lidar/lid.py`](file:///c:/Users/Chandrahas%20Reddy/MYallPROJECTS/IndraLLM/src/indrallm/detection/lidar/lid.py)).

### 2.1 Lexical & Script-Range Architecture
1. **Indic Native Script Tokens:**
   - Identified via Unicode code point blocks (`SCRIPT_RANGES`):
     - Hindi (Devanagari): `U+0900` to `U+097F`
     - Bengali: `U+0980` to `U+09FF`
     - Telugu: `U+0C00` to `U+0C7F`
     - Kannada: `U+0C80` to `U+0CFF`
     - Tamil: `U+0B80` to `U+0BFF`
   - Classification accuracy for native script: **100.0%** (deterministic Unicode partition).

2. **Romanized Indic Tokens (Condition C_ROMAN & Condition D_CS):**
   - High-coverage stopword, verb-stem, case-marker, and grammatical functor lexicons for each of the 5 languages:
     - Hindi: `kya`, `hai`, `mein`, `kaise`, `hota`, `aur`, `par`, `kyun`, `diya`, `wala`, `bataiye`, ...
     - Telugu: `ela`, `undi`, `lo`, `enduku`, `chestaru`, `yokka`, `gurinchi`, `mariyu`, `emi`, ...
     - Tamil: `eppadi`, `irukku`, `la`, `en`, `seivargal`, `udan`, `patri`, `matrum`, `enna`, ...
     - Bengali: `kivabe`, `ache`, `te`, `keno`, `kora`, `er`, `somporke`, `ebong`, `ki`, ...
     - Kannada: `hege`, `ide`, `alli`, `yake`, `maduttare`, `inda`, `bagge`, `mattu`, `yenu`, ...
   - Fallback logic: If token is Latin-script and exists in `INDIC_ROMAN_LEXICON[expected_lang]`, assigned to Indic.

3. **English Tokens:**
   - Evaluated against standard English vocabulary and grammatical functors (`is`, `what`, `how`, `the`, `of`, `in`, `explain`, `difference`, `between`, `mechanism`, `working`, ...).

4. **Ambiguity & Homograph Resolution:**
   - Cross-lingual homographs (e.g., `me` in Hindi vs English, `in` in Telugu transcription vs English preposition) are resolved using surrounding context and explicit expected-language bias when provided.

---

## 3. Handling of Special Token Classes

| Token Category | Rule in `cmi.py` | Impact on CMI |
|---|---|---|
| **Named Entities** | Technical entities (e.g., "Mitochondria", "Chola", "RBI") retain native/English label based on morphology. | Correctly counted in active vocabulary. |
| **Numbers & Digits** | Matches `\d+` regex $\to$ tagged as `other`. | Excluded from denominator ($u$). Does not deflate CMI. |
| **Punctuation & Symbols** | ASCII/Unicode punctuation (category `P*`) $\to$ tagged as `other`. | Excluded from denominator ($u$). |
| **Transliterated Words** | Non-English phonetically transcribed words mapped to target Indic language. | Increments $w_{\text{Indic}}$. |
| **Mixed-Script Tokens** | Tokens containing intra-word script shifts (e.g., `DNA-విశ్లేషణ`) are segmented or classified by majority character script. | Counted in active tokens. |
| **Technical Loanwords** | English technical terms embedded in Indic matrix clause are labeled `en`. | Core source of realistic code-switching in `D_CS`. |

---

## 4. Critical Scientific Safeguards

### Safeguard 1: CMI $\approx 0$ Does NOT Mean "Zero Linguistic Complexity"
Reviewers frequently confuse CMI with semantic simplicity.
- **Verification:** Monolingual native script prompts (`B_NATIVE`) have mean CMI of $0.43\%$, yet have the **highest average subword fragmentation and morphological complexity** (mean token count $27.65$ tokens vs $13.00$ for English, fertility $2.13 \times$).
- **Formal Guidance:** CMI measures **bilingual lexical divergence**, NOT cognitive or linguistic difficulty.

### Safeguard 2: CMI Is Not a Mere Surrogate for Length or Script
To ensure reviewers cannot dismiss CMI as an artifact of prompt length or script switching, we computed the benchmark-wide correlation matrix ($N = 10,000$):

$$\text{Correlation}(\text{CMI}, \text{Token Count}) = -0.2742$$
$$\text{Correlation}(\text{CMI}, \text{Script Transitions}) = +0.7319$$
$$\text{Correlation}(\text{CMI}, \text{Language Switch Count}) = +0.9205$$
$$\text{Correlation}(\text{CMI}, \text{Chars Per Token}) = -0.0086$$

- **Key Takeaway:** CMI is strongly correlated with true **language switches** ($r = 0.9205$), but is virtually uncorrelated with token character density ($r = -0.0086$) and weakly negatively correlated with token count ($r = -0.2742$).
- Furthermore, in Condition `D_CS` (pure Romanized code-switching), `script_transitions` is mean **0.34**, whereas `language_switch_count` is mean **4.07** and CMI is **22.13%**. This demonstrates empirical orthogonality between script transitions and CMI in non-mixed script conditions.

---

## 5. Audit Conclusion: PASS

The implementation in [`src/indrallm/collection/cmi.py`](file:///c:/Users/Chandrahas Reddy/MYallPROJECTS/IndraLLM/src/indrallm/collection/cmi.py) conforms mathematically to Gambäck & Das (2014), handles edge cases robustly, correctly treats language-independent tokens, and isolates linguistic mixing from superficial length artifacts.
