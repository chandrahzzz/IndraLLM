"""Shared statistics helpers for the IndraLLM manuscript (paper_v2).

Everything here is deterministic given its inputs; resampling procedures take an
explicit seed.
"""

from __future__ import annotations

import itertools
import math
import re
import unicodedata

import numpy as np
import pandas as pd
from scipy import stats

QWEN = "qwen/qwen3.8-27b"
ALLAM = "allam-2-7b"

# Condition codes in the prediction files -> manuscript labels.
COND_LABEL = {
    "A_EN": "EN-ORIG",
    "A_EN_MATCHED": "EN-MATCH",
    "D_CS": "CS-LAT",
    "C_ROMAN": "ROMAN",
    "B_NATIVE": "NATIVE",
    "E_MIXED_SCRIPT": "MIXED",
}
ORDER = ["A_EN", "A_EN_MATCHED", "D_CS", "C_ROMAN", "B_NATIVE", "E_MIXED_SCRIPT"]
MATCHED5 = ["A_EN_MATCHED", "D_CS", "C_ROMAN", "B_NATIVE", "E_MIXED_SCRIPT"]

# Pre-specified primary family (manuscript Sec. IV): four Indic conditions vs
# EN-MATCH, plus CS-LAT vs MIXED.  Pairs are (reference, comparison).
PRIMARY = [
    ("A_EN_MATCHED", "D_CS"),
    ("A_EN_MATCHED", "C_ROMAN"),
    ("A_EN_MATCHED", "B_NATIVE"),
    ("A_EN_MATCHED", "E_MIXED_SCRIPT"),
    ("D_CS", "E_MIXED_SCRIPT"),
]
SECONDARY = [
    ("A_EN", "A_EN_MATCHED"),
    ("C_ROMAN", "E_MIXED_SCRIPT"),
    ("B_NATIVE", "E_MIXED_SCRIPT"),
    ("D_CS", "C_ROMAN"),
    ("D_CS", "B_NATIVE"),
    ("C_ROMAN", "B_NATIVE"),
]

BRAHMIC_LO, BRAHMIC_HI = "ऀ", "෿"
NATIVE_DIGITS = {}
for base in (0x0966, 0x09E6, 0x0A66, 0x0AE6, 0x0B66, 0x0BE6, 0x0C66, 0x0CE6, 0x0D66):
    for k in range(10):
        NATIVE_DIGITS[chr(base + k)] = str(k)


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    den = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - half) / den, (centre + half) / den


def mcnemar_exact(x_ref: np.ndarray, x_cmp: np.ndarray) -> dict:
    """b = ref correct & cmp wrong; c = ref wrong & cmp correct."""
    b = int(((x_ref == 1) & (x_cmp == 0)).sum())
    c = int(((x_ref == 0) & (x_cmp == 1)).sum())
    p = stats.binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    return {"b": b, "c": c, "p_exact": float(p)}


def holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def signflip_exact(d: np.ndarray) -> float:
    """Exact two-sided sign-flip permutation p for mean(d) = 0 (all 2^n flips)."""
    d = np.asarray(d, float)
    n = len(d)
    obs = abs(d.mean())
    signs = np.array(list(itertools.product([1.0, -1.0], repeat=n)))
    means = np.abs(signs @ d / n)
    return float((means >= obs - 1e-12).mean())


def topic_bootstrap(per_topic: np.ndarray, n_boot: int = 10000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    per_topic = np.asarray(per_topic, float)
    idx = rng.integers(0, len(per_topic), size=(n_boot, len(per_topic)))
    means = per_topic[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def brahmic_share(text: str) -> float:
    lat = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    # Letters plus combining vowel signs/viramas (categories L*, M*) in U+0900-U+0DFF.
    bra = sum(1 for ch in text if BRAHMIC_LO <= ch <= BRAHMIC_HI and unicodedata.category(ch)[0] in "LM")
    return bra / (lat + bra) if lat + bra else 0.0


def script_transitions(text: str) -> int:
    """Latin<->Brahmic label changes between consecutive words (maximal letter runs)."""
    words = re.findall(r"[^\W\d_]+", text)
    labels = []
    for w in words:
        if any(BRAHMIC_LO <= ch <= BRAHMIC_HI for ch in w):
            labels.append("B")
        elif any(ch.isascii() for ch in w):
            labels.append("L")
    return sum(1 for a, b in zip(labels, labels[1:]) if a != b)


def normalise_digits(text: str) -> str:
    return "".join(NATIVE_DIGITS.get(ch, ch) for ch in text)


def gold_numerals(gold: str) -> list[str]:
    return [x.replace(",", "") for x in re.findall(r"\d[\d,]*", gold)]


def numerals_present(gold: str, response: str, native_digits: bool = False) -> bool:
    resp = normalise_digits(response) if native_digits else response
    resp = resp.replace(",", "")
    return all(re.search(rf"(?<!\d){re.escape(g)}(?!\d)", resp) for g in gold_numerals(gold))


SENTENCE_END = set(list(".!?।\"'`’”})]—-"))
INCOMPLETE_KW = re.compile(
    r"\b(incomplete|truncat|cut off|abrupt|unfinish|missing specific|missing parameter|fails to finish)\b", re.I
)


def ends_mid_sentence(text: str) -> bool:
    s = str(text).strip()
    return bool(s) and s[-1] not in SENTENCE_END


def per_topic_accuracy(df: pd.DataFrame, cond: str, col: str = "correct") -> pd.Series:
    return df[df.condition == cond].groupby("target_entity")[col].mean()
