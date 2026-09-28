"""Gambäck & Das (2014) Code-Mixing Index (CMI) and Multidimensional Code-Switching Suite.

Computes:
1. Gambäck & Das (2014) Code-Mixing Index:
       CMI = 100 * (1 - max(w_lang) / (n - u))  if (n - u) > 0 else 0.0
   where:
       n = total tokens
       u = language-independent tokens (digits, punctuation, symbols)
       w_lang = tokens belonging to the dominant language
2. English Token Ratio (w_en / n)
3. Native-Language Token Ratio (w_indic / n)
4. Language Switch Count (number of language transitions in token sequence)
5. Switch Density (language switches / max(n - 1, 1))
6. Script Transition Count (orthographic shifts between Latin and Indic scripts)
7. Token Fertility (subwords / words)
"""

from __future__ import annotations

import re
import unicodedata
from typing import TypedDict

from indrallm.collection.codeswitch_filter import SCRIPT_RANGES
from indrallm.detection.lidar.lid import token_lid, tokenize

INDIC_LANGS = set(SCRIPT_RANGES.keys())


class MultidimensionalCSMetrics(TypedDict):
    text: str
    language: str | None
    cmi: float
    cmi_level: str  # 'low' (0-15), 'moderate' (15-35), 'high' (>35)
    total_tokens: int
    indic_tokens: int
    english_tokens: int
    other_tokens: int
    indic_token_ratio: float
    english_token_ratio: float
    language_switch_count: int
    switch_density: float
    script_transitions: int
    char_count: int
    chars_per_token: float


def count_script_transitions(text: str) -> int:
    """Count how many times the script transitions between Latin, Indic, and Other."""
    current_script: str | None = None
    transitions = 0
    for ch in text:
        if ch.isspace() or unicodedata.category(ch).startswith("P"):
            continue
        # determine script
        script = "latin" if "LATIN" in unicodedata.name(ch, "") else None
        if not script:
            for lang, (lo, hi) in SCRIPT_RANGES.items():
                if lo <= ch <= hi:
                    script = f"indic_{lang}"
                    break
        if not script:
            script = "other"

        if current_script is not None and script != current_script:
            transitions += 1
        current_script = script
    return transitions


def count_language_switches(labels: list[str]) -> int:
    """Count transitions between 'en' and any Indic language, ignoring 'other'."""
    active_labels = [l for l in labels if l != "other"]
    if len(active_labels) <= 1:
        return 0
    switches = 0
    for i in range(1, len(active_labels)):
        prev_is_indic = active_labels[i - 1] in INDIC_LANGS
        curr_is_indic = active_labels[i] in INDIC_LANGS
        if prev_is_indic != curr_is_indic:
            switches += 1
    return switches


def compute_cmi(text: str, expected_lang: str | None = None) -> MultidimensionalCSMetrics:
    """Compute Gambäck & Das (2014) CMI and multidimensional code-mixing metrics."""
    tokens = tokenize(text)
    char_count = len(text)
    if not tokens:
        return {
            "text": text,
            "language": expected_lang,
            "cmi": 0.0,
            "cmi_level": "low",
            "total_tokens": 0,
            "indic_tokens": 0,
            "english_tokens": 0,
            "other_tokens": 0,
            "indic_token_ratio": 0.0,
            "english_token_ratio": 0.0,
            "language_switch_count": 0,
            "switch_density": 0.0,
            "script_transitions": 0,
            "char_count": char_count,
            "chars_per_token": 0.0,
        }

    labels = token_lid(text, expected_lang=expected_lang)
    n = len(labels)
    n_indic = sum(1 for l in labels if l in INDIC_LANGS)
    n_en = sum(1 for l in labels if l == "en")
    n_other = sum(1 for l in labels if l == "other")

    n_lang = n - n_other
    if n_lang <= 0:
        cmi = 0.0
    else:
        max_w = max(n_indic, n_en)
        cmi = round(100.0 * (1.0 - (max_w / n_lang)), 2)

    if cmi < 15.0:
        cmi_level = "low"
    elif cmi <= 35.0:
        cmi_level = "moderate"
    else:
        cmi_level = "high"

    transitions = count_script_transitions(text)
    lang_switches = count_language_switches(labels)
    switch_density = round(lang_switches / max(n - 1, 1), 3)
    chars_per_token = round(char_count / max(n, 1), 2)

    return {
        "text": text,
        "language": expected_lang,
        "cmi": cmi,
        "cmi_level": cmi_level,
        "total_tokens": n,
        "indic_tokens": n_indic,
        "english_tokens": n_en,
        "other_tokens": n_other,
        "indic_token_ratio": round(n_indic / max(n, 1), 3),
        "english_token_ratio": round(n_en / max(n, 1), 3),
        "language_switch_count": lang_switches,
        "switch_density": switch_density,
        "script_transitions": transitions,
        "char_count": char_count,
        "chars_per_token": chars_per_token,
    }


def compute_token_fertility(text: str, tokenizer) -> float:
    """Compute subword fertility = total subwords / total whitespace words."""
    words = text.strip().split()
    if not words:
        return 0.0
    try:
        subwords = tokenizer.tokenize(text)
        return round(len(subwords) / len(words), 3)
    except Exception:
        return 1.0
