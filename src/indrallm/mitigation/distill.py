"""Teacher -> student distillation to reduce Sarvam-2B hallucination.

Motivation (measured on this benchmark): hallucination rate scales with model
quality — qwen 0.4%, llama70b 3%, llama3 8%, gpt-oss 34%. So the strongest
available model's *correct* code-switched answers are high-quality supervision.
Sequence-level knowledge distillation: fine-tune the student (Sarvam-2B) on the
best teacher's answers, filtered to judge-label==0 (factually correct).

This is distinct from `lora_finetune.py`, which trains on ALL correct answers
regardless of which (possibly weak) model produced them. Here every target comes
from the best teacher that got that question right.

Pipeline:
    python -m indrallm.mitigation.distill --build     # assemble distill_set.csv (CPU)
    python -m indrallm.mitigation.distill --train     # LoRA-SFT student (Colab GPU)
    python -m indrallm.mitigation.distill --eval      # generate + judge, measure drop (GPU)

Teacher preference (best first). Gemini gold is a fallback teacher for questions
no student model answered correctly.
"""

from __future__ import annotations

import argparse
import re
import time

import pandas as pd
from tqdm import tqdm

from indrallm.config import CFG, path

TEACHER_RANK = ["qwen", "llama70b", "llama3", "gpt-oss"]  # lowest -> higher halluc rate
DISTILL_CSV = "distill_set.csv"
TEACHER_CSV = "teacher_answers.csv"

_LANG_NAME = {"ta": "Tamil", "hi": "Hindi", "te": "Telugu", "bn": "Bengali", "kn": "Kannada"}

TEACHER_PROMPT = (
    "You are answering an Indian user who wrote in a natural mix of {lang} and English "
    "(code-switching). Reply in the SAME code-switched style: genuinely mix {lang} "
    "(romanized, the way people type on phones) with English, like a bilingual local "
    "would actually speak. Be factually accurate and concise — 2 to 4 sentences. "
    "Output ONLY the final answer: no reasoning, no thinking steps, no <think> tags, "
    "no preamble.\n\nUser: {q}\nAnswer:"
)

_THINK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _clean(text: str) -> str:
    """Strip reasoning leakage: <think> blocks and 'thinking process' preambles."""
    t = _THINK.sub("", text or "")
    t = re.sub(r"^\s*<?think>?\s*", "", t, flags=re.IGNORECASE)
    # drop everything up to the last 'Answer:'-style marker if the model narrated
    if "\nAnswer:" in t:
        t = t.split("\nAnswer:")[-1]
    return t.strip()


def regen_teacher(model_key: str = "llama70b", limit: int | None = None, sleep: float = 1.0) -> pd.DataFrame:
    """Generate clean, code-switched teacher answers via Groq. Resumable.

    Cost estimate for 547 questions on llama-3.3-70b: ~$0.16. Uses GROQ_API_KEY.
    """
    from indrallm.generation.llm_clients import GroqClient
    spec = CFG["generation"]["models"][model_key]
    if spec["provider"] != "groq":
        raise SystemExit(f"{model_key} is not a Groq model")
    client = GroqClient(spec["model"])

    q = pd.read_csv(path("questions") / "gold_qa_pairs.csv") if (path("questions") / "gold_qa_pairs.csv").exists() \
        else pd.read_csv(path("final") / "benchmark_judged.csv").drop_duplicates("qid")
    out = path("final") / TEACHER_CSV
    done = set(pd.read_csv(out)["qid"]) if out.exists() else set()
    todo = q[~q["qid"].isin(done)]
    if limit:
        todo = todo.head(limit)
    print(f"regenerating {len(todo)} teacher answers with {model_key} ({spec['model']})")

    for r in todo.itertuples():
        lang = _LANG_NAME.get(getattr(r, "language", ""), "the Indian language")
        prompt = TEACHER_PROMPT.format(lang=lang, q=r.question)
        try:
            raw = client.generate(prompt)
        except Exception as e:
            print(f"stop ({e}); rerun to resume"); break
        row = pd.DataFrame([{"qid": r.qid, "language": getattr(r, "language", None),
                             "question": r.question, "answer": _clean(raw), "teacher": model_key}])
        row.to_csv(out, mode="a", header=not out.exists(), index=False)
        time.sleep(sleep)
    print(f"teacher answers -> {out}")
    return pd.read_csv(out) if out.exists() else pd.DataFrame()


def build_distill_set(use_gold_fallback: bool = True) -> pd.DataFrame:
    """One target per question: the best teacher's judged-correct answer.

    Falls back to the Gemini gold answer when no ranked teacher answered the
    question correctly, so every question contributes one clean target.
    """
    src = path("final") / "benchmark_judged.csv"
    if not src.exists():
        raise SystemExit("need data/final/benchmark_judged.csv (run the LLM judge first)")
    df = pd.read_csv(src)
    df["answer"] = df["answer"].fillna("").astype(str)
    rank = {m: i for i, m in enumerate(TEACHER_RANK)}

    rows = []
    for qid, g in df.groupby("qid"):
        correct = g[(g["label"] == 0) & (g["answer"].str.strip() != "")].copy()
        pick = None
        if not correct.empty:
            correct["rk"] = correct["model"].map(lambda m: rank.get(m, 99))
            best = correct.sort_values("rk").iloc[0]
            pick = {"teacher": best["model"], "answer": best["answer"]}
        elif use_gold_fallback:
            gold = str(g.iloc[0].get("ground_truth", "") or "").strip()
            if gold:
                pick = {"teacher": "gemini_gold", "answer": gold}
        if pick:
            r0 = g.iloc[0]
            rows.append({"qid": qid, "language": r0.get("language"),
                         "question": r0["question"], "answer": pick["answer"],
                         "teacher": pick["teacher"]})

    out = pd.DataFrame(rows)
    dest = path("final") / DISTILL_CSV
    out.to_csv(dest, index=False)
    print(f"distill set: {len(out)} question->teacher pairs -> {dest}")
    print("teacher mix:", out["teacher"].value_counts().to_dict())
    print("per-language:", out["language"].value_counts().to_dict())
    return out


def _build_from_teacher() -> pd.DataFrame:
    """Distill set from regenerated teacher answers (kept only if code-switched).

    Uses codeswitch_filter.detect_codeswitch, which is romanized-aware (lexicon
    vote), instead of a raw Indic-token fraction — the latter undercounts
    romanized Tamil/Telugu/etc. and would wrongly drop genuinely code-switched
    answers that happen to be written in Latin script.
    """
    from indrallm.collection.codeswitch_filter import detect_codeswitch
    p = path("final") / TEACHER_CSV
    if not p.exists():
        raise SystemExit("run --regen-teacher first")
    df = pd.read_csv(p)
    df["answer"] = df["answer"].fillna("").astype(str)

    def is_cs(a, l):
        if not str(a).strip():
            return False
        return detect_codeswitch(str(a), l if l in {"ta", "hi", "te", "bn", "kn"} else None)["is_cs"]

    df["cs"] = [is_cs(a, l) for a, l in zip(df["answer"], df["language"])]
    kept = df[df["cs"]].copy()
    dest = path("final") / DISTILL_CSV
    kept[["qid", "language", "question", "answer", "teacher"]].to_csv(dest, index=False)
    print(f"code-switched teacher targets: {len(kept)}/{len(df)} kept -> {dest}")
    print("per-language:", kept["language"].value_counts().to_dict())
    dropped = df[~df["cs"]]
    if len(dropped):
        print(f"dropped {len(dropped)} non-code-switched (mostly-English) answers")
    return kept


def train(epochs: int | None = None) -> None:
    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
    from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
                              DataCollatorForLanguageModeling, Trainer, TrainingArguments)

    lc = CFG["lora"]
    p = path("final") / DISTILL_CSV
    if not p.exists():
        raise SystemExit("run --build first")
    ds_df = pd.read_csv(p).dropna(subset=["answer"])
    print(f"distilling on {len(ds_df)} teacher targets "
          f"(teachers: {ds_df['teacher'].value_counts().to_dict()})")

    name = CFG["mitigation"]["model"]
    tokenizer = AutoTokenizer.from_pretrained(name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        name, quantization_config=BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16),
        device_map="auto")
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=lc["r"], lora_alpha=lc["alpha"], target_modules=lc["target_modules"],
        task_type=TaskType.CAUSAL_LM))
    model.print_trainable_parameters()

    def fmt(batch):
        texts = [f"Question: {q}\nAnswer: {a}{tokenizer.eos_token}"
                 for q, a in zip(batch["question"], batch["answer"])]
        return tokenizer(texts, truncation=True, max_length=CFG["detection"]["max_length"])

    ds = Dataset.from_pandas(ds_df[["question", "answer"]]).map(
        fmt, batched=True, remove_columns=["question", "answer"])

    out_dir = path("models") / "sarvam-distill"
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(out_dir), num_train_epochs=epochs or lc["epochs"],
            learning_rate=lc["lr"], per_device_train_batch_size=lc["batch_size"],
            gradient_accumulation_steps=lc["grad_accum"], logging_steps=25,
            save_strategy="epoch", report_to=[]),
        train_dataset=ds,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False))
    trainer.train()
    model.save_pretrained(str(out_dir / "adapter"))
    tokenizer.save_pretrained(str(out_dir / "adapter"))
    print(f"distilled adapter -> {out_dir / 'adapter'}")


def evaluate(limit: int | None = None, judge: bool = True) -> None:
    """Generate student answers baseline vs distilled on the test questions, judge
    both with the Groq LLM-judge, and report the hallucination-rate drop.

    Generation needs a GPU (Sarvam-2B); judging uses Groq (GROQ_API_KEY). Both run
    fine on a Colab session. Saves data/answers/distill_comparison.csv.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    test = pd.read_csv(path("final") / "test.csv").drop_duplicates("qid")
    if limit:
        test = test.groupby("language").head(max(limit // 5, 1))
    name = CFG["mitigation"]["model"]
    tokenizer = AutoTokenizer.from_pretrained(name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def load(adapter: str | None):
        m = AutoModelForCausalLM.from_pretrained(
            name, quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16),
            device_map="auto")
        if adapter:
            from peft import PeftModel
            m = PeftModel.from_pretrained(m, adapter)
        return m.eval()

    def gen(model, q):
        ids = tokenizer(f"Question: {q}\nAnswer:", return_tensors="pt").input_ids.to(model.device)
        with torch.no_grad():
            o = model.generate(ids, max_new_tokens=CFG["mitigation"]["max_new_tokens"],
                               do_sample=False, pad_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip()

    rows = []
    adapter_path = str(path("models") / "sarvam-distill" / "adapter")
    for tag, adapter in [("baseline", None), ("distilled", adapter_path)]:
        model = load(adapter)
        for r in test.itertuples():
            rows.append({"qid": r.qid, "language": r.language, "question": r.question,
                         "variant": tag, "answer": gen(model, r.question),
                         "ground_truth": str(getattr(r, "ground_truth", "") or "")})
        del model
        torch.cuda.empty_cache()

    comp = pd.DataFrame(rows)
    dest = path("answers") / "distill_comparison.csv"
    comp.to_csv(dest, index=False)
    print(f"generated {len(comp)} answers -> {dest}")

    if not judge:
        return

    from indrallm.annotation.llm_judge_label import _judge
    from indrallm.generation.llm_clients import GroqClient
    client = GroqClient("llama-3.1-8b-instant")
    labels = []
    for r in tqdm(comp.itertuples(), total=len(comp), desc="judging"):
        try:
            lab, _ = _judge(client, r.question, r.ground_truth, r.answer)
        except Exception:
            lab = -1
        labels.append(lab)
        time.sleep(0.5)
    comp["label"] = labels
    comp.to_csv(dest, index=False)

    graded = comp[comp["label"] >= 0]
    print("\n== hallucination rate (lower = better) ==")
    piv = graded.groupby("variant")["label"].mean()
    base, dist = piv.get("baseline", float("nan")), piv.get("distilled", float("nan"))
    print(f"  baseline : {base:.1%}")
    print(f"  distilled: {dist:.1%}")
    if base and not pd.isna(base) and not pd.isna(dist):
        print(f"  reduction: {(base - dist) / base:+.1%} relative")
    print("\nper-language hallucination rate:")
    for lang, g in graded.groupby("language"):
        b = g[g.variant == "baseline"]["label"].mean()
        d = g[g.variant == "distilled"]["label"].mean()
        print(f"  {lang}: baseline {b:.0%} -> distilled {d:.0%}  (n={len(g)//2})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--regen-teacher", action="store_true",
                    help="generate clean code-switched teacher answers via Groq")
    ap.add_argument("--from-teacher", action="store_true",
                    help="build distill set from regenerated teacher_answers.csv")
    ap.add_argument("--model", default="llama70b")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--train", action="store_true")
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--epochs", type=int)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    if args.regen_teacher:
        regen_teacher(args.model, args.limit)
    elif args.from_teacher:
        _build_from_teacher()
    elif args.build:
        build_distill_set()
    elif args.train:
        train(args.epochs)
    elif args.eval:
        evaluate(args.limit)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
