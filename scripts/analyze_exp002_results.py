"""Statistical Analysis for EXP-002 Main Factuality Experiment.

Performs:
1. Cluster-level paired McNemar tests (Edwards continuity correction) on semantic_id.
2. Repeated-measures Logistic Regression with cluster-robust standard errors (GEE).
3. Rogan-Gladen prevalence adjustment for evaluator orthographic bias.
4. Stratified disaggregation: Full vs Authentic Core vs Synthetic Tier; Test-ID vs Test-OOD; by Language and Condition.
5. Holm-Bonferroni family-wise error rate control.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from indrallm.config import PROJECT_ROOT
from indrallm.evaluation.statistical_testing import (
    bootstrap_ci_diff,
    fit_repeated_measures_logistic_regression,
    holm_bonferroni_correction,
    mcnemar_test,
)

PREDICTIONS_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"
OUT_DIR = PROJECT_ROOT / "results" / "EXP-002"


def rogan_gladen_adjust(observed_prev: float, tpr: float = 0.88, fpr: float = 0.10) -> float:
    """Adjust observed prevalence using Rogan-Gladen formula: P_true = (P_obs - FPR) / (TPR - FPR)."""
    adj = (observed_prev - fpr) / max(tpr - fpr, 1e-6)
    return max(0.0, min(1.0, adj))


def run_full_statistical_analysis():
    records = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} predictions across {df['model'].nunique()} models.")

    df["is_correct"] = (df["judge_label"] == 0).astype(int)

    analysis_results: dict[str, Any] = {}

    for model_name, m_df in df.groupby("model"):
        print(f"\n=================== MODEL: {model_name} ===================")
        m_res: dict[str, Any] = {}

        # 1. Overall & Condition Accuracy
        cond_acc = m_df.groupby("condition")["is_correct"].agg(["mean", "count"]).to_dict("index")
        m_res["condition_accuracy"] = {k: round(v["mean"] * 100, 2) for k, v in cond_acc.items()}
        print("Condition Accuracy (%):", m_res["condition_accuracy"])

        # 2. Rogan-Gladen Adjusted Condition Accuracy
        # English: TPR=0.93, FPR=0.02
        # Code-mixed / Vernacular: TPR=0.86, FPR=0.12
        adj_acc = {}
        for c in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]:
            obs = cond_acc[c]["mean"]
            if c == "A_EN":
                adj = rogan_gladen_adjust(obs, tpr=0.93, fpr=0.02)
            else:
                adj = rogan_gladen_adjust(obs, tpr=0.86, fpr=0.12)
            adj_acc[c] = round(adj * 100, 2)
        m_res["adjusted_condition_accuracy"] = adj_acc
        print("Rogan-Gladen Adjusted Condition Accuracy (%):", adj_acc)

        # 3. Disaggregation: Authentic Core (Test-OOD) vs Synthetic Tier (Test-ID)
        auth_df = m_df[m_df["is_authentic"] == True]
        synth_df = m_df[m_df["is_authentic"] == False]

        auth_acc = auth_df.groupby("condition")["is_correct"].mean().to_dict()
        synth_acc = synth_df.groupby("condition")["is_correct"].mean().to_dict()
        m_res["authentic_core_condition_accuracy"] = {k: round(v * 100, 2) for k, v in auth_acc.items()}
        m_res["synthetic_tier_condition_accuracy"] = {k: round(v * 100, 2) for k, v in synth_acc.items()}

        print("Authentic Core (Test-OOD) Accuracy (%):", m_res["authentic_core_condition_accuracy"])
        print("Synthetic Tier (Test-ID) Accuracy (%):", m_res["synthetic_tier_condition_accuracy"])

        # 4. Language Breakdown
        lang_acc = m_df.groupby("language")["is_correct"].mean().to_dict()
        m_res["language_accuracy"] = {k: round(v * 100, 2) for k, v in lang_acc.items()}
        print("Language Accuracy (%):", m_res["language_accuracy"])

        # 5. Paired McNemar Tests across Conditions (on Authentic Core)
        # Pairwise pivots: rows = semantic_id, columns = condition
        piv = auth_df.pivot(index="semantic_id", columns="condition", values="is_correct").dropna()
        contrasts = [
            ("A_EN", "B_NATIVE", "C1_English_vs_Native"),
            ("B_NATIVE", "C_ROMAN", "C2_Native_vs_Roman"),
            ("A_EN", "D_CS", "C3_English_vs_CodeSwitched"),
            ("D_CS", "E_MIXED_SCRIPT", "C4_SingleScript_vs_MixedScript"),
        ]

        mcnemar_results = {}
        raw_p_values = []
        for c_ctrl, c_treat, c_id in contrasts:
            ctrl_vals = piv[c_ctrl].tolist()
            treat_vals = piv[c_treat].tolist()
            y_true = [1] * len(ctrl_vals)  # binary correctness is 1
            res = mcnemar_test(y_true, ctrl_vals, treat_vals, correction=True)
            res["b01_ctrl_correct_treat_wrong"] = res["b01"]
            res["b10_ctrl_wrong_treat_correct"] = res["b10"]
            
            # Bootstrap CI on difference
            boot_res = bootstrap_ci_diff(ctrl_vals, treat_vals, paired=True, n_bootstraps=2000, random_seed=42)
            res["observed_diff_pct"] = round(boot_res["observed_diff"] * 100, 2)
            res["ci_lower_pct"] = round(boot_res["ci_lower"] * 100, 2)
            res["ci_upper_pct"] = round(boot_res["ci_upper"] * 100, 2)
            
            mcnemar_results[c_id] = res
            raw_p_values.append(res["p_value"])

        # Holm-Bonferroni correction
        hb_res = holm_bonferroni_correction(raw_p_values, alpha=0.05)
        for i, (c_ctrl, c_treat, c_id) in enumerate(contrasts):
            mcnemar_results[c_id]["holm_bonferroni"] = hb_res[i]

        m_res["paired_contrasts_authentic_core"] = mcnemar_results

        # 6. Clustered Logistic Regression (Repeated Measures on semantic_id)
        # Using authentic core where variance exists
        try:
            glmm_res = fit_repeated_measures_logistic_regression(
                auth_df,
                formula="is_correct ~ C(condition, Treatment(reference='A_EN')) + C(language)",
                cluster_col="semantic_id",
            )
            m_res["glmm_regression"] = {
                "odds_ratios": {k: round(v, 4) for k, v in glmm_res["odds_ratios"].items()},
                "p_values": {k: round(v, 4) for k, v in glmm_res["p_values"].items()},
                "conf_int_95": {k: {k2: round(v2, 4) for k2, v2 in v.items()} for k, v in glmm_res["conf_int_95"].items()},
                "num_clusters": glmm_res["num_clusters"],
            }
            print("GLMM Odds Ratios:", m_res["glmm_regression"]["odds_ratios"])
        except Exception as e:
            m_res["glmm_regression_error"] = str(e)
            print("GLMM Error:", e)

        analysis_results[model_name] = m_res

    # Save comprehensive statistical summary
    with open(OUT_DIR / "statistical_analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2)

    print("\nStatistical analysis completed and written to results/EXP-002/statistical_analysis_summary.json")


if __name__ == "__main__":
    run_full_statistical_analysis()
