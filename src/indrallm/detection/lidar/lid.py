"""Stage 1: rule-based token-level language identification.

The LIDAR doc proposes fastText + CRF. For the probe we use a cheaper, fully
deterministic labeler built from signals the repo already trusts
(`codeswitch_filter.SCRIPT_RANGES` + `ROMANIZED_HINTS`). This is enough to
compute the Stage-2 boundary/entropy features and costs no model download.

Per-token label is one of:
  - an Indic language code ("ta"/"hi"/"te"/"bn"/"kn") — native script OR romanized hint
  - "en"    — a Latin-script token not matched as romanized-Indic
  - "other" — digits, punctuation-only, emoji, foreign script

If a fastText lid.176 model is available (module installed + bin present), it is
used to disambiguate Latin tokens the lexicon can't place, but it is optional.
"""

from __future__ import annotations

import re
import unicodedata

from indrallm.config import CFG, PROJECT_ROOT
from indrallm.collection.codeswitch_filter import ROMANIZED_HINTS, SCRIPT_RANGES

_INDIC = set(SCRIPT_RANGES)
_HINT_LOOKUP: dict[str, str] = {w: lang for lang, words in ROMANIZED_HINTS.items() for w in words}

_TOKEN_RE = re.compile(r"[^\s\W_]+", re.UNICODE)

_ft_model = None
_ft_tried = False


def _fasttext():
    """Optional lid.176 model; returns None if module or bin is missing."""
    global _ft_model, _ft_tried
    if _ft_tried:
        return _ft_model
    _ft_tried = True
    try:
        import fasttext
        path = PROJECT_ROOT / CFG["paths"]["fasttext_model"]
        if path.exists():
            _ft_model = fasttext.load_model(str(path))
    except Exception:
        _ft_model = None
    return _ft_model


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text or "")


def _script_lang(tok: str) -> str | None:
    for ch in tok:
        for lang, (lo, hi) in SCRIPT_RANGES.items():
            if lo <= ch <= hi:
                return lang
    return None


def _is_latin(tok: str) -> bool:
    return any("LATIN" in unicodedata.name(ch, "") for ch in tok)


def token_lid(text: str, expected_lang: str | None = None) -> list[str]:
    """Return a per-token language label sequence for `text`.

    `expected_lang` biases ambiguous romanized tokens toward the declared
    code-switch partner language (matches how codeswitch_filter votes).
    """
    labels: list[str] = []
    ft = _fasttext()
    for tok in tokenize(text):
        native = _script_lang(tok)
        if native:
            labels.append(native)
            continue
        low = tok.lower()
        hint = _HINT_LOOKUP.get(low)
        if hint:
            # if declared language also claims this word, prefer it
            if expected_lang and low in ROMANIZED_HINTS.get(expected_lang, set()):
                hint = expected_lang
            labels.append(hint)
            continue
        if _is_latin(tok):
            if ft is not None:
                try:
                    lab, prob = ft.predict(low, k=1)
                    code = lab[0].replace("__label__", "")
                    labels.append(code if code in _INDIC else "en")
                    continue
                except Exception:
                    pass
            labels.append("en")
            continue
        labels.append("other")
    return labels
