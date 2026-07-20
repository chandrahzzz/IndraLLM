"""Verify that collected text is genuinely code-switched (Indian language + English).

Two independent signals, either is sufficient:
  1. Script mixing — native-script tokens (Devanagari/Tamil/Telugu/Bengali/Kannada)
     alongside Latin-script tokens.
  2. fastText lid.176 assigns non-trivial probability to two different languages
     (catches romanized code-switching like "enna medicine edukkanum").

Romanized Indian text is the hard case: langdetect/fastText often read it as a
single language, so we additionally do a token-vote using small romanized
function-word lexicons per language.

Usage:
    python -m indrallm.collection.codeswitch_filter            # all raw CSVs
    python -m indrallm.collection.codeswitch_filter --file data/raw/reddit.csv
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd

from indrallm.config import CFG, PROJECT_ROOT, path

SCRIPT_RANGES = {
    "hi": ("ऀ", "ॿ"),  # Devanagari
    "bn": ("ঀ", "৿"),
    "ta": ("஀", "௿"),
    "te": ("ఀ", "౿"),
    "kn": ("ಀ", "೿"),
}

# High-frequency romanized function words per language. Deliberately small and
# high-precision: one hit + majority-English text is strong code-switch evidence.
ROMANIZED_HINTS = {
    "ta": {"enna", "epdi", "eppadi", "iruku", "irukku", "illa", "vendum", "venum",
           "edukkanum", "pannanum", "seri", "romba", "konjam", "inga", "anga", "nalla",
           "panna", "pannalama", "mudiyuma", "aguma", "irukka", "epo", "eppo",
           "yaru", "enga", "vangalam", "kudukanum", "sollunga", "theriyuma"},
    "hi": {"kya", "kaise", "kyu", "kyun", "hai", "hain", "nahi", "nahin", "mujhe",
           "chahiye", "karna", "hona", "lena", "jaana", "krna", "mera", "apna",
           "karein", "hoga", "hogi", "milega", "milta", "milti", "sakta", "sakte",
           "banwana", "karwana", "batao", "bataye", "kitna", "kitne", "kahan"},
    "te": {"enti", "emi", "ela", "undi", "unnayi", "untayi", "kavali", "cheyali",
           "ledu", "nenu", "naaku", "ekkada", "eppudu", "chala", "baga",
           "kuda", "emiti", "enduku", "unda", "avuna",
           "avvali", "ayindi", "cheyyali", "teesukovali", "untundi", "vastundi",
           "cheppandi", "telusa", "dorukutundi", "chesukovali", "padutundi"},
    "bn": {"ki", "kemon", "kothay", "ache", "nei", "amar", "tumi", "korbo",
           "korte", "hobe", "keno", "kobe", "bhalo", "onek",
           "korbo", "korar", "jonno", "kivabe", "kibhabe", "pabo", "korte",
           "lagbe", "dorkar", "bolun", "janate", "chai", "amake"},
    "kn": {"yenu", "hege", "elli", "ide", "illa", "beku", "madbeku", "yaake",
           "yavaga", "nanu", "nanna", "tumba", "swalpa",
           "gottilla", "banni", "madtini", "aagide", "ella",
           "nalli", "madabeku", "sigutte", "sigutta", "ideyena", "idya",
           "maadi", "maadalu", "helide", "helabeku", "aagutte", "andre"},
}

_ft_model = None


def _fasttext():
    global _ft_model
    if _ft_model is None:
        import fasttext
        _ft_model = fasttext.load_model(str(PROJECT_ROOT / CFG["paths"]["fasttext_model"]))
    return _ft_model


def _tokens(text: str) -> list[str]:
    return re.findall(r"[^\s\W_]+", text, flags=re.UNICODE)


def _token_script(tok: str) -> str:
    """'latin', a language code from SCRIPT_RANGES, or 'other'."""
    for ch in tok:
        for lang, (lo, hi) in SCRIPT_RANGES.items():
            if lo <= ch <= hi:
                return lang
        if "LATIN" in unicodedata.name(ch, ""):
            return "latin"
    return "other"


def detect_codeswitch(text: str, expected_lang: str | None = None) -> dict:
    """Return {'is_cs': bool, 'method': str, 'lang': str|None}."""
    min_ratio = CFG["filtering"]["min_minority_token_ratio"]
    toks = _tokens(text)
    if len(toks) < CFG["filtering"]["min_tokens"]:
        return {"is_cs": False, "method": "too_short", "lang": None}

    # Signal 1: script mixing
    scripts = [_token_script(t) for t in toks]
    latin = scripts.count("latin")
    for lang in SCRIPT_RANGES:
        native = scripts.count(lang)
        if native and latin and min(native, latin) / len(toks) >= min_ratio:
            return {"is_cs": True, "method": "script_mix", "lang": lang}

    # Signal 2: fastText two-language probability (skipped if model unavailable)
    try:
        labels, probs = _fasttext().predict(text.replace("\n", " "), k=3)
        langs = [l.replace("__label__", "") for l in labels]
        strong = [l for l, p in zip(langs, probs) if p >= CFG["filtering"]["min_lang_prob"]]
        indic = set(SCRIPT_RANGES) & set(strong)
        if "en" in strong and indic:
            return {"is_cs": True, "method": "fasttext", "lang": indic.pop()}
    except (ImportError, ValueError):
        pass  # fasttext not installed or lid.176.bin missing — lexicon signal still runs

    # Signal 3: romanized lexicon vote (needs mostly-Latin text, no native script)
    # digits/punctuation tokens count as neutral, not as script violations
    native_any = any(s in SCRIPT_RANGES for s in scripts)
    mostly_latin = not native_any and latin >= 0.7 * len(toks)
    lower = {t.lower() for t in toks}
    candidates = ([expected_lang] if expected_lang else []) + \
        [l for l in ROMANIZED_HINTS if l != expected_lang]
    for lang in candidates:
        hits = lower & ROMANIZED_HINTS.get(lang, set())
        # 2 hits from any language, or 1 hit when it matches the declared language
        enough = len(hits) >= 2 or (len(hits) >= 1 and lang == expected_lang)
        if enough and mostly_latin:
            return {"is_cs": True, "method": "romanized_lexicon", "lang": lang}

    return {"is_cs": False, "method": "none", "lang": None}


def filter_file(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "text" not in df.columns:
        raise ValueError(f"{csv_path} needs a 'text' column")
    # per-row expected language (files may mix languages, e.g. synthetic.csv)
    if "language" in df.columns:
        results = df.apply(lambda r: detect_codeswitch(
            str(r["text"]), r["language"] if r["language"] in ROMANIZED_HINTS else None),
            axis=1)
    else:
        results = df["text"].astype(str).apply(lambda t: detect_codeswitch(t, None))
    df["is_cs"] = results.apply(lambda r: r["is_cs"])
    df["cs_method"] = results.apply(lambda r: r["method"])
    df["cs_lang"] = results.apply(lambda r: r["lang"])
    kept = df[df["is_cs"]].drop_duplicates(subset="text").reset_index(drop=True)
    print(f"{csv_path.name}: {len(df)} in -> {len(kept)} code-switched kept")
    return kept


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", type=Path, help="single CSV; default: all of data/raw/*.csv")
    args = ap.parse_args()

    files = [args.file] if args.file else sorted(path("raw").glob("*.csv"))
    if not files:
        print("no raw CSVs found — run a collector first")
        return
    for f in files:
        kept = filter_file(f)
        out = path("filtered") / f.name
        kept.to_csv(out, index=False)
        print(f"  -> {out}")


if __name__ == "__main__":
    main()
