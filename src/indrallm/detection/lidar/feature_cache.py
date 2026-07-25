"""Extract every Phase-1 feature once and cache to parquet, keyed by qid|model.

Feature families (answer-level aggregates; the detector reads these):
  surface     from features.py  — bcs, switch_rate, frac_en, frac_indic, frac_other,
                                   n_tokens, plus repetition_score (behavioral)
  crosslingual from cross_lingual — cla_mean, cla_min, cla_max_drop, n_boundaries
  internal    from internal_probes — hsd_*, ae_*, uc_*, perplexity, conf_mean  (GPU)
  rsc         from self_consistency — rsc_token_div, rsc_embed_div             (GPU, slow)

Surface + crosslingual run on CPU (laptop). internal + rsc need a GPU (Colab T4)
and are opt-in via flags. Output is resumable: rows already in the cache are
skipped, so a run interrupted by a Colab timeout resumes cleanly.

Usage:
    python -m indrallm.detection.lidar.feature_cache                      # CPU: surface + CLA
    python -m indrallm.detection.lidar.feature_cache --internal           # + HSD/AE/UC  (GPU)
    python -m indrallm.detection.lidar.feature_cache --internal --rsc     # + self-consistency (GPU)
"""

from __future__ import annotations

import argparse
import re

import pandas as pd
from tqdm import tqdm

from indrallm.config import path
from indrallm.detection.lidar.features import (extract_features, fit_transition_matrix,
                                               _make_embedder)
from indrallm.detection.lidar.cross_lingual import cla_features


def repetition_score(answer: str, n: int = 3) -> float:
    """Fraction of repeated n-grams — a cheap behavioral degradation signal."""
    toks = re.findall(r"[^\s\W_]+", (answer or "").lower())
    if len(toks) < n + 1:
        return 0.0
    grams = [tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    return 1.0 - len(set(grams)) / len(grams)


def _load_benchmark() -> pd.DataFrame:
    for name in ("benchmark_judged.csv", "benchmark.csv"):
        p = path("final") / name
        if p.exists():
            df = pd.read_csv(p)
            print(f"labels from {name}")
            break
    else:
        raise FileNotFoundError("no benchmark_judged.csv or benchmark.csv in data/final")
    df["answer"] = df["answer"].fillna("").astype(str)
    df = df[df["answer"].str.strip() != ""].reset_index(drop=True)
    df["qid_model"] = df["qid"].astype(str) + "|" + df["model"].astype(str)
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--internal", action="store_true", help="add HSD/AE/UC (needs GPU)")
    ap.add_argument("--rsc", action="store_true", help="add self-consistency (needs GPU, slow)")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    df = _load_benchmark()
    if args.limit:
        df = df.head(args.limit)

    out = path("features") / "answer_features.parquet"
    done: set[str] = set()
    if out.exists():
        done = set(pd.read_parquet(out)["qid_model"])
        print(f"resume: {len(done)} rows cached")
    todo = df[~df["qid_model"].isin(done)]
    print(f"extracting {len(todo)} rows "
          f"(surface+CLA{' +internal' if args.internal else ''}{' +rsc' if args.rsc else ''})")

    tm = fit_transition_matrix(df["question"].tolist(),
                               df.get("language", pd.Series([None] * len(df))).tolist())
    embed = _make_embedder(True)

    internal = None
    if args.internal:
        from indrallm.detection.lidar.internal_probes import InternalProbes
        internal = InternalProbes()
    rsc = None
    if args.rsc:
        from indrallm.detection.lidar.self_consistency import SelfConsistency
        rsc = SelfConsistency()

    buffer, FLUSH = [], 50
    existing = pd.read_parquet(out) if out.exists() else None

    def flush():
        nonlocal existing, buffer
        if not buffer:
            return
        add = pd.DataFrame(buffer)
        existing = add if existing is None else pd.concat([existing, add], ignore_index=True)
        existing.to_parquet(out, index=False)
        buffer = []

    for r in tqdm(todo.itertuples(), total=len(todo)):
        lang = getattr(r, "language", None)
        row = {"qid_model": r.qid_model, "qid": r.qid, "model": r.model,
               "language": lang, "label": int(getattr(r, "label", 0))}
        row.update(extract_features(r.answer, tm, lang, embed))
        row["repetition_score"] = repetition_score(r.answer)
        row.update(cla_features(r.answer, lang))
        if internal is not None:
            row.update(internal.extract(r.question, r.answer)["answer"])
        if rsc is not None:
            row.update(rsc.extract(r.question))
        buffer.append(row)
        if len(buffer) >= FLUSH:
            flush()
    flush()
    print(f"saved -> {out}  ({0 if existing is None else len(existing)} rows total)")


if __name__ == "__main__":
    main()
