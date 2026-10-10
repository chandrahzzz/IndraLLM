"""Analyse EXP-004: harmonised re-judging and the 128 -> 512 output-budget follow-up.

Inputs:
  results/EXP-002/full_predictions.jsonl, results/EXP-003-matched-en/matched_predictions.jsonl
  results/EXP-004-budget-rejudge/gen512_predictions.jsonl
  results/EXP-004-budget-rejudge/judgements.jsonl
Writes paper_v2/output/numbers_exp004.json.

Judges:  STORED = labels saved with the original predictions (EXP-002: T=0.3, generation
system prompt; EXP-003: T=0, evaluator system prompt).  J-QWEN = qwen/qwen3.8-27b, T=0,
evaluator system prompt, applied to everything.  J-OSS = openai/gpt-oss-120b, T=0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_lib import (  # noqa: E402
    COND_LABEL, MATCHED5, ORDER, PRIMARY, QWEN, brahmic_share, holm, mcnemar_exact,
    signflip_exact, topic_bootstrap,
)

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "results" / "EXP-004-budget-rejudge"
OUT = ROOT / "paper_v2" / "output"
KEY = [("A_EN_MATCHED", "D_CS"), ("D_CS", "E_MIXED_SCRIPT"), ("A_EN_MATCHED", "E_MIXED_SCRIPT")]
GEN3 = ["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return float((po - pe) / (1 - pe)) if pe < 1 else 1.0


def contrast(df, ref, cmp_, col):
    piv = df.pivot(index="semantic_id", columns="condition", values=col).dropna()
    topic = df.drop_duplicates("semantic_id").set_index("semantic_id").target_entity.loc[piv.index]
    r = mcnemar_exact(piv[ref].values, piv[cmp_].values)
    d = (piv[cmp_] - piv[ref]).groupby(topic).mean() * 100
    return {"ref": COND_LABEL[ref], "cmp": COND_LABEL[cmp_], "n": int(len(piv)),
            "acc_ref": float(piv[ref].mean() * 100), "acc_cmp": float(piv[cmp_].mean() * 100),
            "delta_pp": float((piv[cmp_] - piv[ref]).mean() * 100), **r,
            "topic_perm_p": signflip_exact(d.values), "topic_boot_ci": list(topic_bootstrap(d.values))}


def main():
    orig = pd.DataFrame(jl(ROOT / "results/EXP-002/full_predictions.jsonl") +
                        jl(ROOT / "results/EXP-003-matched-en/matched_predictions.jsonl"))
    orig = orig[(orig.model == QWEN) & (orig.partition == "TEST-OOD")].copy()
    orig["STORED"] = (orig.judge_label == 0).astype(int)
    g512 = pd.DataFrame(jl(D / "gen512_predictions.jsonl"))
    J = pd.DataFrame(jl(D / "judgements.jsonl"))
    N = {"judge_parse_failures": J[J.judge_label < 0].groupby(["source", "judge"]).size().to_dict()}
    N["judge_parse_failures"] = {f"{k[0]}|{k[1]}": int(v) for k, v in N["judge_parse_failures"].items()}
    J = J[J.judge_label >= 0]
    J["correct"] = (J.judge_label == 0).astype(int)
    wide = J.pivot_table(index=["source", "prompt_id"], columns="judge", values="correct", aggfunc="first").reset_index()

    o = orig.merge(wide[wide.source == "orig128"].drop(columns="source"), on="prompt_id", how="left")
    n = g512.merge(wide[wide.source == "gen512"].drop(columns="source"), on="prompt_id", how="left")
    N["coverage"] = {"orig128": {j: int(o[j].notna().sum()) for j in ["J-QWEN", "J-OSS"]},
                     "gen512": {j: int(n[j].notna().sum()) for j in ["J-QWEN", "J-OSS"]}}

    # 1. Judge agreement on the original 128-token outputs.
    agree = {}
    for c in ORDER:
        s = o[o.condition == c].dropna(subset=["J-QWEN", "J-OSS"])
        agree[COND_LABEL[c]] = {
            "n": int(len(s)),
            "stored_vs_jqwen": float((s.STORED == s["J-QWEN"]).mean()),
            "stored_vs_joss": float((s.STORED == s["J-OSS"]).mean()),
            "jqwen_vs_joss": float((s["J-QWEN"] == s["J-OSS"]).mean()),
            "kappa_jqwen_joss": kappa(s["J-QWEN"], s["J-OSS"]),
        }
    N["agreement_orig128"] = agree

    # 2. Accuracy and primary contrasts on the original outputs under each judge.
    N["orig128"] = {}
    for jname in ["STORED", "J-QWEN", "J-OSS"]:
        sub = o.dropna(subset=[jname]).copy()
        sub[jname] = sub[jname].astype(int)
        acc = {COND_LABEL[c]: float(sub[sub.condition == c][jname].mean() * 100) for c in ORDER}
        cons = [contrast(sub, r, c, jname) for r, c in PRIMARY]
        for cc, h in zip(cons, holm([x["p_exact"] for x in cons])):
            cc["holm_exact"] = h
        for cc, h in zip(cons, holm([x["topic_perm_p"] for x in cons])):
            cc["holm_topic"] = h
        N["orig128"][jname] = {"accuracy": acc, "primary": cons}

    # 3. Budget experiment: same prompts, same judge, 128 vs 512 tokens.
    n["finish_stop"] = (n.finish_reason == "stop").astype(int)
    n["chars"] = n.model_response.str.len()
    n["bshare"] = n.model_response.apply(brahmic_share)
    om = o.set_index("prompt_id")
    n["prefix_consistent"] = [str(r.model_response).startswith(str(om.loc[r.prompt_id, "model_response"]).strip())
                              for r in n.itertuples()]
    N["gen512_descriptives"] = {COND_LABEL[c]: {
        "n": int((n.condition == c).sum()),
        "finished_stop": int(n[n.condition == c].finish_stop.sum()),
        "mean_completion_tokens": float(n[n.condition == c].completion_tokens.mean()),
        "mean_chars": float(n[n.condition == c].chars.mean()),
        "brahmic_majority_pct": float((n[n.condition == c].bshare > 0.5).mean() * 100),
        "prefix_consistent_with_128": int(n[n.condition == c].prefix_consistent.sum()),
    } for c in GEN3}
    N["orig128_mean_chars"] = {COND_LABEL[c]: float(o[o.condition == c].model_response.str.len().mean()) for c in ORDER}

    N["budget"] = {}
    for jname in ["J-QWEN", "J-OSS"]:
        a = o[o.condition.isin(GEN3)][["semantic_id", "prompt_id", "condition", "target_entity", "language", jname]].rename(columns={jname: "c128"})
        b = n[["prompt_id", jname]].rename(columns={jname: "c512"})
        m = a.merge(b, on="prompt_id").dropna()
        res = {"accuracy": {}, "within_condition": {}, "contrasts_128": [], "contrasts_512": [], "gap_change": {}}
        for c in GEN3:
            s = m[m.condition == c]
            r = mcnemar_exact(s.c128.values, s.c512.values)
            d = (s.c512 - s.c128).groupby(s.target_entity).mean() * 100
            res["accuracy"][COND_LABEL[c]] = {"128": float(s.c128.mean() * 100), "512": float(s.c512.mean() * 100), "n": int(len(s))}
            res["within_condition"][COND_LABEL[c]] = {**r, "topic_perm_p": signflip_exact(d.values),
                                                      "topic_boot_ci": list(topic_bootstrap(d.values))}
        for budget, col in [("128", "c128"), ("512", "c512")]:
            mm = m.rename(columns={col: "y"})
            for ref, cmp_ in KEY:
                res[f"contrasts_{budget}"].append(contrast(mm, ref, cmp_, "y"))
        # Difference-in-differences of each key gap, per topic (bootstrap + sign-flip).
        for ref, cmp_ in KEY:
            def gap(col):
                piv = m.pivot(index="semantic_id", columns="condition", values=col)
                t = m.drop_duplicates("semantic_id").set_index("semantic_id").target_entity.loc[piv.index]
                return ((piv[cmp_] - piv[ref]).groupby(t).mean() * 100)
            dd = gap("c512") - gap("c128")
            res["gap_change"][f"{COND_LABEL[cmp_]}-{COND_LABEL[ref]}"] = {
                "gap128": float(gap("c128").mean()), "gap512": float(gap("c512").mean()),
                "change": float(dd.mean()), "topic_boot_ci": list(topic_bootstrap(dd.values)),
                "topic_perm_p": signflip_exact(dd.values)}
        N["budget"][jname] = res

    # 4. Cross-budget comparison: MIXED with 512 tokens vs EN-MATCH with 128.
    for jname in ["J-QWEN", "J-OSS"]:
        en128 = o[o.condition == "A_EN_MATCHED"][["semantic_id", jname]].rename(columns={jname: "en"})
        mx512 = n[n.condition == "E_MIXED_SCRIPT"][["semantic_id", jname, "target_entity"]].rename(columns={jname: "mx"})
        m = en128.merge(mx512, on="semantic_id").dropna()
        r = mcnemar_exact(m.en.values, m.mx.values)
        d = (m.mx - m.en).groupby(m.target_entity).mean() * 100
        N.setdefault("mixed512_vs_en128", {})[jname] = {
            "acc_en128": float(m.en.mean() * 100), "acc_mixed512": float(m.mx.mean() * 100), **r,
            "topic_perm_p": signflip_exact(d.values), "topic_boot_ci": list(topic_bootstrap(d.values))}

    spend = [json.loads(l) for l in open(D / "spend_log.jsonl")]
    sp = pd.DataFrame(spend)
    N["spend_usd"] = {m: float(v) for m, v in sp.groupby("model").usd.sum().items()}
    N["spend_usd"]["total"] = float(sp.usd.sum())
    N["tokens"] = {m: {"in": int(g["in"].sum()), "out": int(g["out"].sum()), "calls": int(len(g))} for m, g in sp.groupby("model")}
    (OUT / "numbers_exp004.json").write_text(json.dumps(N, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print("wrote", OUT / "numbers_exp004.json")


if __name__ == "__main__":
    main()
