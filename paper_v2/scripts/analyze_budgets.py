"""Three-budget analysis (128 / 512 / 1,024 output tokens) under two judges.

Inputs:
  results/EXP-004-budget-rejudge/judgements.jsonl     128 (source orig128) and 512 (gen512) labels
  results/EXP-004-budget-rejudge/gen512_predictions.jsonl
  results/EXP-005-budget1024/gen1024_predictions.jsonl, judgements.jsonl, spend_log.jsonl, failures.jsonl
  results/EXP-002 + EXP-003 prediction files (128-token responses)
Writes paper_v2/output/numbers_budgets.json.

Only EN-MATCH, CS-LAT and MIXED were run at all three budgets.  Every comparison across
budgets uses one judge.  Unit of inference: proposition (exact McNemar) and topic (exact
sign-flip permutation over the 20 per-topic differences, percentile bootstrap over topics).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_lib import COND_LABEL, QWEN, brahmic_share, mcnemar_exact, signflip_exact, topic_bootstrap, wilson  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
E4 = ROOT / "results" / "EXP-004-budget-rejudge"
E5 = ROOT / "results" / "EXP-005-budget1024"
OUT = ROOT / "paper_v2" / "output"
GEN3 = ["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]
KEY = [("A_EN_MATCHED", "D_CS"), ("D_CS", "E_MIXED_SCRIPT"), ("A_EN_MATCHED", "E_MIXED_SCRIPT")]
JUDGES = ["J-QWEN", "J-OSS"]
BUDGETS = ["128", "512", "1024"]


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if Path(p).exists() else []


def kappa(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def kappa_topic_ci(df, n_boot=5000, seed=0):
    rng = np.random.default_rng(seed)
    topics = df.target_entity.unique()
    groups = {t: df[df.target_entity == t] for t in topics}
    ks = []
    for _ in range(n_boot):
        s = pd.concat([groups[t] for t in rng.choice(topics, size=len(topics), replace=True)])
        ks.append(kappa(s["J-QWEN"], s["J-OSS"]))
    return [float(np.nanpercentile(ks, 2.5)), float(np.nanpercentile(ks, 97.5))]


def contrast(m, ref, cmp_, col):
    piv = m.pivot(index="semantic_id", columns="condition", values=col).dropna()
    topic = m.drop_duplicates("semantic_id").set_index("semantic_id").target_entity.loc[piv.index]
    r = mcnemar_exact(piv[ref].values, piv[cmp_].values)
    d = (piv[cmp_] - piv[ref]).groupby(topic).mean() * 100
    return {"ref": COND_LABEL[ref], "cmp": COND_LABEL[cmp_], "n": int(len(piv)),
            "acc_ref": float(piv[ref].mean() * 100), "acc_cmp": float(piv[cmp_].mean() * 100),
            "delta_pp": float((piv[cmp_] - piv[ref]).mean() * 100), **r,
            "topic_perm_p": signflip_exact(d.values), "topic_boot_ci": list(topic_bootstrap(d.values))}


def per_topic_gap(m, ref, cmp_, col):
    piv = m.pivot(index="semantic_id", columns="condition", values=col)
    t = m.drop_duplicates("semantic_id").set_index("semantic_id").target_entity.loc[piv.index]
    return (piv[cmp_] - piv[ref]).groupby(t).mean() * 100


def main():
    orig = pd.DataFrame(jl(ROOT / "results/EXP-002/full_predictions.jsonl") +
                        jl(ROOT / "results/EXP-003-matched-en/matched_predictions.jsonl"))
    orig = orig[(orig.model == QWEN) & (orig.partition == "TEST-OOD") & orig.condition.isin(GEN3)]
    resp = {"128": orig[["prompt_id", "semantic_id", "condition", "language", "target_entity", "model_response",
                         "completion_tokens"]].assign(finish_reason=None)}
    for b, f in [("512", E4 / "gen512_predictions.jsonl"), ("1024", E5 / "gen1024_predictions.jsonl")]:
        g = pd.DataFrame(jl(f))
        resp[b] = g[["prompt_id", "semantic_id", "condition", "language", "target_entity", "model_response",
                     "completion_tokens", "finish_reason"]]

    J = pd.DataFrame(jl(E4 / "judgements.jsonl") + jl(E5 / "judgements.jsonl"))
    J["budget"] = J.source.map({"orig128": "128", "gen512": "512", "gen1024": "1024"})
    J = J[J.condition.isin(GEN3)]
    N = {"parse_failures": {f"{b}|{j}": int(((J.budget == b) & (J.judge == j) & (J.judge_label < 0)).sum())
                            for b in BUDGETS for j in JUDGES}}
    J = J[J.judge_label >= 0].copy()
    J["correct"] = (J.judge_label == 0).astype(int)
    lab = J.pivot_table(index=["budget", "prompt_id"], columns="judge", values="correct", aggfunc="first").reset_index()

    frames = {}
    for b in BUDGETS:
        frames[b] = resp[b].merge(lab[lab.budget == b].drop(columns="budget"), on="prompt_id", how="left")
    N["coverage"] = {b: {j: int(frames[b][j].notna().sum()) for j in JUDGES} | {"responses": int(len(frames[b]))}
                     for b in BUDGETS}

    # Generation descriptives per budget
    N["generation"] = {}
    for b in BUDGETS:
        f = frames[b]
        d = {}
        for c in GEN3:
            s = f[f.condition == c]
            stop = int((s.finish_reason == "stop").sum()) if b != "128" else int((s.completion_tokens < 128).sum())
            d[COND_LABEL[c]] = {
                "n": int(len(s)), "stopped_before_cap": stop,
                "mean_completion_tokens": float(s.completion_tokens.mean()),
                "mean_chars": float(s.model_response.str.len().mean()),
                "mostly_brahmic_pct": float((s.model_response.apply(brahmic_share) > 0.5).mean() * 100),
            }
        N["generation"][b] = d
    # Prefix consistency: does the longer-budget response start with the shorter one?
    def prefix(a, b):
        A = frames[a].set_index("prompt_id").model_response
        B = frames[b].set_index("prompt_id").model_response
        common = A.index.intersection(B.index)
        ok = pd.Series({p: str(B[p]).startswith(str(A[p]).strip()) for p in common})
        cond = frames[b].set_index("prompt_id").condition.loc[common]
        return {COND_LABEL[c]: int(ok[cond == c].sum()) for c in GEN3}
    N["prefix_consistency"] = {"512_starts_with_128": prefix("128", "512"),
                               "1024_starts_with_512": prefix("512", "1024")}

    # Accuracy, contrasts, within-condition changes
    N["accuracy"], N["contrasts"], N["within_condition"], N["gap_change"] = {}, {}, {}, {}
    for j in JUDGES:
        N["accuracy"][j], N["contrasts"][j], N["within_condition"][j], N["gap_change"][j] = {}, {}, {}, {}
        for b in BUDGETS:
            f = frames[b].dropna(subset=[j])
            N["accuracy"][j][b] = {}
            for c in GEN3:
                s = f[f.condition == c][j]
                k = int(s.sum())
                N["accuracy"][j][b][COND_LABEL[c]] = {"k": k, "n": int(len(s)), "pct": 100 * k / len(s),
                                                      "wilson": [100 * x for x in wilson(k, len(s))]}
            N["contrasts"][j][b] = [contrast(f, r, c, j) for r, c in KEY]
        for b0, b1 in [("128", "512"), ("512", "1024"), ("128", "1024")]:
            key = f"{b0}->{b1}"
            N["within_condition"][j][key] = {}
            for c in GEN3:
                a = frames[b0][frames[b0].condition == c][["prompt_id", "target_entity", j]].rename(columns={j: "y0"})
                bb = frames[b1][frames[b1].condition == c][["prompt_id", j]].rename(columns={j: "y1"})
                m = a.merge(bb, on="prompt_id").dropna()
                r = mcnemar_exact(m.y0.values, m.y1.values)
                d = (m.y1 - m.y0).groupby(m.target_entity).mean() * 100
                N["within_condition"][j][key][COND_LABEL[c]] = {
                    "acc0": float(m.y0.mean() * 100), "acc1": float(m.y1.mean() * 100), **r,
                    "topic_perm_p": signflip_exact(d.values), "topic_boot_ci": list(topic_bootstrap(d.values))}
            N["gap_change"][j][key] = {}
            for ref, cmp_ in KEY:
                g0 = per_topic_gap(frames[b0].dropna(subset=[j]), ref, cmp_, j)
                g1 = per_topic_gap(frames[b1].dropna(subset=[j]), ref, cmp_, j)
                dd = (g1 - g0).dropna()
                N["gap_change"][j][key][f"{COND_LABEL[cmp_]}-{COND_LABEL[ref]}"] = {
                    "gap0": float(g0.mean()), "gap1": float(g1.mean()), "change": float(dd.mean()),
                    "topic_boot_ci": list(topic_bootstrap(dd.values)), "topic_perm_p": signflip_exact(dd.values)}

    # Word-identical subset (hi, ta, bn) for MIXED vs CS-LAT at each budget
    N["word_identical_mixed_vs_cslat"] = {
        j: {b: contrast(frames[b][frames[b].language.isin(["hi", "ta", "bn"])].dropna(subset=[j]),
                        "D_CS", "E_MIXED_SCRIPT", j) for b in BUDGETS} for j in JUDGES}

    # Judge disagreement by condition and budget
    N["judge_agreement"] = {}
    for b in BUDGETS:
        f = frames[b].dropna(subset=JUDGES)
        N["judge_agreement"][b] = {}
        for c in GEN3 + ["ALL"]:
            s = f if c == "ALL" else f[f.condition == c]
            q, o = s["J-QWEN"].astype(int), s["J-OSS"].astype(int)
            qc_ow = int(((q == 1) & (o == 0)).sum())
            qw_oc = int(((q == 0) & (o == 1)).sum())
            N["judge_agreement"][b]["ALL" if c == "ALL" else COND_LABEL[c]] = {
                "n": int(len(s)), "both_correct": int(((q == 1) & (o == 1)).sum()),
                "both_wrong": int(((q == 0) & (o == 0)).sum()),
                "qwen_correct_oss_wrong": qc_ow, "qwen_wrong_oss_correct": qw_oc,
                "agreement": float((q == o).mean()), "kappa": kappa(q, o), "kappa_topic_ci": kappa_topic_ci(s),
                # how often each judge says CORRECT when the other says wrong
                "p_qwen_correct_given_oss_wrong": float(qc_ow / max(1, (o == 0).sum())),
                "p_oss_correct_given_qwen_wrong": float(qw_oc / max(1, (q == 0).sum())),
            }

    # Does the conclusion change? (significance at alpha = 0.05, proposition and topic level)
    rows = []
    for j in JUDGES:
        for b in BUDGETS:
            for c in N["contrasts"][j][b]:
                rows.append({"judge": j, "budget": b, "contrast": f"{c['cmp']} vs {c['ref']}",
                             "delta_pp": c["delta_pp"], "p_exact": c["p_exact"], "topic_p": c["topic_perm_p"],
                             "sig_prop": c["p_exact"] < 0.05, "sig_topic": c["topic_perm_p"] < 0.05})
    N["conclusion_matrix"] = rows

    spend = pd.DataFrame(jl(E5 / "spend_log.jsonl"))
    N["exp005_spend"] = {m: float(v) for m, v in spend.groupby("model").usd.sum().items()} if len(spend) else {}
    N["exp005_spend"]["total"] = float(spend.usd.sum()) if len(spend) else 0.0
    N["exp005_tokens"] = {m: {"calls": int(len(g)), "in": int(g["in"].sum()), "out": int(g["out"].sum())}
                          for m, g in spend.groupby("model")} if len(spend) else {}
    N["exp005_failures_logged"] = jl(E5 / "failures.jsonl")
    (OUT / "numbers_budgets.json").write_text(json.dumps(N, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print("wrote", OUT / "numbers_budgets.json")


if __name__ == "__main__":
    main()
