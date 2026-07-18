"""Aggregate labels into the final benchmark dataset + stratified splits.

Two modes:
  --auto (default pipeline): data/final/benchmark.csv already produced by
      annotation/auto_label.py (BERTScore silver labels + human verification);
      only the stratified train/val/test splits are written.
  Label Studio mode (no flag): aggregate per-annotator CSVs. Agreement -> keep
      label. Disagreement -> adjudicator's label if annotator_adjudicator.csv
      exists, else drop. 'unanswerable' dropped.

Output: data/final/benchmark.csv + train/val/test.csv
(label = 0 correct, 1 hallucinated; split per detection.split in config.yaml).

Usage:
    python -m indrallm.annotation.aggregate_labels --auto
    python -m indrallm.annotation.aggregate_labels
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from indrallm.config import CFG, path


def write_splits(final: pd.DataFrame) -> None:
    """Stratified (language x label) train/val/test splits, seeded."""
    out_dir = path("final")
    rng = np.random.default_rng(CFG["detection"]["seed"])
    tr, va, _ = CFG["detection"]["split"]
    final = final.sample(frac=1, random_state=CFG["detection"]["seed"]).reset_index(drop=True)
    splits = {"train": [], "val": [], "test": []}
    for _, grp in final.groupby(["language", "label"]):
        n = len(grp)
        idx = rng.permutation(n)
        n_tr, n_va = int(n * tr), int(n * va)
        splits["train"].append(grp.iloc[idx[:n_tr]])
        splits["val"].append(grp.iloc[idx[n_tr:n_tr + n_va]])
        splits["test"].append(grp.iloc[idx[n_tr + n_va:]])
    for name, parts in splits.items():
        df = pd.concat(parts, ignore_index=True)
        df.to_csv(out_dir / f"{name}.csv", index=False)
        print(f"  {name}: {len(df)}")


def main_auto() -> None:
    bench_file = path("final") / "benchmark.csv"
    if not bench_file.exists():
        raise SystemExit("benchmark.csv missing — run annotation.auto_label first")
    final = pd.read_csv(bench_file)
    print(f"benchmark: {len(final)} examples ({final['label'].mean():.1%} hallucinated)")
    write_splits(final)


def main() -> None:
    files = sorted(path("annotations").glob("annotator_*.csv"))
    adjudicator = None
    frames = []
    for f in files:
        df = pd.read_csv(f)
        if "adjudicator" in f.stem:
            adjudicator = df
        else:
            frames.append(df)
    if not frames:
        raise SystemExit("no annotator CSVs found")
    ann = pd.concat(frames, ignore_index=True)

    # pivot to one row per (qid, model) with all annotator verdicts
    grouped = ann.groupby(["qid", "model"]).agg(
        verdicts=("verdict", list),
        category=("category", lambda s: s.dropna().mode().iat[0] if not s.dropna().empty else ""),
        ground_truth=("ground_truth", lambda s: s.dropna().astype(str).max()),
    ).reset_index()

    def resolve(row):
        v = row["verdicts"]
        if len(set(v)) == 1:
            return v[0]
        if adjudicator is not None:
            hit = adjudicator[(adjudicator["qid"] == row["qid"]) &
                              (adjudicator["model"] == row["model"])]
            if not hit.empty:
                return hit["verdict"].iat[0]
        return None  # unresolved disagreement -> drop

    grouped["verdict"] = grouped.apply(resolve, axis=1)
    n_dropped = grouped["verdict"].isna().sum()
    grouped = grouped.dropna(subset=["verdict"])
    grouped = grouped[grouped["verdict"] != "unanswerable"]
    grouped["label"] = (grouped["verdict"] == "hallucinated").astype(int)

    # join back question metadata + answers
    answers = pd.concat([pd.read_csv(f) for f in sorted(path("answers").glob("*.csv"))],
                        ignore_index=True)
    final = grouped.merge(answers, on=["qid", "model"], how="left")[
        ["qid", "language", "domain", "question", "model", "answer",
         "label", "category", "ground_truth"]]

    out_dir = path("final")
    final.to_csv(out_dir / "benchmark.csv", index=False)
    print(f"benchmark: {len(final)} examples "
          f"({final['label'].mean():.1%} hallucinated, {n_dropped} unresolved dropped)")
    write_splits(final)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--auto", action="store_true",
                    help="split the auto-labeled benchmark.csv (BERTScore pipeline)")
    args = ap.parse_args()
    main_auto() if args.auto else main()
