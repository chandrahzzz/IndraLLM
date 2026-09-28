"""Data structures and validation pipelines for Semantically Paired Benchmark Tuples.

Implements the 5-condition semantic group architecture:
For every canonical fact S_i:
    Condition A: English (A_EN)
    Condition B: Native-script Monolingual (B_NATIVE)
    Condition C: Romanized Monolingual (C_ROMAN)
    Condition D: Natural Code-Switching (D_CS)
    Condition E: Mixed-Script Code-Switching (E_MIXED_SCRIPT)

Ensures zero semantic leakage, complete condition coverage, and verifiable evidence sources.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from indrallm.collection.cmi import compute_cmi


@dataclass
class ConditionPrompt:
    prompt_id: str
    semantic_id: str
    language: str
    condition: str  # 'A_EN', 'B_NATIVE', 'C_ROMAN', 'D_CS', 'E_MIXED_SCRIPT'
    script: str     # 'latin', 'devanagari', 'tamil', 'telugu', 'bengali', 'kannada', 'mixed'
    prompt_text: str
    measured_cmi: float
    cmi_level: str
    token_count: int
    script_transitions: int
    validation_status: str = "unverified"  # 'unverified', 'human_validated', 'rejected'


@dataclass
class SemanticQuestion:
    semantic_id: str
    domain: str
    subdomain: str
    difficulty_level: int
    canonical_fact: str
    reference_answer: str
    evidence_snippet: str
    evidence_source_url: str
    evidence_source_type: str
    language: str
    prompts: dict[str, ConditionPrompt] = field(default_factory=dict)

    def add_condition(
        self,
        condition: str,
        script: str,
        prompt_text: str,
        validation_status: str = "unverified",
    ) -> ConditionPrompt:
        """Add a condition prompt, automatically measuring CMI and transitions."""
        analysis = compute_cmi(prompt_text, expected_lang=self.language)
        pid = f"{self.semantic_id}_{condition}_{self.language}"
        cp = ConditionPrompt(
            prompt_id=pid,
            semantic_id=self.semantic_id,
            language=self.language,
            condition=condition,
            script=script,
            prompt_text=prompt_text,
            measured_cmi=analysis["cmi"],
            cmi_level=analysis["cmi_level"],
            token_count=analysis["total_tokens"],
            script_transitions=analysis["script_transitions"],
            validation_status=validation_status,
        )
        self.prompts[condition] = cp
        return cp

    def is_complete(self) -> bool:
        """Check if all 5 canonical conditions (A through E) are populated."""
        required = {"A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"}
        return required.issubset(self.prompts.keys())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["prompts"] = {k: asdict(v) for k, v in self.prompts.items()}
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SemanticQuestion:
        prompts_raw = data.pop("prompts", {})
        sq = cls(**data)
        for k, pdata in prompts_raw.items():
            sq.prompts[k] = ConditionPrompt(**pdata)
        return sq


def save_semantic_dataset(questions: list[SemanticQuestion], out_path: Path) -> None:
    """Save semantic questions as UTF-8 JSONL."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q.to_dict(), ensure_ascii=False) + "\n")


def load_semantic_dataset(in_path: Path) -> list[SemanticQuestion]:
    """Load semantic questions from UTF-8 JSONL."""
    if not in_path.exists():
        return []
    questions = []
    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questions.append(SemanticQuestion.from_dict(json.loads(line)))
    return questions


def flatten_condition_prompts(questions: list[SemanticQuestion]) -> list[dict[str, Any]]:
    """Flatten semantic dataset into rows suitable for generation or tabular evaluation."""
    rows = []
    for q in questions:
        for cond, p in q.prompts.items():
            rows.append({
                "prompt_id": p.prompt_id,
                "semantic_id": q.semantic_id,
                "language": q.language,
                "domain": q.domain,
                "subdomain": q.subdomain,
                "difficulty_level": q.difficulty_level,
                "condition": p.condition,
                "script": p.script,
                "prompt_text": p.prompt_text,
                "reference_answer": q.reference_answer,
                "evidence_snippet": q.evidence_snippet,
                "evidence_source_url": q.evidence_source_url,
                "evidence_source_type": q.evidence_source_type,
                "measured_cmi": p.measured_cmi,
                "cmi_level": p.cmi_level,
                "token_count": p.token_count,
                "script_transitions": p.script_transitions,
                "validation_status": p.validation_status,
            })
    return rows


def validate_splits(train_sq: list[SemanticQuestion], val_sq: list[SemanticQuestion], test_sq: list[SemanticQuestion]) -> dict[str, Any]:
    """Verify zero semantic leakage across train, val, and test splits."""
    train_ids = {q.semantic_id for q in train_sq}
    val_ids = {q.semantic_id for q in val_sq}
    test_ids = {q.semantic_id for q in test_sq}

    overlap_train_val = train_ids.intersection(val_ids)
    overlap_train_test = train_ids.intersection(test_ids)
    overlap_val_test = val_ids.intersection(test_ids)

    valid = len(overlap_train_val) == 0 and len(overlap_train_test) == 0 and len(overlap_val_test) == 0

    return {
        "valid": valid,
        "n_train": len(train_ids),
        "n_val": len(val_ids),
        "n_test": len(test_ids),
        "overlap_train_val": list(overlap_train_val),
        "overlap_train_test": list(overlap_train_test),
        "overlap_val_test": list(overlap_val_test),
    }
