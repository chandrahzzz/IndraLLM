"""Phase 6 Comprehensive Numerical Reproduction & Verification Script.

Independently recalculates all statistics from raw artifacts:
- results/EXP-002/full_predictions.jsonl
- results/phase4/phase4_statistical_investigation.json
- data/questions/IndraLLM-CS-v1.1-CANDIDATE/
- data/questions/IndraLLM-CS-v1.2-PILOT/
"""

import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

def wilson_ci(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denominator = 1 + z**2 / n
    centre_adjusted_probability = p + z**2 / (2 * n)
    adjusted_limits = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    lower = max(0.0, (centre_adjusted_probability - adjusted_limits) / denominator)
    upper = min(1.0, (centre_adjusted_probability + adjusted_limits) / denominator)
    return round(lower * 100, 1), round(upper * 100, 1)

def main():
    root = Path(".")
    pred_path = root / "results/EXP-002/full_predictions.jsonl"
    
    print("=== LOADING RAW EXP-002 ARTIFACTS ===")
    records = []
    with open(pred_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    
    df = pd.DataFrame(records)
    print(f"Total raw predictions: {len(df)}")
    
    # 1. Authentic Core Qwen
    auth_qwen = df[(df["is_authentic"] == True) & (df["model"] == "qwen/qwen3.8-27b")].copy()
    auth_qwen["is_correct"] = (auth_qwen["judge_label"] == 0).astype(int)
    print(f"Authentic Qwen rows: {len(auth_qwen)}")
    
    # Accuracy by condition
    print("\n--- CONDITION ACCURACIES & WILSON CIS (Qwen Authentic Core) ---")
    cond_stats = {}
    for cond in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]:
        sub = auth_qwen[auth_qwen["condition"] == cond]
        k = sub["is_correct"].sum()
        n = len(sub)
        acc = k / n * 100
        low, high = wilson_ci(k, n)
        cond_stats[cond] = {"k": int(k), "n": int(n), "acc": round(acc, 1), "ci": [low, high]}
        print(f"  {cond}: {k}/{n} = {acc:.1f}% [95% CI: {low}%, {high}%]")
    
    # 2. Pairwise Differences & McNemar tests
    print("\n--- PAIRWISE CONTRASTS RELATIVE TO A_EN ---")
    piv = auth_qwen.pivot(index="semantic_id", columns="condition", values="is_correct")
    contrasts = {}
    for cond in ["B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]:
        # paired table
        ct = pd.crosstab(piv["A_EN"], piv[cond])
        b = ct.loc[1, 0] if (1 in ct.index and 0 in ct.columns) else 0
        c = ct.loc[0, 1] if (0 in ct.index and 1 in ct.columns) else 0
        diff = cond_stats[cond]["acc"] - cond_stats["A_EN"]["acc"]
        # McNemar exact / chi2
        stat = (abs(b - c) - 1)**2 / (b + c) if (b + c) > 0 else 0.0
        p_val = stats.chi2.sf(stat, df=1)
        contrasts[f"A_EN_vs_{cond}"] = {
            "diff": round(diff, 1),
            "b": int(b),
            "c": int(c),
            "chi2": round(stat, 4),
            "p_val": float(f"{p_val:.6g}")
        }
        print(f"  A_EN vs {cond}: Diff = {diff:+.1f}%, Discordant=(b={b}, c={c}), chi2={stat:.3f}, p={p_val:.6g}")
    
    # D_CS vs E_MIXED_SCRIPT
    ct_de = pd.crosstab(piv["D_CS"], piv["E_MIXED_SCRIPT"])
    b_de = ct_de.loc[1, 0] if (1 in ct_de.index and 0 in ct_de.columns) else 0
    c_de = ct_de.loc[0, 1] if (0 in ct_de.index and 1 in ct_de.columns) else 0
    diff_de = cond_stats["E_MIXED_SCRIPT"]["acc"] - cond_stats["D_CS"]["acc"]
    stat_de = (abs(b_de - c_de) - 1)**2 / (b_de + c_de) if (b_de + c_de) > 0 else 0.0
    p_de = stats.chi2.sf(stat_de, df=1)
    print(f"  D_CS vs E_MIXED_SCRIPT: Diff = {diff_de:+.1f}%, Discordant=(b={b_de}, c={c_de}), chi2={stat_de:.3f}, p={p_de:.6g}")
    
    # 3. Allam-2-7B on Authentic Core
    print("\n--- ALLAM-2-7B AUTHENTIC CORE ACCURACY ---")
    auth_allam = df[(df["is_authentic"] == True) & (df["model"] == "allam-2-7b")].copy()
    auth_allam["is_correct"] = (auth_allam["judge_label"] == 0).astype(int)
    allam_stats = {}
    for cond in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]:
        sub = auth_allam[auth_allam["condition"] == cond]
        k = sub["is_correct"].sum()
        n = len(sub)
        acc = k / n * 100
        allam_stats[cond] = {"k": int(k), "n": int(n), "acc": round(acc, 1)}
        print(f"  {cond}: {k}/{n} = {acc:.1f}%")
    allam_overall = auth_allam["is_correct"].mean() * 100
    print(f"  Overall Authentic Allam: {allam_overall:.1f}%")
    
    # 4. Rank correlation between Qwen and Allam
    q_vec = [cond_stats[c]["acc"] for c in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]]
    a_vec = [allam_stats[c]["acc"] for c in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]]
    rho, p_rho = stats.spearmanr(q_vec, a_vec)
    print(f"\n  Spearman rho(Qwen, Allam): {rho:.4f}, p = {p_rho:.4f}")
    
    # 5. Language Breakdown
    print("\n--- LANGUAGE BREAKDOWN (Qwen Authentic Core) ---")
    for lang in ["hi", "bn", "ta", "te", "kn"]:
        sub = auth_qwen[auth_qwen["language"] == lang]
        acc = sub["is_correct"].mean() * 100
        print(f"  {lang}: {sub['is_correct'].sum()}/{len(sub)} = {acc:.1f}%")
        
    # 6. GEE and Clustering
    print("\n--- GEE & CLUSTERING SUMMARY FROM PHASE 4 INVESTIGATION ---")
    with open("results/phase4/phase4_statistical_investigation.json", "r") as f:
        p4_data = json.load(f)
    gee = p4_data.get("gee_models", {})
    for lvl in ["level_1_unclustered", "level_2_semantic_id", "level_3_topic_id"]:
        info = gee.get(lvl, {})
        print(f"  {lvl}: clusters={info.get('n_clusters')}, beta={info.get('beta_cs')}, se={info.get('se_cs')}, p={info.get('p_value_cs')}")
    
    # 7. Prospective Power Calculation: 20 vs 45 topics
    print("\n--- PROSPECTIVE POWER VERIFICATION ---")
    icc = 0.2663
    m_cond = 5
    deff_cond = 1.0 + (m_cond - 1) * icc
    delta = 0.21
    var_p = 2 * 0.40 * 0.60
    z_alpha = 1.95996
    
    for n_top, name in [(20, "20 Topics (Empirical)"), (45, "45 Topics (Prospective)"), (50, "50 Topics")]:
        n_obs = n_top * m_cond
        se = math.sqrt(var_p * deff_cond / n_obs)
        z = (delta - z_alpha * se) / se
        pwr = stats.norm.cdf(z)
        mde = (z_alpha + 0.84162) * se
        print(f"  {name}: N_obs={n_obs}, SE={se:.5f}, z={z:.4f}, Power={pwr*100:.2f}%, MDE={mde*100:.2f}%")

    # 8. Script Transitions in E_MIXED_SCRIPT
    e_mixed = auth_qwen[auth_qwen["condition"] == "E_MIXED_SCRIPT"]
    # Check script transitions distribution
    # Let's count Roman words in native script
    import re
    def count_script_switches(text):
        # count transitions between latin and non-latin blocks
        tokens = text.split()
        transitions = 0
        prev_type = None
        for t in tokens:
            has_latin = bool(re.search(r'[a-zA-Z]', t))
            has_indic = bool(re.search(r'[\u0900-\u0D7F]', t))
            curr_type = "latin" if has_latin else ("indic" if has_indic else "other")
            if prev_type and curr_type != "other" and prev_type != "other" and curr_type != prev_type:
                transitions += 1
            if curr_type != "other":
                prev_type = curr_type
        return transitions

    switches = [count_script_switches(t) for t in e_mixed["prompt_text"]]
    print(f"\n  Mean script switches per prompt in E_MIXED_SCRIPT: {np.mean(switches):.2f} (median: {np.median(switches)})")

if __name__ == "__main__":
    main()
