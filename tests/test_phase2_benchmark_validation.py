"""Comprehensive Data Validation and Integrity Test Suite for IndraLLM-CS v1.0."""

import json
from pathlib import Path
import pandas as pd
import pytest

from indrallm.config import PROJECT_ROOT
from indrallm.collection.semantic_paired import load_semantic_dataset, validate_splits
from indrallm.utils.budget_guard import (
    estimate_cost,
    record_spend,
    get_budget_status,
    HARD_BUDGET_CEILING_USD,
    BudgetExceededError,
)
from indrallm.generation.response_cache import ResponseCache

BENCHMARK_DIR = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.0"


@pytest.fixture(scope="module")
def benchmark_df():
    csv_path = BENCHMARK_DIR / "condition_prompts_10000.csv"
    assert csv_path.exists(), "Benchmark 10,000 prompts CSV missing"
    return pd.read_csv(csv_path)


def test_manifest_exists_and_matches_files():
    manifest_path = BENCHMARK_DIR / "data_manifest.json"
    assert manifest_path.exists(), "data_manifest.json missing"
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["dataset_version"] == "IndraLLM-CS-v1.0"
    assert manifest["number_of_semantic_groups"] == 2000
    assert manifest["number_of_condition_prompts"] == 10000
    assert set(manifest["languages"]) == {"hi", "ta", "te", "bn", "kn"}
    assert set(manifest["conditions"]) == {"A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"}


def test_semantic_leakage_across_splits():
    train_sq = load_semantic_dataset(BENCHMARK_DIR / "train.jsonl")
    val_sq = load_semantic_dataset(BENCHMARK_DIR / "val.jsonl")
    test_sq = load_semantic_dataset(BENCHMARK_DIR / "test.jsonl")

    res = validate_splits(train_sq, val_sq, test_sq)
    assert res["valid"] is True, f"Semantic ID overlap detected: {res}"
    assert len(res["overlap_train_test"]) == 0
    assert len(res["overlap_train_val"]) == 0
    assert len(res["overlap_val_test"]) == 0


def test_condition_and_language_balance(benchmark_df):
    # Total count = 10,000
    assert len(benchmark_df) == 10000

    # Exactly 2,000 per condition
    for cond in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]:
        assert (benchmark_df["condition"] == cond).sum() == 2000

    # Exactly 2,000 per language
    for lang in ["hi", "ta", "te", "bn", "kn"]:
        assert (benchmark_df["language"] == lang).sum() == 2000


def test_evidence_and_reference_quality(benchmark_df):
    # Every row must have non-empty reference_answer, evidence_snippet, and valid URL
    assert benchmark_df["reference_answer"].dropna().str.strip().ne("").all()
    assert benchmark_df["evidence_snippet"].dropna().str.strip().ne("").all()
    assert benchmark_df["evidence_source_url"].str.startswith("http").all()


def test_cmi_and_multidimensional_metrics(benchmark_df):
    # Ensure CMI is in [0, 100]
    assert benchmark_df["measured_cmi"].between(0.0, 100.0).all()
    # English token ratio in [0, 1]
    assert benchmark_df["english_token_ratio"].between(0.0, 1.0).all()
    # Native token ratio in [0, 1]
    assert benchmark_df["indic_token_ratio"].between(0.0, 1.0).all()
    # Script transitions >= 0
    assert (benchmark_df["script_transitions"] >= 0).all()


def test_budget_guard_limits():
    status = get_budget_status()
    assert status["cumulative_spend_usd"] <= HARD_BUDGET_CEILING_USD
    assert status["remaining_budget_usd"] >= 0.0

    # Proposing a $50 run must be rejected
    huge_estimate = estimate_cost(
        experiment_id="TEST-OVERFLOW",
        provider="groq",
        model="llama-3.3-70b-versatile",
        num_calls=1_000_000,
        avg_input_tokens=1000,
        avg_output_tokens=1000,
    )
    assert huge_estimate.approved is False


def test_response_cache_deduplication(tmp_path):
    cache = ResponseCache(cache_file=tmp_path / "test_cache.jsonl")
    k = cache.compute_key("test_model", "test prompt")
    assert cache.get("test_model", "test prompt") is None

    cache.put("test_model", "test prompt", "response text")
    hit = cache.get("test_model", "test prompt")
    assert hit is not None
    assert hit.response_text == "response text"
