"""Independent cross-check of the key reported numbers.

Re-derives numbers from the raw prediction and judgement files using code paths that do not
use stats_lib.py: statsmodels' exact McNemar, statsmodels' Wilson interval, scikit-learn's
Cohen's kappa, a Monte Carlo sign-flip test (instead of exact enumeration) and a bootstrap with
a different seed.  Compares them with the JSON files the manuscript is built from and prints
PASS/FAIL.  Writes paper_v2/output/independent_check.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper_v2" / "output"
LAB = {"A_EN": "EN-ORIG", "A_EN_MATCHED": "EN-MATCH", "D_CS": "CS-LAT", "C_ROMAN": "ROMAN",
       "B_NATIVE": "NATIVE", "E_MIXED_SCRIPT": "MIXED"}
INV = {v: k for k, v in LAB.items()}


def jl(p):
    return [json.loads(l) for l in open(ROOT / p, encoding="utf-8") if l.strip()]


NJ = json.loads((OUT / "numbers_jqwen.json").read_text(encoding="utf-8"))
NB = json.loads((OUT / "numbers_budgets.json").read_text(encoding="utf-8"))
rows = []


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    rows.append((name, got, want, tol, "PASS" if ok else "FAIL"))


# ---- raw data -------------------------------------------------------------------------
pred = pd.DataFrame(jl("results/EXP-002/full_predictions.jsonl") + jl("results/EXP-003-matched-en/matched_predictions.jsonl"))
pred = pred[(pred.model == "qwen/qwen3.8-27b") & (pred.partition == "TEST-OOD")]
J = pd.DataFrame(jl("results/EXP-004-budget-rejudge/judgements.jsonl") + jl("results/EXP-005-budget1024/judgements.jsonl"))
J["budget"] = J.source.map({"orig128": "128", "gen512": "512", "gen1024": "1024"})
J["y"] = (J.judge_label == 0).astype(int)
topic_of = pred.drop_duplicates("semantic_id").set_index("semantic_id").target_entity


def labels(budget, judge):
    s = J[(J.budget == budget) & (J.judge == judge)]
    return s.pivot_table(index="semantic_id", columns="condition", values="y", aggfunc="first")


def signflip_mc(d, n=200_000, seed=12345):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float)
    signs = rng.choice([-1.0, 1.0], size=(n, len(d)))
    return float((np.abs(signs @ d / len(d)) >= abs(d.mean()) - 1e-12).mean())


def topic_diff(piv, ref, cmp_):
    return ((piv[cmp_] - piv[ref]).groupby(topic_of.loc[piv.index]).mean() * 100).values


# ---- 128-token accuracy, Wilson, McNemar, topic p (J-QWEN) ------------------------------
piv = labels("128", "J-QWEN")
for c in LAB:
    k = int(piv[c].sum())
    lo, hi = proportion_confint(k, 100, method="wilson")
    check(f"J-QWEN 128 accuracy {LAB[c]}", k, NJ["accuracy"][LAB[c]]["k"], 0)
    check(f"J-QWEN 128 Wilson low {LAB[c]}", lo * 100, NJ["accuracy"][LAB[c]]["wilson"][0], 0.05)
for x in NJ["contrasts"]:
    ref, cmp_ = INV[x["ref"]], INV[x["cmp"]]
    t = pd.crosstab(piv[ref], piv[cmp_]).reindex(index=[0, 1], columns=[0, 1], fill_value=0).values
    p_sm = mcnemar(t, exact=True).pvalue
    check(f"exact McNemar {x['cmp']} vs {x['ref']}", p_sm, x["p_exact"], 1e-9)
    check(f"topic sign-flip (MC) {x['cmp']} vs {x['ref']}", signflip_mc(topic_diff(piv, ref, cmp_)), x["topic_perm_p"], 0.005)

# ---- budgets: accuracy, McNemar, topic p, kappa ----------------------------------------
for j in ["J-QWEN", "J-OSS"]:
    for b in ["128", "512", "1024"]:
        piv = labels(b, j)
        for c in ["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]:
            check(f"{j} {b} accuracy {LAB[c]}", piv[c].mean() * 100, NB["accuracy"][j][b][LAB[c]]["pct"], 1e-9)
        for x in NB["contrasts"][j][b]:
            ref, cmp_ = INV[x["ref"]], INV[x["cmp"]]
            t = pd.crosstab(piv[ref], piv[cmp_]).reindex(index=[0, 1], columns=[0, 1], fill_value=0).values
            check(f"{j} {b} McNemar {x['cmp']} vs {x['ref']}", mcnemar(t, exact=True).pvalue, x["p_exact"], 1e-9)
            check(f"{j} {b} topic p (MC) {x['cmp']} vs {x['ref']}", signflip_mc(topic_diff(piv, ref, cmp_)),
                  x["topic_perm_p"], 0.005)
            rng = np.random.default_rng(999)
            d = topic_diff(piv, ref, cmp_)
            bs = d[rng.integers(0, len(d), size=(20000, len(d)))].mean(1)
            check(f"{j} {b} topic CI low (seed 999) {x['cmp']} vs {x['ref']}", np.percentile(bs, 2.5),
                  x["topic_boot_ci"][0], 2.5)
for b in ["128", "512", "1024"]:
    q, o = labels(b, "J-QWEN"), labels(b, "J-OSS")
    for c in ["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]:
        k = cohen_kappa_score(q[c], o.loc[q.index, c])
        check(f"kappa {b} {LAB[c]} (sklearn)", k, NB["judge_agreement"][b][LAB[c]]["kappa"], 1e-9)
    allq = q[["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]].values.ravel()
    allo = o.loc[q.index, ["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]].values.ravel()
    check(f"agreement {b} all", (allq == allo).mean(), NB["judge_agreement"][b]["ALL"]["agreement"], 1e-9)

# ---- report ------------------------------------------------------------------------------
lines = ["# Independent check of reported numbers", "",
         "Re-derived from raw files with statsmodels (exact McNemar, Wilson), scikit-learn (Cohen's kappa), "
         "a Monte Carlo sign-flip test (200,000 draws, tolerance 0.005 against the exact enumeration) and a "
         "bootstrap with a different seed (tolerance 2.5 points on the CI bound).", "",
         "| Check | Independent value | Reported value | Tolerance | Result |", "|---|---|---|---|---|"]
for name, got, want, tol, res in rows:
    lines.append(f"| {name} | {got:.6g} | {want:.6g} | {tol:g} | {res} |")
n_fail = sum(r[4] == "FAIL" for r in rows)
lines += ["", f"**{len(rows)} checks, {len(rows) - n_fail} passed, {n_fail} failed.**"]
(OUT / "independent_check.md").write_text("\n".join(lines), encoding="utf-8")
print(f"{len(rows)} checks, {n_fail} failed")
for r in rows:
    if r[4] == "FAIL":
        print("FAIL", r)
