# IndraLLM — Detection & Mitigation Build Notes (post-cleanup)

> Status: the surface-feature detection approaches were **removed** after they
> failed empirically. This document now describes only the two viable detection
> paths and the intervention scaffold that sits on top of a working detector.

---

## 0. What was tried and removed, and why

Three surface/linguistic detection designs were built and each was measured
against the LLM-judge labels (`benchmark_judged.csv`, 2078 rows, 9.4% positive,
`corr(frac_indic, label) = +0.03`). All three failed — real hallucinations here
are **fluent factual errors**, so surface linguistics reads as noise:

| Removed approach | Signal | Result | Deleted |
|---|---|---|---|
| LIDAR surface features | CLSC / LES / BCS boundary+entropy | AUC ≤ 0.51 | `lidar/features.py`, `lidar/probe.py` |
| Cross-Lingual Alignment | cla_min / cla_mean / cla_max_drop | AUC 0.52 | `lidar/cross_lingual.py` |
| Linguistic Fidelity Filter | switch/perplexity/coherence | AUC 0.539, 0.3% compute saved | `filter/` |

The lesson is load-bearing: **do not rebuild surface-feature detectors.** If a
signal cannot be shown to separate the judged label with AUC ≥ 0.65, it does not
get built on.

---

## 1. The two viable paths

### Path A — Internal probes (novel, unproven, GPU)
Read the base model's own internals over each answer and test whether *the model's
uncertainty/representation* betrays a fluent-but-wrong answer.

- `detection/lidar/internal_probes.py` — HSD (hidden-state divergence), AE
  (attention entropy), UC (uncertainty), + perplexity/logit-variance, from one
  forward pass with `output_hidden_states/attentions`.
- `detection/lidar/self_consistency.py` — RSC, divergence across re-sampled
  generations.
- `detection/lidar/feature_cache.py` — extract + cache to
  `data/features/answer_features.parquet` (resumable).
- `evaluation/feature_report.py` — **the gate**: per-feature AUC/PR vs judged
  label on val; needs ≥3 internal features at AUC ≥ 0.65 to proceed to a detector.

Run order (Colab T4):
```
python -m indrallm.detection.lidar.feature_cache --internal --rsc
python -m indrallm.evaluation.feature_report          # gate: internal features only
# if it PASSES:
python -m indrallm.detection.multi_view.train         # detector over the kept features
```

### Path B — IndicBERT text classifier (fallback, likely to work)
Fine-tune a transformer directly on `(question, answer)` → judged label. Reads the
text, so it can learn factual-error patterns hand-crafted features can't.
```
python -m indrallm.detection.train_indicbert
```

If Path A's gate fails, Path B is the detector.

---

## 2. Mitigation scaffold (Claim Family 2 — depends on a working detector)

The type-aware selective-intervention design is kept but **detection is stubbed**
until Path A or B yields a detector to trigger it:

- `mitigation/interventions.py` — language_constraint, fact_rerank, rollback,
  repetition_penalty.
- `mitigation/lidar_decoder.py` — per-step decode loop, signature match,
  `get_intensity(t)` position-aware modulator (1.5× early / 1.0× mid / 0.5× late).
  `_detect` is a stub returning 0.0; wire the internal-probe detector into it once
  the gate passes (see the module docstring).
- `detection/signatures.py` — active signatures use only internal features
  (FACTUAL_ERROR via UC+RSC, SEMANTIC_DRIFT via HSD). The two surface-dependent
  signatures (UNINTENDED_SWITCH via cla, REPETITION via repetition_score) are
  disabled with a note.
- `mitigation/lita_trainer.py` — optional adversarial training; unchanged.

---

## 3. Data & labels (unchanged, trusted)

- `data/final/benchmark_judged.csv` — LLM-judge labels, the only label source.
- `data/final/{train,val,test}.csv` — stratified splits on judged labels.
- `detection/lidar/lid.py` — token-level language ID, retained (internal probes
  may key on switch positions).

---

## 4. The rule that still governs

Gate before you build. A detector gets written only for features that clear
AUC ≥ 0.65 on the judged label. If neither internal probes nor IndicBERT clears a
useful bar, report that honestly — a truthful negative result is the deliverable.
