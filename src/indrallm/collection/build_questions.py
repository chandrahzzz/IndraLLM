"""Turn filtered code-switched text into the final question set.

Merges all data/filtered/*.csv, keeps question-like items, assigns question ids,
balances per language up to `target_per_language`, and writes
data/questions/questions.csv with columns:
    qid, language, domain, question, source

Domain assignment: keyword heuristic; blank domains should be fixed by hand or
during annotation.

Usage:
    python -m indrallm.collection.build_questions
"""

from __future__ import annotations

import re

import pandas as pd

from indrallm.config import CFG, DOMAINS, LANGUAGES, path

DOMAIN_KEYWORDS = {
    "health": ["medicine", "doctor", "hospital", "fever", "tablet", "vaccine",
               "clinic", "symptom", "pain", "pregnan", "bp", "sugar", "dose"],
    "education": ["exam", "college", "school", "admission", "scholarship",
                  "syllabus", "result", "marks", "degree", "neet", "jee"],
    "government": ["scheme", "yojana", "aadhaar", "aadhar", "pension", "ration",
                   "passport", "license", "certificate", "pan card", "voter"],
    "agriculture": ["crop", "farmer", "fertilizer", "seed", "irrigation",
                    "kisan", "mandi", "harvest", "pesticide", "subsidy"],
}

QUESTION_MARKERS = re.compile(
    r"\?|^(what|how|when|where|why|which|who|can|is|are|do|does|should)\b"
    r"|(enna|epdi|eppadi|kya|kaise|kab|kahan|enti|ela|eppudu|kemon|kothay|hege|yenu|elli)\b",
    re.IGNORECASE,
)


def assign_domain(text: str) -> str:
    low = text.lower()
    scores = {d: sum(kw in low for kw in kws) for d, kws in DOMAIN_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else ""


def main() -> None:
    files = sorted(path("filtered").glob("*.csv"))
    if not files:
        raise SystemExit("no filtered CSVs — run codeswitch_filter first")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

    # prefer language from filter (cs_lang) over collector guess
    if "cs_lang" in df.columns:
        df["language"] = df["cs_lang"].fillna(df.get("language"))
    df = df[df["language"].isin(LANGUAGES)]

    df = df[df["text"].astype(str).apply(lambda t: bool(QUESTION_MARKERS.search(t)))]
    if "domain" not in df.columns:
        df["domain"] = ""
    df["domain"] = df.apply(
        lambda r: r["domain"] if r["domain"] in DOMAINS else assign_domain(str(r["text"])), axis=1)

    target = CFG["target_per_language"]
    parts = []
    for lang in LANGUAGES:
        sub = df[df["language"] == lang].drop_duplicates(subset="text")
        parts.append(sub.head(target))
        print(f"{lang}: {len(sub)} available, kept {min(len(sub), target)} / {target}")
    out_df = pd.concat(parts, ignore_index=True)
    out_df["qid"] = [f"{r.language}-{i:04d}" for i, r in enumerate(out_df.itertuples())]
    out_df = out_df.rename(columns={"text": "question"})[
        ["qid", "language", "domain", "question", "source"]]

    out = path("questions") / "questions.csv"
    out_df.to_csv(out, index=False)
    print(f"saved {len(out_df)} questions -> {out}")


if __name__ == "__main__":
    main()
