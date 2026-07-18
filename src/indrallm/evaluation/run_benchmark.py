"""Produce the paper's results tables.

Table 1 (--hallucination-rates): per-model, per-language hallucination rate from
    human labels (data/final/benchmark.csv). This is the headline benchmark table.

Table 2 (--detector): fine-tuned IndicBERT detector F1/precision/recall on the
    test split, overall / per language / per category.

Table 3 (--mitigation): baseline vs contrastive-decoding hallucination rate on
    data/answers/mitigation_comparison.csv, scored by the trained detector.

Table 4 (--nli): zero-shot NLI judge baseline (deberta-large-mnli): answer is
    hallucinated if it is not entailed by the gold answer. Compared against the
    fine-tuned detector on the same test split.

Usage:
    python -m indrallm.evaluation.run_benchmark                # all available tables
    python -m indrallm.evaluation.run_benchmark --detector
"""

from __future__ import annotations

import argparse

import pandas as pd

from indrallm.config import path

RESULTS_DIR_KEY = "final"


def _markdown(df: pd.DataFrame, title: str, fname: str) -> None:
    out = path(RESULTS_DIR_KEY) / fname
    text = f"## {title}\n\n{df.to_markdown()}\n"
    out.write_text(text, encoding="utf-8")
    print(f"\n{text}\nsaved -> {out}")


def hallucination_rates() -> None:
    bench = pd.read_csv(path("final") / "benchmark.csv")
    table = (bench.pivot_table(index="model", columns="language",
                               values="label", aggfunc="mean") * 100).round(1)
    table["overall"] = (bench.groupby("model")["label"].mean() * 100).round(1)
    _markdown(table, "Hallucination rate (%) by model and language (human-labeled)",
              "table1_hallucination_rates.md")

    by_cat = (bench[bench["label"] == 1].groupby(["model", "category"]).size()
              .unstack(fill_value=0))
    _markdown(by_cat, "Hallucination counts by category", "table1b_categories.md")


def detector_metrics() -> None:
    import numpy as np
    import torch
    from sklearn.metrics import f1_score, precision_score, recall_score
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    model_dir = path("models") / "indicbert-halludetect" / "best"
    if not model_dir.exists():
        print("detector not trained yet — run detection.train_indicbert first")
        return
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
    model.eval()
    if torch.cuda.is_available():
        model.cuda()

    test = pd.read_csv(path("final") / "test.csv")
    test["answer"] = test["answer"].fillna("")
    preds = []
    with torch.no_grad():
        for i in range(0, len(test), 64):
            batch = test.iloc[i:i + 64]
            enc = tokenizer(batch["question"].tolist(), batch["answer"].tolist(),
                            truncation=True, max_length=256, padding=True,
                            return_tensors="pt").to(model.device)
            preds.extend(model(**enc).logits.argmax(-1).cpu().tolist())
    test["pred"] = preds

    rows = [{"slice": "overall",
             "F1": f1_score(test["label"], test["pred"]),
             "precision": precision_score(test["label"], test["pred"]),
             "recall": recall_score(test["label"], test["pred"]),
             "n": len(test)}]
    for lang, grp in test.groupby("language"):
        rows.append({"slice": lang, "F1": f1_score(grp["label"], grp["pred"]),
                     "precision": precision_score(grp["label"], grp["pred"], zero_division=0),
                     "recall": recall_score(grp["label"], grp["pred"], zero_division=0),
                     "n": len(grp)})
    table = pd.DataFrame(rows).set_index("slice").round(3)
    _markdown(table, "IndicBERT detector performance (test split)",
              "table2_detector.md")


def mitigation_effect() -> None:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    comp_file = path("answers") / "mitigation_comparison.csv"
    model_dir = path("models") / "indicbert-halludetect" / "best"
    if not comp_file.exists() or not model_dir.exists():
        print("mitigation comparison and/or detector missing — skip")
        return
    comp = pd.read_csv(comp_file)
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
    model.eval()
    if torch.cuda.is_available():
        model.cuda()

    def score(col: str) -> pd.Series:
        preds = []
        with torch.no_grad():
            for i in range(0, len(comp), 64):
                batch = comp.iloc[i:i + 64]
                enc = tokenizer(batch["question"].tolist(),
                                batch[col].fillna("").tolist(),
                                truncation=True, max_length=256, padding=True,
                                return_tensors="pt").to(model.device)
                preds.extend(model(**enc).logits.argmax(-1).cpu().tolist())
        return pd.Series(preds, index=comp.index)

    comp["halluc_baseline"] = score("baseline")
    comp["halluc_contrastive"] = score("contrastive")
    table = (comp.groupby("language")[["halluc_baseline", "halluc_contrastive"]]
             .mean() * 100).round(1)
    table["reduction_pp"] = (table["halluc_baseline"] - table["halluc_contrastive"]).round(1)
    _markdown(table, "Hallucination rate (%): greedy vs contrastive decoding "
                     "(detector-scored)", "table3_mitigation.md")


def nli_baseline() -> None:
    """Zero-shot NLI judge: hallucinated if answer not entailed by gold answer."""
    import torch
    from sklearn.metrics import f1_score, precision_score, recall_score
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    from indrallm.config import CFG

    test_file = path("final") / "test.csv"
    if not test_file.exists():
        print("test.csv missing — run aggregate_labels first")
        return
    test = pd.read_csv(test_file)
    if "ground_truth" not in test.columns or test["ground_truth"].isna().all():
        print("no ground_truth column — NLI judge needs gold answers")
        return
    test = test.dropna(subset=["ground_truth"]).reset_index(drop=True)
    test["answer"] = test["answer"].fillna("")

    n = CFG["nli"]
    tokenizer = AutoTokenizer.from_pretrained(n["model"])
    model = AutoModelForSequenceClassification.from_pretrained(n["model"])
    model.eval()
    if torch.cuda.is_available():
        model.cuda()
    entail_idx = int(model.config.label2id.get(
        "ENTAILMENT", model.config.label2id.get("entailment", 2)))

    preds = []
    with torch.no_grad():
        for i in range(0, len(test), 32):
            batch = test.iloc[i:i + 32]
            enc = tokenizer(batch["ground_truth"].astype(str).tolist(),  # premise
                            batch["answer"].astype(str).tolist(),        # hypothesis
                            truncation=True, max_length=256, padding=True,
                            return_tensors="pt").to(model.device)
            probs = model(**enc).logits.softmax(-1)[:, entail_idx].cpu()
            preds.extend((probs < n["entail_threshold"]).int().tolist())
    test["pred"] = preds

    rows = [{"slice": "overall (NLI)",
             "F1": f1_score(test["label"], test["pred"]),
             "precision": precision_score(test["label"], test["pred"], zero_division=0),
             "recall": recall_score(test["label"], test["pred"], zero_division=0),
             "n": len(test)}]
    for lang, grp in test.groupby("language"):
        rows.append({"slice": f"{lang} (NLI)",
                     "F1": f1_score(grp["label"], grp["pred"], zero_division=0),
                     "precision": precision_score(grp["label"], grp["pred"], zero_division=0),
                     "recall": recall_score(grp["label"], grp["pred"], zero_division=0),
                     "n": len(grp)})
    table = pd.DataFrame(rows).set_index("slice").round(3)
    _markdown(table, "Zero-shot NLI judge baseline (vs fine-tuned detector, Table 2)",
              "table4_nli_baseline.md")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hallucination-rates", action="store_true")
    ap.add_argument("--detector", action="store_true")
    ap.add_argument("--mitigation", action="store_true")
    ap.add_argument("--nli", action="store_true")
    args = ap.parse_args()

    run_all = not (args.hallucination_rates or args.detector or args.mitigation or args.nli)
    if args.hallucination_rates or run_all:
        hallucination_rates()
    if args.detector or run_all:
        detector_metrics()
    if args.mitigation or run_all:
        mitigation_effect()
    if args.nli or run_all:
        nli_baseline()


if __name__ == "__main__":
    main()
