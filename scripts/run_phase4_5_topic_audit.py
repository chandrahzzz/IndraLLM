"""Phase 4.5 Independent Verification Script: Topic Independence & Overlap Audit."""

import json
from pathlib import Path
import pandas as pd
import re

PROJECT_ROOT = Path("c:/Users/Chandrahas Reddy/MYallPROJECTS/IndraLLM")
CANDIDATE_DIR = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.1-CANDIDATE"
PILOT_DIR = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.2-PILOT"

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())

def get_word_ngrams(text: str, n: int = 3) -> set[str]:
    words = normalize_text(text).split()
    if len(words) < n:
        return set([" ".join(words)])
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}

def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    return len(set_a.intersection(set_b)) / len(set_a.union(set_b))

def main():
    # Load candidate propositions (AUTH-001 to AUTH-020)
    # They are in TEST-ID / TEST-OOD or full candidate dataset
    # Let's inspect candidate files
    print("Checking Candidate Dataset...")
    candidate_files = list(CANDIDATE_DIR.glob("*.csv")) + list(CANDIDATE_DIR.glob("*.jsonl"))
    print(f"Candidate files: {[f.name for f in candidate_files]}")

    # Load pilot propositions (AUTH-021 to AUTH-045)
    pilot_props_path = PILOT_DIR / "pilot_propositions_25.jsonl"
    with open(pilot_props_path, "r", encoding="utf-8") as f:
        pilot_props = [json.loads(line) for line in f]
    print(f"Loaded {len(pilot_props)} pilot propositions.")

    # Load authentic core predictions to get AUTH-001 to AUTH-020 prompts/entities/acts
    preds_path = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"
    auth_preds = []
    with open(preds_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("is_authentic") and rec.get("model") == "qwen/qwen3.8-27b":
                auth_preds.append(rec)
    auth_df = pd.DataFrame(auth_preds)
    print(f"Loaded {len(auth_df)} authentic core records for Qwen.")

    # Distinct existing acts/entities in authentic core
    existing_entities = set(auth_df["target_entity"].unique())
    existing_prompts = set(auth_df["prompt_text"].apply(normalize_text).unique())
    existing_answers = set(auth_df["reference_answer"].apply(normalize_text).unique())
    existing_evidence = set(auth_df["evidence_snippet"].apply(normalize_text).unique())

    print(f"Existing entities ({len(existing_entities)}): {sorted(list(existing_entities))[:5]}...")

    # Now verify Pilot Props against existing
    pilot_acts = [p["act_title"] for p in pilot_props]
    pilot_entities = [p["target_entity"] for p in pilot_props]
    pilot_facts = [p["canonical_fact"] for p in pilot_props]
    pilot_sources = [p["evidence_source_url"] for p in pilot_props]
    pilot_evidence = [p["evidence_snippet"] for p in pilot_props]

    # A. Are there 25 new propositions?
    assert len(pilot_props) == 25

    # B. Are AUTH-021 through AUTH-045 distinct?
    prop_ids = [p["proposition_id"] for p in pilot_props]
    expected_ids = [f"AUTH-{i:03d}" for i in range(21, 46)]
    assert prop_ids == expected_ids, f"ID mismatch: {prop_ids}"

    # Check internal uniqueness
    assert len(set(pilot_acts)) == 25, f"Duplicate acts: {len(set(pilot_acts))}"
    assert len(set(pilot_entities)) == 25, f"Duplicate entities: {len(set(pilot_entities))}"
    assert len(set(pilot_facts)) == 25, f"Duplicate facts: {len(set(pilot_facts))}"
    assert len(set(pilot_sources)) == 25, f"Duplicate sources: {len(set(pilot_sources))}"

    # Check external overlap with existing AUTH-001..AUTH-020
    entity_overlaps = set(pilot_entities).intersection(existing_entities)
    print(f"Entity overlaps with AUTH-001..AUTH-020: {entity_overlaps}")

    # N-gram overlap and max Jaccard similarity across evidence
    max_evidence_jaccard = 0.0
    most_similar_evidence_pair = None
    for p_ev in pilot_evidence:
        p_ngrams = get_word_ngrams(p_ev, 3)
        for e_ev in existing_evidence:
            e_ngrams = get_word_ngrams(e_ev, 3)
            jac = jaccard_similarity(p_ngrams, e_ngrams)
            if jac > max_evidence_jaccard:
                max_evidence_jaccard = jac
                most_similar_evidence_pair = (p_ev[:60], e_ev[:60])

    print(f"Max 3-gram Jaccard similarity between pilot and existing evidence: {max_evidence_jaccard:.4f}")
    if most_similar_evidence_pair:
        print(f"Most similar pair:\n  Pilot: {most_similar_evidence_pair[0]}\n  Exist: {most_similar_evidence_pair[1]}")

    # Prompt text overlap
    pilot_prompts_df = pd.read_csv(PILOT_DIR / "pilot_prompts_125.csv")
    pilot_prompt_texts = set(pilot_prompts_df["prompt_text"].apply(normalize_text).unique())
    prompt_exact_overlaps = pilot_prompt_texts.intersection(existing_prompts)
    print(f"Prompt exact overlaps: {len(prompt_exact_overlaps)}")

    max_prompt_jaccard = 0.0
    most_similar_prompt_pair = None
    for p_text in pilot_prompt_texts:
        p_ngrams = get_word_ngrams(p_text, 3)
        for e_text in existing_prompts:
            e_ngrams = get_word_ngrams(e_text, 3)
            jac = jaccard_similarity(p_ngrams, e_ngrams)
            if jac > max_prompt_jaccard:
                max_prompt_jaccard = jac
                most_similar_prompt_pair = (p_text[:60], e_text[:60])

    print(f"Max 3-gram Jaccard similarity between pilot and existing prompts: {max_prompt_jaccard:.4f}")
    if most_similar_prompt_pair:
        print(f"Most similar pair:\n  Pilot: {most_similar_prompt_pair[0]}\n  Exist: {most_similar_prompt_pair[1]}")

    # Output report data
    audit_data = {
        "pilot_propositions_count": len(pilot_props),
        "pilot_prompts_count": len(pilot_prompts_df),
        "prop_ids_range": [prop_ids[0], prop_ids[-1]],
        "unique_acts_count": len(set(pilot_acts)),
        "unique_entities_count": len(set(pilot_entities)),
        "unique_facts_count": len(set(pilot_facts)),
        "unique_sources_count": len(set(pilot_sources)),
        "entity_overlaps_count": len(entity_overlaps),
        "prompt_exact_overlaps_count": len(prompt_exact_overlaps),
        "max_evidence_3gram_jaccard": round(max_evidence_jaccard, 4),
        "max_prompt_3gram_jaccard": round(max_prompt_jaccard, 4),
        "pilot_acts_list": pilot_acts,
    }
    
    with open(PROJECT_ROOT / "results" / "phase4" / "phase4_5_topic_audit.json", "w") as f:
        json.dump(audit_data, f, indent=2)
    print("Topic independence audit completed successfully!")

if __name__ == "__main__":
    main()
