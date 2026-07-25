"""View definitions + feature->view routing for the multi-view detector.

The cached features are answer-level scalars, so each view is a small MLP over
its feature subset (light, meets the latency budget — no large Transformer).
Four views mirror docs/BUILD_INDRALLM.md Section 7.
"""

from __future__ import annotations

# feature-name prefixes/exact-names that belong to each view
VIEW_FEATURES: dict[str, list[str]] = {
    "surface": ["bcs", "switch_rate", "frac_en", "frac_indic", "frac_other", "n_tokens"],
    "internal": ["hsd_mean", "hsd_max", "hsd_var", "hsd_slope",
                 "ae_mean", "ae_max", "ae_var", "ae_spike_rate",
                 "uc_mean", "uc_max", "uc_var", "conf_mean"],
    "behavioral": ["perplexity", "repetition_score", "logit_var_mean"],
    "crosslingual": ["cla_mean", "cla_min", "cla_max_drop", "n_boundaries",
                     "rsc_token_div", "rsc_embed_div"],
}


def resolve_views(available: list[str], keep: list[str] | None = None) -> dict[str, list[str]]:
    """Return {view: [features present in the cache (and in `keep` if given)]}."""
    keepset = set(keep) if keep else None
    out: dict[str, list[str]] = {}
    for view, feats in VIEW_FEATURES.items():
        cols = [f for f in feats if f in available and (keepset is None or f in keepset)]
        if cols:
            out[view] = cols
    return out


def _make_encoder(in_dim: int, hidden: int):
    import torch.nn as nn
    return nn.Sequential(
        nn.Linear(in_dim, hidden), nn.LayerNorm(hidden), nn.GELU(),
        nn.Linear(hidden, hidden), nn.GELU(),
    )
