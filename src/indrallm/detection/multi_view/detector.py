"""Multi-View Detector: encode 4 views, cross-attend, fuse, output prob + type.

Lightweight by design (per-view MLP + one cross-attention block + attention
fusion) so it can run inside the decode loop within the <20% latency budget.

Outputs:
  prob        (B,)    hallucination probability
  type_logits (B, 5)  NONE, UNINTENDED_SWITCH, FACTUAL_ERROR, SEMANTIC_DRIFT, REPETITION
  weights     (B, V)  per-input view weights (interpretability + ablation)
"""

from __future__ import annotations

TYPES = ["NONE", "UNINTENDED_SWITCH", "FACTUAL_ERROR", "SEMANTIC_DRIFT", "REPETITION"]


def build_detector(view_dims: dict[str, int], hidden: int = 64):
    import torch
    import torch.nn as nn
    from indrallm.detection.multi_view.views import _make_encoder

    class MultiViewDetector(nn.Module):
        def __init__(self):
            super().__init__()
            self.views = list(view_dims)
            self.encoders = nn.ModuleDict(
                {v: _make_encoder(view_dims[v], hidden) for v in self.views})
            self.cross_attn = nn.MultiheadAttention(hidden, num_heads=4, batch_first=True)
            self.weight_gate = nn.Linear(hidden, 1)
            self.prob_head = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, 1))
            self.type_head = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(),
                                           nn.Linear(hidden, len(TYPES)))

        def forward(self, batch: dict):
            # batch[view] -> (B, dim_view)
            enc = torch.stack([self.encoders[v](batch[v]) for v in self.views], dim=1)  # (B,V,H)
            attn, _ = self.cross_attn(enc, enc, enc)                                     # (B,V,H)
            w = torch.softmax(self.weight_gate(attn).squeeze(-1), dim=1)                 # (B,V)
            fused = (attn * w.unsqueeze(-1)).sum(dim=1)                                  # (B,H)
            prob = torch.sigmoid(self.prob_head(fused)).squeeze(-1)
            return prob, self.type_head(fused), w

    return MultiViewDetector()
