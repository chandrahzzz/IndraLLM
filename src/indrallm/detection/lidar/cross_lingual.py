"""Phase 1 Probe 3: Cross-Lingual Alignment (CLA).

At every language-switch boundary in the answer (detected by lid.py), measure the
cosine similarity of the two tokens' embeddings under a MULTILINGUAL encoder. A
clean code-switch keeps meaning across the boundary (high CLA); a hallucinated
switch ruptures it (low CLA / large drop).

Critical: the encoder MUST be multilingual (paraphrase-multilingual-MiniLM), or a
correct Indic-vs-English boundary looks like a rupture and CLA re-introduces the
exact language confound this project spent effort removing.

Emits answer-level: cla_mean, cla_min, cla_max_drop, n_boundaries.
Degrades to neutral (cla_mean=1.0, no boundaries) if the encoder is unavailable
or the answer has no boundary.
"""

from __future__ import annotations

from indrallm.detection.lidar.lid import token_lid, tokenize

_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_ENC = None
_TRIED = False

_NEUTRAL = {"cla_mean": 1.0, "cla_min": 1.0, "cla_max_drop": 0.0, "n_boundaries": 0.0}


def _encoder():
    global _ENC, _TRIED
    if _TRIED:
        return _ENC
    _TRIED = True
    try:
        from sentence_transformers import SentenceTransformer
        _ENC = SentenceTransformer(_MODEL)
    except Exception:
        _ENC = None
    return _ENC


def _cos(u, v) -> float:
    du = sum(x * x for x in u) ** 0.5
    dv = sum(x * x for x in v) ** 0.5
    if not du or not dv:
        return 0.0
    return sum(a * b for a, b in zip(u, v)) / (du * dv)


def cla_features(answer: str, expected_lang: str | None = None) -> dict:
    enc = _encoder()
    toks = tokenize(answer)
    seq = token_lid(answer, expected_lang)
    boundaries = [i for i in range(len(seq) - 1)
                  if seq[i] != seq[i + 1] and seq[i] != "other" and seq[i + 1] != "other"]
    if not boundaries or enc is None:
        return dict(_NEUTRAL)
    need = sorted({toks[i] for i in boundaries} | {toks[i + 1] for i in boundaries})
    vecs = dict(zip(need, enc.encode(need, show_progress_bar=False)))
    clas = [_cos(vecs[toks[i]], vecs[toks[i + 1]]) for i in boundaries]
    drops = [clas[k - 1] - clas[k] for k in range(1, len(clas))]
    return {
        "cla_mean": sum(clas) / len(clas),
        "cla_min": min(clas),
        "cla_max_drop": max(drops) if drops else 0.0,
        "n_boundaries": float(len(boundaries)),
    }
