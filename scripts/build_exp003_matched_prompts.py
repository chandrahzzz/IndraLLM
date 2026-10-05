"""Build matched English prompts for EXP-003 without running any API call."""

import json
from pathlib import Path

def build_matched_prompts():
    project_root = Path(".")
    pred_path = project_root / "results" / "EXP-002" / "full_predictions.jsonl"
    out_dir = project_root / "results" / "EXP-003-matched-en"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "matched_prompts_100.jsonl"

    with open(pred_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    auth_qwen = [r for r in records if r.get("is_authentic") and r.get("model") == "qwen/qwen3.8-27b"]
    a_en_records = [r for r in auth_qwen if r.get("condition") == "A_EN"]
    print(f"Total authentic A_EN rows loaded: {len(a_en_records)}")

    matched_records = []
    for r in a_en_records:
        entity = r["target_entity"]
        matched_prompt = f"What is the main rule, date or parameter regarding {entity}?"
        rec = {
            "semantic_id": r["semantic_id"],
            "prompt_id": f"{r['semantic_id']}_A_EN_MATCHED_{r['language']}",
            "language": r["language"],
            "condition": "A_EN_MATCHED",
            "partition": r["partition"],
            "is_authentic": r["is_authentic"],
            "template_family_id": "TF-MATCHED",
            "difficulty_level": r["difficulty_level"],
            "target_entity": entity,
            "old_a_en_prompt": r["prompt_text"],
            "prompt_text": matched_prompt,
            "reference_answer": r["reference_answer"],
            "evidence_snippet": r["evidence_snippet"],
        }
        matched_records.append(rec)

    with open(out_path, "w", encoding="utf-8") as f:
        for rec in matched_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Saved {len(matched_records)} matched prompts to {out_path}")
    print("\n--- FIRST 3 SAMPLE MATCHED PROMPTS ---")
    for i, r in enumerate(matched_records[:3], 1):
        print(f"[{i}] Semantic ID: {r['semantic_id']} | Language: {r['language']}")
        print(f"    Target Entity: {r['target_entity']}")
        print(f"    Old A_EN Prompt:     {r['old_a_en_prompt']}")
        print(f"    Matched Prompt Text: {r['prompt_text']}")
        print(f"    Reference Answer:    {r['reference_answer']}")
        print()

if __name__ == "__main__":
    build_matched_prompts()
