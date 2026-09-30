"""Phase 4.5 Independent Verification Script: Mechanism & Mediation Audit."""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

PROJECT_ROOT = Path("c:/Users/Chandrahas Reddy/MYallPROJECTS/IndraLLM")
PREDICTIONS_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"
CANDIDATE_DIR = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.1-CANDIDATE"

def main():
    records = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    df = pd.DataFrame(records)
    df["is_correct"] = (df["judge_label"] == 0).astype(int)

    # Load metadata for chars_per_token and script transitions
    t_id = pd.read_csv(CANDIDATE_DIR / "test_id.csv")
    t_ood = pd.read_csv(CANDIDATE_DIR / "test_ood.csv")
    meta = pd.concat([t_id, t_ood], ignore_index=True)
    cols = ["prompt_id", "measured_cmi", "token_count", "script_transitions", "chars_per_token"]
    merged = df.merge(meta[cols], on="prompt_id", how="left")

    auth_qwen = merged[(merged["model"] == "qwen/qwen3.8-27b") & (merged["is_authentic"] == True)].copy()

    # 1. Script transitions by condition
    trans_by_cond = auth_qwen.groupby("condition")["script_transitions"].mean()
    print("Mean script transitions by condition:")
    print(trans_by_cond)
    e_trans_mean = float(trans_by_cond.get("E_MIXED_SCRIPT", 0.0))

    # 2. Chars per token by condition
    cpt_by_cond = auth_qwen.groupby("condition")["chars_per_token"].mean()
    print("\nMean chars_per_token by condition:")
    print(cpt_by_cond)

    # 3. Reasoning truncation from judge_reason / error taxonomy
    # In EXP-002, errors were classified into: Numeric drift, Truncation/Incomplete, Hallucination
    # Let's inspect judge_reason for truncation indicators
    # From Phase 3.5 Error analysis:
    # A_EN: 1/100 (1%)
    # D_CS: 6/100 (6%)
    # B_NATIVE: 19/100 (19%)
    # E_MIXED_SCRIPT: 20/100 (20%)
    print("\nVerifying mediation on contrast D_CS vs E_MIXED_SCRIPT...")
    cs_mixed = auth_qwen[auth_qwen["condition"].isin(["D_CS", "E_MIXED_SCRIPT"])].copy()
    cs_mixed["is_mixed"] = (cs_mixed["condition"] == "E_MIXED_SCRIPT").astype(int)

    # Path c (Total Effect): is_correct ~ is_mixed
    m_tot = smf.logit("is_correct ~ is_mixed", data=cs_mixed).fit(disp=False)
    beta_c = float(m_tot.params["is_mixed"])
    p_c = float(m_tot.pvalues["is_mixed"])

    # Path a (Mediator model): chars_per_token ~ is_mixed
    m_med = smf.ols("chars_per_token ~ is_mixed", data=cs_mixed).fit()
    beta_a = float(m_med.params["is_mixed"])
    se_a = float(m_med.bse["is_mixed"])
    p_a = float(m_med.pvalues["is_mixed"])

    # Path b & c' (Outcome model): is_correct ~ is_mixed + chars_per_token
    m_out = smf.logit("is_correct ~ is_mixed + chars_per_token", data=cs_mixed).fit(disp=False)
    beta_b = float(m_out.params["chars_per_token"])
    se_b = float(m_out.bse["chars_per_token"])
    p_b = float(m_out.pvalues["chars_per_token"])
    beta_c_prime = float(m_out.params["is_mixed"])
    p_c_prime = float(m_out.pvalues["is_mixed"])

    # Sobel test
    sobel_num = beta_a * beta_b
    sobel_denom = np.sqrt(beta_b**2 * se_a**2 + beta_a**2 * se_b**2)
    sobel_z = float(sobel_num / sobel_denom)
    from scipy import stats
    sobel_p = float(2 * (1 - stats.norm.cdf(abs(sobel_z))))

    print(f"Path c: beta={beta_c:.4f}, p={p_c:.4f}")
    print(f"Path a: beta={beta_a:.4f}, se={se_a:.4f}, p={p_a:.4f}")
    print(f"Path b: beta={beta_b:.4f}, se={se_b:.4f}, p={p_b:.4f}")
    print(f"Path c': beta={beta_c_prime:.4f}, p={p_c_prime:.4f}")
    print(f"Sobel test: z={sobel_z:.4f}, p={sobel_p:.4f}")

    results = {
        "e_mixed_script_mean_transitions": round(e_trans_mean, 2),
        "path_c_total": {"beta": round(beta_c, 4), "p": round(p_c, 4)},
        "path_a_mediator": {"beta": round(beta_a, 4), "se": round(se_a, 4), "p": round(p_a, 4)},
        "path_b_mediator_to_outcome": {"beta": round(beta_b, 4), "se": round(se_b, 4), "p": round(p_b, 4)},
        "path_c_prime_direct": {"beta": round(beta_c_prime, 4), "p": round(p_c_prime, 4)},
        "sobel_test": {"z": round(sobel_z, 4), "p": round(sobel_p, 4)},
    }
    with open(PROJECT_ROOT / "results" / "phase4" / "phase4_5_mechanism_reproduction.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nMechanism verification saved to results/phase4/phase4_5_mechanism_reproduction.json")

if __name__ == "__main__":
    main()
