"""Unit tests for statistical testing suite and inter-annotator agreement metrics."""

import numpy as np
import pytest

from indrallm.evaluation.statistical_testing import (
    mcnemar_test,
    bootstrap_ci_proportion,
    bootstrap_ci_diff,
    holm_bonferroni_correction,
    cohens_kappa,
    fleiss_kappa,
    krippendorff_alpha_nominal,
)


def test_mcnemar_test_identical_models():
    # If control and treatment make identical predictions, p-value is 1.0
    y_true = [1, 1, 0, 0, 1, 0, 1, 1]
    y_ctrl = [1, 1, 0, 0, 1, 0, 1, 1]
    y_treat = [1, 1, 0, 0, 1, 0, 1, 1]
    res = mcnemar_test(y_true, y_ctrl, y_treat)
    assert res["discordant_count"] == 0
    assert res["p_value"] == 1.0


def test_mcnemar_test_discordant():
    y_true = [1] * 20
    # Control gets 15 correct, Treatment gets 5 correct
    y_ctrl = [1] * 15 + [0] * 5
    y_treat = [1] * 5 + [0] * 15
    res = mcnemar_test(y_true, y_ctrl, y_treat)
    assert res["discordant_count"] == 10
    assert res["p_value"] < 0.05


def test_bootstrap_ci_bounds():
    arr = [1] * 90 + [0] * 10
    res = bootstrap_ci_proportion(arr, n_bootstraps=500, confidence_level=0.95, random_seed=42)
    assert 0.80 <= res["ci_lower"] <= 0.90
    assert 0.90 <= res["ci_upper"] <= 1.00
    assert res["ci_lower"] <= res["mean"] <= res["ci_upper"]


def test_holm_bonferroni():
    raw_p = [0.005, 0.04, 0.15]
    res = holm_bonferroni_correction(raw_p, alpha=0.05)
    # Ranked: 0.005 (rank 1, threshold 0.05/3 = 0.0167 -> sig)
    #         0.04 (rank 2, threshold 0.05/2 = 0.025 -> non-sig)
    #         0.15 (rank 3, non-sig)
    assert res[0]["significant"] is True
    assert res[1]["significant"] is False
    assert res[2]["significant"] is False


def test_cohens_kappa_perfect_agreement():
    r1 = [1, 0, 1, 1, 0, 0, 1]
    r2 = [1, 0, 1, 1, 0, 0, 1]
    assert cohens_kappa(r1, r2) == 1.0


def test_fleiss_kappa_known():
    # 3 items, 3 raters, perfect agreement
    matrix = np.array([
        [3, 0],
        [0, 3],
        [3, 0],
    ])
    assert fleiss_kappa(matrix) == 1.0


def test_krippendorff_alpha_nominal_perfect():
    matrix = np.array([
        [3, 0],
        [0, 3],
        [3, 0],
    ])
    assert krippendorff_alpha_nominal(matrix) == 1.0
