# IndraLLM — Related Work & Competitive Benchmark Matrix

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Scope:** Multilingual Hallucination, Indian Language LLMs, Code-Switching, Factuality Detection & Mitigation  

---

## 1. Literature Positioning Overview

The intersection of Large Language Models (LLMs), Indian languages, code-switching, and factuality has historically suffered from fragmented focus. Most prior works investigate either:
1. **Monolingual Indian language benchmarks** (evaluating translation, NLU, or general knowledge without code-switching);
2. **Code-switching linguistics and generation** (evaluating perplexity, fluency, or sentiment without evaluating factual hallucination); or
3. **English-centric hallucination benchmarks** (evaluating factuality and knowledge retrieval with zero cross-script or code-mixing coverage).

IndraLLM bridges this critical gap through **semantically matched 5-condition pairing** ($EN \leftrightarrow Native \leftrightarrow Roman \leftrightarrow CS \leftrightarrow Mixed$), isolating the causal effect of code-switching and script choice on factual reliability.

---

## 2. Competitive Benchmark Comparison Matrix

| Paper / Benchmark | Year | Venue | Languages | Code-Switching? | Hallucination? | Human Gold Eval? | Controlled Semantic Pairing? | Detector Built? | Mitigation Studied? | Main Limitation | How IndraLLM Differs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **BHRAM-IL** (Chakraborty et al.) | 2024 | EMNLP | 10+ Indic | ❌ Monolingual only | ✅ Yes | Partial | ❌ No | ❌ No | ❌ No | Tests only native script monolingual inputs; completely ignores code-switching and Romanization. | IndraLLM explicitly tests code-switching, Romanization, mixed scripts, with controlled semantic pairing. |
| **IndicGLUE** (Kakwani et al.) | 2020 | EMNLP | 11 Indic | ❌ No | ❌ No (NLU tasks) | ✅ Yes | ❌ No | ❌ No | ❌ No | Classical pre-LLM NLU tasks (sentiment, NLI); no hallucination evaluation. | IndraLLM is dedicated to factual hallucination under generative LLM regimes. |
| **Airavata** (Gala et al.) | 2024 | ACL Findings | Hindi + Indic | ❌ Minimal | ❌ Instruction follow | Partial | ❌ No | ❌ No | ❌ SFT only | Focuses on instruction-tuning datasets for Hindi; no factuality error analysis. | IndraLLM isolates factuality failure modes across 5 languages and 5 orthographic conditions. |
| **CoSDA-ML** (Qin et al.) | 2020 | IJCAI | Multilingual | ✅ Data Augment | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No | Code-switching used solely for data augmentation in classification; no factual reliability study. | IndraLLM investigates code-switching as a primary variable impacting model truthfulness. |
| **LinCE Benchmark** (Aguilar et al.) | 2020 | LREC | Spanish, Hindi, etc. | ✅ Yes | ❌ No (POS, NER) | ✅ Yes | ❌ No | ❌ No | ❌ No | Traditional sequence tagging on code-switched text; no generative LLM factuality. | IndraLLM evaluates generative hallucination, continuous CMI, and factuality preservation. |
| **HaluEval** (Wang et al.) | 2023 | EMNLP | English | ❌ Monolingual English | ✅ Yes | ✅ Yes | ❌ No | ✅ Simple NLI | ❌ No | Strictly English; fails under South Asian multilingual and non-standard orthographic contexts. | IndraLLM provides cross-lingual, cross-script, and code-mixing factual evaluation. |
| **FActScore** (Min et al.) | 2023 | EMNLP | English | ❌ Monolingual English | ✅ Yes (Atomic facts) | ✅ Yes | ❌ No | ❌ Retrieval only | ❌ No | Atomic fact decomposition is English-specific and brittle on code-switched inputs. | IndraLLM provides human-grounded tri-layer evaluation calibrated on bilingual code-switched text. |
| **Cross-Lingual Factuality** (Zhang et al.) | 2024 | ACL | High-resource multilingual | ❌ Monolingual | ✅ Yes | Partial | ⚠️ Parallel translations | ❌ No | ❌ No | Parallel translation between high-resource languages (EN/FR/DE/ZH); no code-switching or Romanization. | IndraLLM studies intra-sentential mixing, Romanization, and subword fragmentation in low/mid-resource Indic languages. |
| **IndraLLM (Ours)** | **2026** | **Target: ACL/EMNLP** | **5 Indic + English** | **✅ Continuous CMI & Script** | **✅ Core focus** | **✅ 3 bilingual raters** | **✅ 5-way semantic tuples** | **✅ Multi-view OOD benchmark** | **✅ SFT/Distill/DPO Pareto frontier** | None of the above combine controlled pairing, continuous CMI, human gold, OOD detection, and mitigation. | **First controlled benchmark isolating orthography, CMI, and language mixing effects on LLM factuality.** |

---

## 3. Methodological Differentiation Summary

1. **Why Not Just BHRAM-IL?**
   BHRAM-IL was a crucial milestone establishing hallucination rates in monolingual Indian languages. However, in reality, over 70% of digital Indian communication on mobile devices and social platforms is **code-switched with English and written in the Latin alphabet (Romanized)**. A system evaluated solely on native script Devanagari or Tamil script tests an artificial distribution. IndraLLM is the first to test whether code-switching and Romanization introduce independent, measurable degradation in factual reliability when the underlying question is semantically identical.

2. **Why Controlled Semantic Pairing is Mandatory:**
   Prior multilingual benchmarks compare a set of English questions against a different set of Hindi or Tamil questions. If accuracy on Tamil is lower, one cannot determine whether:
   - The Tamil questions were harder;
   - The entities queried are low-resource / geographically obscure; or
   - The linguistic representation caused the error.
   By holding the semantic unit $S_i$ strictly invariant across Condition A (English), Condition B (Native), Condition C (Roman), Condition D (Code-Switched), and Condition E (Mixed-Script), IndraLLM provides the first scientifically defensible test of linguistic representation effects.
