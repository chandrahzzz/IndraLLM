"""Build gold QA pairs: for each filtered code-switched text, Gemini generates a
factual context, a code-switched question, and the gold answer.

The gold answer is the reference for BERTScore auto-labeling (annotation/auto_label.py).

Resumable: appends to gold_qa_pairs.csv, skips texts already processed.
Also writes data/questions/questions.csv (qid, language, domain, question, source)
so generate_answers works unchanged.

Usage:
    python -m indrallm.collection.build_gold_qa
    python -m indrallm.collection.build_gold_qa --limit 50    # smoke test
"""

from __future__ import annotations

import argparse
import time

import pandas as pd
from tqdm import tqdm

from indrallm.config import CFG, LANGUAGES, path

PROMPT = """Given this code-mixed sentence: "{text}"

1. Write a 2-sentence factual English context related to it.
2. Write ONE code-switched question in Romanized {lang_name}-English based on that context.
3. Write the exact factual answer to that question (1-2 sentences).

Output EXACTLY one line in this format (single pipes, no extra text):
context|question|answer"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, help="cap new items (for testing)")
    args = ap.parse_args()

    import google.generativeai as genai
    from indrallm.config import api_key
    genai.configure(api_key=api_key("GOOGLE_API_KEY"))
    g = CFG["gold"]
    model = genai.GenerativeModel(g["model"])

    files = sorted(path("filtered").glob("*.csv"))
    if not files:
        raise SystemExit("no filtered CSVs — run codeswitch_filter first")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    if "cs_lang" in df.columns:
        df["language"] = df["cs_lang"].fillna(df.get("language"))
    df = df[df["language"].isin(LANGUAGES)].drop_duplicates(subset="text")

    out_path = path("questions") / "gold_qa_pairs.csv"
    done: set[str] = set()
    if out_path.exists():
        done = set(pd.read_csv(out_path)["source_text"].astype(str))
    todo = df[~df["text"].astype(str).isin(done)]
    if args.limit:
        todo = todo.head(args.limit)
    print(f"{len(done)} done, {len(todo)} to generate")

    rows: list[dict] = []
    for r in tqdm(todo.itertuples(), total=len(todo), desc="gold QA"):
        try:
            resp = model.generate_content(PROMPT.format(
                text=r.text, lang_name=LANGUAGES[r.language]))
            parts = [p.strip() for p in resp.text.strip().split("|")]
            if len(parts) != 3 or not all(parts):
                print(f"  bad format, skip: {str(r.text)[:60]}")
                continue
            rows.append({
                "language": r.language,
                "domain": getattr(r, "domain", "") or "",
                "source": getattr(r, "source", "") or "",
                "source_text": r.text,
                "context": parts[0], "question": parts[1], "gold_answer": parts[2],
            })
        except Exception as e:
            print(f"  skip: {e}")
        time.sleep(g["sleep_seconds"])
        if len(rows) % 25 == 0 and rows:  # checkpoint
            _flush(rows, out_path)
            rows = []
    _flush(rows, out_path)

    # rebuild qids + questions.csv for the generation stage
    gold = pd.read_csv(out_path)
    gold["qid"] = [f"{r.language}-{i:04d}" for i, r in enumerate(gold.itertuples())]
    gold.to_csv(out_path, index=False)
    q = gold.rename(columns={})[["qid", "language", "domain", "question", "source"]]
    qfile = path("questions") / "questions.csv"
    q.to_csv(qfile, index=False)
    print(f"{len(gold)} gold QA pairs -> {out_path}\n{len(q)} questions -> {qfile}")


def _flush(rows: list[dict], out_path) -> None:
    if rows:
        pd.DataFrame(rows).to_csv(out_path, mode="a", index=False,
                                  header=not out_path.exists())


if __name__ == "__main__":
    main()
