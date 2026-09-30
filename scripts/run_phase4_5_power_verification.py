"""Phase 4.5 Independent Verification Script: Power & Effective N Reproduction."""

import math
from scipy import stats
import json
from pathlib import Path

def main():
    icc = 0.2663
    m_full = 25
    deff_full = 1.0 + (m_full - 1) * icc
    
    # Original 20 topics
    n_20 = 20 * 25 # 500
    n_eff_20 = n_20 / deff_full
    
    # Expanded 45 topics
    n_45 = 45 * 25 # 1125
    n_eff_45 = n_45 / deff_full

    # Expanded 50 topics
    n_50 = 50 * 25 # 1250
    n_eff_50 = n_50 / deff_full

    # Power calculations for condition contrasts (m_cond = 5)
    m_cond = 5
    deff_cond = 1.0 + (m_cond - 1) * icc
    z_alpha = 1.96 # alpha = 0.05 two-sided
    z_beta_80 = 0.8416 # 80% power
    delta_obs = 0.21 # 64% vs 43%
    var_p = 2 * 0.40 * 0.60 # approximate Bernoulli variance under contrast

    # Power for 20 topics
    se_20 = math.sqrt(var_p * deff_cond / (20 * 5))
    z_20 = (delta_obs - z_alpha * se_20) / se_20
    power_20 = stats.norm.cdf(z_20)
    mde_20 = (z_alpha + z_beta_80) * se_20

    # Power for 45 topics
    se_45 = math.sqrt(var_p * deff_cond / (45 * 5))
    z_45 = (delta_obs - z_alpha * se_45) / se_45
    power_45 = stats.norm.cdf(z_45)
    mde_45 = (z_alpha + z_beta_80) * se_45

    # Power for 50 topics
    se_50 = math.sqrt(var_p * deff_cond / (50 * 5))
    z_50 = (delta_obs - z_alpha * se_50) / se_50
    power_50 = stats.norm.cdf(z_50)
    mde_50 = (z_alpha + z_beta_80) * se_50

    results = {
        "icc": round(icc, 4),
        "deff_full_25": round(deff_full, 4),
        "deff_cond_5": round(deff_cond, 4),
        "topics_20": {
            "n_prompts": n_20,
            "n_eff": round(n_eff_20, 2),
            "se_diff": round(se_20, 4),
            "power_pct": round(power_20 * 100, 2),
            "mde_pct": round(mde_20 * 100, 2)
        },
        "topics_45": {
            "n_prompts": n_45,
            "n_eff": round(n_eff_45, 2),
            "se_diff": round(se_45, 4),
            "power_pct": round(power_45 * 100, 2),
            "mde_pct": round(mde_45 * 100, 2)
        },
        "topics_50": {
            "n_prompts": n_50,
            "n_eff": round(n_eff_50, 2),
            "se_diff": round(se_50, 4),
            "power_pct": round(power_50 * 100, 2),
            "mde_pct": round(mde_50 * 100, 2)
        }
    }

    out_path = Path("c:/Users/Chandrahas Reddy/MYallPROJECTS/IndraLLM/results/phase4/phase4_5_power_verification.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print("Power verification recomputed:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
