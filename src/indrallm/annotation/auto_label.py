"""BERTScore silver-standard auto-labeling + targeted human verification.

Instead of hand-annotating 5,000 pairs, each model answer is scored against the
Gemini gold answer with BERTScore:
  F1 >= threshold (0.65)  -> correct (label 0)
  F1 <  threshold         -> hallucinated (label 1)

Ambiguous band (0.55-0.75) is exported to data/annotations/human_verify.csv:
send to 2 human verifiers (Google Sheet), have them fill a `human_verdict`
column with correct/hallucinated, then merge back with --merge-votes.

Paper framing: "BERTScore silver-standard labeling followed by human
verification on ambiguous samples."

Usage:
    python -m indrallm.annotation.auto_label                      # score + label + export band
    python -m indrallm.annotation.auto_label --merge-votes data/annotations/human_verify_done.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from indrallm.config import CFG, path


def auto_label() -> None:
    gold_file = path("questions") / "gold_qa_pairs.csv"
    if not gold_file.exists():
        raise SystemExit("gold_qa_pairs.csv missing — run build_gold_qa first")
    gold = pd.read_csv(gold_file)[["qid", "gold_answer", "context"]]

    answer_files = sorted(path("answers").glob("*.csv"))
    answer_files = [f for f in answer_files if "mitigation" not in f.stem]
    if not answer_files:
        raise SystemExit("no answer CSVs — run generate_answers first")

    from bert_score import score

    # BERTScore on CPU segfaults on repeated per-file model loads and on very
    # long/empty inputs. Score ONCE over all files with a light model, clamped.
    MAX_CHARS = 2000

    def clean(s: str) -> str:
        s = str(s).strip()
        return s[:MAX_CHARS] if s else "[no answer]"

    frames = []
    for f in answer_files:
        df = pd.read_csv(f).merge(gold, on="qid", how="inner")
        if df.empty:
            print(f"{f.stem}: no qid overlap with gold, skipping")
            continue
        df["answer"] = df["answer"].fillna("")
        frames.append(df)
    if not frames:
        raise SystemExit("no answers overlap the gold qids")
    allans = pd.concat(frames, ignore_index=True)

    print(f"scoring {len(allans)} answers with BERTScore (single pass)...")
    _, _, f1 = score(
        allans["answer"].map(clean).tolist(),
        allans["gold_answer"].map(clean).tolist(),
        model_type="distilbert-base-uncased", num_layers=5,  # light, CPU-safe
        verbose=True, batch_size=32,
    )
    allans["bertscore_f1"] = [float(x) for x in f1]
    allans.loc[allans["answer"].str.strip() == "", "bertscore_f1"] = 0.0

    thr = CFG["annotation"]["bertscore_threshold"]
    lo, hi = CFG["annotation"]["verify_band"]
    allans["label"] = (allans["bertscore_f1"] < thr).astype(int)
    allans["label_source"] = "bertscore"
    allans["category"] = ""  # filled by humans for verified samples
    allans = allans.rename(columns={"gold_answer": "ground_truth"})

    out = path("final") / "benchmark.csv"
    cols = ["qid", "language", "domain", "question", "model", "answer",
            "label", "category", "ground_truth", "bertscore_f1", "label_source"]
    allans[cols].to_csv(out, index=False)
    print(f"benchmark: {len(allans)} examples "
          f"({allans['label'].mean():.1%} auto-hallucinated) -> {out}")

    band = allans[(allans["bertscore_f1"] > lo) & (allans["bertscore_f1"] < hi)]
    vf = path("annotations") / "human_verify.csv"
    band = band[["qid", "model", "language", "question", "answer", "ground_truth",
                 "bertscore_f1"]].copy()
    band["human_verdict"] = ""   # correct | hallucinated
    band["human_category"] = ""  # factual | temporal | entity | cultural
    band.to_csv(vf, index=False)
    print(f"{len(band)} ambiguous samples ({lo} < F1 < {hi}) -> {vf}\n"
          f"  -> send to 2 verifiers, fill human_verdict, then --merge-votes")


def merge_votes(votes_file: Path) -> None:
    bench_file = path("final") / "benchmark.csv"
    bench = pd.read_csv(bench_file)
    votes = pd.read_csv(votes_file)
    votes = votes[votes["human_verdict"].isin(["correct", "hallucinated"])]
    votes["human_label"] = (votes["human_verdict"] == "hallucinated").astype(int)

    keep = ["qid", "model", "human_label"]
    if "human_category" in votes.columns:
        keep.append("human_category")
    bench = bench.merge(votes[keep], on=["qid", "model"], how="left")
    n = bench["human_label"].notna().sum()
    mask = bench["human_label"].notna()
    bench.loc[mask, "label"] = bench.loc[mask, "human_label"].astype(int)
    bench.loc[mask, "label_source"] = "human"
    if "human_category" in bench.columns:
        cat = bench.pop("human_category")
        bench.loc[mask, "category"] = cat[mask].fillna("")
    bench = bench.drop(columns=["human_label"])
    bench.to_csv(bench_file, index=False)
    print(f"merged {n} human verdicts into {bench_file} "
          f"({bench['label'].mean():.1%} hallucinated after merge)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge-votes", type=Path,
                    help="CSV with filled human_verdict column to merge back")
    args = ap.parse_args()
    if args.merge_votes:
        merge_votes(args.merge_votes)
    else:
        auto_label()


if __name__ == "__main__":
    main()
