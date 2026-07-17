"""Cohen's kappa between each annotator pair on their shared (qid, model) items.

Fails loudly (exit code 1) if any pair is below `annotation.min_kappa` (0.75) —
those examples need re-annotation with clarified guidelines.

Usage:
    python -m indrallm.annotation.agreement
"""

from __future__ import annotations

import sys
from itertools import combinations

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from indrallm.config import CFG, path


def main() -> int:
    files = sorted(path("annotations").glob("annotator_*.csv"))
    if len(files) < 2:
        raise SystemExit("need >= 2 annotator CSVs — import from Label Studio first")
    frames = {f.stem.removeprefix("annotator_"): pd.read_csv(f) for f in files}

    min_kappa = CFG["annotation"]["min_kappa"]
    ok = True
    for (a, dfa), (b, dfb) in combinations(frames.items(), 2):
        merged = dfa.merge(dfb, on=["qid", "model"], suffixes=("_a", "_b"))
        if merged.empty:
            continue  # different languages, no overlap
        kappa = cohen_kappa_score(merged["verdict_a"], merged["verdict_b"])
        status = "OK" if kappa >= min_kappa else "BELOW THRESHOLD"
        print(f"{a} vs {b}: n={len(merged)}  kappa={kappa:.3f}  [{status}]")
        if kappa < min_kappa:
            ok = False
            disagreements = merged[merged["verdict_a"] != merged["verdict_b"]]
            out = path("annotations") / f"disagreements_{a}_{b}.csv"
            disagreements.to_csv(out, index=False)
            print(f"  {len(disagreements)} disagreements -> {out} (re-annotate these)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
