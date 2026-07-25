"""Real hallucination labels via a Gemini LLM-judge (free tier — no Groq spend).

Why this exists: BERTScore(answer, English-gold) and multilingual embedding
similarity are both *surface-similarity* proxies. A factually correct answer
phrased differently scores low; a fluent wrong answer scores high. Neither is a
trustworthy hallucination label — see the LIDAR probe confound analysis.

This judge reads the question, the model answer, and the gold answer, and rules
CORRECT / HALLUCINATED on *factual* grounds, tolerating code-switching and
paraphrase. Output is a real label the detector and the LIDAR features can be
honestly evaluated against.

Cost: Gemini free tier only. Rate-limited by `gold.sleep_seconds`. Resumable:
progress is flushed to data/annotations/llm_judge.csv after every row, so a run
killed by the daily quota can be restarted and picks up where it stopped.

Usage:
    python -m indrallm.annotation.llm_judge_label --limit 40      # pilot
    python -m indrallm.annotation.llm_judge_label                 # full (hours)
    python -m indrallm.annotation.llm_judge_label --merge         # write benchmark_judged.csv
"""

from __future__ import annotations

import argparse
import re
import time

import pandas as pd

from indrallm.config import CFG, path

# flash-lite has the highest free-tier cap; plenty for a binary factual verdict.
JUDGE_MODEL = CFG["gold"].get("seed_model", CFG["gold"]["model"])
# free-tier RPM is ~5 for flash / higher for lite; keep a safe gap to avoid quota crashes
JUDGE_SLEEP = 13

PROMPT = """You are grading whether a model's ANSWER to a user QUESTION is factually correct.
You are given a trusted GOLD answer. The answer may mix an Indian language with English
(code-switching) and may be phrased very differently from the gold — that is fine.
Judge ONLY factual correctness and whether it actually addresses the question.

Reply on a single line in exactly this format:
VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>

QUESTION: {question}
GOLD ANSWER: {gold}
MODEL ANSWER: {answer}"""

_VERDICT_RE = re.compile(r"VERDICT:\s*(CORRECT|HALLUCINATED)", re.I)


def _judge(client, question: str, gold: str, answer: str) -> tuple[int, str]:
    """Return (label, reason); label 1 = hallucinated. Parse-failure -> (-1, raw)."""
    try:
        raw = client.generate(PROMPT.format(question=question, gold=gold, answer=answer))
    except Exception as e:  # quota / network — signal caller to stop cleanly
        raise RuntimeError(f"judge call failed: {e}") from e
    m = _VERDICT_RE.search(raw or "")
    if not m:
        return -1, (raw or "").strip()[:120]
    label = 0 if m.group(1).upper() == "CORRECT" else 1
    reason = raw.split("REASON:", 1)[1].strip()[:120] if "REASON:" in raw else ""
    return label, reason


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, help="grade only the first N ungraded rows (pilot)")
    ap.add_argument("--merge", action="store_true",
                    help="join graded labels onto benchmark.csv -> benchmark_judged.csv")
    ap.add_argument("--provider", default="google", choices=["google", "groq"],
                    help="google=free/slow (5 rpm), groq=fast/cheap (~$0.06 for all rows)")
    ap.add_argument("--model", help="override model id (default per provider)")
    ap.add_argument("--sleep", type=float, help="seconds between calls (default: provider-based)")
    args = ap.parse_args()

    out = path("annotations") / "llm_judge.csv"

    if args.merge:
        _merge(out)
        return

    df = pd.read_csv(path("final") / "benchmark.csv")
    df["answer"] = df["answer"].fillna("").astype(str)
    df["ground_truth"] = df["ground_truth"].fillna("").astype(str)
    df = df[(df["answer"].str.strip() != "") & (df["ground_truth"].str.strip() != "")]

    done: set[str] = set()
    if out.exists():
        prev = pd.read_csv(out)
        done = set(prev["qid_model"])
        print(f"resume: {len(done)} rows already graded")

    df["qid_model"] = df["qid"].astype(str) + "|" + df["model"].astype(str)
    todo = df[~df["qid_model"].isin(done)]
    if args.limit:
        todo = todo.head(args.limit)

    if args.provider == "groq":
        from indrallm.generation.llm_clients import GroqClient
        model = args.model or "llama-3.1-8b-instant"
        client = GroqClient(model)
        sleep = args.sleep if args.sleep is not None else 1.0  # ~30 rpm free-tier safe
    else:
        from indrallm.generation.llm_clients import GoogleClient
        model = args.model or JUDGE_MODEL
        client = GoogleClient(model)
        sleep = args.sleep if args.sleep is not None else JUDGE_SLEEP
    print(f"grading {len(todo)} rows with {args.provider}:{model} ({sleep}s gap)")

    graded, fails = 0, 0
    for r in todo.itertuples():
        try:
            label, reason = _judge(client, r.question, r.ground_truth, r.answer)
        except RuntimeError as e:
            print(f"stopping ({e}) — progress saved, rerun to resume")
            break
        row = pd.DataFrame([{"qid_model": r.qid_model, "qid": r.qid, "model": r.model,
                             "judge_label": label, "judge_reason": reason}])
        row.to_csv(out, mode="a", header=not out.exists(), index=False)
        graded += 1
        fails += label == -1
        if graded % 25 == 0:
            print(f"  {graded}/{len(todo)} graded ({fails} parse-fails)")
        time.sleep(sleep)

    print(f"done: {graded} graded, {fails} parse-fails -> {out}")
    if graded:
        print("next: python -m indrallm.annotation.llm_judge_label --merge")


def _merge(judge_csv) -> None:
    if not judge_csv.exists():
        print(f"no {judge_csv} yet — run the judge first")
        return
    j = pd.read_csv(judge_csv)
    j = j[j["judge_label"] >= 0]  # drop parse failures
    df = pd.read_csv(path("final") / "benchmark.csv")
    df["qid_model"] = df["qid"].astype(str) + "|" + df["model"].astype(str)
    merged = df.merge(j[["qid_model", "judge_label", "judge_reason"]], on="qid_model", how="inner")
    merged["label_bertscore"] = merged["label"]
    merged["label"] = merged["judge_label"].astype(int)
    merged["label_source"] = "llm_judge_gemini"
    merged = merged.drop(columns=["qid_model", "judge_label"])
    dest = path("final") / "benchmark_judged.csv"
    merged.to_csv(dest, index=False)
    n1 = int(merged["label"].sum())
    print(f"merged {len(merged)} judged rows -> {dest}")
    print(f"label balance: correct={len(merged) - n1} hallucinated={n1} ({merged['label'].mean():.1%} positive)")
    print("next: probe --file benchmark_judged.csv ; then aggregate_labels for splits")


if __name__ == "__main__":
    main()
