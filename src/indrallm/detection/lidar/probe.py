"""Falsifiable probe: do LIDAR Stage-2 features separate hallucinated from correct?

Verdict test, not a product. Loads the labeled benchmark, DROPS empty-answer rows
(BERTScore-0 artifacts that pollute the positive class), fits the boundary
transition matrix on questions only (no label leak), extracts features, and reports:

  1. per-feature ROC-AUC vs label  (|AUC-0.5| is the signal; >~0.60 is interesting)
  2. logistic-regression CV AUC over all features (does the combination beat chance?)

If every |AUC-0.5| is tiny and the combined CV AUC hugs 0.5, the language-identity
hypothesis is not supported on this data — build no multi-head transformer, no LITA.

Usage:
    python -m indrallm.detection.lidar.probe
    python -m indrallm.detection.lidar.probe --no-sbert      # skip CLSC embeddings (fast)
    python -m indrallm.detection.lidar.probe --limit 400     # quick smoke
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from indrallm.config import path
from indrallm.detection.lidar.features import (FEATURE_NAMES, extract_features,
                                               fit_transition_matrix, _make_embedder)


def _auc(y, x) -> float:
    from sklearn.metrics import roc_auc_score
    x = np.asarray(x, float)
    if np.all(x == x[0]):
        return 0.5
    return roc_auc_score(y, x)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-sbert", action="store_true", help="skip CLSC token embeddings")
    ap.add_argument("--limit", type=int, help="subsample rows for a fast smoke test")
    ap.add_argument("--file", default="benchmark.csv",
                    help="labeled CSV under data/final (e.g. benchmark_relabeled.csv)")
    args = ap.parse_args()

    df = pd.read_csv(path("final") / args.file)
    df["answer"] = df["answer"].fillna("").astype(str)
    before = len(df)
    df = df[df["answer"].str.strip() != ""].reset_index(drop=True)
    print(f"rows: {before} -> {len(df)} after dropping empty answers")
    if args.limit:
        df = df.groupby("label", group_keys=False).apply(
            lambda g: g.sample(min(len(g), args.limit // 2), random_state=0)).reset_index(drop=True)
    y = df["label"].to_numpy()
    print(f"label balance: correct={int((y == 0).sum())}  hallucinated={int((y == 1).sum())}"
          f"  ({y.mean():.1%} positive)\n")

    tm = fit_transition_matrix(df["question"].tolist(),
                               df.get("language", pd.Series([None] * len(df))).tolist())
    embed = _make_embedder(not args.no_sbert)
    if not args.no_sbert and embed is None:
        print("(sentence-transformers unavailable — CLSC falls back to neutral 1.0)\n")

    feats = [extract_features(a, tm, el, embed)
             for a, el in zip(df["answer"], df.get("language", [None] * len(df)))]
    X = pd.DataFrame(feats)[FEATURE_NAMES]

    print("per-feature ROC-AUC vs label (0.5 = no signal):")
    for name in FEATURE_NAMES:
        a = _auc(y, X[name].values)
        bar = "#" * int(abs(a - 0.5) * 100)
        print(f"  {name:12s} AUC={a:.3f}  |d|={abs(a - 0.5):.3f}  {bar}")

    if len(np.unique(y)) < 2:
        print("\nonly one class present — cannot fit classifier")
        return

    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score, StratifiedKFold

    clf = make_pipeline(StandardScaler(),
                        LogisticRegression(max_iter=1000, class_weight="balanced"))
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    scores = cross_val_score(clf, X.values, y, cv=cv, scoring="roc_auc")
    print(f"\nLogReg (all features) 5-fold CV AUC: {scores.mean():.3f} +/- {scores.std():.3f}")
    verdict = ("SIGNAL — features beat chance, LIDAR premise supported"
               if scores.mean() - scores.std() > 0.55 else
               "WEAK/NONE — language-identity features do not clearly separate the label")
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
