"""Phase 4.5 Independent Verification Script: Language Interaction Audit."""

import json
from pathlib import Path
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

PROJECT_ROOT = Path("c:/Users/Chandrahas Reddy/MYallPROJECTS/IndraLLM")
PREDICTIONS_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"

def main():
    records = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    df = pd.DataFrame(records)
    df["is_correct"] = (df["judge_label"] == 0).astype(int)
    auth_qwen = df[(df["model"] == "qwen/qwen3.8-27b") & (df["is_authentic"] == True)].copy()
    auth_qwen["base_topic_id"] = auth_qwen["target_entity"]

    # Language breakdown table
    lang_cond = auth_qwen.groupby(["language", "condition"])["is_correct"].agg(["count", "mean"])
    lang_cond["pct"] = (lang_cond["mean"] * 100).round(1)
    print("Language x Condition breakdown:")
    print(lang_cond[["count", "pct"]])

    # GEE with interaction terms
    formula = "is_correct ~ C(condition, Treatment(reference='A_EN')) * C(language, Treatment(reference='bn'))"
    m_int = smf.gee(
        formula,
        groups="base_topic_id",
        data=auth_qwen,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable()
    ).fit()

    int_terms = {}
    for term in m_int.params.index:
        if ":" in term:
            b = float(m_int.params[term])
            se = float(m_int.bse[term])
            p = float(m_int.pvalues[term])
            int_terms[term] = {"beta": round(b, 4), "se": round(se, 4), "p": round(p, 4)}

    print(f"\nInteraction terms count: {len(int_terms)}")
    min_p_term = min(int_terms.items(), key=lambda x: x[1]["p"])
    print(f"Minimum interaction p-value: {min_p_term}")

    out = {
        "interaction_terms": int_terms,
        "min_interaction_p": min_p_term,
        "n_terms": len(int_terms)
    }
    with open(PROJECT_ROOT / "results" / "phase4" / "phase4_5_language_reproduction.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Language verification saved to results/phase4/phase4_5_language_reproduction.json")

if __name__ == "__main__":
    main()
