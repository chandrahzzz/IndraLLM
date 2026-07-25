"""Evaluate the Linguistic Fidelity Filter — the spec target AND the honest test.

Two questions, one run:

  A. Can it tell coherent code-switch from corrupted?  (spec Task 2.3, target >0.85)
     Trains on gold answers vs corrupted gold, reports held-out accuracy.

  B. THE ONE THAT MATTERS — does the fidelity score gate real hallucinations?
     Scores the model answers, then measures whether low fidelity predicts the
     JUDGED hallucination label, and simulates the gate:
       - compute_saved   = fraction of answers the filter lets skip the factual check
       - halluc_caught   = fraction of real hallucinations the filter flags (recall)
     The design claims "cut compute 50-70% while maintaining accuracy." That holds
     ONLY if compute_saved is high AND halluc_caught is high. If hallucinations pass
     the filter (halluc_caught low), the gate saves compute by dropping the very
     cases it exists to catch — the claim fails.

Usage:
    python -m indrallm.filter.evaluate
    python -m indrallm.filter.evaluate --threshold 0.6
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from indrallm.config import path
from indrallm.filter.fidelity_filter import LinguisticFidelityFilter, corrupt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold", type=float, default=0.6)
    args = ap.parse_args()
    from sklearn.metrics import roc_auc_score, accuracy_score

    df = pd.read_csv(path("final") / "benchmark_judged.csv")
    df["answer"] = df["answer"].fillna("").astype(str)
    df["ground_truth"] = df["ground_truth"].fillna("").astype(str)
    df = df[df["answer"].str.strip() != ""].reset_index(drop=True)
    langs = df["language"].tolist()

    # train the filter on coherent gold answers (unique)
    gold = df.drop_duplicates("qid")[["ground_truth", "language"]]
    gold = gold[gold["ground_truth"].str.strip() != ""]
    filt = LinguisticFidelityFilter().fit(gold["ground_truth"].tolist(), gold["language"].tolist())

    # ---- A. gold vs corrupted (the easy, spec-target metric) ----
    import random
    rng = random.Random(7)
    test_gold = gold["ground_truth"].tolist()
    test_lang = gold["language"].tolist()
    pos_scores = [filt.score(t, l) for t, l in zip(test_gold, test_lang)]
    neg_scores = [filt.score(corrupt(t, l, rng), l) for t, l in zip(test_gold, test_lang)]
    ya = [1] * len(pos_scores) + [0] * len(neg_scores)
    pa = pos_scores + neg_scores
    acc = accuracy_score(ya, [1 if s >= 0.5 else 0 for s in pa])
    auc_a = roc_auc_score(ya, pa)
    print("== A. coherent-vs-corrupted (spec target >0.85) ==")
    print(f"   accuracy={acc:.3f}  AUC={auc_a:.3f}   (this is the EASY task)")

    # ---- B. the honest test: fidelity vs REAL judged hallucination ----
    df["fidelity"] = [filt.score(a, l) for a, l in zip(df["answer"], langs)]
    y = df["label"].to_numpy()
    # low fidelity should predict hallucination -> use (1 - fidelity) as the score
    auc_b = roc_auc_score(y, 1 - df["fidelity"]) if len(set(y)) > 1 else 0.5

    thr = args.threshold
    flagged = df["fidelity"] < thr
    compute_saved = 1 - flagged.mean()
    halluc = df[df["label"] == 1]
    correct = df[df["label"] == 0]
    halluc_caught = (halluc["fidelity"] < thr).mean() if len(halluc) else 0.0
    correct_skipped = (correct["fidelity"] >= thr).mean() if len(correct) else 0.0

    print("\n== B. does fidelity gate REAL hallucinations? (the claim) ==")
    print(f"   AUC(low-fidelity -> judged hallucination) = {auc_b:.3f}   (0.5 = useless gate)")
    print(f"   gate @ fidelity<{thr}:")
    print(f"     compute_saved   = {compute_saved:.1%}  (answers that skip the factual check)")
    print(f"     halluc_caught   = {halluc_caught:.1%}  (real hallucinations the filter flags)")
    print(f"     correct_skipped = {correct_skipped:.1%} (correct answers correctly skipped)")

    ok = auc_b >= 0.65 and halluc_caught >= 0.7
    print("\n== VERDICT ==")
    if ok:
        print("   Filter gates hallucinations — Claim Family 1 SUPPORTED. Build the type classifier.")
    else:
        print("   Filter does NOT gate hallucinations (AUC~0.5 and/or most hallucinations pass).")
        print("   Real hallucinations here are linguistically fluent, so a linguistic filter")
        print("   cannot select them. Claim Family 1 (fidelity-as-gate) is NOT supported on this")
        print("   data. Do not build the efficiency story around it; a factual detector must see")
        print("   every answer, or gate on a factual signal instead.")


if __name__ == "__main__":
    main()
