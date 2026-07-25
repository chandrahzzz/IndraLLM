"""Extract model-internal probe features once and cache to parquet, keyed by qid|model.

Only the two viable feature families remain (surface + cross-lingual features were
removed after they failed the gate):

  internal  from internal_probes — hsd_*, ae_*, uc_*, perplexity, conf_mean,
            logit_var_mean, n_tokens                                   (GPU)
  rsc       from self_consistency — rsc_token_div, rsc_embed_div       (GPU, slow)

Both need Sarvam-2B forward passes, so this runs on a Colab T4. Output is
resumable: rows already cached are skipped, so a run cut off by a Colab timeout
resumes cleanly.

Usage:
    python -m indrallm.detection.lidar.feature_cache --internal          # HSD/AE/UC
    python -m indrallm.detection.lidar.feature_cache --internal --rsc    # + self-consistency
"""

from __future__ import annotations

import argparse

import pandas as pd
from tqdm import tqdm

from indrallm.config import path


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
    ap.add_argument("--internal", action="store_true",
                    help="extract HSD/AE/UC (default action; needs GPU)")
    ap.add_argument("--rsc", action="store_true", help="add self-consistency (needs GPU, slow)")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    # internal is the only base feature source now; run it unless only --rsc was asked
    do_internal = args.internal or not args.rsc

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
          f"({'internal' if do_internal else ''}{' +rsc' if args.rsc else ''})")

    internal = None
    if do_internal:
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
