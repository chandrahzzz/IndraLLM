"""THE GATE (internal probes -> detector). Rank each feature; decide KEEP / DROP.

Now evaluates only the surviving model-internal features (HSD/AE/UC, plus RSC and
the internal behavioral signals perplexity/logit_var). Surface and cross-lingual
features were removed after they failed this gate on the judge labels; if a
frac_indic column is absent the language-proxy check is simply skipped.

Reads the cached features, evaluates each against the trusted (judge) label on
the VALIDATION split, and writes docs/feature_analysis.md with ROC-AUC, PR-AUC,
optional corr(frac_indic), and a KEEP / DROP verdict + threshold.

Pass condition: >= 3 internal features with AUC >= 0.65 (or <= 0.35). If not met,
STOP — the internal signals do not detect these hallucinations either; use the
IndicBERT text classifier (train_indicbert.py) instead of a feature detector.

Usage:
    python -m indrallm.evaluation.feature_report
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from indrallm.config import path

ID_COLS = {"qid_model", "qid", "model", "language", "label"}
GATE_AUC = 0.65
PROXY_CORR = 0.5


def _val_ids() -> set[str] | None:
    p = path("final") / "val.csv"
    if not p.exists():
        return None
    v = pd.read_csv(p)
    if "qid" not in v or "model" not in v:
        return None
    return set(v["qid"].astype(str) + "|" + v["model"].astype(str))


def main() -> None:
    from sklearn.metrics import roc_auc_score, average_precision_score

    fp = path("features") / "answer_features.parquet"
    if not fp.exists():
        print("no data/features/answer_features.parquet — run feature_cache first")
        return
    df = pd.read_parquet(fp)

    val = _val_ids()
    if val:
        sub = df[df["qid_model"].isin(val)]
        scope = f"validation split ({len(sub)} rows)"
        if len(sub) < 40:
            sub, scope = df, f"ALL rows ({len(df)}) — val split too small"
    else:
        sub, scope = df, f"ALL rows ({len(df)}) — no val.csv found"

    y = sub["label"].to_numpy()
    feats = [c for c in sub.columns if c not in ID_COLS and pd.api.types.is_numeric_dtype(sub[c])]
    fi = sub["frac_indic"] if "frac_indic" in sub else pd.Series(np.zeros(len(sub)))

    rows = []
    for f in feats:
        x = sub[f].to_numpy(float)
        if np.all(x == x[0]) or len(np.unique(y)) < 2:
            auc, ap = 0.5, float(np.mean(y))
        else:
            auc = roc_auc_score(y, x)
            ap = average_precision_score(y, x)
        corr = float(np.corrcoef(x, fi)[0, 1]) if x.std() and fi.std() else 0.0
        strength = abs(auc - 0.5)
        proxy = abs(corr) >= PROXY_CORR and f != "frac_indic"
        keep = (auc >= GATE_AUC or auc <= 1 - GATE_AUC) and not proxy and f not in ("frac_indic", "frac_en")
        op = ">" if auc >= 0.5 else "<"
        thr = float(np.median(sub.loc[sub["label"] == 1, f])) if (y == 1).any() else float(np.median(x))
        rows.append({"feature": f, "auc": auc, "pr_auc": ap, "corr_frac_indic": corr,
                     "strength": strength, "keep": keep, "op": op, "threshold": round(thr, 4),
                     "proxy": proxy})

    rank = sorted(rows, key=lambda r: r["strength"], reverse=True)
    kept = [r for r in rank if r["keep"]]
    passed = len(kept) >= 3

    lines = ["# IndraLLM — Feature Analysis (the Gate)", "",
             f"Scope: {scope}.  Positive rate: {y.mean():.1%}.  "
             f"Gate: >=3 features with AUC>={GATE_AUC} (or <={1-GATE_AUC:.2f}) "
             f"and |corr(frac_indic)|<{PROXY_CORR}.", "",
             "| feature | ROC-AUC | PR-AUC | corr(frac_indic) | verdict | rule |",
             "|---|---|---|---|---|---|"]
    for r in rank:
        verdict = "**KEEP**" if r["keep"] else ("DROP (proxy)" if r["proxy"] else "DROP")
        rule = f"{r['feature']} {r['op']} {r['threshold']}" if r["keep"] else "—"
        lines.append(f"| {r['feature']} | {r['auc']:.3f} | {r['pr_auc']:.3f} | "
                     f"{r['corr_frac_indic']:+.3f} | {verdict} | {rule} |")
    lines += ["", f"## GATE VERDICT: {'PASS' if passed else 'FAIL'}", "",
              (f"{len(kept)} features passed: " + ", ".join(r["feature"] for r in kept) +
               ". Proceed to Phase 2 with these only."
               if passed else
               f"Only {len(kept)} feature(s) passed (need 3). STOP — do not build the "
               "detector. Add probes (contrastive HSD full-vs-Indic-stripped, per-layer "
               "probing classifiers) and re-gate.")]

    doc = path("final").parent.parent / "docs" / "feature_analysis.md"
    doc.parent.mkdir(exist_ok=True)
    doc.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:6]))
    print(f"...\nGATE: {'PASS' if passed else 'FAIL'} ({len(kept)} kept)  -> {doc}")


if __name__ == "__main__":
    main()
