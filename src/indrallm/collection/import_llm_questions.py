"""Import externally-generated (question[, answer]) pairs from an LLM.

Accepts pipe-separated text files produced by prompting a strong LLM
(Claude/GPT) — see the prompt in the project chat. Two accepted line formats:

    language|domain|question|answer      (4 fields: gold answer included — preferred)
    language|domain|question             (3 fields: answer generated later)

Lines are validated (known language code, non-empty), deduped, and written to
data/raw/llm_imported.csv with columns: source, language, domain, text[, gold_answer].
Then run codeswitch_filter and build_gold_qa as usual. If gold answers are present
they seed data/questions/gold_qa_pairs.csv directly (skipping Gemini).

Usage:
    python -m indrallm.collection.import_llm_questions --files data/raw/llm_questions.txt
    python -m indrallm.collection.import_llm_questions --files data/raw/llm_*.txt --seed-gold
"""

from __future__ import annotations

import argparse
import glob
import hashlib
from pathlib import Path

import pandas as pd

from indrallm.config import DOMAINS, LANGUAGES, path


def _qid(lang: str, src: str) -> str:
    return f"{lang}-{hashlib.sha1(f'{lang}|{src}'.encode()).hexdigest()[:8]}"


def parse_files(patterns: list[str]) -> pd.DataFrame:
    rows: list[dict] = []
    skipped = 0
    files: list[str] = []
    for p in patterns:
        files.extend(glob.glob(p))
    if not files:
        raise SystemExit(f"no files matched: {patterns}")
    for fp in files:
        for raw in Path(fp).read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [c.strip() for c in line.split("|")]
            if len(parts) < 3:
                skipped += 1
                continue
            lang, domain, question = parts[0].lower(), parts[1].lower(), parts[2]
            answer = parts[3] if len(parts) >= 4 else ""
            if lang not in LANGUAGES or not question:
                skipped += 1
                continue
            if domain not in DOMAINS:
                domain = ""
            rows.append({"source": "llm", "language": lang, "domain": domain,
                         "text": question, "gold_answer": answer})
    df = pd.DataFrame(rows).drop_duplicates(subset="text").reset_index(drop=True)
    print(f"parsed {len(df)} questions ({skipped} lines skipped) from {len(files)} file(s)")
    print("  by language:", df.groupby("language").size().to_dict())
    with_gold = (df["gold_answer"].str.len() > 0).sum()
    print(f"  {with_gold} include a gold answer")
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--files", nargs="+", required=True,
                    help="text file(s) or glob(s), pipe-separated lines")
    ap.add_argument("--seed-gold", action="store_true",
                    help="also append rows-with-answers straight into gold_qa_pairs.csv")
    args = ap.parse_args()

    df = parse_files(args.files)
    out = path("raw") / "llm_imported.csv"
    df.to_csv(out, index=False)
    print(f"saved -> {out}  (next: codeswitch_filter, then build_gold_qa)")

    if args.seed_gold:
        gold = df[df["gold_answer"].str.len() > 0].copy()
        if gold.empty:
            print("--seed-gold: no answered rows found, nothing seeded")
            return
        gold["source_text"] = gold["text"]
        gold["question"] = gold["text"]
        gold["context"] = ""
        gold["qid"] = [_qid(r.language, r.source_text) for r in gold.itertuples()]
        cols = ["qid", "language", "domain", "source", "source_text",
                "context", "question", "gold_answer"]
        gp = path("questions") / "gold_qa_pairs.csv"
        if gp.exists():
            prev = pd.read_csv(gp)
            gold = pd.concat([prev, gold[cols]]).drop_duplicates(subset="qid")
        else:
            gold = gold[cols]
        gold.to_csv(gp, index=False)
        # rebuild questions.csv
        q = gold[["qid", "language", "domain", "question", "source"]]
        q.to_csv(path("questions") / "questions.csv", index=False)
        print(f"seeded gold_qa_pairs.csv -> {len(gold)} total pairs "
              f"(still run codeswitch_filter on data/raw to validate NEW ones)")


if __name__ == "__main__":
    main()
