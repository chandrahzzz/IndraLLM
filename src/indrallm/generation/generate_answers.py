"""Generate answers for every benchmark question from one or more LLMs.

Resumable: answers are appended to data/answers/<model>.csv and already-answered
qids are skipped, so a crashed/rate-limited run can simply be restarted.

Usage:
    python -m indrallm.generation.generate_answers --models gpt-4o claude
    python -m indrallm.generation.generate_answers --models sarvam --limit 50
"""

from __future__ import annotations

import argparse
import time

import pandas as pd
from tqdm import tqdm

from indrallm.config import CFG, path
from indrallm.generation.llm_clients import get_client


def answer_model(model_name: str, questions: pd.DataFrame, limit: int | None) -> None:
    out_path = path("answers") / f"{model_name}.csv"
    done: set[str] = set()
    if out_path.exists():
        done = set(pd.read_csv(out_path)["qid"].astype(str))
    todo = questions[~questions["qid"].isin(done)]
    if limit:
        todo = todo.head(limit)
    if todo.empty:
        print(f"{model_name}: nothing to do ({len(done)} already answered)")
        return

    client = get_client(model_name)
    rows: list[dict] = []
    for r in tqdm(todo.itertuples(), total=len(todo), desc=model_name):
        try:
            ans = client.generate(r.question)
        except Exception as e:
            print(f"  {r.qid}: {e} — backing off 20s")
            time.sleep(20)
            try:
                ans = client.generate(r.question)
            except Exception as e2:
                print(f"  {r.qid}: failed twice ({e2}), skipping")
                continue
        rows.append({"qid": r.qid, "language": r.language, "domain": r.domain,
                     "question": r.question, "model": model_name, "answer": ans})
        if len(rows) % 25 == 0:  # checkpoint
            _flush(rows, out_path)
            rows = []
    _flush(rows, out_path)
    print(f"{model_name}: done -> {out_path}")


def _flush(rows: list[dict], out_path) -> None:
    if rows:
        pd.DataFrame(rows).to_csv(out_path, mode="a", index=False,
                                  header=not out_path.exists())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--models", nargs="+", required=True,
                    choices=list(CFG["generation"]["models"]))
    ap.add_argument("--limit", type=int, help="cap questions per model (for testing)")
    args = ap.parse_args()

    qfile = path("questions") / "questions.csv"
    if not qfile.exists():
        raise SystemExit("questions.csv missing — run build_questions first")
    questions = pd.read_csv(qfile)
    for m in args.models:
        answer_model(m, questions, args.limit)


if __name__ == "__main__":
    main()
