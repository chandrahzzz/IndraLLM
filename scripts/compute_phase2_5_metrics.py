import pandas as pd
import numpy as np
from scipy import stats

def analyze():
    df = pd.read_csv('data/questions/IndraLLM-CS-v1.0/condition_prompts_10000.csv')
    print("=== OVERALL DATASET SHAPE ===")
    print(df.shape)
    
    print("\n=== CONDITION CMI DISTRIBUTION ===")
    records = []
    for cond in ['A_EN', 'B_NATIVE', 'C_ROMAN', 'D_CS', 'E_MIXED_SCRIPT']:
        grp = df[df['condition'] == cond]['measured_cmi']
        q25, q75 = grp.quantile(0.25), grp.quantile(0.75)
        records.append({
            'condition': cond,
            'mean': grp.mean(),
            'std': grp.std(),
            'median': grp.median(),
            'iqr': q75 - q25,
            'p95': grp.quantile(0.95),
            'min': grp.min(),
            'max': grp.max()
        })
    cmi_df = pd.DataFrame(records)
    print(cmi_df.to_string(index=False))

    print("\n=== CMI BY CONDITION AND LANGUAGE ===")
    pivot = df.groupby(['condition', 'language'])['measured_cmi'].agg(['mean', 'std', 'median']).round(2)
    print(pivot)

    print("\n=== CORRELATIONS WITH MEASURED CMI ===")
    num_cols = ['measured_cmi', 'token_count', 'script_transitions', 
                'english_token_ratio', 'indic_token_ratio', 
                'language_switch_count', 'switch_density', 'chars_per_token']
    corr_mat = df[num_cols].corr().round(4)
    print(corr_mat)

    print("\n=== SCRIPT TRANSITIONS VS LANGUAGE SWITCHES ===")
    for cond in ['A_EN', 'B_NATIVE', 'C_ROMAN', 'D_CS', 'E_MIXED_SCRIPT']:
        sub = df[df['condition'] == cond]
        print(f"Condition {cond}:")
        print(f"  Script Transitions: mean={sub['script_transitions'].mean():.2f}, std={sub['script_transitions'].std():.2f}, max={sub['script_transitions'].max()}")
        print(f"  Language Switches:  mean={sub['language_switch_count'].mean():.2f}, std={sub['language_switch_count'].std():.2f}, max={sub['language_switch_count'].max()}")
        print(f"  Token Count:        mean={sub['token_count'].mean():.2f}, std={sub['token_count'].std():.2f}")
        print(f"  Chars Per Token:    mean={sub['chars_per_token'].mean():.2f}, std={sub['chars_per_token'].std():.2f}")

    print("\n=== WITHIN-CONDITION VARIANCE IN D_CS AND E_MIXED_SCRIPT ===")
    for cond in ['D_CS', 'E_MIXED_SCRIPT']:
        sub = df[df['condition'] == cond]['measured_cmi']
        print(f"{cond} CMI: Variance={sub.var():.2f}, Range=({sub.min():.2f}, {sub.max():.2f}), Non-zero count={(sub > 0).sum()}/{len(sub)}")

    print("\n=== D_CS BY LANGUAGE ===")
    d_cs = df[df['condition'] == 'D_CS']
    print(d_cs.groupby('language')['measured_cmi'].agg(['count', 'mean', 'std', 'var', 'min', 'median', 'max']).round(2))

    print("\n=== E_MIXED_SCRIPT BY LANGUAGE ===")
    e_ms = df[df['condition'] == 'E_MIXED_SCRIPT']
    print(e_ms.groupby('language')['measured_cmi'].agg(['count', 'mean', 'std', 'var', 'min', 'median', 'max']).round(2))

    # ANOVA: Condition effect on CMI
    grand_mean = df['measured_cmi'].mean()
    between_ss = sum(len(g) * ((g['measured_cmi'].mean() - grand_mean) ** 2) for _, g in df.groupby('condition'))
    within_ss = sum(((g['measured_cmi'] - g['measured_cmi'].mean()) ** 2).sum() for _, g in df.groupby('condition'))
    total_ss = between_ss + within_ss
    eta_sq = between_ss / total_ss
    df_between = df['condition'].nunique() - 1
    df_within = len(df) - df['condition'].nunique()
    ms_between = between_ss / df_between
    ms_within = within_ss / df_within
    f_stat = ms_between / ms_within
    p_val = stats.f.sf(f_stat, df_between, df_within)
    print(f"\n=== ANOVA FOR CMI BY CONDITION ===")
    print(f"Between SS: {between_ss:.2f} (df={df_between}), Within SS: {within_ss:.2f} (df={df_within})")
    print(f"F-statistic: {f_stat:.2f}, p-value: {p_val}, Eta-squared: {eta_sq:.4f}")

if __name__ == '__main__':
    analyze()
