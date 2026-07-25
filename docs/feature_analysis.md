# IndraLLM — Feature Analysis (the Gate)

Scope: validation split (312 rows).  Positive rate: 9.6%.  Gate: >=3 features with AUC>=0.65 (or <=0.35) and |corr(frac_indic)|<0.5.

| feature | ROC-AUC | PR-AUC | corr(frac_indic) | verdict | rule |
|---|---|---|---|---|---|
| bcs | 0.346 | 0.071 | -0.734 | DROP (proxy) | — |
| frac_other | 0.639 | 0.141 | -0.167 | DROP | — |
| frac_en | 0.373 | 0.074 | -0.974 | DROP (proxy) | — |
| les | 0.618 | 0.191 | +0.243 | DROP | — |
| switch_rate | 0.596 | 0.133 | +0.113 | DROP | — |
| frac_indic | 0.580 | 0.134 | +1.000 | DROP | — |
| repetition_score | 0.577 | 0.223 | +0.059 | DROP | — |
| n_tokens | 0.449 | 0.097 | -0.182 | DROP | — |
| cla_min | 0.522 | 0.109 | -0.095 | DROP | — |
| cla_mean | 0.488 | 0.102 | -0.076 | DROP | — |
| clsc | 0.490 | 0.106 | -0.178 | DROP | — |
| cla_max_drop | 0.510 | 0.103 | +0.092 | DROP | — |
| n_boundaries | 0.500 | 0.107 | +0.191 | DROP | — |

## GATE VERDICT: FAIL

Only 0 feature(s) passed (need 3). STOP — do not build the detector. Add probes (contrastive HSD full-vs-Indic-stripped, per-layer probing classifiers) and re-gate.