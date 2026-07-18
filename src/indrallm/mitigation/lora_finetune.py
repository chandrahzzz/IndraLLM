"""QLoRA supervised fine-tuning of Sarvam-2B on the CORRECT (label=0) answers.

Complements contrastive decoding (inference-time) with a training-time fix:
SFT on human/silver-verified correct code-switched QA pairs teaches the model
to hallucinate less natively. 4-bit base + LoRA adapters -> fits a free T4.

Saves adapters to models/sarvam-lora. To evaluate, generate answers with the
adapter merged and score with the detector (evaluation.run_benchmark).

Usage (Colab GPU):
    python -m indrallm.mitigation.lora_finetune
    python -m indrallm.mitigation.lora_finetune --epochs 1   # smoke test
"""

from __future__ import annotations

import argparse

import pandas as pd

from indrallm.config import CFG, path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--epochs", type=int, default=CFG["lora"]["epochs"])
    args = ap.parse_args()

    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
    from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
                              DataCollatorForLanguageModeling, Trainer, TrainingArguments)

    lc = CFG["lora"]
    train_df = pd.read_csv(path("final") / "train.csv")
    correct = train_df[train_df["label"] == 0].dropna(subset=["answer"])
    if correct.empty:
        raise SystemExit("no correct (label=0) examples in train.csv")
    print(f"SFT on {len(correct)} correct QA pairs")

    name = CFG["mitigation"]["model"]
    tokenizer = AutoTokenizer.from_pretrained(name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        name,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16),
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=lc["r"], lora_alpha=lc["alpha"], target_modules=lc["target_modules"],
        task_type=TaskType.CAUSAL_LM))
    model.print_trainable_parameters()

    def fmt(batch):
        texts = [f"Question: {q}\nAnswer: {a}{tokenizer.eos_token}"
                 for q, a in zip(batch["question"], batch["answer"])]
        return tokenizer(texts, truncation=True, max_length=CFG["detection"]["max_length"])

    ds = Dataset.from_pandas(correct[["question", "answer"]]).map(
        fmt, batched=True, remove_columns=["question", "answer"])

    out_dir = path("models") / "sarvam-lora"
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(out_dir),
            num_train_epochs=args.epochs,
            learning_rate=lc["lr"],
            per_device_train_batch_size=lc["batch_size"],
            gradient_accumulation_steps=lc["grad_accum"],
            logging_steps=25,
            save_strategy="epoch",
            report_to=[],
        ),
        train_dataset=ds,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    trainer.train()
    model.save_pretrained(str(out_dir / "adapter"))
    tokenizer.save_pretrained(str(out_dir / "adapter"))
    print(f"LoRA adapter saved -> {out_dir / 'adapter'}")


if __name__ == "__main__":
    main()
