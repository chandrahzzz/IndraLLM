"""Phase 3: signature database — map a feature vector to a hallucination type.

A signature is a set of (feature, op, threshold) conditions that all must hold.
Defaults are starting hypotheses from docs/BUILD_INDRALLM.md; retune on the
validation split with `tune()` and persist to data/final/signatures.json.

A type whose defining features were DROPPED at the gate must be removed before
use — call `prune(kept_features)`.
"""

from __future__ import annotations

import json
import operator

from indrallm.config import path

_OPS = {"<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge}

# Only signatures keyed on surviving (internal) features are active. Two were
# disabled because they depended on removed surface features:
#   UNINTENDED_SWITCH -> needed cla_min (cross-lingual alignment, removed)
#   REPETITION        -> needed repetition_score (surface, removed)
# Re-enable them once an internal proxy for those signals exists (e.g. an
# attention-collapse feature for repetition). Their interventions
# (language_constraint, repetition_penalty) remain available in interventions.py.
DEFAULT_SIGNATURES: dict[str, dict] = {
    "FACTUAL_ERROR": {"conditions": [{"feature": "uc_mean", "op": ">", "value": 0.7},
                                      {"feature": "rsc_embed_div", "op": ">", "value": 0.5}],
                       "intervention": "fact_rerank"},
    "SEMANTIC_DRIFT": {"conditions": [{"feature": "hsd_slope", "op": ">", "value": 0.2},
                                       {"feature": "hsd_var", "op": ">", "value": 0.5}],
                        "intervention": "rollback"},
    # "UNINTENDED_SWITCH": needs a non-surface switch signal — disabled
    # "REPETITION":        needs a non-surface repetition signal — disabled
}


class SignatureDB:
    def __init__(self, signatures: dict | None = None):
        self.sig = signatures or dict(DEFAULT_SIGNATURES)

    @classmethod
    def load(cls) -> "SignatureDB":
        p = path("final") / "signatures.json"
        if p.exists():
            return cls(json.loads(p.read_text(encoding="utf-8")))
        return cls()

    def save(self) -> None:
        p = path("final") / "signatures.json"
        p.write_text(json.dumps(self.sig, indent=2), encoding="utf-8")

    def prune(self, kept_features: set[str]) -> None:
        """Drop any signature that relies on a feature not in kept_features."""
        self.sig = {t: s for t, s in self.sig.items()
                    if all(c["feature"] in kept_features for c in s["conditions"])}

    def match(self, feats: dict) -> tuple[str, str | None]:
        """Return (type, intervention) for the first fully-satisfied signature, else NONE."""
        best, best_n = None, 0
        for t, s in self.sig.items():
            ok = all(c["feature"] in feats and _OPS[c["op"]](feats[c["feature"]], c["value"])
                     for c in s["conditions"])
            if ok and len(s["conditions"]) > best_n:
                best, best_n = (t, s["intervention"]), len(s["conditions"])
        return best if best else ("NONE", None)

    def tune(self, df, label_col: str = "label") -> None:
        """Set each condition threshold to the median of that feature among positives
        (label==1) so the signature centers on real hallucinated examples."""
        pos = df[df[label_col] == 1]
        for t, s in self.sig.items():
            for c in s["conditions"]:
                f = c["feature"]
                if f in pos and len(pos):
                    c["value"] = round(float(pos[f].median()), 4)
