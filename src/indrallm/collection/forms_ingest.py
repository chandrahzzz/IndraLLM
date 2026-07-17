"""Ingest crowdsourced questions from a Google Forms response CSV.

Expected form columns (rename via --map if yours differ):
  "Your question (code-switched)", "Language", "Domain"

Usage:
    python -m indrallm.collection.forms_ingest --csv data/raw/forms_export.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from indrallm.config import DOMAINS, LANGUAGES, path

DEFAULT_MAP = {
    "Your question (code-switched)": "text",
    "Language": "language",
    "Domain": "domain",
}

LANG_NAME_TO_CODE = {v.lower(): k for k, v in LANGUAGES.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--map", nargs="*", default=[],
                    help='column renames as "Form Column=target", targets: text/language/domain')
    args = ap.parse_args()

    rename = dict(DEFAULT_MAP)
    for m in args.map:
        src, dst = m.split("=", 1)
        rename[src] = dst

    df = pd.read_csv(args.csv).rename(columns=rename)
    missing = {"text", "language"} - set(df.columns)
    if missing:
        raise SystemExit(f"missing columns after mapping: {missing}; use --map")

    df["language"] = (df["language"].astype(str).str.strip().str.lower()
                      .map(lambda s: LANG_NAME_TO_CODE.get(s, s)))
    df = df[df["language"].isin(LANGUAGES)]
    if "domain" in df.columns:
        df["domain"] = df["domain"].astype(str).str.strip().str.lower()
        df.loc[~df["domain"].isin(DOMAINS), "domain"] = ""
    df["source"] = "forms"
    df = df[["source", "language", "text"] + (["domain"] if "domain" in df.columns else [])]
    df = df.drop_duplicates(subset="text").reset_index(drop=True)

    out = path("raw") / "forms.csv"
    df.to_csv(out, index=False)
    print(f"saved {len(df)} form responses -> {out}")


if __name__ == "__main__":
    main()
