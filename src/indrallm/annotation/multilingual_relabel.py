"""Language-agnostic relabeling to remove the English-gold BERTScore confound.

Problem (see the LIDAR probe): gold answers are ~94% English and labels came from
BERTScore(answer, English-gold). A correct answer written in code-switched Indic
scores low and gets mislabeled "hallucinated". `frac_indic` then predicts the
label for the wrong reason.

Fix: score answer-vs-gold semantic similarity with a *multilingual* sentence
encoder that maps a code-switched Indic answer and its English gold into the same
space. A correct Indic answer now scores high. Free, CPU, no API, no Groq spend.

Outputs `data/final/benchmark_relabeled.csv` with:
  ml_sim    cosine(answer, ground_truth) under paraphrase-multilingual-MiniLM
  label     1 if ml_sim < --threshold else 0   (overwrites old label column)
  label_bertscore  the original label, kept for comparison

Also prints the confound test: corr(frac_indic, ml_sim) should be ~0, versus the
old corr(frac_indic, bertscore_f1) = -0.375.

Usage:
    python -m indrallm.annotation.multilingual_relabel
    python -m indrallm.annotation.multilingual_relabel --threshold 0.5 --resplit
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from indrallm.config import CFG, path
from indrallm.detection.lidar.lid import token_lid

_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_INDIC = {"ta", "hi", "te", "bn", "kn"}


def _frac_indic(text: str, lang: str | None) -> float:
    seq = token_lid(str(text), lang)
    return sum(s in _INDIC for s in seq) / len(seq) if seq else 0.0


def _suggest_threshold(sims: np.ndarray) -> float:
    """Deepest gap in the sorted similarity distribution between the 20th-80th pct."""
    s = np.sort(sims)
    lo, hi = int(0.2 * len(s)), int(0.8 * len(s))
    if hi - lo < 2:
        return float(np.median(s))
    gaps = np.diff(s[lo:hi])
    return float(s[lo + int(np.argmax(gaps))])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold", type=float, help="ml_sim below this -> hallucinated (default: auto)")
    ap.add_argument("--resplit", action="store_true", help="also write train/val/test on new labels")
    ap.add_argument("--batch", type=int, default=64)
    args = ap.parse_args()

    df = pd.read_csv(path("final") / "benchmark.csv")
    df["answer"] = df["answer"].fillna("").astype(str)
    df["ground_truth"] = df["ground_truth"].fillna("").astype(str)
    before = len(df)
    df = df[(df["answer"].str.strip() != "") & (df["ground_truth"].str.strip() != "")].reset_index(drop=True)
    print(f"rows: {before} -> {len(df)} (dropped empty answer/gold)")

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(_MODEL)
    av = model.encode(df["answer"].tolist(), batch_size=args.batch,
                      normalize_embeddings=True, show_progress_bar=True)
    gv = model.encode(df["ground_truth"].tolist(), batch_size=args.batch,
                      normalize_embeddings=True, show_progress_bar=True)
    df["ml_sim"] = np.sum(av * gv, axis=1)

    df["frac_indic"] = [_frac_indic(a, l) for a, l in zip(df["answer"], df.get("language", [None] * len(df)))]

    thr = args.threshold if args.threshold is not None else round(_suggest_threshold(df["ml_sim"].values), 3)
    df["label_bertscore"] = df["label"]
    df["label"] = (df["ml_sim"] < thr).astype(int)
    df["label_source"] = "multilingual_sim"

    print(f"\nthreshold = {thr}")
    print(f"new labels: correct={int((df.label == 0).sum())} "
          f"hallucinated={int((df.label == 1).sum())} ({df.label.mean():.1%} positive)")

    print("\nCONFOUND TEST (want |corr with frac_indic| ~ 0):")
    print(f"  old  corr(frac_indic, bertscore_f1) = {df['frac_indic'].corr(df['bertscore_f1']):+.3f}")
    print(f"  new  corr(frac_indic, ml_sim)       = {df['frac_indic'].corr(df['ml_sim']):+.3f}")
    print(f"  new  corr(frac_indic, label)        = {df['frac_indic'].corr(df['label'].astype(float)):+.3f}")
    agree = (df["label"] == df["label_bertscore"]).mean()
    print(f"  label agreement old-vs-new          = {agree:.1%}")

    out = path("final") / "benchmark_relabeled.csv"
    df.drop(columns=["frac_indic"]).to_csv(out, index=False)
    print(f"\nsaved -> {out}")

    if args.resplit:
        from sklearn.model_selection import train_test_split
        tr_frac, va_frac, te_frac = CFG["detection"]["split"]
        strat = df["label"]
        train, tmp = train_test_split(df, test_size=va_frac + te_frac,
                                      stratify=strat, random_state=CFG["detection"]["seed"])
        val, test = train_test_split(tmp, test_size=te_frac / (va_frac + te_frac),
                                     stratify=tmp["label"], random_state=CFG["detection"]["seed"])
        for name, part in [("train", train), ("val", val), ("test", test)]:
            p = path("final") / f"{name}.csv"
            part.drop(columns=["frac_indic"], errors="ignore").to_csv(p, index=False)
            print(f"  {name}: {len(part)} -> {p}")


if __name__ == "__main__":
    main()
