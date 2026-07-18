# IndraLLM — Code-Switched Hallucination Benchmark for Indian Languages

**Zero-cost pipeline** (free Gemini tier + free Colab T4 + free Reddit API). Three contributions:

1. **IndraLLM-Benchmark** — 5,000 (question, answer) pairs in 5 code-switched
   Indian language pairs (Tamil-, Hindi-, Telugu-, Bengali-, Kannada-English),
   labeled *Correct* or *Hallucinated* via **BERTScore silver-standard labeling
   with human verification on ambiguous samples**.
2. **Detection** — fine-tuned IndicBERT hallucination detector, benchmarked
   against a zero-shot NLI judge baseline; served via a FastAPI backend.
3. **Mitigation** — multilingual contrastive decoding (inference-time) +
   QLoRA SFT (training-time) on Sarvam-2B.

## Pipeline

```
collect (Reddit + Gemini synthetic seeds) → filter (code-switch verify)
    → build gold QA (Gemini: context + question + gold answer)
    → generate answers (4 local HF models, one per Colab session)
    → auto-label (BERTScore vs gold) → human-verify ~500 ambiguous samples
    → split → train IndicBERT detector → NLI baseline
    → mitigate (contrastive decoding + QLoRA SFT) → evaluate → publish + serve
```

## Setup

```bash
git clone https://github.com/chandrahzzz/IndraLLM.git
cd IndraLLM
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env           # fill GOOGLE_API_KEY, HF_TOKEN, REDDIT_* (all free)
python -m indrallm.collection.download_models   # fetches fasttext lid.176.bin
```

> API keys, the fastText model, trained models, and generated data are
> git-ignored (see `.gitignore`). Never commit `.env`.

## Run order

| Step | Command | Where |
|---|---|---|
| 1. Collect Reddit | `python -m indrallm.collection.reddit_collector --max 2000` | laptop |
| 2. Synthetic seeds (Gemini, free) | `python -m indrallm.collection.synthetic_seeder --rounds 10` | laptop |
| 3. Ingest Google Forms CSV (optional) | `python -m indrallm.collection.forms_ingest --csv data/raw/forms.csv` | laptop |
| 4. Filter code-switched | `python -m indrallm.collection.codeswitch_filter` | laptop |
| 5. Gold QA pairs (Gemini) | `python -m indrallm.collection.build_gold_qa` | laptop |
| 6. Generate answers (ONE model per session) | `python -m indrallm.generation.generate_answers --models sarvam` | Colab GPU |
| 7. Auto-label (BERTScore) | `python -m indrallm.annotation.auto_label` | laptop |
| 8. Human-verify ambiguous → merge | `python -m indrallm.annotation.auto_label --merge-votes <csv>` | laptop |
| 9. Train/val/test splits | `python -m indrallm.annotation.aggregate_labels --auto` | laptop |
| 10. Train detector | `python -m indrallm.detection.train_indicbert` | Colab GPU |
| 11. Contrastive decoding | `python -m indrallm.mitigation.contrastive_decoding --eval --limit 1000` | Colab GPU |
| 12. QLoRA SFT (optional, stronger paper) | `python -m indrallm.mitigation.lora_finetune` | Colab GPU |
| 13. Paper tables (1–4) | `python -m indrallm.evaluation.run_benchmark` | laptop |
| 14. Publish dataset + detector | `python -m indrallm.publish.push_to_hub --detector` | laptop |
| 15. Serve detector API | `uvicorn indrallm.api.server:app --port 8000` | anywhere |

GPU steps on Colab: see [docs/COLAB.md](docs/COLAB.md). **Never load two 7B+
models in one Colab session** — generate with one model, save the CSV, restart
the runtime, load the next. hf_local models load in 4-bit by default
(`generation.load_in_4bit` in config.yaml) so Llama-3-8B fits a free T4.

## Answer-generating models (all free)

`gemini-flash` (API free tier), `sarvam` (2B), `llama3` (8B), `airavata`, `gemma` (9B)
— configured in `config.yaml` under `generation.models`.

## Labeling: silver-standard + human verification

No 5,000-sample human annotation. Each answer is BERTScored against the Gemini
gold answer (threshold 0.65). Samples in the ambiguous band (0.55–0.75 F1,
~500 rows) are exported to `data/annotations/human_verify.csv` for 2 human
verifiers, then merged back. Label Studio tooling
(`annotation/label_studio_setup.py`, `agreement.py`) is kept for a fully
human-annotated track if annotators become available.

## Detector API

```bash
uvicorn indrallm.api.server:app --host 0.0.0.0 --port 8000
curl -X POST localhost:8000/detect -H "Content-Type: application/json" \
  -d '{"question": "Enna medicine edukkanum for fever?", "answer": "Take 4 paracetamol every hour."}'
# -> {"label": "hallucinated", "hallucination_prob": 0.91}
```

Interactive docs: `http://localhost:8000/docs`.

## Data layout

```
data/
  raw/          Reddit posts, synthetic seeds, forms — unfiltered
  filtered/     verified code-switched text
  questions/    gold_qa_pairs.csv (context/question/gold answer) + questions.csv
  answers/      per-model generated answers + mitigation_comparison.csv
  annotations/  human_verify.csv (ambiguous band) + optional Label Studio files
  final/        benchmark.csv, train/val/test splits, paper tables (md)
```

## Target venues

ACL 2027 Findings, EMNLP 2026, TALLIP (rolling).
