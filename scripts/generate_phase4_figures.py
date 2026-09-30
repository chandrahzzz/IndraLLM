"""Generate 8 Publication-Quality Figures for Phase 4 Master Report.

1. Effect size by clustering level (Prompt L1 vs Semantic L2 vs Topic L3)
2. Accuracy by condition with 95% CI (Authentic Core)
3. Tokenization fragmentation vs accuracy
4. Script transitions vs error
5. Condition x language
6. Condition x model
7. Error taxonomy by condition
8. Authentic proposition-level effects (20 statutory topics)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PREDICTIONS_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"
INVESTIGATION_JSON = PROJECT_ROOT / "results" / "phase4" / "phase4_statistical_investigation.json"
FIGS_DIR = PROJECT_ROOT / "results" / "phase4" / "figures"
FIGS_DIR.mkdir(parents=True, exist_ok=True)

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
    merged["base_topic_id"] = merged["target_entity"]
    merged["prompt_char_len"] = merged["prompt_text"].str.len()
    return merged


def generate_figures():
    df = load_data()
    qwen = df[df["model"] == "qwen/qwen3.8-27b"]
    auth_qwen = qwen[qwen["is_authentic"] == True]

    with open(INVESTIGATION_JSON, "r", encoding="utf-8") as f:
        inv = json.load(f)

    conditions = ["A_EN", "D_CS", "C_ROMAN", "B_NATIVE", "E_MIXED_SCRIPT"]
    cond_labels = ["English\n(A_EN)", "Code-Switch\n(D_CS)", "Roman Indic\n(C_ROMAN)", "Native Script\n(B_NATIVE)", "Mixed Script\n(E_MIXED)"]
    palette = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd"]

    # -------------------------------------------------------------
    # 1. Effect size by clustering level (Prompt L1 vs Semantic L2 vs Topic L3)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    levels = ["Level 1: Prompt (N=500)", "Level 2: Semantic (N=100)", "Level 3: Topic (N=20)"]
    beta_dcs = [
        inv["workstream_1_topic_hierarchy"]["level_1_naive"]["params"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
        inv["workstream_1_topic_hierarchy"]["level_2_semantic_id"]["params"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
        inv["workstream_1_topic_hierarchy"]["level_3_base_topic"]["params"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
    ]
    se_dcs = [
        inv["workstream_1_topic_hierarchy"]["level_1_naive"]["bse"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
        inv["workstream_1_topic_hierarchy"]["level_2_semantic_id"]["bse"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
        inv["workstream_1_topic_hierarchy"]["level_3_base_topic"]["bse"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
    ]
    p_dcs = [
        inv["workstream_1_topic_hierarchy"]["level_1_naive"]["pvalues"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
        inv["workstream_1_topic_hierarchy"]["level_2_semantic_id"]["pvalues"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
        inv["workstream_1_topic_hierarchy"]["level_3_base_topic"]["pvalues"]["C(condition, Treatment(reference='A_EN'))[T.D_CS]"],
    ]

    y_pos = np.arange(len(levels))
    ax.errorbar(beta_dcs, y_pos, xerr=[1.96 * s for s in se_dcs], fmt="o", color="#1f77b4", ecolor="#d62728", elinewidth=2.5, capsize=6, markersize=8)
    ax.axvline(0, color="gray", linestyle="--", alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(levels)
    ax.set_xlabel("Log-Odds Ratio (D_CS vs. A_EN)")
    ax.set_title("Figure 1: Code-Switching Effect Size & 95% CI across Clustering Levels")
    for i, (b, p) in enumerate(zip(beta_dcs, p_dcs)):
        ax.text(b, i - 0.22, f"β = {b:.3f} (p = {p:.4f})", ha="center", fontweight="bold", fontsize=9)
    ax.set_xlim(-2.2, 0.4)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig1_effect_size_by_clustering_level.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 2. Accuracy by condition with 95% CI
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    accs = [auth_qwen[auth_qwen["condition"] == c]["is_correct"].mean() * 100 for c in conditions]
    n = 100
    yerr = []
    for p_pct in accs:
        p = p_pct / 100.0
        se = math.sqrt(p * (1 - p) / n) * 100.0
        yerr.append(1.96 * se)
    bars = ax.bar(cond_labels, accs, yerr=yerr, capsize=5, color=palette, edgecolor="black", alpha=0.85)
    ax.set_ylabel("Factual Retrieval Accuracy (%)")
    ax.set_title("Figure 2: Factual Accuracy by Representation Condition (Authentic Core, Qwen-27B)")
    ax.set_ylim(0, 85)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 3, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig2_accuracy_by_condition_ci.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 3. Tokenization fragmentation vs accuracy
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    cpt = [auth_qwen[auth_qwen["condition"] == c]["chars_per_token"].mean() for c in conditions]
    scatter = ax.scatter(cpt, accs, s=180, c=palette, edgecolor="black", zorder=3)
    for x_val, y_val, label in zip(cpt, accs, ["A_EN", "D_CS", "C_ROMAN", "B_NATIVE", "E_MIXED"]):
        ax.text(x_val + 0.02, y_val - 1.5, label, fontweight="bold", fontsize=10)
    ax.plot(np.unique(cpt), np.poly1d(np.polyfit(cpt, accs, 1))(np.unique(cpt)), color="black", linestyle=":", alpha=0.7)
    ax.set_xlabel("Token Efficiency (Characters per Token)")
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 3: Subword Tokenization Density vs. Factual Retrieval Accuracy")
    ax.set_xlim(0.6, 1.8)
    ax.set_ylim(15, 75)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig3_tokenization_fragmentation_vs_accuracy.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 4. Script transitions vs error
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    auth_qwen_copy = auth_qwen.copy()
    auth_qwen_copy["trans_bin"] = pd.cut(auth_qwen_copy["script_transitions"], bins=[-1, 0.5, 2.5, 4.5, 10], labels=["0", "1-2", "3-4", "5+"])
    trans_acc = auth_qwen_copy.groupby("trans_bin", observed=True)["is_correct"].mean() * 100
    bars = ax.bar(trans_acc.index, trans_acc.values, color=["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"], edgecolor="black", width=0.55)
    ax.set_xlabel("Number of Intra-Sentential Script Transitions")
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 4: Factual Retrieval Accuracy across Script Transition Densities")
    ax.set_ylim(0, 75)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 2, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig4_script_transitions_vs_error.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 5. Condition x language
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5))
    languages = ["te", "hi", "kn", "bn", "ta"]
    lang_labels = {"te": "Telugu", "hi": "Hindi", "kn": "Kannada", "bn": "Bengali", "ta": "Tamil"}
    markers = ["o", "s", "^", "D", "v"]
    x = np.arange(len(conditions))
    for l, m in zip(languages, markers):
        l_accs = [auth_qwen[(auth_qwen["language"] == l) & (auth_qwen["condition"] == c)]["is_correct"].mean() * 100 for c in conditions]
        ax.plot(x, l_accs, marker=m, linewidth=1.8, markersize=6, label=lang_labels[l])
    ax.set_xticks(x)
    ax.set_xticklabels(cond_labels)
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 5: Condition x Language Interaction Profiles (Authentic Core)")
    ax.set_ylim(0, 80)
    ax.legend(title="Language", frameon=True)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig5_condition_x_language.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 6. Condition x model
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    allam_accs = [df[(df["model"] == "allam-2-7b") & (df["is_authentic"] == True) & (df["condition"] == c)]["is_correct"].mean() * 100 for c in conditions]
    ax.plot(x, accs, marker="o", linewidth=2.5, markersize=8, color="#1f77b4", label="Qwen-2.5-27B (27B)")
    ax.plot(x, allam_accs, marker="s", linewidth=2.5, markersize=8, color="#d62728", linestyle="--", label="Allam-2-7B (7B Baseline)")
    ax.set_xticks(x)
    ax.set_xticklabels(cond_labels)
    ax.set_ylabel("Factual Accuracy (%)")
    ax.set_title("Figure 6: Model x Condition Trajectory Comparison (Authentic Core)")
    ax.set_ylim(0, 75)
    ax.legend(frameon=True)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig6_condition_x_model.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 7. Error taxonomy by condition
    # -------------------------------------------------------------
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
    fig.savefig(FIGS_DIR / "fig7_error_taxonomy_by_condition.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 8. Authentic proposition-level effects (20 statutory topics)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    topic_acc = auth_qwen.groupby(["base_topic_id", "condition"])["is_correct"].mean().unstack()[["A_EN", "D_CS", "E_MIXED_SCRIPT"]]
    topic_acc = topic_acc.sort_values(by="A_EN", ascending=True)

    y_indices = np.arange(len(topic_acc))
    bar_width = 0.28
    ax.barh(y_indices - bar_width, topic_acc["A_EN"] * 100, height=bar_width, color="#1f77b4", label="A_EN (English)", alpha=0.85)
    ax.barh(y_indices, topic_acc["D_CS"] * 100, height=bar_width, color="#2ca02c", label="D_CS (Code-Switch)", alpha=0.85)
    ax.barh(y_indices + bar_width, topic_acc["E_MIXED_SCRIPT"] * 100, height=bar_width, color="#9467bd", label="E_MIXED (Dual-Script)", alpha=0.85)

    ax.set_yticks(y_indices)
    ax.set_yticklabels([t[:30] for t in topic_acc.index], fontsize=8)
    ax.set_xlabel("Factual Accuracy (%)")
    ax.set_title("Figure 8: Accuracy across All 20 Individual Authentic Statutory Topics")
    ax.set_xlim(0, 110)
    ax.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig8_authentic_proposition_level_effects.png", dpi=300)
    plt.close(fig)

    print(f"Generated all 8 publication-quality figures in {FIGS_DIR}")


if __name__ == "__main__":
    generate_figures()
