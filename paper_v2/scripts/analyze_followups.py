"""Analyse EXP-006 (complete answers) and EXP-007 (second answering model) once they have been run.

EXP-006: build the "complete" set for EN-MATCH / CS-LAT / MIXED: the 1,024-token response where it
finished on its own, otherwise the 3,072-token re-answer.  Report how many are still capped, accuracy
under both judges, and the paired contrasts (proposition-level exact McNemar; topic-level exact
sign-flip and bootstrap).

EXP-007: Gemini accuracy by budget x condition x judge, the same contrasts, cap rates, and judge
agreement.  Writes paper_v2/output/numbers_followups.json; sections whose inputs are missing are skipped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_lib import mcnemar_exact, signflip_exact, topic_bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper_v2" / "output"
LAB = {"A_EN_MATCHED": "EN-MATCH", "D_CS": "CS-LAT", "E_MIXED_SCRIPT": "MIXED", "B_NATIVE": "NATIVE", "C_ROMAN": "ROMAN"}
KEY = [("A_EN_MATCHED", "D_CS"), ("D_CS", "E_MIXED_SCRIPT"), ("A_EN_MATCHED", "E_MIXED_SCRIPT")]


def jl(p: Path):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []


def contrasts(df: pd.DataFrame, col: str) -> list[dict]:
    out = []
    for ref, cmp_ in KEY:
        piv = df.pivot_table(index="semantic_id", columns="condition", values=col, aggfunc="first")
        if ref not in piv or cmp_ not in piv:
            continue
        piv = piv[[ref, cmp_]].dropna()
        topic = df.drop_duplicates("semantic_id").set_index("semantic_id").target_entity.loc[piv.index]
        r = mcnemar_exact(piv[ref].values, piv[cmp_].values)
        d = (piv[cmp_] - piv[ref]).groupby(topic).mean() * 100
        out.append({"ref": LAB[ref], "cmp": LAB[cmp_], "n": int(len(piv)),
                    "acc_ref": float(piv[ref].mean() * 100), "acc_cmp": float(piv[cmp_].mean() * 100),
                    "delta_pp": float((piv[cmp_] - piv[ref]).mean() * 100), **r,
                    "topic_perm_p": signflip_exact(d.values) if len(d) >= 2 else None,
                    "topic_boot_ci": list(topic_bootstrap(d.values)) if len(d) >= 2 else None})
    return out


def labels(rows: list[dict]) -> pd.DataFrame:
    j = pd.DataFrame(rows)
    j = j[j.judge_label >= 0].copy()
    j["y"] = (j.judge_label == 0).astype(int)
    return j


def exp006() -> dict | None:
    g1024 = pd.DataFrame(jl(ROOT / "results/EXP-005-budget1024/gen1024_predictions.jsonl"))
    g3072 = pd.DataFrame(jl(ROOT / "results/EXP-006-complete/gen3072_predictions.jsonl"))
    if g3072.empty:
        return None
    j1024 = labels(jl(ROOT / "results/EXP-005-budget1024/judgements.jsonl"))
    j3072 = labels(jl(ROOT / "results/EXP-006-complete/judgements.jsonl"))
    finished = g1024[g1024.finish_reason == "stop"].copy()
    finished["source"] = "1024"
    rerun = g3072.copy()
    rerun["source"] = "3072"
    comp = pd.concat([finished, rerun], ignore_index=True)
    lab1024 = j1024.pivot_table(index="prompt_id", columns="judge", values="y", aggfunc="first")
    lab3072 = j3072.pivot_table(index="prompt_id", columns="judge", values="y", aggfunc="first")
    for jn in ["J-QWEN", "J-OSS"]:
        comp[jn] = [lab1024.get(jn, pd.Series(dtype=float)).get(p) if s == "1024" else
                    lab3072.get(jn, pd.Series(dtype=float)).get(p) for p, s in zip(comp.prompt_id, comp.source)]
    N = {"n_responses": int(len(comp)),
         "still_capped_at_3072": {LAB[c]: int(((comp.condition == c) & (comp.source == "3072") &
                                               (comp.finish_reason == "length")).sum()) for c in LAB if c in set(comp.condition)},
         "rerun_count": {LAB[c]: int(((comp.condition == c) & (comp.source == "3072")).sum()) for c in LAB if c in set(comp.condition)}}
    for jn in ["J-QWEN", "J-OSS"]:
        d = comp.dropna(subset=[jn])
        N[jn] = {"accuracy": {LAB[c]: float(d[d.condition == c][jn].mean() * 100) for c in LAB if c in set(d.condition)},
                 "contrasts": contrasts(d, jn)}
    return N


def exp007() -> dict | None:
    g = pd.DataFrame(jl(ROOT / "results/EXP-007-second-model/gemini_predictions.jsonl"))
    j = jl(ROOT / "results/EXP-007-second-model/judgements.jsonl")
    if g.empty or not j:
        return None
    J = labels(j)
    lab = J.pivot_table(index=["prompt_id", "max_tokens"], columns="judge", values="y", aggfunc="first").reset_index()
    df = g.merge(lab, on=["prompt_id", "max_tokens"], how="left")
    N = {"model": sorted(df.model.unique().tolist()), "budgets": {}}
    for b, d in df.groupby("max_tokens"):
        e = {"n": int(len(d)),
             "hit_cap": {LAB[c]: int(d[(d.condition == c)].finish_reason.str.contains("MAX_TOKENS").sum()) for c in sorted(set(d.condition))},
             "n_per_condition": {LAB[c]: int((d.condition == c).sum()) for c in sorted(set(d.condition))}}
        for jn in ["J-QWEN", "J-OSS"]:
            dd = d.dropna(subset=[jn])
            e[jn] = {"accuracy": {LAB[c]: float(dd[dd.condition == c][jn].mean() * 100) for c in sorted(set(dd.condition))},
                     "contrasts": contrasts(dd, jn)}
        both = d.dropna(subset=["J-QWEN", "J-OSS"])
        if len(both):
            q, o = both["J-QWEN"].astype(int), both["J-OSS"].astype(int)
            pe = q.mean() * o.mean() + (1 - q.mean()) * (1 - o.mean())
            e["judge_agreement"] = {"agreement": float((q == o).mean()),
                                    "kappa": float(((q == o).mean() - pe) / (1 - pe)) if pe < 1 else None,
                                    "qwen_correct_oss_wrong": int(((q == 1) & (o == 0)).sum()),
                                    "qwen_wrong_oss_correct": int(((q == 0) & (o == 1)).sum())}
        N["budgets"][str(b)] = e
    return N


def main():
    N = {"exp006_complete_answers": exp006(), "exp007_second_model": exp007()}
    (OUT / "numbers_followups.json").write_text(json.dumps(N, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    for k, v in N.items():
        print(k, "->", "not run yet" if v is None else "analysed")
    print("wrote", OUT / "numbers_followups.json")


if __name__ == "__main__":
    main()
