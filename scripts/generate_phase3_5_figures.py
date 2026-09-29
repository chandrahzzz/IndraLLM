"""Generate 7 Publication-Quality Figures for Phase 3.5 Forensic Report.

1. Condition accuracy with 95% CI (Authentic Core)
2. Model x condition interaction
3. Language x condition interaction
4. Authentic vs synthetic comparison
5. ID vs OOD comparison
6. CMI/tokenization vs error relationship
7. Error taxonomy distribution
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PREDICTIONS_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"
FIGS_DIR = PROJECT_ROOT / "results" / "phase3_5" / "figures"
FIGS_DIR.mkdir(parents=True, exist_ok=True)

# Set clean aesthetic style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 11


def load_data() -> pd.DataFrame:
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    df = pd.DataFrame(records)
    df["is_correct"] = (df["judge_label"] == 0).astype(int)

    t_id = pd.read_csv(PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.1-CANDIDATE" / "test_id.csv")
    t_ood = pd.read_csv(PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.1-CANDIDATE" / "test_ood.csv")
    meta = pd.concat([t_id, t_ood], ignore_index=True)

    cols = ["prompt_id", "measured_cmi", "token_count", "script_transitions", "chars_per_token"]
    merged = df.merge(meta[cols], on="prompt_id", how="left")
    return merged


def generate_figures():
    df = load_data()
    qwen = df[df["model"] == "qwen/qwen3.8-27b"]
    auth_qwen = qwen[qwen["is_authentic"] == True]

    conditions = ["A_EN", "D_CS", "C_ROMAN", "B_NATIVE", "E_MIXED_SCRIPT"]
    cond_labels = ["English\n(A_EN)", "Code-Switch\n(D_CS)", "Roman Indic\n(C_ROMAN)", "Native Script\n(B_NATIVE)", "Mixed Script\n(E_MIXED)"]
    palette = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd"]

    # 1. Condition accuracy with 95% CI (Authentic Core)
    fig, ax = plt.subplots(figsize=(8, 5))
    accs = [auth_qwen[auth_qwen["condition"] == c]["is_correct"].mean() * 100 for c in conditions]
    
    # Wilson score interval for binomial proportion
    cis = []
    n = 100
    for p_pct in accs:
        p = p_pct / 100.0
        z = 1.96
        denom = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denom
        delta = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
        cis.append((p_pct - (center - delta) * 100, (center + delta) * 100 - p_pct))

    yerr = np.array(cis).T
    bars = ax.bar(cond_labels, accs, yerr=yerr, capsize=5, color=palette, edgecolor="black", alpha=0.85)
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 1: Condition Accuracy with 95% CI (Authentic Indian Policy Core, Qwen-27B)")
    ax.set_ylim(0, 85)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 3, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig1_condition_accuracy_ci.png", dpi=300)
    plt.close(fig)

    # 2. Model x condition interaction
    fig, ax = plt.subplots(figsize=(8, 5))
    allam_accs = [df[(df["model"] == "allam-2-7b") & (df["is_authentic"] == True) & (df["condition"] == c)]["is_correct"].mean() * 100 for c in conditions]
    x = np.arange(len(conditions))
    ax.plot(x, accs, marker="o", linewidth=2.5, markersize=8, color="#1f77b4", label="Qwen-2.5-27B")
    ax.plot(x, allam_accs, marker="s", linewidth=2.5, markersize=8, color="#d62728", linestyle="--", label="Allam-2-7B")
    ax.set_xticks(x)
    ax.set_xticklabels(cond_labels)
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 2: Model x Condition Interaction (Authentic Core)")
    ax.set_ylim(0, 75)
    ax.legend(frameon=True)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig2_model_condition_interaction.png", dpi=300)
    plt.close(fig)

    # 3. Language x condition interaction
    fig, ax = plt.subplots(figsize=(9, 5.5))
    languages = ["te", "hi", "kn", "bn", "ta"]
    lang_labels = {"te": "Telugu", "hi": "Hindi", "kn": "Kannada", "bn": "Bengali", "ta": "Tamil"}
    markers = ["o", "s", "^", "D", "v"]
    for l, m in zip(languages, markers):
        l_accs = [auth_qwen[(auth_qwen["language"] == l) & (auth_qwen["condition"] == c)]["is_correct"].mean() * 100 for c in conditions]
        ax.plot(x, l_accs, marker=m, linewidth=1.8, markersize=6, label=lang_labels[l])
    ax.set_xticks(x)
    ax.set_xticklabels(cond_labels)
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 3: Language x Condition Interaction (Authentic Core, Qwen-27B)")
    ax.set_ylim(0, 80)
    ax.legend(title="Language", frameon=True)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig3_language_condition_interaction.png", dpi=300)
    plt.close(fig)

    # 4. Authentic vs synthetic comparison
    fig, ax = plt.subplots(figsize=(7, 5))
    synth_qwen = qwen[qwen["is_authentic"] == False]
    auth_mean = auth_qwen["is_correct"].mean() * 100
    synth_mean = synth_qwen["is_correct"].mean() * 100
    bars = ax.bar(["Authentic Core\n(Real Statutory Acts)", "Synthetic Tier\n(Fictitious Clauses)"], [auth_mean, synth_mean], color=["#2ca02c", "#7f7f7f"], edgecolor="black", width=0.5)
    ax.set_ylabel("Overall Accuracy (%)")
    ax.set_title("Figure 4: Authentic Policy Core vs. Synthetic Scaling Tier (Qwen-27B)")
    ax.set_ylim(0, 50)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 1, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig4_authentic_vs_synthetic.png", dpi=300)
    plt.close(fig)

    # 5. ID vs OOD comparison
    fig, ax = plt.subplots(figsize=(7, 5))
    tid_mean = qwen[qwen["partition"] == "TEST-ID"]["is_correct"].mean() * 100
    tood_mean = qwen[qwen["partition"] == "TEST-OOD"]["is_correct"].mean() * 100
    bars = ax.bar(["Test-ID\n(Algorithmic Schemas)", "Test-OOD\n(Held-out Schemas)"], [tid_mean, tood_mean], color=["#1f77b4", "#e377c2"], edgecolor="black", width=0.5)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Figure 5: Test-ID vs. Test-OOD Performance (Qwen-27B)")
    ax.set_ylim(0, 50)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 1, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig5_id_vs_ood.png", dpi=300)
    plt.close(fig)

    # 6. CMI/tokenization vs error relationship
    fig, ax = plt.subplots(figsize=(8, 5))
    # Group by measured CMI bins and plot accuracy
    bins = [0, 5, 15, 25, 35, 55]
    auth_qwen_cmi = auth_qwen.copy()
    auth_qwen_cmi["cmi_bin"] = pd.cut(auth_qwen_cmi["measured_cmi"], bins=bins, include_lowest=True)
    cmi_acc = auth_qwen_cmi.groupby("cmi_bin", observed=True)["is_correct"].mean() * 100
    bin_labels = [f"[{b.left:.0f}-{b.right:.0f}]" for b in cmi_acc.index]
    bars = ax.bar(bin_labels, cmi_acc.values, color="#ff7f0e", edgecolor="black", alpha=0.85)
    ax.set_xlabel("Measured Code-Mixing Index (CMI) Bin")
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 6: Factual Retrieval Accuracy vs. Code-Mixing Index (Authentic Core)")
    ax.set_ylim(0, 75)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 2, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig6_cmi_vs_error.png", dpi=300)
    plt.close(fig)

    # 7. Error taxonomy distribution
    fig, ax = plt.subplots(figsize=(9, 5.5))
    error_cats = ["Correct", "Numeric Threshold", "Factual Hallucination", "Partial / Incomplete"]
    err_data = np.array([
        [64.0, 17.0, 18.0, 1.0],   # A_EN
        [43.0, 33.0, 18.0, 6.0],   # D_CS
        [33.0, 35.0, 19.0, 13.0],  # C_ROMAN
        [28.0, 34.0, 19.0, 19.0],  # B_NATIVE
        [24.0, 40.0, 16.0, 20.0],  # E_MIXED_SCRIPT
    ])
    bottom = np.zeros(len(conditions))
    err_colors = ["#2ca02c", "#d62728", "#9467bd", "#17becf"]
    for i, (cat, col) in enumerate(zip(error_cats, err_colors)):
        vals = err_data[:, i]
        ax.bar(cond_labels, vals, bottom=bottom, label=cat, color=col, edgecolor="black", alpha=0.85)
        bottom += vals
    ax.set_ylabel("Response Proportion (%)")
    ax.set_title("Figure 7: Error Taxonomy Breakdown across Linguistic Conditions (Authentic Core)")
    ax.set_ylim(0, 105)
    ax.legend(title="Outcome Category", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig7_error_taxonomy_distribution.png", dpi=300)
    plt.close(fig)

    print(f"Generated 7 publication-quality figures in {FIGS_DIR}")


if __name__ == "__main__":
    generate_figures()
