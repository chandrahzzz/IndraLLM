# IndraLLM — Code-Switched Hallucination Benchmark for Indian Languages

**Two contributions:**

1. **IndraLLM-Benchmark** — 5,000 human-annotated (question, answer) pairs in 5 code-switched
   Indian language pairs (Tamil-, Hindi-, Telugu-, Bengali-, Kannada-English), labeled
   *Correct* or *Hallucinated* (+ category: Factual / Temporal / Entity / Cultural).
2. **Mitigation** — fine-tuned IndicBERT hallucination detector + multilingual contrastive
   decoding for Sarvam-2B that reduces hallucination rate on code-switched input.

## Pipeline

```
collect (Twitter/Reddit/forms) → filter (code-switch verify) → build questions
    → generate answers (8 LLMs) → annotate (Label Studio, 2 annotators, κ ≥ 0.75)
    → aggregate labels → train IndicBERT detector → contrastive decoding on Sarvam-2B
    → evaluate → push to HuggingFace Hub
```

## Setup

```bash
git clone https://github.com/chandrahzzz/IndraLLM.git
cd IndraLLM
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env           # then fill in API keys
python -m indrallm.collection.download_models   # fetches fasttext lid.176.bin
```

> API keys, the fastText model, trained models, and generated data are
> git-ignored (see `.gitignore`). Never commit `.env`.

## Run order

| Step | Command | Where |
|---|---|---|
| 1. Collect Twitter | `python -m indrallm.collection.twitter_collector --lang ta --max 2000` | laptop |
| 2. Collect Reddit | `python -m indrallm.collection.reddit_collector --max 2000` | laptop |
| 3. Ingest Google Forms CSV | `python -m indrallm.collection.forms_ingest --csv data/raw/forms.csv` | laptop |
| 4. Filter code-switched | `python -m indrallm.collection.codeswitch_filter` | laptop |
| 5. Generate LLM answers | `python -m indrallm.generation.generate_answers --models gpt-4o claude sarvam` | laptop (API) |
| 6. Export to Label Studio | `python -m indrallm.annotation.label_studio_setup --export` | laptop |
| 7. Compute agreement | `python -m indrallm.annotation.agreement` | laptop |
| 8. Aggregate final labels | `python -m indrallm.annotation.aggregate_labels` | laptop |
| 9. Train detector | `python -m indrallm.detection.train_indicbert` | Colab/Kaggle GPU |
| 10. Mitigation decode | `python -m indrallm.mitigation.contrastive_decoding --eval` | Colab/Kaggle GPU |
| 11. Benchmark 8 models | `python -m indrallm.evaluation.run_benchmark` | laptop + GPU |
| 12. Publish dataset | `python -m indrallm.publish.push_to_hub` | laptop |

GPU steps on Colab: see [docs/COLAB.md](docs/COLAB.md).

## Data layout

```
data/
  raw/          scraped tweets/posts/forms, unfiltered
  filtered/     verified code-switched text
  questions/    final question set (5 × 1000)
  answers/      per-model generated answers
  annotations/  Label Studio exports, per-annotator
  final/        aggregated labeled dataset (train/val/test)
```

## Note on Twitter API

Free academic access to Twitter/X API v2 was discontinued; Basic tier is paid.
Fallbacks that work today: Reddit (free via PRAW), Google Forms crowdsourcing (VIT
students), and seeding from existing code-switch corpora (L3Cube HingCorpus,
Dakshina, LinCE) then rewriting into questions. The Twitter collector is included
in case institutional access is available.

## Target venues

ACL 2027 Findings, EMNLP 2026, TALLIP (rolling).
