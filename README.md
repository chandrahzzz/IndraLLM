# IndraLLM — Code-Switched Hallucination Benchmark, Detector & Mitigation for Indian Languages

I built IndraLLM to answer a simple question: when an LLM answers a question written
in **code-switched Indian-language text** (Tamil, Hindi, Telugu, Bengali, or Kannada
mixed with English — the way people actually type), does it make things up, can I
detect it, and can I make the model do it less? The whole thing runs on a near-zero
budget (free Gemini tier + free Colab T4 + a few cents of Groq).

Three things I ended up with, all with real numbers:

1. **A benchmark** — ~2,600 `(question, model_answer)` pairs across 5 code-switched
   language pairs, from 4 answering models, each labeled *correct* or *hallucinated*
   by a language-agnostic LLM-judge.
2. **A detector** — an IndicBERT hallucination detector at **ROC-AUC 0.75**
   (per-language 0.63–0.86).
3. **A mitigation** — teacher distillation that cuts Sarvam-2B's hallucination rate
   from **64.9% → 26.8% (−58.7% relative)** *while keeping* the code-switching
   (code-switched output actually went up, 40% → 72%).

## Results

| Piece | Result |
|---|---|
| Benchmark | 2,649 judged QA pairs, 5 languages, ~10% hallucinated |
| Detector (IndicBERT) | Test **ROC-AUC 0.75**, F1 0.35 (tuned); per-lang AUC ta 0.86 / bn 0.77 / te 0.77 / kn 0.68 / hi 0.65 |
| Mitigation (distillation) | Sarvam-2B hallucination **64.9% → 26.8%**, all 5 languages down; code-switching preserved (40% → 72%) |

## The one thing I got wrong first (and fixed)

My original labels came from BERTScore against a Gemini gold answer — but the gold
answers were ~94% English, so **any answer written in Indic scored low and got
labeled "hallucinated."** The label was secretly measuring *"did the model reply in
Indic,"* not *"did it hallucinate"* (`corr(indic_fraction, label) = +0.52`). I
replaced it with an **LLM-judge** (Groq `llama-3.1-8b-instant`) that reads
`(question, gold, answer)` and rules on *factual* correctness regardless of surface
language — confound gone (`corr = +0.04`). Everything downstream uses these judged
labels. I also tried three surface-linguistic detectors (boundary/entropy features,
cross-lingual alignment, a linguistic fidelity filter) — all sat at AUC ~0.50 on the
honest labels, because the real hallucinations are *fluent* factual errors. I deleted
them rather than pretend they worked.

## Pipeline

```
collect (Reddit + Gemini seeds + hand-written code-switched QA)
  → codeswitch_filter (verify genuine mixing, romanized-aware)
  → gold QA (Gemini) / seed imported answers as gold
  → generate answers (4 Groq models: llama3, llama70b, qwen, gpt-oss)
  → LLM-judge labels (Groq) → benchmark_judged.csv → stratified splits (by qid, no leakage)
  → train IndicBERT detector (Colab GPU)  ── AUC 0.75
  → teacher distillation: regen code-switched teacher answers (llama70b) →
     LoRA-SFT Sarvam-2B → evaluate hallucination drop (Colab GPU)  ── −58.7%
```

## Setup

```bash
git clone https://github.com/chandrahzzz/IndraLLM.git
cd IndraLLM
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env           # fill GOOGLE_API_KEY, GROQ_API_KEY, HF_TOKEN
```

> API keys, the fastText model, trained weights, and generated data are git-ignored.
> Never commit `.env`.

## Run order

Laptop (CPU) steps are cheap; GPU steps run on a free Colab T4 (runbooks in `docs/`).

| Step | Command | Where |
|---|---|---|
| 1. Import hand-written QA | `python -m indrallm.collection.import_llm_questions --files data/raw/llm_*.txt --seed-gold` | laptop |
| 2. Verify code-switching | `python -m indrallm.collection.codeswitch_filter` | laptop |
| 3. Generate answers | `python -m indrallm.generation.generate_answers --models llama3 llama70b qwen gpt-oss` | laptop |
| 4. Carrier labels (BERTScore) | `python -m indrallm.annotation.auto_label` | laptop |
| 5. **Real labels (LLM-judge)** | `python -m indrallm.annotation.llm_judge_label --provider groq` then `--merge` | laptop |
| 6. Train detector | `python -m indrallm.detection.train_indicbert --no-wandb` | Colab — see `docs/COLAB_DETECTOR.md` |
| 7. Distill teacher answers | `python -m indrallm.mitigation.distill --regen-teacher --model llama70b` then `--from-teacher` | laptop |
| 8. Train + eval distillation | `python -m indrallm.mitigation.distill --train` then `--eval --limit 100` | Colab — see `docs/COLAB_DISTILL.md` |

> **Split by `qid`, never by row** — each question has 4 model-answers sharing one
> gold, so a row-level split leaks the same question across train/test.

## Models

- **Answering (Groq, laptop):** `llama3` (8B), `llama70b`, `qwen` (27B), `gpt-oss` (20B)
- **Judge (Groq):** `llama-3.1-8b-instant`
- **Detector:** `ai4bharat/IndicBERTv2-MLM-only` (class-weighted — the label is ~10%
  positive, so an unweighted loss collapses to F1=0)
- **Student for distillation:** `sarvamai/sarvam-2b-v0.5` (4-bit + LoRA, fits a T4)
- **Teacher:** `llama-3.3-70b` re-prompted for clean code-switched answers

## Detector API

```bash
uvicorn indrallm.api.server:app --host 0.0.0.0 --port 8000
curl -X POST localhost:8000/detect -H "Content-Type: application/json" \
  -d '{"question": "Fever ku enna medicine edukkanum?", "answer": "Take 4 paracetamol every hour."}'
# -> {"label": "hallucinated", "hallucination_prob": 0.9x}
```

## Data layout

```
data/
  raw/          Reddit posts, synthetic seeds, hand-written QA — unfiltered
  filtered/     verified code-switched text
  questions/    gold_qa_pairs.csv, questions.csv
  answers/      per-model answers + distill_comparison.csv
  annotations/  llm_judge.csv (judge labels), teacher answers
  final/        benchmark_judged.csv, train/val/test splits, distill_set.csv
```

## Notes to self / limitations

- Baseline Sarvam-2B hallucinating 64.9% is high because it's a small 2B base model —
  the distillation gain is "lots of headroom filled," not "a strong model fixed."
- Per-language eval n is small (17–20) — the overall numbers are the reliable ones;
  multiple seeds would firm up the per-language breakdown.
- Teacher answers are trusted from llama70b (3% hallucination rate), not separately
  judged — judging them first is the obvious next refinement.
