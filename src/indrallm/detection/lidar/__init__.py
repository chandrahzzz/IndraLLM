"""LIDAR — Language-Identity-Aware hallucination features.

Stage 1 (lid): rule-based token-level language identification.
Stage 2 (features): Boundary-Coherence, Cross-Lingual-Semantic, Language-Entropy.

This package deliberately starts as a *falsifiable probe*, not the full
multi-head transformer. If the Stage-2 features do not separate hallucinated
from correct answers on real (non-empty) labeled data, the premise is dead and
no downstream classifier rescues it. Run `python -m indrallm.detection.lidar.probe`.
"""

from indrallm.detection.lidar.lid import token_lid
from indrallm.detection.lidar.features import extract_features, FEATURE_NAMES

__all__ = ["token_lid", "extract_features", "FEATURE_NAMES"]
