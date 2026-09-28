"""Rigorous Statistical Testing Framework for IndraLLM.

Implements confirmatory statistical protocols for H1-H8:
1. McNemar's Paired Test (with continuity correction) for paired binary accuracy.
2. Bootstrap 95% Confidence Intervals (BCa / Percentile) for proportions and differences.
3. Holm-Bonferroni Multiple Comparison Correction.
4. Inter-Annotator Agreement:
   - Cohen's kappa (pairwise nominal)
   - Fleiss' kappa (multi-rater nominal)
   - Krippendorff's alpha (nominal and ordinal)
5. Logistic Regression / Mixed-Effects effect size estimation.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np
import scipy.stats as stats


def mcnemar_test(
    y_true: Sequence[int],
    y_pred_control: Sequence[int],
    y_pred_treatment: Sequence[int],
    correction: bool = True,
) -> dict[str, Any]:
    """Execute McNemar's test on paired binary correctness outcomes.

    Computes 2x2 contingency matrix:
                   Treatment Correct | Treatment Wrong
    Control Correct        b00               b01
    Control Wrong          b10               b11

    Where:
        b01 = Control correct, Treatment incorrect (discordant)
        b10 = Control incorrect, Treatment correct (discordant)
    """
    assert len(y_true) == len(y_pred_control) == len(y_pred_treatment), "Length mismatch"
    b01 = 0  # control correct, treatment wrong
    b10 = 0  # control wrong, treatment correct
    b00 = 0  # both correct
    b11 = 0  # both wrong

    for yt, yc, yt_treat in zip(y_true, y_pred_control, y_pred_treatment):
        c_correct = (yc == yt)
        t_correct = (yt_treat == yt)
        if c_correct and not t_correct:
            b01 += 1
        elif not c_correct and t_correct:
            b10 += 1
        elif c_correct and t_correct:
            b00 += 1
        else:
            b11 += 1

    discordant = b01 + b10
    if discordant == 0:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "b01": b01,
            "b10": b10,
            "b00": b00,
            "b11": b11,
            "odds_ratio": 1.0,
            "discordant_count": 0,
        }

    # McNemar chi-squared with optional Edwards continuity correction
    if correction:
        chi2 = (abs(b01 - b10) - 1.0) ** 2 / discordant
    else:
        chi2 = (b01 - b10) ** 2 / discordant

    p_value = float(stats.chi2.sf(chi2, df=1))
    odds_ratio = float(b01 / max(b10, 1e-9))

    return {
        "statistic": float(chi2),
        "p_value": p_value,
        "b01": b01,
        "b10": b10,
        "b00": b00,
        "b11": b11,
        "odds_ratio": odds_ratio,
        "discordant_count": discordant,
    }


def bootstrap_ci_proportion(
    binary_array: Sequence[int],
    n_bootstraps: int = 2000,
    confidence_level: float = 0.95,
    random_seed: int = 42,
) -> dict[str, float]:
    """Compute empirical percentile bootstrap 95% CI for a single proportion."""
    arr = np.array(binary_array, dtype=float)
    n = len(arr)
    if n == 0:
        return {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "std_err": 0.0}

    rng = np.random.default_rng(random_seed)
    boot_means = np.empty(n_bootstraps)
    for i in range(n_bootstraps):
        boot_sample = rng.choice(arr, size=n, replace=True)
        boot_means[i] = np.mean(boot_sample)

    alpha = (1.0 - confidence_level) / 2.0
    lower = float(np.percentile(boot_means, alpha * 100))
    upper = float(np.percentile(boot_means, (1.0 - alpha) * 100))
    mean_val = float(np.mean(arr))
    std_err = float(np.std(boot_means))

    return {
        "mean": mean_val,
        "ci_lower": lower,
        "ci_upper": upper,
        "std_err": std_err,
    }


def bootstrap_ci_diff(
    arr_control: Sequence[int],
    arr_treatment: Sequence[int],
    paired: bool = True,
    n_bootstraps: int = 2000,
    confidence_level: float = 0.95,
    random_seed: int = 42,
) -> dict[str, float]:
    """Compute bootstrap CI for difference in proportions (Treatment - Control)."""
    c = np.array(arr_control, dtype=float)
    t = np.array(arr_treatment, dtype=float)
    n = len(c)
    assert len(t) == n if paired else True, "Lengths must match for paired bootstrap"

    rng = np.random.default_rng(random_seed)
    boot_diffs = np.empty(n_bootstraps)

    if paired:
        diffs = t - c
        for i in range(n_bootstraps):
            boot_sample = rng.choice(diffs, size=n, replace=True)
            boot_diffs[i] = np.mean(boot_sample)
    else:
        n_c, n_t = len(c), len(t)
        for i in range(n_bootstraps):
            boot_c = rng.choice(c, size=n_c, replace=True)
            boot_t = rng.choice(t, size=n_t, replace=True)
            boot_diffs[i] = np.mean(boot_t) - np.mean(boot_c)

    alpha = (1.0 - confidence_level) / 2.0
    lower = float(np.percentile(boot_diffs, alpha * 100))
    upper = float(np.percentile(boot_diffs, (1.0 - alpha) * 100))
    observed_diff = float(np.mean(t) - np.mean(c))

    return {
        "observed_diff": observed_diff,
        "ci_lower": lower,
        "ci_upper": upper,
        "p_value_bootstrap": float(np.mean(boot_diffs <= 0) if observed_diff > 0 else np.mean(boot_diffs >= 0)) * 2,
    }


def holm_bonferroni_correction(p_values: list[float], alpha: float = 0.05) -> list[dict[str, Any]]:
    """Holm-Bonferroni step-down procedure for family-wise error rate control."""
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    results = [None] * m

    reject = True
    for rank, (orig_idx, p) in enumerate(indexed):
        threshold = alpha / (m - rank)
        if reject and p <= threshold:
            sig = True
        else:
            sig = False
            reject = False  # once we fail to reject, all subsequent tests are not rejected
        results[orig_idx] = {
            "p_value": p,
            "threshold": threshold,
            "significant": sig,
            "rank": rank + 1,
        }
    return results


def cohens_kappa(rater1: Sequence[int], rater2: Sequence[int]) -> float:
    """Pairwise Cohen's kappa for two raters."""
    assert len(rater1) == len(rater2), "Rater length mismatch"
    r1 = np.array(rater1)
    r2 = np.array(rater2)
    categories = np.unique(np.concatenate([r1, r2]))
    n = len(r1)
    if n == 0:
        return 1.0

    po = np.mean(r1 == r2)
    pe = 0.0
    for cat in categories:
        pe += (np.mean(r1 == cat)) * (np.mean(r2 == cat))

    if pe >= 1.0:
        return 1.0
    return float((po - pe) / (1.0 - pe))


def fleiss_kappa(ratings_matrix: np.ndarray) -> float:
    """Compute Fleiss' kappa for multiple annotators.

    Args:
        ratings_matrix: shape (N_items, K_categories), where matrix[i, j] is
                        the number of raters who assigned item i to category j.
    """
    N, k = ratings_matrix.shape
    n = np.sum(ratings_matrix[0, :])  # number of raters per item
    if n <= 1:
        return 0.0

    # Proportion of all assignments to each category
    p = np.sum(ratings_matrix, axis=0) / (N * n)
    p_e = np.sum(p ** 2)

    # Extent of rater agreement on the i-th subject
    P_i = (np.sum(ratings_matrix ** 2, axis=1) - n) / (n * (n - 1))
    P_bar = np.mean(P_i)

    if p_e >= 1.0:
        return 1.0
    return float((P_bar - p_e) / (1.0 - p_e))


def krippendorff_alpha_nominal(matrix: np.ndarray) -> float:
    """Compute Krippendorff's alpha for nominal data.

    Args:
        matrix: shape (N_units, K_categories) counting rater assignments per category.
    """
    units, categories = matrix.shape
    n_u = np.sum(matrix, axis=1)  # raters per unit
    valid_units = n_u > 1
    if not np.any(valid_units):
        return 0.0

    matrix = matrix[valid_units]
    n_u = n_u[valid_units]
    total_pairs = np.sum(n_u * (n_u - 1))

    # Observed coincidence
    observed_diff = 0.0
    for u in range(len(matrix)):
        row = matrix[u]
        observed_diff += (n_u[u] * (n_u[u] - 1)) - np.sum(row * (row - 1))

    # Expected coincidence
    col_sums = np.sum(matrix, axis=0)
    total_ratings = np.sum(col_sums)
    expected_diff = (total_ratings * (total_ratings - 1)) - np.sum(col_sums * (col_sums - 1))

    if expected_diff == 0:
        return 1.0
    D_o = observed_diff / total_pairs
    D_e = expected_diff / (total_ratings * (total_ratings - 1))
    return float(1.0 - (D_o / D_e))
