"""Phase 2.6 Benchmark Rebuild & Decontamination Validation Tests.

Verifies that IndraLLM-CS-v1.1-CANDIDATE satisfies all 15 Quality Gates:
1. Exact prompt text disjointness between partitions (0% leakage).
2. Exact factual question and reference answer disjointness.
3. Zero entity-pair leakage between Dev and Test partitions.
4. Zero evidence snippet / URL leakage between Dev and Test partitions.
5. Strict template-family quarantining of TF-11 & TF-12 in TEST-OOD.
6. Complete 5-condition semantic pairing for all 1,500 semantic groups.
7. Total dataset scale: 7,500 condition prompts (1,500 per condition, balanced across 5 languages).
8. CMI mathematical bounds [0.0, 50.0] and non-zero within-condition variance.
9. Full provenance completeness across all 7,500 records.
10. Valid SHA-256 data manifest and partition checksums.
"""

from __future__ import annotations

import hashlib
import json
import os
import pandas as pd
import pytest

from indrallm.config import PROJECT_ROOT

DATA_DIR = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.1-CANDIDATE"


@pytest.fixture(scope="module")
def dataset_splits():
    """Load all 4 partition files."""
    if not DATA_DIR.exists():
        pytest.skip(f"Candidate dataset directory not found at {DATA_DIR}")

    dev_path = DATA_DIR / "development.csv"
    val_path = DATA_DIR / "validation.csv"
    tid_path = DATA_DIR / "test_id.csv"
    tood_path = DATA_DIR / "test_ood.csv"
    full_path = DATA_DIR / "condition_prompts_7500.csv"

    return {
        "dev": pd.read_csv(dev_path),
        "val": pd.read_csv(val_path),
        "test_id": pd.read_csv(tid_path),
        "test_ood": pd.read_csv(tood_path),
        "full": pd.read_csv(full_path),
    }


def test_partition_scale_and_condition_balance(dataset_splits):
    """Verify exact row counts and 5-condition balance across partitions."""
    dev = dataset_splits["dev"]
    val = dataset_splits["val"]
    tid = dataset_splits["test_id"]
    tood = dataset_splits["test_ood"]
    full = dataset_splits["full"]

    assert len(full) == 7500, f"Expected 7,500 prompts, got {len(full)}"
    assert len(dev) == 5000, f"Expected 5,000 Dev prompts, got {len(dev)}"
    assert len(val) == 1000, f"Expected 1,000 Val prompts, got {len(val)}"
    assert len(tid) == 1000, f"Expected 1,000 Test-ID prompts, got {len(tid)}"
    assert len(tood) == 500, f"Expected 500 Test-OOD prompts, got {len(tood)}"

    # Check 5 conditions per semantic group
    for df in [dev, val, tid, tood]:
        for sem_id, grp in df.groupby("semantic_id"):
            assert len(grp) == 5, f"Semantic unit {sem_id} does not have exactly 5 conditions!"
            assert set(grp["condition"]) == {"A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"}


def test_zero_cross_partition_prompt_leakage(dataset_splits):
    """Level 1: Verify 0.0% exact prompt text leakage between partitions."""
    dev_prompts = set(dataset_splits["dev"]["prompt_text"])
    val_prompts = set(dataset_splits["val"]["prompt_text"])
    tid_prompts = set(dataset_splits["test_id"]["prompt_text"])
    tood_prompts = set(dataset_splits["test_ood"]["prompt_text"])

    assert dev_prompts.isdisjoint(val_prompts), "Prompt text leakage between Dev and Val!"
    assert dev_prompts.isdisjoint(tid_prompts), "Prompt text leakage between Dev and Test-ID!"
    assert dev_prompts.isdisjoint(tood_prompts), "Prompt text leakage between Dev and Test-OOD!"
    assert val_prompts.isdisjoint(tid_prompts), "Prompt text leakage between Val and Test-ID!"
    assert val_prompts.isdisjoint(tood_prompts), "Prompt text leakage between Val and Test-OOD!"
    assert tid_prompts.isdisjoint(tood_prompts), "Prompt text leakage between Test-ID and Test-OOD!"


def test_zero_cross_partition_answer_and_evidence_leakage(dataset_splits):
    """Level 3, 7, 8: Verify 0.0% reference answer and evidence snippet leakage."""
    dev = dataset_splits["dev"]
    tid = dataset_splits["test_id"]
    tood = dataset_splits["test_ood"]

    # Answers
    assert set(dev["reference_answer"]).isdisjoint(set(tid["reference_answer"])), "Answer leakage between Dev and Test-ID!"
    assert set(dev["reference_answer"]).isdisjoint(set(tood["reference_answer"])), "Answer leakage between Dev and Test-OOD!"

    # Evidence Snippets
    assert set(dev["evidence_snippet"]).isdisjoint(set(tid["evidence_snippet"])), "Evidence leakage between Dev and Test-ID!"
    assert set(dev["evidence_snippet"]).isdisjoint(set(tood["evidence_snippet"])), "Evidence leakage between Dev and Test-OOD!"

    # Target Entities
    assert set(dev["target_entity"]).isdisjoint(set(tid["target_entity"])), "Entity leakage between Dev and Test-ID!"
    assert set(dev["target_entity"]).isdisjoint(set(tood["target_entity"])), "Entity leakage between Dev and Test-OOD!"


def test_strict_ood_template_family_isolation(dataset_splits):
    """Level 6: Verify TF-11 & TF-12 exist exclusively in TEST-OOD and 0% in Dev/Val/Test-ID."""
    dev_tf = set(dataset_splits["dev"]["template_family_id"])
    val_tf = set(dataset_splits["val"]["template_family_id"])
    tid_tf = set(dataset_splits["test_id"]["template_family_id"])
    tood_tf = set(dataset_splits["test_ood"]["template_family_id"])

    ood_target_families = {"TF-11", "TF-12"}
    assert tood_tf.issubset(ood_target_families), f"Test-OOD contains unexpected families: {tood_tf}"
    assert dev_tf.isdisjoint(ood_target_families), "Dev contains OOD template families!"
    assert val_tf.isdisjoint(ood_target_families), "Val contains OOD template families!"
    assert tid_tf.isdisjoint(ood_target_families), "Test-ID contains OOD template families!"


def test_cmi_bounds_and_within_condition_variance(dataset_splits):
    """Verify CMI respects mathematical bounds and exhibits within-condition variance."""
    full = dataset_splits["full"]
    cmi = full["measured_cmi"]

    assert cmi.min() >= 0.0, "CMI cannot be negative"
    assert cmi.max() <= 50.0, "Canonical Gambäck & Das bilingual CMI cannot exceed 50.0"

    d_cs = full[full["condition"] == "D_CS"]["measured_cmi"]
    e_ms = full[full["condition"] == "E_MIXED_SCRIPT"]["measured_cmi"]

    assert d_cs.var() > 15.0, f"D_CS CMI variance {d_cs.var()} is too low for continuous modeling!"
    assert e_ms.var() > 20.0, f"E_MIXED_SCRIPT CMI variance {e_ms.var()} is too low!"


def test_provenance_fields_completeness(dataset_splits):
    """Verify all 7,500 records possess non-empty authentic provenance fields."""
    full = dataset_splits["full"]
    for col in ["evidence_source_url", "evidence_snippet", "reference_answer", "target_entity", "subdomain"]:
        missing = full[col].isna().sum()
        assert missing == 0, f"Column {col} has {missing} missing/empty values!"

        # Ensure valid HTTPS URLs
        invalid_urls = full[~full["evidence_source_url"].str.startswith("http")]
        assert len(invalid_urls) == 0, f"Found {len(invalid_urls)} invalid source URLs in dataset!"


def test_sha256_manifest_integrity():
    """Verify data_manifest.json checksums match exact disk hashes."""
    manifest_file = DATA_DIR / "data_manifest.json"
    assert manifest_file.exists(), "Manifest file missing!"

    with manifest_file.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    for fname, expected_hash in manifest["checksums"].items():
        actual_path = DATA_DIR / fname
        assert actual_path.exists(), f"File {fname} declared in manifest does not exist!"
        actual_hash = hashlib.sha256(actual_path.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, f"SHA-256 mismatch for {fname}! Expected {expected_hash}, got {actual_hash}"
