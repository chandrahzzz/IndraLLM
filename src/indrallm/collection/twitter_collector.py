"""Collect candidate code-switched tweets via Twitter/X API v2 recent search.

Requires TWITTER_BEARER_TOKEN in .env. NOTE: free academic access is discontinued;
this works on Basic (paid) or institutional access. If unavailable, rely on the
Reddit collector + Google Forms crowdsourcing (see README).

Usage:
    python -m indrallm.collection.twitter_collector --lang ta --max 2000
"""

from __future__ import annotations

import argparse
import time

import pandas as pd
import requests

from indrallm.config import LANGUAGES, api_key, path

SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

# Domain keyword seeds per language: (romanized native hint) + English domain word.
# Queries mix both so results skew code-switched.
QUERY_SEEDS = {
    "ta": ["(medicine OR doctor OR fever) (enna OR epdi OR iruku) lang:en",
           "#Tanglish (health OR exam OR government)",
           "(scheme OR application) (epdi OR pannanum)"],
    "hi": ["(medicine OR doctor OR hospital) (kya OR kaise OR chahiye) lang:en",
           "#Hinglish (health OR exam OR sarkari)",
           "(scheme OR yojana) (kaise OR milega)"],
    "te": ["(medicine OR doctor OR fever) (enti OR ela OR kavali) lang:en",
           "(scheme OR pension) (ela OR eppudu)"],
    "bn": ["(medicine OR doctor) (kemon OR kothay OR hobe) lang:en",
           "(scheme OR card) (kibhabe OR korbo)"],
    "kn": ["(medicine OR doctor OR fever) (hege OR yenu OR beku) lang:en",
           "(scheme OR pension) (hege OR yavaga)"],
}


def search(query: str, bearer: str, max_results: int) -> list[dict]:
    headers = {"Authorization": f"Bearer {bearer}"}
    rows, next_token = [], None
    while len(rows) < max_results:
        params = {
            "query": f"{query} -is:retweet",
            "max_results": min(100, max_results - len(rows)) if max_results - len(rows) >= 10 else 10,
            "tweet.fields": "id,text,created_at,lang",
        }
        if next_token:
            params["next_token"] = next_token
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("x-rate-limit-reset", time.time() + 60)) - time.time()
            print(f"rate limited, sleeping {max(wait, 5):.0f}s")
            time.sleep(max(wait, 5))
            continue
        resp.raise_for_status()
        body = resp.json()
        rows.extend(body.get("data", []))
        next_token = body.get("meta", {}).get("next_token")
        if not next_token:
            break
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lang", required=True, choices=list(LANGUAGES))
    ap.add_argument("--max", type=int, default=2000, help="max tweets across all seed queries")
    args = ap.parse_args()

    bearer = api_key("TWITTER_BEARER_TOKEN")
    per_query = max(args.max // len(QUERY_SEEDS[args.lang]), 10)
    all_rows: list[dict] = []
    for q in QUERY_SEEDS[args.lang]:
        print(f"query: {q}")
        for t in search(q, bearer, per_query):
            all_rows.append({
                "source": "twitter",
                "source_id": t["id"],
                "language": args.lang,
                "text": t["text"],
                "created_at": t.get("created_at", ""),
            })

    df = pd.DataFrame(all_rows).drop_duplicates(subset="text")
    out = path("raw") / f"twitter_{args.lang}.csv"
    df.to_csv(out, index=False)
    print(f"saved {len(df)} tweets -> {out}")


if __name__ == "__main__":
    main()
