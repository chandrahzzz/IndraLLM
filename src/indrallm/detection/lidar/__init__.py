"""Internal-signal hallucination probes for code-switched text.

After the surface-feature approaches (CLSC/LES/BCS, cross-lingual alignment, and
the linguistic fidelity filter) were empirically rejected — none separated
hallucinated from correct answers on the LLM-judge labels (AUC 0.50-0.64) — this
package keeps only the model-internal probes:

  internal_probes  HSD (hidden-state divergence), AE (attention entropy),
                   UC (uncertainty calibration) — from a single forward pass.
  self_consistency RSC — divergence across re-sampled generations.

Extract with `feature_cache`, gate with `indrallm.evaluation.feature_report`.
`lid.py` (token-level language ID) is retained; internal probes may still key on
language-switch positions.
"""

from indrallm.detection.lidar.lid import token_lid

__all__ = ["token_lid"]
