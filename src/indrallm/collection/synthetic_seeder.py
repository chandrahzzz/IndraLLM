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
import random
import time

import pandas as pd
from tqdm import tqdm

from indrallm.collection.build_gold_qa import generate_with_retry
from indrallm.config import CFG, DOMAINS, LANGUAGES, api_key, path

# Per-domain subtopic spices — 2 random ones per request so repeated rounds
# don't regenerate the same questions (dedup was eating ~90% without this).
SUBTOPICS = {
    "health": ["fever and dengue", "diabetes/sugar", "BP", "pregnancy care",
               "child vaccination", "eye problems", "dental", "mental health",
               "ayurveda vs allopathy", "health insurance", "generic medicines",
               "first aid", "skin problems", "diet and nutrition"],
    "education": ["NEET/JEE prep", "scholarships", "college admission",
                  "school fees", "online classes", "exam results", "hostel life",
                  "engineering vs arts", "study abroad", "government schools",
                  "coaching centres", "degree certificates"],
    "government": ["Aadhaar", "ration card", "PAN card", "voter ID", "passport",
                   "driving license", "pension schemes", "PM-Kisan", "MGNREGA",
                   "property registration", "income certificate", "RTI",
                   "electricity bill", "water connection"],
    "agriculture": ["crop insurance", "fertilizer subsidy", "drip irrigation",
                    "seed varieties", "mandi prices", "soil testing",
                    "organic farming", "tractor loans", "pest control",
                    "monsoon planning", "dairy farming", "cold storage"],
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rounds", type=int, default=1,
                    help="passes over all (language, domain) combos")
    args = ap.parse_args()

    import google.generativeai as genai
    from indrallm.collection.build_gold_qa import RotatingGemini
    genai.configure(api_key=api_key("GOOGLE_API_KEY"))
    g = CFG["gold"]
    model = RotatingGemini()  # rotate pool for 4x free-tier throughput
    per_prompt = g["synthetic_per_prompt"]

    from indrallm.collection.build_gold_qa import QuotaExhausted

    out_path = path("raw") / "synthetic.csv"
    rows: list[dict] = []

    def flush():
        nonlocal rows
        if not rows:
            return
        df = pd.DataFrame(rows).drop_duplicates(subset="text")
        if out_path.exists():
            df = pd.concat([pd.read_csv(out_path), df]).drop_duplicates(subset="text")
        df.to_csv(out_path, index=False)
        rows = []  # persisted; start fresh

    combos = [(lc, ln, d) for lc, ln in LANGUAGES.items() for d in DOMAINS] * args.rounds
    quota_done = False
    for i, (lang_code, lang_name, domain) in enumerate(tqdm(combos, desc="synthetic")):
        spice = ", ".join(random.sample(SUBTOPICS[domain], 2))
        prompt = (
            f"Generate {per_prompt} factual QUESTIONS a real Indian user might ask about "
            f"{domain} (specifically: {spice}), written in Romanized {lang_name}-English "
            f"code-switching (Latin alphabet only, mixing {lang_name} and English words "
            f"naturally). Output just the questions, one per line, no numbering."
        )
        try:
            resp_text = model.generate(prompt, generation_config={"temperature": 1.0})
            for line in resp_text.strip().splitlines():
                line = line.strip().lstrip("-*0123456789. ")
                if line:
                    rows.append({"source": "synthetic", "language": lang_code,
                                 "domain": domain, "text": line})
        except QuotaExhausted:
            print("\ndaily Gemini quota spent — saving progress, resume tomorrow")
            quota_done = True
            break
        except Exception as e:  # safety block etc — skip combo, keep going
            print(f"  skip {lang_code}/{domain}: {e}")
        if i % 20 == 0 and i:  # periodic checkpoint
            flush()
        time.sleep(1)

    flush()
    total = len(pd.read_csv(out_path)) if out_path.exists() else 0
    print(f"synthetic.csv now holds {total} seeds"
          + (" (quota-limited this run)" if quota_done else ""))


if __name__ == "__main__":
    main()
