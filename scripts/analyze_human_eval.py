"""Analyse the returned v2 human-validation workbooks (build_human_eval_v2.py).

Put each reviewer's filled workbook in results/human_eval_v2/returned/ (same file name as sent).
Run:  python scripts/analyze_human_eval.py [--returned-dir DIR] [--out-dir DIR]

Steps
 1. Completeness: labels per reviewer, invalid / missing labels.
 2. Inter-annotator agreement on items with two usable labels (UNREADABLE excluded):
    six-way % agreement, Cohen's kappa on the primary binary collapse (CORRECT = 1, else 0),
    by language.  Writes adjudication.xlsx listing every binary disagreement; fill its
    'final_label' column (after discussion or by a third reader) and re-run.
 3. Final human label per item: adjudicated label if given; otherwise the agreed label; otherwise
    unresolved (reported, and bounded both ways).
 4. Judge validation against the human label, for J-QWEN and J-OSS: sensitivity
    P(judge CORRECT | human CORRECT), specificity, agreement, kappa — weighted by the inverse
    sampling weights so they describe all 900 outputs, and broken down by budget and condition.
 5. Human-estimated accuracy per budget x condition (stratified estimator using the weights) with a
    stratified bootstrap CI, and the MIXED-CS-LAT and CS-LAT-EN-MATCH gaps per budget.
 6. Secondary collapse (CORRECT + PARTIAL + CORRECT_OTHER_READING = 1) repeated as sensitivity.
Writes <out-dir>/numbers_human_eval.json and human_eval_report.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook, load_workbook
from sklearn.metrics import cohen_kappa_score

ROOT = Path(__file__).resolve().parents[1]
HE = ROOT / "results" / "human_eval_v2"
LABELS = ["CORRECT", "PARTIAL", "INCOMPLETE_NO_ERROR", "INCORRECT", "CORRECT_OTHER_READING", "UNREADABLE"]
PRIMARY = {"CORRECT"}
SECONDARY = {"CORRECT", "PARTIAL", "CORRECT_OTHER_READING"}


def read_returned(d: Path) -> pd.DataFrame:
    rows = []
    for f in sorted(d.glob("*.xlsx")):
        wb = load_workbook(f, read_only=True, data_only=True)
        ws = wb["Items"]
        it = ws.iter_rows(values_only=True)
        head = [str(h) for h in next(it)]
        for r in it:
            rec = dict(zip(head, r))
            if not rec.get("item_id"):
                continue
            lab = (rec.get("label") or "").strip().upper() if isinstance(rec.get("label"), str) else ""
            rows.append({"reviewer": f.stem, "item_id": rec["item_id"], "label": lab,
                         "gold_problem": str(rec.get("gold_problem (Y/N)") or "").strip().upper(),
                         "note": rec.get("note") or ""})
    return pd.DataFrame(rows)


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0 or (len(set(a)) == 1 and len(set(b)) == 1 and a[0] == b[0]):
        return float("nan")
    return float(cohen_kappa_score(a, b))


def weighted_rates(df, judge, human):
    w = df.weight.values
    j = df[judge].values
    h = df[human].values
    pos, neg = h == 1, h == 0
    return {
        "n_items": int(len(df)),
        "sensitivity": float((w[pos] * (j[pos] == 1)).sum() / w[pos].sum()) if pos.any() else None,
        "specificity": float((w[neg] * (j[neg] == 0)).sum() / w[neg].sum()) if neg.any() else None,
        "agreement": float((w * (j == h)).sum() / w.sum()),
        "kappa_unweighted": kappa(j, h),
    }


def cell_estimate(df, human):
    """Stratified estimate of cell accuracy: sum over strata of N_s * mean(human in stratum) / N."""
    g = df.groupby("stratum").agg(N=("stratum_size", "first"), m=(human, "mean"))
    return float((g.N * g.m).sum() / g.N.sum())


def boot_cell(df, human, rng, B=4000):
    """Stratified bootstrap of cell_estimate (resample items within each stratum), vectorised."""
    total, num = 0.0, np.zeros(B)
    for _, g in df.groupby("stratum"):
        v = g[human].to_numpy(float)
        n_s = float(g.stratum_size.iloc[0])
        means = v[rng.integers(0, len(v), size=(B, len(v)))].mean(axis=1)
        num += n_s * means
        total += n_s
    return num / total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returned-dir", default=str(HE / "returned"))
    ap.add_argument("--out-dir", default=str(ROOT / "paper_v2" / "output"))
    ap.add_argument("--adj-path", default=str(HE / "adjudication.xlsx"))
    ap.add_argument("--exclude-topic", action="append", default=[],
                    help="drop items of this target_entity (sensitivity, e.g. a topic with a disputed gold answer)")
    a = ap.parse_args()
    ret, out = Path(a.returned_dir), Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    key = pd.read_csv(HE / "key_v2.csv")
    assign = pd.read_csv(HE / "assignments_v2.csv")
    lab = read_returned(ret)
    if lab.empty:
        raise SystemExit(f"No returned workbooks found in {ret}")
    N = {"reviewers": {}}

    # 1. completeness
    for rev, g in lab.groupby("reviewer"):
        N["reviewers"][rev] = {"assigned": int((assign.reviewer == rev).sum()), "rows": int(len(g)),
                               "labelled": int(g.label.isin(LABELS).sum()),
                               "invalid": int((~g.label.isin(LABELS) & (g.label != "")).sum()),
                               "blank": int((g.label == "").sum()),
                               "unreadable": int((g.label == "UNREADABLE").sum())}
    usable = lab[lab.label.isin(LABELS) & (lab.label != "UNREADABLE")].copy()
    usable["p"] = usable.label.isin(PRIMARY).astype(int)
    usable["s"] = usable.label.isin(SECONDARY).astype(int)
    N["gold_problem_flags"] = lab[lab.gold_problem == "Y"][["reviewer", "item_id", "note"]].to_dict("records")

    # 2. inter-annotator agreement
    pairs = usable.groupby("item_id").filter(lambda g: len(g) >= 2).sort_values(["item_id", "reviewer"])
    first = pairs.groupby("item_id").nth(0).set_index("item_id")
    second = pairs.groupby("item_id").nth(1).set_index("item_id")
    common = first.index.intersection(second.index)
    ia = {"n_double_labelled": int(len(common))}
    if len(common):
        f, s = first.loc[common], second.loc[common]
        ia["six_way_agreement"] = float((f.label == s.label).mean())
        ia["binary_agreement"] = float((f.p == s.p).mean())
        ia["kappa_binary"] = kappa(f.p, s.p)
        ia["kappa_binary_secondary"] = kappa(f.s, s.s)
        lang = key.set_index("item_id").reader_language.loc[common]
        ia["by_language"] = {l: {"n": int((lang == l).sum()),
                                 "binary_agreement": float((f.p[lang == l] == s.p[lang == l]).mean()),
                                 "kappa": kappa(f.p[lang == l], s.p[lang == l])} for l in sorted(lang.unique())}
    N["inter_annotator"] = ia

    # adjudication file
    adj_path = Path(a.adj_path)
    disagree = [i for i in common if first.loc[i, "p"] != second.loc[i, "p"]]
    adjudicated = {}
    if adj_path.exists():
        wb = load_workbook(adj_path, read_only=True)
        rows = list(wb.active.iter_rows(values_only=True))
        h = list(rows[0])
        for r in rows[1:]:
            rec = dict(zip(h, r))
            if rec.get("final_label") and str(rec["final_label"]).strip().upper() in LABELS:
                adjudicated[rec["item_id"]] = str(rec["final_label"]).strip().upper()
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["item_id", "reviewer_1", "label_1", "reviewer_2", "label_2", "final_label", "rationale"])
        for i in disagree:
            ws.append([i, first.loc[i, "reviewer"], first.loc[i, "label"], second.loc[i, "reviewer"],
                       second.loc[i, "label"], "", ""])
        wb.save(adj_path)
    N["adjudication"] = {"binary_disagreements": len(disagree), "adjudicated": len(adjudicated),
                         "file": str(adj_path)}

    # 3. final label
    final = {}
    unresolved = []
    for i, g in usable.groupby("item_id"):
        if i in adjudicated:
            final[i] = adjudicated[i]
        elif len(g) == 1 or g.p.nunique() == 1:
            final[i] = g.label.iloc[0] if g.label.nunique() == 1 else ("CORRECT" if g.p.iloc[0] == 1 else g.label.iloc[0])
        else:
            unresolved.append(i)
    k = key.set_index("item_id")
    res = k.loc[list(final)].copy()
    res = res[~res.target_entity.isin(a.exclude_topic)].copy()
    N["excluded_topics"] = a.exclude_topic
    res["human_label"] = pd.Series(final)
    res["h_p"] = res.human_label.isin(PRIMARY).astype(int)
    res["h_s"] = res.human_label.isin(SECONDARY).astype(int)
    N["final_labels"] = {"resolved": int(len(res)), "unresolved": len(unresolved), "not_labelled": int(len(k) - len(res) - len(unresolved)),
                         "label_counts": res.human_label.value_counts().to_dict()}

    # 4. judge validation
    rng = np.random.default_rng(0)
    N["judge_validation"] = {}
    for human in ["h_p", "h_s"]:
        tag = "primary" if human == "h_p" else "secondary"
        N["judge_validation"][tag] = {}
        for j in ["J-QWEN", "J-OSS"]:
            d = {"overall": weighted_rates(res, j, human), "by_cell": {}}
            for (b, c), g in res.groupby(["budget", "condition"]):
                d["by_cell"][f"{b}|{c}"] = weighted_rates(g, j, human)
            N["judge_validation"][tag][j] = d

    # 5. human-estimated accuracy and gaps
    N["human_accuracy"] = {}
    for human in ["h_p", "h_s"]:
        tag = "primary" if human == "h_p" else "secondary"
        est, boots = {}, {}
        for (b, c), g in res.groupby(["budget", "condition"]):
            est[(b, c)] = cell_estimate(g, human)
            boots[(b, c)] = boot_cell(g, human, rng)
        acc = {f"{b}|{c}": {"estimate": 100 * v, "ci": [100 * float(np.percentile(boots[(b, c)], 2.5)),
                                                         100 * float(np.percentile(boots[(b, c)], 97.5))]}
               for (b, c), v in est.items()}
        gaps = {}
        for b in sorted({b for b, _ in est}, key=int):
            for ref, cmp_ in [("CS-LAT", "MIXED"), ("EN-MATCH", "CS-LAT")]:
                if (b, ref) in est and (b, cmp_) in est:
                    diff = boots[(b, cmp_)] - boots[(b, ref)]
                    gaps[f"{b}|{cmp_}-{ref}"] = {"estimate": 100 * (est[(b, cmp_)] - est[(b, ref)]),
                                                 "ci": [100 * float(np.percentile(diff, 2.5)), 100 * float(np.percentile(diff, 97.5))]}
        N["human_accuracy"][tag] = {"cells": acc, "gaps": gaps}

    (out / "numbers_human_eval.json").write_text(json.dumps(N, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    # report
    L = ["# Human validation of the judges — results", ""]
    L += ["## Completeness", "", "| Reviewer | Assigned | Labelled | Blank | Invalid | Unreadable |", "|---|---|---|---|---|---|"]
    for r, v in N["reviewers"].items():
        L.append(f"| {r} | {v['assigned']} | {v['labelled']} | {v['blank']} | {v['invalid']} | {v['unreadable']} |")
    L += ["", "## Inter-annotator agreement", "", f"Double-labelled items: {ia['n_double_labelled']}"]
    if ia.get("n_double_labelled"):
        L.append(f"Six-way agreement {ia['six_way_agreement']:.2f}; binary agreement {ia['binary_agreement']:.2f}; "
                 f"Cohen's κ (primary) {ia['kappa_binary']:.2f}; κ (secondary) {ia['kappa_binary_secondary']:.2f}.")
    L += ["", f"Binary disagreements: {len(disagree)}; adjudicated: {len(adjudicated)} (file `{N['adjudication']['file']}`).",
          f"Resolved items: {N['final_labels']['resolved']}; unresolved: {N['final_labels']['unresolved']}.", ""]
    for tag in ["primary", "secondary"]:
        L += [f"## Judge validation ({tag} collapse; weighted to all 900 outputs)", "",
              "| Judge | Sensitivity | Specificity | Agreement | κ (sample) |", "|---|---|---|---|---|"]
        for j in ["J-QWEN", "J-OSS"]:
            o = N["judge_validation"][tag][j]["overall"]
            fmt = lambda x: "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.2f}"
            L.append(f"| {j} | {fmt(o['sensitivity'])} | {fmt(o['specificity'])} | {fmt(o['agreement'])} | {fmt(o['kappa_unweighted'])} |")
        L += ["", "| Budget × condition | Human accuracy % [95% CI] |", "|---|---|"]
        for cell, v in N["human_accuracy"][tag]["cells"].items():
            L.append(f"| {cell} | {v['estimate']:.0f} [{v['ci'][0]:.0f}, {v['ci'][1]:.0f}] |")
        L += ["", "| Gap | Human estimate (pp) [95% CI] |", "|---|---|"]
        for g, v in N["human_accuracy"][tag]["gaps"].items():
            L.append(f"| {g} | {v['estimate']:+.0f} [{v['ci'][0]:.0f}, {v['ci'][1]:.0f}] |")
        L.append("")
    (out / "human_eval_report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
