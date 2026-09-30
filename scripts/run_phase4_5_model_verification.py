"""Phase 4.5 Independent Verification Script: Model Generalization Audit."""

import json
from pathlib import Path
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path("c:/Users/Chandrahas Reddy/MYallPROJECTS/IndraLLM")
PREDICTIONS_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"

def main():
    records = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    df = pd.DataFrame(records)
    df["is_correct"] = (df["judge_label"] == 0).astype(int)
    auth = df[df["is_authentic"] == True].copy()

    qwen_acc = auth[auth["model"] == "qwen/qwen3.8-27b"].groupby("condition")["is_correct"].mean() * 100
    allam_acc = auth[auth["model"] == "allam-2-7b"].groupby("condition")["is_correct"].mean() * 100

    comp_df = pd.DataFrame({"qwen": qwen_acc, "allam": allam_acc})
    comp_df["rank_qwen"] = comp_df["qwen"].rank(ascending=False)
    comp_df["rank_allam"] = comp_df["allam"].rank(ascending=False)

    print("Model comparison across conditions:")
    print(comp_df)

    rho, p_val = stats.spearmanr(comp_df["qwen"], comp_df["allam"])
    print(f"\nSpearman rho: {rho:.4f}")
    print(f"Spearman p-value: {p_val:.6f}")

    out = {
        "comparison_table": comp_df.to_dict(),
        "spearman_rho": round(float(rho), 4),
        "spearman_pvalue": round(float(p_val), 6)
    }
    with open(PROJECT_ROOT / "results" / "phase4" / "phase4_5_model_reproduction.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Model reproduction saved to results/phase4/phase4_5_model_reproduction.json")

if __name__ == "__main__":
    main()
