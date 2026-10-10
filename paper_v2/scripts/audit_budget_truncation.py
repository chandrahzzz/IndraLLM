"""Post-review audit of the budget follow-up (128 / 512 / 1,024 tokens).

1. Truncation at each budget, from raw outputs: finish reason, responses that hit the cap,
   responses that end mid-sentence, and whether capped responses end mid-sentence.
2. Complete-answers sensitivity (exploratory; selecting on completion can bias):
   (a) paired: propositions where BOTH conditions of a contrast stopped before the cap;
   (b) unpaired: accuracy among responses that stopped before the cap.
3. Multiplicity for the follow-up: Holm across all 18 tests (3 budgets x 2 judges x 3 contrasts)
   at proposition and topic level, in addition to Holm within each budget-judge cell.
4. Intervals for the non-significant MIXED-CS-LAT gaps (no equivalence test was pre-specified).
Writes paper_v2/output/numbers_audit.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_lib import COND_LABEL, QWEN, ends_mid_sentence, holm, mcnemar_exact  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper_v2" / "output"
GEN3 = ["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]
CAP = {"128": 128, "512": 512, "1024": 1024}
KEY = [("A_EN_MATCHED", "D_CS"), ("D_CS", "E_MIXED_SCRIPT"), ("A_EN_MATCHED", "E_MIXED_SCRIPT")]


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main():
    orig = pd.DataFrame(jl(ROOT / "results/EXP-002/full_predictions.jsonl") +
                        jl(ROOT / "results/EXP-003-matched-en/matched_predictions.jsonl"))
    orig = orig[(orig.model == QWEN) & (orig.partition == "TEST-OOD") & orig.condition.isin(GEN3)].copy()
    orig["finish_reason"] = None
    resp = {"128": orig,
            "512": pd.DataFrame(jl(ROOT / "results/EXP-004-budget-rejudge/gen512_predictions.jsonl")),
            "1024": pd.DataFrame(jl(ROOT / "results/EXP-005-budget1024/gen1024_predictions.jsonl"))}
    J = pd.DataFrame(jl(ROOT / "results/EXP-004-budget-rejudge/judgements.jsonl") +
                     jl(ROOT / "results/EXP-005-budget1024/judgements.jsonl"))
    J["budget"] = J.source.map({"orig128": "128", "gen512": "512", "gen1024": "1024"})
    J["correct"] = (J.judge_label == 0).astype(int)
    lab = J.pivot_table(index=["budget", "prompt_id"], columns="judge", values="correct", aggfunc="first").reset_index()

    N = {"truncation": {}, "complete_sensitivity": {}}
    frames = {}
    for b, r in resp.items():
        f = r[["prompt_id", "semantic_id", "condition", "target_entity", "model_response", "completion_tokens",
               "finish_reason"]].merge(lab[lab.budget == b].drop(columns="budget"), on="prompt_id")
        f["hit_cap"] = f.completion_tokens >= CAP[b]
        if b != "128":
            f["hit_cap"] = f.finish_reason == "length"
        f["mid"] = f.model_response.apply(ends_mid_sentence)
        frames[b] = f
        N["truncation"][b] = {}
        for c in GEN3:
            s = f[f.condition == c]
            N["truncation"][b][COND_LABEL[c]] = {
                "n": int(len(s)),
                "finish_reasons": {str(k): int(v) for k, v in s.finish_reason.value_counts(dropna=False).items()},
                "hit_cap": int(s.hit_cap.sum()),
                "stopped_before_cap": int((~s.hit_cap).sum()),
                "ends_mid_sentence": int(s.mid.sum()),
                "hit_cap_and_mid_sentence": int((s.hit_cap & s.mid).sum()),
                "stopped_but_mid_sentence": int((~s.hit_cap & s.mid).sum()),
                "mean_completion_tokens": float(s.completion_tokens.mean()),
                "max_completion_tokens": int(s.completion_tokens.max()),
            }

    for b in ["512", "1024"]:
        f = frames[b]
        N["complete_sensitivity"][b] = {}
        for j in ["J-QWEN", "J-OSS"]:
            res = {"unpaired_accuracy_complete_only": {}, "paired_both_complete": []}
            for c in GEN3:
                s = f[(f.condition == c) & ~f.hit_cap]
                res["unpaired_accuracy_complete_only"][COND_LABEL[c]] = {
                    "n": int(len(s)), "acc": float(s[j].mean() * 100) if len(s) else None}
            for ref, cmp_ in KEY:
                sub = f[f.condition.isin([ref, cmp_])]
                piv = sub.pivot(index="semantic_id", columns="condition", values=j)
                done = sub.pivot(index="semantic_id", columns="condition", values="hit_cap")
                both = done.index[(~done[ref].astype(bool)) & (~done[cmp_].astype(bool))]
                p = piv.loc[both]
                r = mcnemar_exact(p[ref].values, p[cmp_].values) if len(p) else {"b": 0, "c": 0, "p_exact": float("nan")}
                res["paired_both_complete"].append({
                    "ref": COND_LABEL[ref], "cmp": COND_LABEL[cmp_], "n_pairs": int(len(p)),
                    "acc_ref": float(p[ref].mean() * 100) if len(p) else None,
                    "acc_cmp": float(p[cmp_].mean() * 100) if len(p) else None, **r})
            N["complete_sensitivity"][b][j] = res

    # Multiplicity across the whole follow-up (3 budgets x 2 judges x 3 contrasts = 18 tests)
    NB = json.loads((OUT / "numbers_budgets.json").read_text(encoding="utf-8"))
    tests = []
    for j in ["J-QWEN", "J-OSS"]:
        for b in ["128", "512", "1024"]:
            for c in NB["contrasts"][j][b]:
                tests.append({"judge": j, "budget": b, "contrast": f"{c['cmp']} vs {c['ref']}",
                              "delta_pp": c["delta_pp"], "p_exact": c["p_exact"], "topic_p": c["topic_perm_p"],
                              "topic_ci": c["topic_boot_ci"]})
    hp = holm([t["p_exact"] for t in tests])
    ht = holm([t["topic_p"] for t in tests])
    for t, a, bq in zip(tests, hp, ht):
        t["holm18_exact"], t["holm18_topic"] = a, bq
    # Holm within each budget-judge cell (3 tests)
    for j in ["J-QWEN", "J-OSS"]:
        for b in ["128", "512", "1024"]:
            cell = [t for t in tests if t["judge"] == j and t["budget"] == b]
            for t, a, bq in zip(cell, holm([t["p_exact"] for t in cell]), holm([t["topic_p"] for t in cell])):
                t["holm3_exact"], t["holm3_topic"] = a, bq
    N["multiplicity"] = tests

    (OUT / "numbers_audit.json").write_text(json.dumps(N, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print("wrote", OUT / "numbers_audit.json")


if __name__ == "__main__":
    main()
