"""Stage 2: language-identity feature extraction (the falsifiable core).

Three features from the LIDAR doc, plus a few cheap descriptive scalars so the
probe can tell whether *any* language-identity signal — not just the three named
ones — tracks the hallucination label.

  BCS  Boundary-Coherence Score  — mean log-prob of the answer's language-switch
       sequence under a transition matrix estimated from the (unlabeled) question
       corpus. Low = the answer switches languages in patterns the corpus rarely
       does. (Higher returned value = more coherent.)
  CLSC Cross-Lingual Semantic Consistency — mean cosine similarity of adjacent
       token embeddings *across* language boundaries. Low = semantic rupture at
       the switch point. Requires sentence-transformers; degrades to NaN-free
       neutral 1.0 if unavailable.
  LES  Language-Entropy — Shannon entropy of the answer's per-token language
       distribution. High = unstable mixing.

Descriptive: switch_rate, frac_en, frac_indic, frac_other, n_tokens.

The transition matrix is fit on questions (no labels) so BCS never peeks at the
target. See `fit_transition_matrix`.
"""

from __future__ import annotations

import math
from collections import defaultdict

from indrallm.detection.lidar.lid import token_lid, tokenize

FEATURE_NAMES = [
    "bcs", "clsc", "les",
    "switch_rate", "frac_en", "frac_indic", "frac_other", "n_tokens",
]

_INDIC = {"ta", "hi", "te", "bn", "kn"}
_SBERT = None
_SBERT_TRIED = False


def _sbert():
    global _SBERT, _SBERT_TRIED
    if _SBERT_TRIED:
        return _SBERT
    _SBERT_TRIED = True
    try:
        from sentence_transformers import SentenceTransformer
        _SBERT = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception:
        _SBERT = None
    return _SBERT


def fit_transition_matrix(texts, expected_langs=None):
    """Estimate P(lang_i | lang_{i-1}) from an unlabeled text corpus (Laplace-smoothed)."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    exp = expected_langs if expected_langs is not None else [None] * len(texts)
    for text, el in zip(texts, exp):
        seq = token_lid(str(text), el)
        for a, b in zip(seq, seq[1:]):
            counts[a][b] += 1
    states = sorted({s for d in counts for s in [*d, *counts[d]]} | set(counts))
    trans: dict[str, dict[str, float]] = {}
    for a in states:
        row = counts.get(a, {})
        total = sum(row.values()) + len(states)  # +1 Laplace per target state
        trans[a] = {b: (row.get(b, 0) + 1) / total for b in states}
    return {"trans": trans, "states": states, "default": 1.0 / max(len(states), 1)}


def _bcs(seq, tm) -> float:
    if len(seq) < 2:
        return 0.0  # no switch information
    trans, default = tm["trans"], tm["default"]
    logp = 0.0
    for a, b in zip(seq, seq[1:]):
        p = trans.get(a, {}).get(b, default)
        logp += math.log(max(p, 1e-9))
    return logp / (len(seq) - 1)


def _les(seq) -> float:
    if not seq:
        return 0.0
    dist: dict[str, int] = defaultdict(int)
    for s in seq:
        dist[s] += 1
    n = len(seq)
    return -sum((c / n) * math.log(c / n) for c in dist.values())


def _clsc(tokens, seq, embed) -> float:
    """Mean cosine sim across language boundaries; 1.0 (coherent) if no boundary/embedder."""
    boundaries = [i for i in range(len(seq) - 1)
                  if seq[i] != seq[i + 1] and seq[i] != "other" and seq[i + 1] != "other"]
    if not boundaries or embed is None:
        return 1.0
    need = sorted({tokens[i] for i in boundaries} | {tokens[i + 1] for i in boundaries})
    vecs = dict(zip(need, embed(need)))
    sims = []
    for i in boundaries:
        u, v = vecs[tokens[i]], vecs[tokens[i + 1]]
        du = sum(x * x for x in u) ** 0.5
        dv = sum(x * x for x in v) ** 0.5
        if du and dv:
            sims.append(sum(a * b for a, b in zip(u, v)) / (du * dv))
    return sum(sims) / len(sims) if sims else 1.0


def _make_embedder(use_sbert: bool):
    if not use_sbert:
        return None
    model = _sbert()
    if model is None:
        return None

    def embed(words):
        return model.encode(list(words), normalize_embeddings=False, show_progress_bar=False)

    return embed


def extract_features(text, tm, expected_lang=None, embed=None) -> dict[str, float]:
    tokens = tokenize(str(text))
    seq = token_lid(str(text), expected_lang)
    n = len(seq)
    switches = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    n_indic = sum(1 for s in seq if s in _INDIC)
    n_en = sum(1 for s in seq if s == "en")
    n_other = n - n_indic - n_en
    return {
        "bcs": _bcs(seq, tm),
        "clsc": _clsc(tokens, seq, embed),
        "les": _les(seq),
        "switch_rate": switches / n if n else 0.0,
        "frac_en": n_en / n if n else 0.0,
        "frac_indic": n_indic / n if n else 0.0,
        "frac_other": n_other / n if n else 0.0,
        "n_tokens": float(n),
    }
