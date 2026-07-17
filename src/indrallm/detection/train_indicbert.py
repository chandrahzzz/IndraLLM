"""Fine-tune IndicBERT to classify (question, answer) pairs as correct/hallucinated.

Input encoding: "<question> [SEP] <answer>", binary label (1 = hallucinated).
Needs a GPU — run on Colab/Kaggle (docs/COLAB.md) or a VIT cluster node.

Usage:
    python -m indrallm.detection.train_indicbert
    python -m indrallm.detection.train_indicbert --no-wandb --epochs 1   # smoke test
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from indrallm.config import CFG, path


def load_split(name: str):
    from datasets import Dataset
    df = pd.read_csv(path("final") / f"{name}.csv")
    df["answer"] = df["answer"].fillna("")
    return Dataset.from_pandas(df[["question", "answer", "label", "language"]])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--epochs", type=int, default=CFG["detection"]["epochs"])
    ap.add_argument("--no-wandb", action="store_true")
    args = ap.parse_args()

    import evaluate
    import torch
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                              Trainer, TrainingArguments)

    d = CFG["detection"]
    tokenizer = AutoTokenizer.from_pretrained(d["base_model"])
    model = AutoModelForSequenceClassification.from_pretrained(d["base_model"], num_labels=2)

    def preprocess(batch):
        return tokenizer(batch["question"], batch["answer"],
                         truncation=True, max_length=d["max_length"])

    train_ds = load_split("train").map(preprocess, batched=True)
    val_ds = load_split("val").map(preprocess, batched=True)
    test_ds = load_split("test").map(preprocess, batched=True)

    f1 = evaluate.load("f1")
    acc = evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {**f1.compute(predictions=preds, references=labels),
                **acc.compute(predictions=preds, references=labels)}

    out_dir = path("models") / "indicbert-halludetect"
    training_args = TrainingArguments(
        output_dir=str(out_dir),
        num_train_epochs=args.epochs,
        learning_rate=d["lr"],
        per_device_train_batch_size=d["batch_size"],
        per_device_eval_batch_size=d["batch_size"] * 2,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        seed=d["seed"],
        fp16=torch.cuda.is_available(),
        report_to=[] if args.no_wandb or not os.environ.get("WANDB_API_KEY") else ["wandb"],
        run_name="indicbert-halludetect",
        logging_steps=25,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=train_ds,
                      eval_dataset=val_ds, compute_metrics=compute_metrics)
    trainer.train()

    print("\n== test set ==")
    metrics = trainer.evaluate(test_ds)
    print(metrics)

    # per-language F1 on test
    preds = np.argmax(trainer.predict(test_ds).predictions, axis=-1)
    test_df = pd.DataFrame({"language": test_ds["language"],
                            "label": test_ds["label"], "pred": preds})
    from sklearn.metrics import f1_score
    for lang, grp in test_df.groupby("language"):
        print(f"  {lang}: F1={f1_score(grp['label'], grp['pred']):.3f}  n={len(grp)}")

    trainer.save_model(str(out_dir / "best"))
    tokenizer.save_pretrained(str(out_dir / "best"))
    print(f"saved -> {out_dir / 'best'}")


if __name__ == "__main__":
    main()
