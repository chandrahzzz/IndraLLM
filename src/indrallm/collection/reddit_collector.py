"""Collect candidate code-switched posts/comments from Indian subreddits via PRAW.

Free: create a "script" app at https://www.reddit.com/prefs/apps and put the
client id/secret in .env.

Usage:
    python -m indrallm.collection.reddit_collector --max 2000
"""

from __future__ import annotations

import argparse
import os

import pandas as pd

from indrallm.config import api_key, path

SUBREDDITS = [
    "india", "AskIndia", "IndiaSpeaks", "indiasocial",
    "TamilNadu", "Chennai", "hyderabad", "telugu",
    "kolkata", "bangalore", "karnataka", "delhi", "mumbai",
]

# Health/education/government/agriculture flavored search terms; mixed-language
# phrasing so results skew code-switched. Language is verified later by the filter.
SEARCH_TERMS = [
    "doctor kaise", "medicine chahiye", "hospital appointment kaise",
    "exam epdi", "medicine edukkanum", "scheme apply pannanum",
    "pension ela", "ration card kibhabe", "fever medicine yenu",
    "aadhaar kaise", "scholarship kaise milega", "crop insurance kaise",
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max", type=int, default=2000, help="max items overall")
    args = ap.parse_args()

    import praw

    reddit = praw.Reddit(
        client_id=api_key("REDDIT_CLIENT_ID"),
        client_secret=api_key("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT", "IndraLLM research script"),
    )

    rows: list[dict] = []
    per_term = max(args.max // (len(SEARCH_TERMS)), 5)
    for term in SEARCH_TERMS:
        for sub in SUBREDDITS:
            if len(rows) >= args.max:
                break
            try:
                for post in reddit.subreddit(sub).search(term, limit=per_term):
                    text = f"{post.title} {post.selftext or ''}".strip()
                    rows.append({
                        "source": "reddit",
                        "source_id": post.id,
                        "language": "",  # determined by codeswitch_filter
                        "text": text,
                        "created_at": post.created_utc,
                    })
            except Exception as e:  # subreddit may be private/banned; skip
                print(f"  skip r/{sub} '{term}': {e}")

    df = pd.DataFrame(rows).drop_duplicates(subset="text")
    out = path("raw") / "reddit.csv"
    df.to_csv(out, index=False)
    print(f"saved {len(df)} posts -> {out}")


if __name__ == "__main__":
    main()
