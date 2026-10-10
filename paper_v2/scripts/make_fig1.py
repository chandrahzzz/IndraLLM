"""Study-design diagram (manuscript Fig. 1). Writes paper_v2/output/fig1.png."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "paper_v2" / "output" / "fig1.png"
plt.rcParams.update({"font.family": "serif", "font.size": 6.6})
COL = {"EN-ORIG": "#4C78A8", "EN-MATCH": "#4C78A8", "CS-LAT": "#E69F00", "ROMAN": "#59A14F",
       "NATIVE": "#B07AA1", "MIXED": "#E15759"}


def box(ax, x, y, w, h, title, lines, fc="#F7F8FA"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012",
                                fc=fc, ec="#9AA3AE", lw=0.7))
    ax.text(x + 0.012, y + h - 0.035, title, weight="bold", va="top", fontsize=7)
    for k, s in enumerate(lines):
        ax.text(x + 0.012, y + h - 0.095 - k * 0.056, s, va="top", fontsize=6.1)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", lw=0.7, color="#555555"))


fig = plt.figure(figsize=(6.6, 3.25))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
box(ax, 0.01, 0.31, 0.17, 0.66, "1  Benchmark", ["20 public-policy topics", "5 languages: hi, bn,", "ta, te, kn",
                                                    "5 propositions/topic", "100 propositions,", "one gold answer each"])
box(ax, 0.21, 0.31, 0.31, 0.66, "2  Six renderings per proposition", [])
desc = {"EN-ORIG": "English, original template", "EN-MATCH": "English, shared template",
        "CS-LAT": "English frame + Latin Indic words", "ROMAN": "Romanized Indic",
        "NATIVE": "Indic in native script", "MIXED": "English frame + native-script words"}
for k, (c, t) in enumerate(desc.items()):
    y = 0.82 - k * 0.083
    ax.add_patch(FancyBboxPatch((0.225, y), 0.085, 0.052, boxstyle="round,pad=0.004", fc=COL[c], ec="none"))
    ax.text(0.2675, y + 0.026, c, ha="center", va="center", color="white", weight="bold", fontsize=5.8)
    ax.text(0.32, y + 0.026, t, va="center", fontsize=6)
box(ax, 0.55, 0.64, 0.19, 0.32, "3  Generation", ["Qwen3.8-27B (Groq API)", "greedy; max 128 tokens",
                                                  "600 responses, one run"])
box(ax, 0.55, 0.31, 0.19, 0.29, "4  Judging", ["J-QWEN: same model", "J-OSS: gpt-oss-120b",
                                                "label: CORRECT or", "HALLUCINATED"])
box(ax, 0.77, 0.31, 0.22, 0.66, "5  Analysis", ["Wilson intervals", "Exact McNemar + Holm",
                                                 "Topic sign-flip test,", "  topic bootstrap", "GEE at 3 levels",
                                                 "Tokenizer mediation", "Judge tipping points"])
arrow(ax, 0.18, 0.63, 0.21, 0.63)
arrow(ax, 0.52, 0.80, 0.55, 0.80)
arrow(ax, 0.645, 0.64, 0.645, 0.60)
arrow(ax, 0.74, 0.45, 0.77, 0.45)
box(ax, 0.01, 0.015, 0.98, 0.265, "Key contrasts and follow-up", [
    "EN-MATCH vs. CS-LAT: code-switching (shared English template)",
    "CS-LAT vs. MIXED: script of the Indic words (word-identical in hi, bn, ta)",
    "Follow-up: EN-MATCH, CS-LAT, MIXED re-answered with max 512 tokens; both budgets graded by J-QWEN and J-OSS"])
fig.savefig(OUT, dpi=300)
print("wrote", OUT)
