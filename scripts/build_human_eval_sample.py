"""Build the blinded, stratified human-evaluation sample (research/HUMAN_EVAL_PROTOCOL.md).

Writes results/EXP-004-budget-rejudge/human_eval/:
  items_blinded.csv  item_id, question, gold_answer, model_answer + empty label columns
  key.csv            item_id -> prompt_id, condition, language, verdicts, sampling weight
  reviewers.csv      empty template
No API calls.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "EXP-004-budget-rejudge" / "human_eval"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20261010
PER_CELL_LANG = 2  # items per condition x verdict x language


def load() -> pd.DataFrame:
    rows = [json.loads(l) for f in ["results/EXP-002/full_predictions.jsonl",
                                    "results/EXP-003-matched-en/matched_predictions.jsonl"]
            for l in open(ROOT / f, encoding="utf-8")]
    df = pd.DataFrame(rows)
    return df[(df.model == "qwen/qwen3.8-27b") & (df.partition == "TEST-OOD")].reset_index(drop=True)


def main() -> None:
    rng = np.random.default_rng(SEED)
    df = load()
    jfile = ROOT / "results/EXP-004-budget-rejudge/judgements.jsonl"
    if jfile.exists():
        j = pd.DataFrame([json.loads(l) for l in open(jfile, encoding="utf-8")])
        j = j[j.source == "orig128"].pivot_table(index="prompt_id", columns="judge", values="judge_label", aggfunc="first")
        df = df.merge(j, left_on="prompt_id", right_index=True, how="left")
    picked = []
    for (cond, verdict), cell in df.groupby(["condition", "judge_label"]):
        target = PER_CELL_LANG * 5
        chosen = []
        for lang, sub in cell.groupby("language"):
            take = min(PER_CELL_LANG, len(sub))
            chosen += list(rng.choice(sub.index, size=take, replace=False))
        rest = cell.index.difference(chosen)
        short = min(target - len(chosen), len(rest))
        if short > 0:
            chosen += list(rng.choice(rest, size=short, replace=False))
        for i in chosen:
            picked.append((i, len(chosen) / len(cell), "main"))
    main_idx = {i for i, _, _ in picked}
    if {"J-QWEN", "J-OSS"} <= set(df.columns):
        dis = df[(df["J-QWEN"] != df["J-OSS"]) & df["J-OSS"].isin([0, 1]) & ~df.index.isin(main_idx)]
        if len(dis):
            extra = rng.choice(dis.index, size=min(30, len(dis)), replace=False)
            picked += [(i, np.nan, "judge_disagreement") for i in extra]

    sample = df.loc[[i for i, _, _ in picked]].copy()
    sample["sampling_fraction"] = [w for _, w, _ in picked]
    sample["subset"] = [s for _, _, s in picked]
    sample = sample.sample(frac=1, random_state=SEED).reset_index(drop=True)
    sample["item_id"] = [f"H{k:03d}" for k in range(1, len(sample) + 1)]

    blinded = sample[["item_id", "prompt_text", "reference_answer", "model_response"]].rename(
        columns={"prompt_text": "question", "reference_answer": "gold_answer", "model_response": "model_answer"})
    for col in ["reviewer", "label", "answer_language_matches_question", "gold_seems_wrong_or_outdated", "note"]:
        blinded[col] = ""
    blinded.to_csv(OUT / "items_blinded.csv", index=False, encoding="utf-8-sig")
    keep = ["item_id", "prompt_id", "semantic_id", "condition", "language", "target_entity", "subset",
            "sampling_fraction", "judge_label", "judge_reason"] + [c for c in ["J-QWEN", "J-OSS"] if c in sample]
    sample[keep].to_csv(OUT / "key.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=["reviewer_id", "languages_read", "background", "items_assigned"]).to_csv(
        OUT / "reviewers.csv", index=False)
    print(sample.groupby(["subset", "condition", "judge_label"]).size())
    wave2(rng)
    print("wrote", OUT)


def wave2(rng) -> None:
    """512-token outputs: 3 conditions x J-QWEN verdict x 10 items (stratified by language)."""
    g = pd.DataFrame([json.loads(l) for l in open(ROOT / "results/EXP-004-budget-rejudge/gen512_predictions.jsonl", encoding="utf-8")])
    j = pd.DataFrame([json.loads(l) for l in open(ROOT / "results/EXP-004-budget-rejudge/judgements.jsonl", encoding="utf-8")])
    j = j[j.source == "gen512"].pivot_table(index="prompt_id", columns="judge", values="judge_label", aggfunc="first")
    g = g.merge(j, left_on="prompt_id", right_index=True)
    picked = []
    for (cond, verdict), cell in g.groupby(["condition", "J-QWEN"]):
        chosen = []
        for _, sub in cell.groupby("language"):
            chosen += list(rng.choice(sub.index, size=min(2, len(sub)), replace=False))
        rest = cell.index.difference(chosen)
        extra = min(10 - len(chosen), len(rest))
        if extra > 0:
            chosen += list(rng.choice(rest, size=extra, replace=False))
        picked += [(i, len(chosen) / len(cell)) for i in chosen]
    s = g.loc[[i for i, _ in picked]].copy()
    s["sampling_fraction"] = [w for _, w in picked]
    s = s.sample(frac=1, random_state=SEED).reset_index(drop=True)
    s["item_id"] = [f"W{k:03d}" for k in range(1, len(s) + 1)]
    b = s[["item_id", "prompt_text", "reference_answer", "model_response"]].rename(
        columns={"prompt_text": "question", "reference_answer": "gold_answer", "model_response": "model_answer"})
    for col in ["reviewer", "label", "answer_language_matches_question", "gold_seems_wrong_or_outdated", "note"]:
        b[col] = ""
    b.to_csv(OUT / "items_blinded_512.csv", index=False, encoding="utf-8-sig")
    s[["item_id", "prompt_id", "semantic_id", "condition", "language", "target_entity", "sampling_fraction",
       "finish_reason", "J-QWEN", "J-OSS"]].to_csv(OUT / "key_512.csv", index=False, encoding="utf-8-sig")
    print("wave 2 (512 tokens):", len(s), "items")


if __name__ == "__main__":
    main()
