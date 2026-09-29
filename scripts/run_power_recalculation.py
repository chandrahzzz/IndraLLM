import math
import numpy as np
from scipy import stats

def compute_mcnemar_power(n, p_discordant, p_diff, alpha=0.05):
    # p_diff = |p10 - p01|, p_discordant = p10 + p01
    # Under H0, test statistic (b - c)^2 / (b + c) ~ chi2(1)
    # Under H1, normal approximation with non-centrality
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    # expected discordant pairs = n * p_discordant
    n_d = n * p_discordant
    if n_d <= 0:
        return 0.0
    # effect size = p_diff / sqrt(p_discordant)
    delta = (n * p_diff) / math.sqrt(n_d)
    power = 1 - stats.norm.cdf(z_alpha - delta) + stats.norm.cdf(-z_alpha - delta)
    return float(power)

def find_mde(n, p_discordant, target_power=0.80, alpha=0.05):
    # binary search for p_diff
    low, high = 0.001, p_discordant
    for _ in range(100):
        mid = (low + high) / 2
        p = compute_mcnemar_power(n, p_discordant, mid, alpha)
        if p < target_power:
            low = mid
        else:
            high = mid
    return mid

print("=== POWER ANALYSIS FOR PAIRED REPEATED MEASURES (CLUSTERS = SEMANTIC GROUPS) ===")

# Test-ID: N = 200 semantic groups
# Test-OOD: N = 100 semantic groups
results = {}

for name, n in [('Test-ID', 200), ('Test-OOD', 100)]:
    # Primary planned contrasts: A_EN vs B_NATIVE, A_EN vs D_CS, B_NATIVE vs D_CS, D_CS vs E_MIXED_SCRIPT
    # Assume discordant proportion p_disc in range [0.15, 0.25, 0.35]
    print(f"\n--- {name} (N = {n} semantic groups) ---")
    results[name] = {}
    for p_disc in [0.15, 0.20, 0.25, 0.30]:
        mde_80 = find_mde(n, p_disc, target_power=0.80)
        mde_90 = find_mde(n, p_disc, target_power=0.90)
        # CI expected width for paired difference in proportions: 2 * 1.96 * sqrt(p_disc / n)
        ci_width = 2 * 1.96 * math.sqrt(p_disc / n)
        
        # Power for realistic anticipated effects: delta = 5%, 8%, 10%, 12%, 15%
        powers = {}
        for d in [0.05, 0.08, 0.10, 0.12, 0.15]:
            powers[f"diff_{int(d*100)}pct"] = round(compute_mcnemar_power(n, p_disc, d), 4) if d <= p_disc else 1.0
            
        results[name][f"disc_{int(p_disc*100)}pct"] = {
            'mde_80pct_power': round(mde_80, 4),
            'mde_90pct_power': round(mde_90, 4),
            'expected_95ci_width': round(ci_width, 4),
            'powers': powers
        }
        print(f"Discordant rate {p_disc*100:.0f}%: MDE(80%) = {mde_80*100:.2f}%, MDE(90%) = {mde_90*100:.2f}%, 95% CI Width = ±{ci_width*50:.2f}% (Total {ci_width*100:.2f}%)")
        print(f"  Power for 5% effect: {powers['diff_5pct']*100:.1f}%, 8% effect: {powers['diff_8pct']*100:.1f}%, 10% effect: {powers['diff_10pct']*100:.1f}%, 15% effect: {powers['diff_15pct']*100:.1f}%")

# Save results for markdown inclusion
import json
with open('research/scratch_power_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nPower calculations completed and written to research/scratch_power_results.json")
