"""Unit tests for Gamback & Das (2014) CMI calculation and script transitions."""

import pytest
from indrallm.collection.cmi import compute_cmi, count_script_transitions


def test_monolingual_english_cmi():
    res = compute_cmi("What is the capital of India?", expected_lang="en")
    assert res["cmi"] == 0.0
    assert res["cmi_level"] == "low"
    assert res["script_transitions"] == 0


def test_code_mixed_tamil_cmi():
    text = "Tamil Nadu oda capital enna?"
    res = compute_cmi(text, expected_lang="ta")
    assert res["total_tokens"] > 0
    assert res["cmi"] > 0.0
    assert res["indic_tokens"] >= 1
    assert res["english_tokens"] >= 1


def test_mixed_script_transitions():
    text = "Tamil Nadu-வின் capital city என்ன?"
    res = compute_cmi(text, expected_lang="ta")
    assert res["script_transitions"] >= 2
    assert res["cmi"] > 20.0


def test_script_transitions_counter():
    # Only latin -> 0 transitions
    assert count_script_transitions("This is purely english text.") == 0
    # Latin -> Devanagari -> Latin
    assert count_script_transitions("Hello नमस्ते world") == 2


def test_empty_string_cmi():
    res = compute_cmi("")
    assert res["cmi"] == 0.0
    assert res["total_tokens"] == 0
