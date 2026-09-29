"""Forensic Auditor Module for Experimental Verification & Statistical Integrity.

Provides reusable methods to:
1. Recompute metrics directly from raw JSONL predictions.
2. Compute Rogan-Gladen adjusted prevalence with Delta-method variance propagation.
3. Fit multi-level clustered GEE regressions across semantic and topic hierarchies.
4. Execute Family-Wise Error Rate (FWER) step-down Holm-Bonferroni corrections.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf


def recompute_experiment_metrics(predictions_path: Path | str) -> dict[str, Any]:
    """Recompute full suite of model, condition, partition, and language metrics."""
    records = []
    with open(predictions_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    df = pd.DataFrame(records)
    df["is_correct"] = (df["judge_label"] == 0).astype(int)

    metrics: dict[str, Any] = {
        "total_records": len(df),
        "models": sorted(df["model"].unique().tolist()),
        "conditions": sorted(df["condition"].unique().tolist()),
        "partitions": sorted(df["partition"].unique().tolist()),
        "overall_accuracy": {},
        "by_condition": {},
        "by_language": {},
        "by_partition": {},
        "authentic_core_condition_accuracy": {},
    }

    for m in df["model"].unique():
        m_df = df[df["model"] == m]
        metrics["overall_accuracy"][m] = round(m_df["is_correct"].mean() * 100, 2)

        for c in sorted(df["condition"].unique()):
            sub = m_df[m_df["condition"] == c]
            metrics["by_condition"][f"{m}_{c}"] = round(sub["is_correct"].mean() * 100, 2)

        for l in sorted(df["language"].unique()):
            sub = m_df[m_df["language"] == l]
            metrics["by_language"][f"{m}_{l}"] = round(sub["is_correct"].mean() * 100, 2)

        for p in sorted(df["partition"].unique()):
            sub = m_df[m_df["partition"] == p]
            metrics["by_partition"][f"{m}_{p}"] = round(sub["is_correct"].mean() * 100, 2)

        auth_sub = m_df[m_df["is_authentic"] == True]
        for c in sorted(df["condition"].unique()):
            sub = auth_sub[auth_sub["condition"] == c]
            metrics["authentic_core_condition_accuracy"][f"{m}_{c}"] = round(sub["is_correct"].mean() * 100, 2)

    return metrics


def rogan_gladen_with_variance(
    observed_prev: float,
    tpr: float,
    fpr: float,
    n_samples: int,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Compute Rogan-Gladen adjusted prevalence with Delta-method confidence intervals."""
    denom = max(tpr - fpr, 1e-6)
    raw_adj = (observed_prev - fpr) / denom
    clamped_adj = max(0.0, min(1.0, raw_adj))

    # Delta method standard error
    var_obs = (observed_prev * (1.0 - observed_prev)) / max(n_samples, 1)
    se_adj = math.sqrt(var_obs) / denom

    z_crit = stats.norm.ppf(1.0 - alpha / 2.0)
    ci_lower = max(0.0, raw_adj - z_crit * se_adj)
    ci_upper = min(1.0, raw_adj + z_crit * se_adj)

    return {
        "observed_prevalence": round(observed_prev, 4),
        "tpr": round(tpr, 4),
        "fpr": round(fpr, 4),
        "raw_adjusted": round(raw_adj, 4),
        "clamped_adjusted": round(clamped_adj, 4),
        "se_adjusted": round(se_adj, 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "is_truncated": raw_adj < 0.0,
    }


def fit_clustered_gee_model(
    df: pd.DataFrame,
    formula: str = "is_correct ~ C(condition, Treatment(reference='A_EN'))",
    cluster_col: str = "semantic_id",
) -> dict[str, Any]:
    """Fit a GEE logistic regression with exchangeable correlation structure."""
    model = smf.gee(
        formula,
        groups=cluster_col,
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit()

    return {
        "params": {k: float(v) for k, v in model.params.items()},
        "bse": {k: float(v) for k, v in model.bse.items()},
        "pvalues": {k: float(v) for k, v in model.pvalues.items()},
        "num_clusters": int(df[cluster_col].nunique()),
    }


def audit_step_down_holm_bonferroni(
    labeled_p_values: list[tuple[str, float]],
    alpha: float = 0.05,
) -> list[dict[str, Any]]:
    """Step-down Holm-Bonferroni correction over labeled hypothesis tests."""
    sorted_tests = sorted(labeled_p_values, key=lambda x: x[1])
    m = len(sorted_tests)
    results = []

    for rank, (name, p_val) in enumerate(sorted_tests, start=1):
        threshold = alpha / (m - rank + 1)
        is_sig = p_val <= threshold
        results.append({
            "name": name,
            "rank": rank,
            "raw_p": float(p_val),
            "threshold": float(threshold),
            "significant": bool(is_sig),
        })

    return results
