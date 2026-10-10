"""Regenerate manuscript Figs. 2-5.

Figs. 2-4 use the harmonised judge labels (numbers_jqwen.json); Fig. 5 combines the
128-token response descriptors with the EXP-004 budget follow-up (numbers_exp004.json).
Run make_all.py --labels jqwen and analyze_exp004.py first.  Writes paper_v2/output/fig{2,3,4,5}.png at 300 dpi, sized to
the slots in the IEEE manuscript.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_lib import COND_LABEL, MATCHED5, ORDER, QWEN, topic_bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper_v2" / "output"
N = json.loads((OUT / "numbers_jqwen.json").read_text(encoding="utf-8"))
E = json.loads((OUT / "numbers_exp004.json").read_text(encoding="utf-8"))
COL = {"EN-ORIG": "#999999", "EN-MATCH": "#000000", "CS-LAT": "#E69F00",
       "ROMAN": "#56B4E9", "NATIVE": "#009E73", "MIXED": "#D55E00"}
LAB = [COND_LABEL[c] for c in ORDER]
plt.rcParams.update({"font.family": "serif", "font.size": 7.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.linewidth": 0.6})


def load():
    rows = [json.loads(l) for f in ["results/EXP-002/full_predictions.jsonl",
                                    "results/EXP-003-matched-en/matched_predictions.jsonl"]
            for l in open(ROOT / f, encoding="utf-8")]
    q = pd.DataFrame(rows)
    q = q[(q.model == QWEN) & (q.partition == "TEST-OOD")].copy()
    j = pd.DataFrame([json.loads(l) for l in open(ROOT / "results/EXP-004-budget-rejudge/judgements.jsonl", encoding="utf-8")])
    j = j[(j.source == "orig128") & (j.judge == "J-QWEN")].set_index("prompt_id").judge_label
    q["correct"] = (q.prompt_id.map(j) == 0).astype(int)
    return q


def fig2(q):
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 3.0), gridspec_kw={"width_ratios": [1, 1.25]})
    for i, c in enumerate(LAB):
        acc = N["accuracy"][c]
        k = acc["k"]
        lo, hi = acc["wilson"]
        a.errorbar(i, k, yerr=[[k - lo], [hi - k]], fmt="o", color=COL[c], capsize=2.5, ms=4, lw=0.9)
        a.text(i, hi + 2, f"{k}", ha="center", fontsize=7)
    a.set_xticks(range(6), LAB, rotation=35, ha="right")
    a.set_ylim(0, 85)
    a.set_ylabel("Accuracy (% judged correct)")
    a.set_title("(a) Accuracy, Wilson 95% CI, n = 100 each", fontsize=8)
    a.grid(axis="y", lw=0.3, alpha=0.5)
    topic = pd.DataFrame(N["by_topic"]).T[LAB]
    topic = topic.sort_values(["EN-MATCH", "EN-ORIG"], ascending=False)
    b.imshow(topic.values, cmap="Blues", vmin=0, vmax=5, aspect="auto")
    for (i, j), v in np.ndenumerate(topic.values):
        b.text(j, i, str(v), ha="center", va="center", fontsize=5.2, color="white" if v >= 3 else "black")
    b.set_yticks(range(len(topic)), topic.index, fontsize=5.2)
    b.set_xticks(range(6), LAB, rotation=35, ha="right")
    b.set_title("(b) Languages correct (of 5), per topic", fontsize=8)
    b.tick_params(length=0)
    for s in b.spines.values():
        s.set_visible(False)
    fig.tight_layout(w_pad=1.0)
    fig.savefig(OUT / "fig2.png", dpi=300)


def fig3(q):
    fig, ax = plt.subplots(figsize=(3.2, 2.6))
    names = {"hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu", "kn": "Kannada"}
    marks = {"hi": "o", "bn": "s", "ta": "^", "te": "D", "kn": "v"}
    for l, nm in names.items():
        ax.plot(range(6), [N["by_language"][l][c] for c in LAB], marker=marks[l], ms=3.5, lw=0.9, label=nm)
    ax.set_xticks(range(6), LAB, rotation=35, ha="right")
    ax.set_ylabel("Accuracy (%), n = 20 per cell")
    ax.set_ylim(0, 80)
    ax.grid(axis="y", lw=0.3, alpha=0.5)
    ax.legend(fontsize=6, ncol=2, frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "fig3.png", dpi=300)


def fig4(q):
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 2.7), gridspec_kw={"width_ratios": [1.1, 1]})
    units = ["prompt", "proposition", "topic"]
    offs = {"prompt": -0.22, "proposition": 0.0, "topic": 0.22}
    mk = {"prompt": "o", "proposition": "s", "topic": "D"}
    conds = ["CS-LAT", "ROMAN", "NATIVE", "MIXED"]
    for i, c in enumerate(conds):
        for u in units:
            g = N["gee"][c][u]
            a.errorbar(i + offs[u], g["beta"], yerr=1.959964 * g["se_robust"], fmt=mk[u], color=COL[c],
                       ms=3.5, capsize=2, lw=0.9, label=u if i == 0 else None)
    a.axhline(0, color="k", lw=0.5)
    a.set_xticks(range(4), conds)
    a.set_xlabel("Contrast with EN-MATCH")
    a.set_ylabel("Log-odds difference (GEE, robust 95% CI)")
    a.set_title("(a) GEE effect by clustering unit", fontsize=7.5)
    leg = a.legend(fontsize=6, frameon=False, loc="lower left")
    for h in leg.legend_handles:
        h.set_color("gray")
    piv = q.pivot(index="semantic_id", columns="condition", values="correct")
    topic = q.drop_duplicates("semantic_id").set_index("semantic_id").target_entity
    d = ((piv["D_CS"] - piv["E_MIXED_SCRIPT"]).groupby(topic).mean() * 100).sort_values()
    lo, hi = topic_bootstrap(d.values)
    b.axhspan(lo, hi, color=COL["MIXED"], alpha=0.12, lw=0)
    b.axhline(d.mean(), color=COL["MIXED"], lw=0.9)
    b.bar(range(len(d)), d.values, color=[COL["CS-LAT"] if v > 0 else "#777777" for v in d.values], width=0.75)
    b.axhline(0, color="k", lw=0.5)
    b.set_xticks([])
    b.set_xlabel("20 topics, sorted")
    b.set_ylabel("CS-LAT minus MIXED (pp)")
    b.set_title(f"(b) Per-topic CS-LAT minus MIXED\nmean {d.mean():.0f} pp, bootstrap CI [{lo:.0f}, {hi:.0f}]", fontsize=7.5)
    fig.tight_layout(w_pad=1.2)
    fig.savefig(OUT / "fig4.png", dpi=300)


def fig5(q):
    R = N["response"]
    T = N["tokenizer_check"]["Qwen3.8-27B"]["cpt_by_condition"]
    G = E["gen512_descriptives"]
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(6.6, 2.6), gridspec_kw={"width_ratios": [1.25, 1, 1]})
    x = np.arange(6)
    a.bar(x - 0.2, [R[k]["mean_chars"] for k in LAB], width=0.4, color=[COL[k] for k in LAB], label="128 tokens")
    for i, k in enumerate(LAB):
        a.text(i - 0.2, R[k]["mean_chars"] + 25, f"{R[k]['brahmic_majority_pct']:.0f}", ha="center", fontsize=5.5)
        if k in G:
            a.bar(i + 0.2, G[k]["mean_chars"], width=0.4, color=COL[k], alpha=0.45, hatch="////", lw=0)
    a.set_xticks(x, LAB, rotation=45, ha="right")
    a.set_ylabel("Mean response length (chars)")
    a.set_title("(a) Response length: solid 128, hatched 512\ntokens; labels = % mostly Brahmic", fontsize=7)
    for k in ["EN-MATCH", "CS-LAT", "MIXED"]:
        for jn, ls, mk in [("J-QWEN", "-", "o"), ("J-OSS", "--", "s")]:
            acc = E["budget"][jn]["accuracy"][k]
            b.plot([0, 1], [acc["128"], acc["512"]], ls=ls, marker=mk, ms=3.5, color=COL[k], lw=1)
        b.text(1.04, E["budget"]["J-QWEN"]["accuracy"][k]["512"], k, fontsize=5.8, va="center", color=COL[k])
    b.set_xticks([0, 1], ["128", "512"])
    b.set_xlim(-0.15, 1.45)
    b.set_ylim(0, 90)
    b.set_xlabel("Output budget (tokens)")
    b.set_ylabel("Judge-assessed accuracy (%)")
    b.set_title("(b) Same prompts, larger budget\n(solid: J-QWEN; dashed: J-OSS)", fontsize=7)
    for k in LAB:
        c.scatter(T[k], 100 * R[k]["acc"], color=COL[k], s=14)
        c.annotate(k, (T[k], 100 * R[k]["acc"]), xytext=(3, 2), textcoords="offset points", fontsize=5.6)
    c.set_xlabel("Prompt chars per token (Qwen3.8)")
    c.set_ylabel("Accuracy at 128 tokens (%)")
    c.set_xlim(2, 6.8)
    c.set_title("(c) Condition-level fertility vs.\naccuracy (six points, descriptive)", fontsize=7)
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "fig5.png", dpi=300)


if __name__ == "__main__":
    q = load()
    for f in (fig2, fig3, fig4, fig5):
        f(q)
    print("figures written to", OUT)
