"""Phase 4.5 Independent Verification Script: Original 20-Topic Reproduction."""

import json
from pathlib import Path
import pandas as pd
import numpy as np
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
    
    # Filter authentic core for Qwen
    auth_qwen = df[(df["model"] == "qwen/qwen3.8-27b") & (df["is_authentic"] == True)].copy()
    auth_qwen["base_topic_id"] = auth_qwen["target_entity"]
    
    print(f"Authentic Qwen rows: {len(auth_qwen)}")
    print(f"Unique base topics: {auth_qwen['base_topic_id'].nunique()}")
    print(f"Unique semantic IDs: {auth_qwen['semantic_id'].nunique()}")
    
    # Accuracies
    accs = auth_qwen.groupby("condition")["is_correct"].mean() * 100
    print("Condition Accuracies:")
    print(accs)
    
    # 1. MixedLM for Variance Components & ICC
    m_mixed = smf.mixedlm(
        "is_correct ~ C(condition, Treatment(reference='A_EN'))",
        data=auth_qwen,
        groups="base_topic_id"
    ).fit()
    
    var_topic = float(m_mixed.cov_re.iloc[0, 0])
    var_resid = float(m_mixed.scale)
    icc = var_topic / (var_topic + var_resid)
    m = 25
    deff = 1.0 + (m - 1) * icc
    n_eff = len(auth_qwen) / deff
    
    print(f"\nVariance Components:")
    print(f"  Var(Topic): {var_topic:.4f}")
    print(f"  Var(Residual): {var_resid:.4f}")
    print(f"  ICC: {icc:.4f}")
    print(f"  DEFF (m=25): {deff:.4f}")
    print(f"  N_eff: {n_eff:.2f}")
    
    # 2. Level 3 GEE
    m_l3 = smf.gee(
        "is_correct ~ C(condition, Treatment(reference='A_EN'))",
        groups="base_topic_id",
        data=auth_qwen,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable()
    ).fit()
    
    print("\nLevel 3 GEE Model Results:")
    for term in m_l3.params.index:
        b = m_l3.params[term]
        se = m_l3.bse[term]
        p = m_l3.pvalues[term]
        print(f"  {term}: beta={b:.4f}, se={se:.4f}, p={p:.4f}")
        
    out = {
        "n_prompts": len(auth_qwen),
        "n_topics": int(auth_qwen["base_topic_id"].nunique()),
        "var_topic": round(var_topic, 4),
        "var_resid": round(var_resid, 4),
        "icc": round(icc, 4),
        "deff": round(deff, 4),
        "n_eff": round(n_eff, 2),
        "d_cs_pvalue_l3": round(float(m_l3.pvalues["C(condition, Treatment(reference='A_EN'))[T.D_CS]"]), 4),
        "d_cs_beta_l3": round(float(m_l3.params["C(condition, Treatment(reference='A_EN'))[T.D_CS]"]), 4),
        "d_cs_se_l3": round(float(m_l3.bse["C(condition, Treatment(reference='A_EN'))[T.D_CS]"]), 4),
    }
    with open(PROJECT_ROOT / "results" / "phase4" / "phase4_5_original_reproduction.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nReproduction output saved to results/phase4/phase4_5_original_reproduction.json")

if __name__ == "__main__":
    main()
