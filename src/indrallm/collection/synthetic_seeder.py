"""Gemini synthetic booster: generate romanized code-switched seed sentences.

Reddit alone won't reach 1000/language, so we seed with Gemini 1.5 Flash
(free tier). Output goes through codeswitch_filter like every other source,
so bad generations are dropped, not trusted.

Free-tier safe: sleeps `gold.sleep_seconds` between requests (~15 req/min).

Usage:
    python -m indrallm.collection.synthetic_seeder                # 1 round
    python -m indrallm.collection.synthetic_seeder --rounds 10    # more data
"""

from __future__ import annotations

import argparse
import time

import pandas as pd
from tqdm import tqdm

from indrallm.config import CFG, DOMAINS, LANGUAGES, api_key, path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rounds", type=int, default=1,
                    help="passes over all (language, domain) combos")
    args = ap.parse_args()

    import google.generativeai as genai
    genai.configure(api_key=api_key("GOOGLE_API_KEY"))
    g = CFG["gold"]
    model = genai.GenerativeModel(g["model"])
    per_prompt = g["synthetic_per_prompt"]

    out_path = path("raw") / "synthetic.csv"
    rows: list[dict] = []
    combos = [(lc, ln, d) for lc, ln in LANGUAGES.items() for d in DOMAINS] * args.rounds
    for lang_code, lang_name, domain in tqdm(combos, desc="synthetic"):
        prompt = (
            f"Generate {per_prompt} factual QUESTIONS a real Indian user might ask about "
            f"{domain}, written in Romanized {lang_name}-English code-switching "
            f"(Latin alphabet only, mixing {lang_name} and English words naturally). "
            f"Vary the topics. Output just the questions, one per line, no numbering."
        )
        try:
            resp = model.generate_content(prompt)
            for line in resp.text.strip().splitlines():
                line = line.strip().lstrip("-*0123456789. ")
                if line:
                    rows.append({"source": "synthetic", "language": lang_code,
                                 "domain": domain, "text": line})
        except Exception as e:  # rate limit / safety block — skip combo, keep going
            print(f"  skip {lang_code}/{domain}: {e}")
        time.sleep(g["sleep_seconds"])

    df = pd.DataFrame(rows).drop_duplicates(subset="text")
    if out_path.exists():  # append across runs, dedup
        df = pd.concat([pd.read_csv(out_path), df]).drop_duplicates(subset="text")
    df.to_csv(out_path, index=False)
    print(f"saved {len(df)} synthetic seeds -> {out_path}")


if __name__ == "__main__":
    main()
