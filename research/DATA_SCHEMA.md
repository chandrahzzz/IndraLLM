# IndraLLM — Formal Data Schema & Provenance Specification

**Document Version:** 1.0  
**Date:** 2026-09-29  
**Specification:** Semantically Paired Benchmark Schema (v1.0)  

---

## 1. Relational Entity Architecture

The benchmark transitions from disconnected text rows into a relational, semantically paired graph:

```
                      [Semantic Group S_i]
           (1 canonical question, ground truth, evidence)
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
         [Condition A]   [Condition B]   [Condition D] ...
           (English)       (Native)         (CS)
               │               │               │
               └───────────────┼───────────────┘
                               │
                               ▼
                    [Model Response M_j]
                (Raw generated text, tokens)
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       [Automated Judge]              [Human Gold Label]
  (Dual LLM, NLI, BertScore)   (3 Independent Bilingual Raters)
```

---

## 2. Table Specifications

### 2.1 Table 1: `semantic_questions.jsonl` / `parquet`
*The fundamental invariant unit containing verified factual ground truth.*

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `semantic_id` | `VARCHAR(16)` | Primary Key, `^S[0-9]{6}$` | Unique identifier for semantic concept (e.g., `S000101`) |
| `domain` | `VARCHAR(32)` | Enum: `[governance, agriculture, education, history, science, public_health]` | High-level knowledge domain |
| `subdomain` | `VARCHAR(64)` | Non-null | Fine-grained subject matter |
| `canonical_fact` | `TEXT` | Non-null | Clear statement of the underlying fact being queried |
| `reference_answer` | `TEXT` | Non-null | Concise canonical answer to the question |
| `evidence_snippet` | `TEXT` | Non-null | Authoritative 1–3 sentence excerpt validating the answer |
| `evidence_source_url`| `VARCHAR(512)`| Valid URL or citation | Permanent link or DOI to authoritative source |
| `evidence_source_type`| `VARCHAR(32)` | Enum: `[govt_portal, academic_encyclopedia, census, official_archive, peer_reviewed]` | Categorization of external authority |
| `difficulty_level` | `INTEGER` | Range: `[1, 5]` | 1: Simple factual, 2: Specific entity, 3: Multi-hop, 4: Temporal nuance, 5: Adversarial |
| `created_timestamp`| `TIMESTAMP` | UTC | Ingestion timestamp |

### 2.2 Table 2: `condition_prompts.jsonl` / `parquet`
*Controlled linguistic transformations of the semantic questions.*

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `prompt_id` | `VARCHAR(32)` | Primary Key, `^{semantic_id}_[A-E]_[a-z]{2}$` | e.g., `S000101_D_ta` (Semantic 101, Condition D, Tamil) |
| `semantic_id` | `VARCHAR(16)` | Foreign Key $\to$ `semantic_questions` | Parent semantic group |
| `language` | `VARCHAR(8)` | Enum: `[en, hi, ta, te, bn, kn]` | Primary Indian language involved (or `en`) |
| `condition` | `VARCHAR(16)` | Enum: `[A_EN, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT]` | Experimental condition |
| `script` | `VARCHAR(16)` | Enum: `[latin, devanagari, tamil, telugu, bengali, kannada, mixed]` | Script used |
| `prompt_text` | `TEXT` | Non-null | Exact prompt presented to the LLM |
| `measured_cmi` | `FLOAT` | Range: `[0.0, 100.0]` | Token-level Code-Mixing Index |
| `token_count` | `INTEGER` | $> 0$ | Word token count |
| `script_transitions`| `INTEGER`| $\ge 0$ | Number of script switches in the prompt |
| `validation_status`| `VARCHAR(16)` | Enum: `[unverified, human_validated, rejected]` | Quality status from native bilingual audit |

### 2.3 Table 3: `model_responses.jsonl` / `parquet`
*Raw, immutable outputs from evaluated models.*

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `response_id` | `VARCHAR(64)` | Primary Key | e.g., `S000101_D_ta_llama3_70b_s42` |
| `prompt_id` | `VARCHAR(32)` | Foreign Key $\to$ `condition_prompts` | Prompt that generated this response |
| `semantic_id` | `VARCHAR(16)` | Foreign Key $\to$ `semantic_questions` | Redundant foreign key for partition filtering |
| `model_name` | `VARCHAR(64)` | Non-null | Identifier (e.g., `meta-llama/Llama-3.3-70B-Instruct`) |
| `model_family` | `VARCHAR(32)` | Enum: `[llama, qwen, sarvam, airavata, gemma, mistral]` | Model family |
| `inference_engine`| `VARCHAR(32)` | Enum: `[groq_api, vllm_local, hf_transformers]` | Execution runtime |
| `temperature` | `FLOAT` | Typically `0.3` or `0.0` | Sampling temperature |
| `top_p` | `FLOAT` | Typically `0.9` | Nucleus sampling |
| `response_text` | `TEXT` | Non-null | Raw untruncated model generation |
| `output_tokens` | `INTEGER` | $\ge 0$ | Number of generated tokens |
| `response_cmi` | `FLOAT` | Range: `[0.0, 100.0]` | CMI of the generated answer |
| `refusal_flag` | `BOOLEAN` | True/False | Automatic regex & classifier detection of model refusal |
| `timestamp` | `TIMESTAMP` | UTC | Time of inference |

### 2.4 Table 4: `evaluations_automated.jsonl` / `parquet`
*Automated judgment and metrics for every model response.*

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `eval_id` | `VARCHAR(64)` | Primary Key | Evaluation record identifier |
| `response_id` | `VARCHAR(64)` | Foreign Key $\to$ `model_responses` | Target response |
| `judge_name` | `VARCHAR(32)` | Enum: `[llama3_8b_judge, gemini_flash_judge, qwen_judge, nli_deberta]` | Evaluating judge |
| `judge_verdict` | `INTEGER` | Enum: `[0, 1]` | 0 = Faithful / Correct, 1 = Hallucinated |
| `judge_confidence`| `FLOAT` | Range: `[0.0, 1.0]` | Model confidence or logit probability |
| `reasoning_snippet`| `TEXT` | Max 256 chars | Extracted explanation from judge |
| `bertscore_f1` | `FLOAT` | Range: `[-1.0, 1.0]` | Token-level semantic similarity to reference |
| `rouge_l` | `FLOAT` | Range: `[0.0, 1.0]` | Longest common subsequence recall |

### 2.5 Table 5: `human_gold_annotations.jsonl` / `parquet`
*Gold-standard ground-truth human annotations.*

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `annotation_id` | `VARCHAR(64)` | Primary Key | e.g., `ANN_S000101_D_ta_R1` |
| `response_id` | `VARCHAR(64)` | Foreign Key $\to$ `model_responses` | Evaluated response |
| `annotator_id` | `VARCHAR(16)` | Anonymized (e.g., `RATER_01`) | Unique bilingual rater ID |
| `annotator_language`| `VARCHAR(8)` | Native language of rater | Must match target language |
| `factual_accuracy`| `INTEGER` | Enum: `[0, 1]` | 0 = Inaccurate / Hallucinated, 1 = Factually Correct |
| `hallucination_severity`| `INTEGER`| Enum: `[0, 1, 2, 3]` | 0: None, 1: Minor entity slip, 2: Contradiction, 3: Complete fabrication |
| `naturalness_score`| `INTEGER` | Likert: `[1, 5]` | 1: Unnatural / Broken, 5: Fully natural native code-switch |
| `language_fidelity`| `INTEGER` | Likert: `[1, 5]` | 1: Monolingual English, 5: Balanced appropriate mixing |
| `time_spent_seconds`| `INTEGER` | $> 0$ | Verification duration |

---

## 3. Benchmark Splitting Strategy & Leakage Rules

To prevent data contamination and spurious memorization, 6 canonical splits are defined:

1. **Random Split (`split_random`):** Stratified 80/10/10 split partitioned strictly by `semantic_id`. All conditions ($A-E$) for a given `semantic_id` reside in the same split.
2. **Question-Disjoint Split (`split_qid_disjoint`):** Guarantees zero lexical, entity, or template overlap between train and test.
3. **Domain-Disjoint Split (`split_domain_disjoint`):** Holds out entire domains (e.g., train on 5 domains, test on `public_health` and `agriculture`).
4. **Language-Disjoint Split (`split_lolo`):** Leave-One-Language-Out evaluation for detector transfer.
5. **Model-Disjoint Split (`split_lomo`):** Leave-One-Model-Family-Out for detector cross-model generalization.
6. **Hard Evaluation Split (`split_hard`):** Difficulty levels 4 and 5 (temporal nuance, entity ambiguity).

---

## 4. Storage Architecture & Immutability Rules

```
data/
  ├── raw/                  <-- IMMUTABLE: external source texts, seed catalogs
  ├── questions/
  │     ├── semantic/       <-- semantic_questions.jsonl
  │     └── conditions/     <-- condition_prompts.jsonl
  ├── outputs/
  │     └── {model_id}/     <-- model_responses.jsonl (resumable, immutable)
  ├── annotations/
  │     ├── automated/      <-- evaluations_automated.jsonl
  │     └── human/          <-- human_gold_annotations.jsonl
  └── final/
        └── benchmarks/     <-- Versioned parquet snapshots (v1.0-pilot, v1.0-full)
```

**Rule 1:** Files under `data/raw/` and `data/outputs/` are append-only and never modified or overwritten once written.  
**Rule 2:** All processed artifacts must be traceable via SHA256 checksum to a specific git commit and configuration file.
