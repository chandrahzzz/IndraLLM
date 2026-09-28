"""Unit tests for semantic pairing and condition prompt data integrity."""

import tempfile
from pathlib import Path
import pytest

from indrallm.collection.semantic_paired import (
    SemanticQuestion,
    save_semantic_dataset,
    load_semantic_dataset,
    flatten_condition_prompts,
)


@pytest.fixture
def sample_semantic_question():
    sq = SemanticQuestion(
        semantic_id="S000001",
        domain="governance",
        subdomain="welfare",
        difficulty_level=1,
        canonical_fact="PM-KISAN provides 6000 rupees annually.",
        reference_answer="₹6,000 per year.",
        evidence_snippet="Under PM-KISAN, ₹6,000 per year is given in 3 installments.",
        evidence_source_url="https://pmkisan.gov.in",
        evidence_source_type="govt_portal",
        language="hi",
    )
    sq.add_condition("A_EN", "latin", "How much financial support is given under PM-KISAN?")
    sq.add_condition("B_NATIVE", "devanagari", "पीएम-किसान योजना के तहत कितनी सहायता मिलती है?")
    sq.add_condition("C_ROMAN", "latin", "PM-Kisan yojana ke antargat kitni sahayata milti hai?")
    sq.add_condition("D_CS", "latin", "PM-Kisan scheme me kitna financial support milta hai?")
    sq.add_condition("E_MIXED_SCRIPT", "mixed", "PM-Kisan scheme में कितना financial support मिलता है?")
    return sq


def test_semantic_question_completeness(sample_semantic_question):
    assert sample_semantic_question.is_complete()
    assert len(sample_semantic_question.prompts) == 5
    assert "A_EN" in sample_semantic_question.prompts
    assert "E_MIXED_SCRIPT" in sample_semantic_question.prompts


def test_serialization_roundtrip(sample_semantic_question):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test_semantic.jsonl"
        save_semantic_dataset([sample_semantic_question], tmp_path)
        loaded = load_semantic_dataset(tmp_path)
        assert len(loaded) == 1
        sq_loaded = loaded[0]
        assert sq_loaded.semantic_id == "S000001"
        assert sq_loaded.is_complete()
        assert sq_loaded.prompts["A_EN"].prompt_text == sample_semantic_question.prompts["A_EN"].prompt_text


def test_flatten_prompts(sample_semantic_question):
    flattened = flatten_condition_prompts([sample_semantic_question])
    assert len(flattened) == 5
    conditions = {row["condition"] for row in flattened}
    assert conditions == {"A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"}
