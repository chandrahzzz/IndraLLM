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

# Free tier gives EACH model its own daily request quota, so rotating across a
# pool multiplies daily throughput (~N models x per-model RPD).
GEMINI_POOL = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-3-flash-preview",
]


class RotatingGemini:
    """Round-robins a pool of Gemini models; on 429 drops to the next model and
    only sleeps once every model in the pool is rate-limited."""

    def __init__(self, models: list[str] | None = None):
        import google.generativeai as genai
        names = models or GEMINI_POOL
        self._models = [genai.GenerativeModel(n) for n in names]
        self._names = names
        self._i = 0

    def generate(self, prompt: str, **kwargs) -> str:
        import re as _re
        n = len(self._models)
        consecutive_429 = 0
        while True:
            idx = self._i % n
            try:
                resp = self._models[idx].generate_content(prompt, **kwargs)
                return resp.text
            except Exception as e:
                msg = str(e)
                is_429 = "429" in msg or "ResourceExhausted" in type(e).__name__
                if not is_429:
                    raise
                self._i += 1
                consecutive_429 += 1
                if consecutive_429 >= n:  # whole pool exhausted -> back off
                    m = _re.search(r"seconds:?\s*(\d+)", msg)
                    wait = int(m.group(1)) + 2 if m else 30
                    print(f"  all {n} models rate-limited — waiting {wait}s")
                    time.sleep(wait)
                    consecutive_429 = 0


def generate_with_retry(model, prompt: str, retries: int = 4, **kwargs):
    """Single-model 429 retry (kept for seeder; honors server retry_delay)."""
    import re as _re
    for attempt in range(retries):
        try:
            return model.generate_content(prompt, **kwargs)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "ResourceExhausted" in type(e).__name__:
                m = _re.search(r"seconds:?\s*(\d+)", msg)
                wait = int(m.group(1)) + 2 if m else 30
                print(f"  429 — waiting {wait}s (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("still rate-limited after retries")


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
    model = RotatingGemini()  # rotates the pool for 4x free-tier throughput

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
            resp_text = model.generate(PROMPT.format(
                text=r.text, lang_name=LANGUAGES[r.language]))
            parts = [p.strip() for p in resp_text.strip().split("|")]
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
